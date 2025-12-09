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
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.callbacks import EarlyStopping

LOOKBACK = 50
EPOCHS = 60
BATCH = 64
LR = 1e-3
THRESH = 0.0
DATA_DIR = 'stock_data'

def load_df(path):
    df = pd.read_csv(path)
    df = df[['Date','Close/Last','Volume','Open','High','Low']].copy()
    for c in ['Close/Last','Open','High','Low']:
        df[c] = df[c].str.replace('$','', regex=False).astype(float)
    df['Volume'] = df['Volume'].astype(float)
    df = df.sort_values('Date').reset_index(drop=True)
    return df

def make_features(df):
    close = df['Close/Last'].values
    openp = df['Open'].values
    high = df['High'].values
    low = df['Low'].values
    vol = df['Volume'].values
    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]
    ret = (close - prev_close) / (prev_close + 1e-9)
    intraday = (close - openp) / (openp + 1e-9)
    range_pct = (high - low) / (openp + 1e-9)
    vol_change = np.concatenate([[0.0], (vol[1:] - vol[:-1]) / (vol[:-1] + 1e-9)])
    df_feat = pd.DataFrame({
        'ret': ret,
        'intraday': intraday,
        'range_pct': range_pct,
        'vol_change': vol_change,
        'close': close
    })
    df_feat['ma5'] = df_feat['ret'].rolling(5, min_periods=1).mean()
    df_feat['ma10'] = df_feat['ret'].rolling(10, min_periods=1).mean()
    df_feat['std5'] = df_feat['ret'].rolling(5, min_periods=1).std().fillna(0)
    return df_feat.fillna(0)

X_windows = []
y_labels = []
company_idx = []
files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
for cid, f in enumerate(files):
    df = load_df(f)
    feats = make_features(df).values
    scaler = StandardScaler()
    feats = scaler.fit_transform(feats)
    n = len(feats)
    for i in range(n - LOOKBACK - 1):
        window = feats[i:i+LOOKBACK]
        next_ret = feats[i+LOOKBACK, 0]
        label = 1 if next_ret > THRESH else 0
        X_windows.append(window)
        y_labels.append(label)
        company_idx.append(cid)

X = np.array(X_windows, dtype=np.float32)
y = np.array(y_labels, dtype=np.int32)
company_idx = np.array(company_idx, dtype=np.int32)

X_train, X_test, y_train, y_test, cid_train, cid_test = train_test_split(
    X, y, company_idx, test_size=0.2, stratify=y, random_state=1
)

class_weights_arr = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
class_weights = {i: w for i, w in enumerate(class_weights_arr)}

model = Sequential([
    Bidirectional(LSTM(64, return_sequences=True), input_shape=(LOOKBACK, X.shape[2])),
    Dropout(0.2),
    LSTM(32),
    Dropout(0.2),
    Dense(1, activation='sigmoid')
])
opt = tf.keras.optimizers.Adam(learning_rate=LR)
model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy'])

es = EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True, verbose=1)

history = model.fit(
    X_train, y_train,
    validation_split=0.15,
    epochs=EPOCHS,
    batch_size=BATCH,
    class_weight=class_weights,
    callbacks=[es],
    verbose=1
)

probs = model.predict(X_test, batch_size=256).flatten()
preds = (probs > 0.5).astype(int)

print('Accuracy:', accuracy_score(y_test, preds))
print('Confusion matrix:\n', confusion_matrix(y_test, preds))
print(classification_report(y_test, preds, digits=4))

per_company = {}
for cid in np.unique(cid_test):
    mask = cid_test == cid
    if mask.sum() == 0: continue
    acc = accuracy_score(y_test[mask], preds[mask])
    per_company[cid] = acc
print('Per-company accuracies (test):')
for k,v in per_company.items():
    print(k, round(v,4))

if bool(input("enregistrer ?")):
    model.save('stock.keras')