import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

lr = 0.05
epochs = 1000
LOOKBACK = 5

df = pd.read_csv("stock_data/apple.csv")
df = df[["Open","High","Low","Close/Last","Volume"]]

for col in ["Open","High","Low","Close/Last"]:
    df[col] = df[col].str.replace("$","", regex=False).astype(float)

df["Volume"] = df["Volume"].astype(float)

df["Return"] = df["Close/Last"].pct_change()
df["Range"]  = (df["High"] - df["Low"]) / df["Low"]
df["SMA5"]   = df["Close/Last"].rolling(5).mean()
df["SMA10"]  = df["Close/Last"].rolling(10).mean()

delta = df["Close/Last"].diff()
gain  = delta.clip(lower=0).rolling(14).mean()
loss  = (-delta.clip(upper=0)).rolling(14).mean()
df["RSI"] = 100 - (100 / (1 + gain / loss))

df = df.bfill()

feature_cols = df.columns
mean = df.mean()
std  = df.std()

df_norm = (df - mean) / std  # normalized data

X, y = [], []
values = df_norm.values

for i in range(LOOKBACK, len(values)):
    X.append(values[i-LOOKBACK:i])
    y.append(values[i, feature_cols.get_loc("Close/Last")])  # normalized target

X = np.array(X)
y = np.array(y)

split = int(len(X)*0.8)
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

X_train = X_train.reshape(len(X_train), -1)
X_test  = X_test.reshape(len(X_test), -1)

n_features = X_train.shape[1]

np.random.seed(1)
H = 64

W1 = np.random.randn(n_features, H) / np.sqrt(n_features)
b1 = np.zeros((1, H))

W2 = np.random.randn(H, 1) / np.sqrt(H)
b2 = np.zeros((1, 1))

loss_history = []

def relu(x):
    return np.maximum(0, x)

def relu_deriv(x):
    return (x > 0).astype(float)

for epoch in range(epochs):

    z1 = X_train @ W1 + b1
    a1 = relu(z1)
    y_pred = a1 @ W2 + b2

    loss = np.mean((y_pred - y_train.reshape(-1,1))**2)
    loss_history.append(loss)

    dloss = 2*(y_pred - y_train.reshape(-1,1)) / len(X_train)

    dW2 = a1.T @ dloss
    db2 = np.sum(dloss, axis=0, keepdims=True)

    da1 = dloss @ W2.T
    dz1 = da1 * relu_deriv(z1)

    dW1 = X_train.T @ dz1
    db1 = np.sum(dz1, axis=0, keepdims=True)

    # gradient descent
    W2 -= lr * dW2
    b2 -= lr * db2
    W1 -= lr * dW1
    b1 -= lr * db1

    if epoch % 100 == 0:
        print("Epoch", epoch, "Loss:", loss)

z1 = X_test @ W1 + b1
a1 = relu(z1)
pred_norm = (a1 @ W2 + b2).flatten()

# denormalize predictions and real values
real = y_test * std["Close/Last"] + mean["Close/Last"]
pred = pred_norm * std["Close/Last"] + mean["Close/Last"]

plt.figure(figsize=(14,5))
plt.plot(real, label="Real", linewidth=2)
plt.plot(pred,  label="Predicted", linewidth=2)
plt.legend()
plt.title("Apple – Real vs Predicted")
plt.show()

plt.figure(figsize=(10,4))
plt.plot(pd.Series(loss_history))
plt.title("Smoothed Loss")
plt.show()
