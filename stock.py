import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

lr = 0.01
epochs = 1000
LOOKBACK = 50

df = pd.read_csv("stock_data/apple.csv")
df = df[["Open","High","Low","Close/Last","Volume"]]

df["Open"] = df["Open"].str.replace("$","", regex=False).astype(float)
df["Close/Last"] = df["Close/Last"].str.replace("$","", regex=False).astype(float)

diff = df["Open"].values - df["Close/Last"].values

X = []
Y = []

for i in range(len(diff) - LOOKBACK):
    X.append(diff[i:i+LOOKBACK])
    Y.append(diff[i+LOOKBACK])

X = np.array(X)
Y = np.array(Y)

split = int(len(X) * 0.8)

X_train, X_test = X[:split], X[split:]
Y_train, Y_test = Y[:split], Y[split:]

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
    return (x > 0)

for epoch in range(epochs):

    z1 = X_train @ W1 + b1
    a1 = relu(z1)
    y_pred = a1 @ W2 + b2

    loss = np.mean((y_pred - Y_train.reshape(-1,1))**2)
    loss_history.append(loss)

    if not np.isfinite(loss):
        break

    dloss = 2*(y_pred - Y_train.reshape(-1,1)) / len(X_train)

    dW2 = a1.T @ dloss
    db2 = np.sum(dloss, axis=0, keepdims=True)

    da1 = dloss @ W2.T
    dz1 = da1 * relu_deriv(z1)

    dW1 = X_train.T @ dz1
    db1 = np.sum(dz1, axis=0, keepdims=True)

    W2 -= lr * dW2
    b2 -= lr * db2
    W1 -= lr * dW1
    b1 -= lr * db1

    if epoch % 100 == 0:
        print(f"Epoch {epoch} | Loss: {loss:.6f}")

z1 = X_test @ W1 + b1
a1 = relu(z1)
pred = (a1 @ W2 + b2).flatten()

plt.figure(figsize=(14,5))
plt.plot(Y_test, label="Real", linewidth=2)
plt.plot(pred, label="Predicted", linewidth=2)
plt.legend()
plt.title("Real vs Predicted")
plt.show()

plt.figure(figsize=(10,4))
plt.plot(loss_history)
plt.title("Training Loss")
plt.show()
