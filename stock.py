# This train a model to predict if the following day return will be positive or negative

import glob
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

LOOKBACK = 50
EPOCHS = 60
BATCH = 128
LR = 1e-3
THRESH = 0.001      # noise filter for labels
DATA_DIR = 'stock_data'


def load_df(path):
    df = pd.read_csv(path)
    df = df[['Date','Close/Last','Volume','Open','High','Low']].copy()
    
    # remove any $ sign otherwise it will be taken for a string 
    for c in ['Close/Last','Open','High','Low']:
        df[c] = df[c].str.replace('$','', regex=False).astype(float)
    df['Volume'] = df['Volume'].astype(float)
    
    return df.sort_values('Date').reset_index(drop=True)


def make_features(df):
    # base features
    close = df['Close/Last'].values
    openp = df['Open'].values
    high = df['High'].values
    low = df['Low'].values
    vol = df['Volume'].values

    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]

    ret = (close - prev_close) / (prev_close + 1e-9) # return on invest
    intraday = (close - openp) / (openp + 1e-9)
    range_pct = (high - low) / (openp + 1e-9)
    vol_change = np.concatenate([[0], np.diff(vol) / (vol[:-1] + 1e-9)])

    df_feat = pd.DataFrame({
        'ret': ret,
        'intraday': intraday,
        'range_pct': range_pct,
        'vol_change': vol_change,
        'ma5': pd.Series(ret).rolling(5, min_periods=1).mean(),# averages
        'ma10': pd.Series(ret).rolling(10, min_periods=1).mean(),
        'std5': pd.Series(ret).rolling(5, min_periods=1).std().fillna(0), # 5 day volatility
    }).fillna(0)

    return df_feat.values.astype(np.float32)


def sliding_windows(X, lookback):
    return np.lib.stride_tricks.sliding_window_view(
        X, (lookback, X.shape[1])
    )[:,0]


X_all, y_all, cid_all = [], [], []

files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
# loop to get data from files and process it
for cid, f in enumerate(files):
    df = load_df(f)
    feats = make_features(df)

    # if ther is not enough data
    n = len(feats)
    if n <= LOOKBACK:
        continue
    
    # scale data to prevent explosion
    scaler = StandardScaler()
    feats = scaler.fit_transform(feats)

    # make windows (0:49, 1:50, ...)
    windows = sliding_windows(feats, LOOKBACK)
    windows = windows[:-1]   # drop last unmatched window

    next_ret = feats[LOOKBACK:, 0]
    labels = (next_ret > THRESH).astype(np.int32) # create label 1|0 depending on + or -

    X_all.append(windows)
    y_all.append(labels)
    cid_all.append(np.full(len(labels), cid))


X = np.vstack(X_all)
y = np.concatenate(y_all)
company_idx = np.concatenate(cid_all)


X_train, X_test, y_train, y_test, cid_train, cid_test = train_test_split(
    X, y, company_idx,
    test_size=0.2,
    stratify=y,
    random_state=1
)

# to equalize the model
class_weights_arr = compute_class_weight(
    'balanced',
    classes=np.unique(y_train),
    y=y_train
)

class_weights = {i: w for i, w in enumerate(class_weights_arr)}


model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(LOOKBACK, X.shape[2])),# price trend, momentum patern, volatility sign
    Dropout(0.3), # to prevent memorization
    LSTM(32), # overall state
    Dropout(0.3), # same as previous
    Dense(1, activation='sigmoid') # output
])

# optimisation
opt = tf.keras.optimizers.Adam(
    learning_rate=LR,
    beta_1=0.9
)

model.compile(
    optimizer=opt,
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# to prevent overfitting
es = EarlyStopping(
    monitor='val_loss',
    patience=8,
    restore_best_weights=True,
    verbose=1
)

history = model.fit(
    X_train, y_train,
    validation_split=0.15,
    epochs=EPOCHS,
    batch_size=BATCH,
    class_weight=class_weights,
    callbacks=[es],
    verbose=1
)

# test the model
probs = model.predict(X_test, batch_size=256).ravel()
preds = (probs > 0.5).astype(int)

print('Accuracy:', accuracy_score(y_test, preds))
print('Confusion matrix:\n', confusion_matrix(y_test, preds))
print(classification_report(y_test, preds, digits=4))

print('Per-company accuracies (test):')
for cid in np.unique(cid_test):
    mask = cid_test == cid
    print(cid, round(accuracy_score(y_test[mask], preds[mask]), 4))

if bool(input("enregistrer ?")):
    model.save('stock.keras')
