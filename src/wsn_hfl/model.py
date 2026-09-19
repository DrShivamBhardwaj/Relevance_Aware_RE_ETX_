import numpy as np


def add_bias(x: np.ndarray) -> np.ndarray:
    return np.concatenate([x, np.ones((x.shape[0], 1), dtype=x.dtype)], axis=1)


def softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(z)
    return exp / exp.sum(axis=1, keepdims=True)


def loss_and_grad(w: np.ndarray, x: np.ndarray, y: np.ndarray, l2: float = 0.0):
    xb = add_bias(x)
    probs = softmax(xb @ w)
    n = x.shape[0]
    loss = -np.log(np.clip(probs[np.arange(n), y], 1e-12, 1.0)).mean()
    loss += 0.5 * l2 * float(np.sum(w[:-1] ** 2))
    onehot = np.zeros_like(probs)
    onehot[np.arange(n), y] = 1.0
    grad = xb.T @ (probs - onehot) / n
    grad[:-1] += l2 * w[:-1]
    return float(loss), grad


def local_train(w: np.ndarray, x: np.ndarray, y: np.ndarray, steps: int, lr: float, l2: float):
    w_local = w.copy()
    before, _ = loss_and_grad(w_local, x, y, l2)
    for _ in range(steps):
        _, grad = loss_and_grad(w_local, x, y, l2)
        w_local -= lr * grad
    after, _ = loss_and_grad(w_local, x, y, l2)
    return w_local - w, before, after
def predict(w: np.ndarray, x: np.ndarray) -> np.ndarray:
    xb = add_bias(x)
    return np.argmax(xb @ w, axis=1)


def accuracy(w: np.ndarray, x: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean(predict(w, x) == y))


def macro_f1(w: np.ndarray, x: np.ndarray, y: np.ndarray, num_classes: int) -> float:
    pred = predict(w, x)
    scores = []
    for c in range(num_classes):
        tp = np.sum((pred == c) & (y == c))
        fp = np.sum((pred == c) & (y != c))
        fn = np.sum((pred != c) & (y == c))
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        if precision + recall == 0:
            scores.append(0.0)
        else:
            scores.append(float(2 * precision * recall / (precision + recall)))
    return float(np.mean(scores))


def cosine_novelty(update: np.ndarray, reference: np.ndarray) -> float:
    a = update.ravel()
    b = reference.ravel()
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom <= 1e-12:
        return 1.0
    cos = float(np.dot(a, b) / denom)
    return float(np.clip(1.0 - cos, 0.0, 2.0) / 2.0)


def topk_compress(update: np.ndarray, ratio: float, residual: np.ndarray):
    effective = update + residual
    flat = effective.ravel()
    k = max(1, int(np.ceil(flat.size * ratio)))
    if k >= flat.size:
        compressed = effective.copy()
        new_residual = np.zeros_like(effective)
        return compressed, new_residual, flat.size
    idx = np.argpartition(np.abs(flat), -k)[-k:]
    out = np.zeros_like(flat)
    out[idx] = flat[idx]
    compressed = out.reshape(effective.shape)
    new_residual = effective - compressed
    return compressed, new_residual, k
