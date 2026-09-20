import numpy as np

from .config import SimConfig


def _class_probabilities(cfg: SimConfig, rng: np.random.Generator, difficulty: np.ndarray):
    probs = []
    order = np.argsort(difficulty)
    rank = np.empty_like(order, dtype=float)
    rank[order] = np.linspace(0.0, 1.0, len(order))
    for i in range(cfg.num_clients):
        alpha = np.full(cfg.num_classes, cfg.noniid_alpha, dtype=float)
        rare_bias = cfg.correlation * rank[i]
        if rng.random() < rare_bias:
            alpha[-1] += cfg.rare_class_boost
        else:
            dominant = int(rng.integers(0, cfg.num_classes - 1))
            alpha[dominant] += 2.5
        probs.append(rng.dirichlet(alpha))
    return np.asarray(probs)


def make_synthetic_data(cfg: SimConfig, rng: np.random.Generator, route_difficulty: np.ndarray):
    centers = rng.normal(0.0, cfg.class_separation, size=(cfg.num_classes, cfg.feature_dim))
    client_probs = _class_probabilities(cfg, rng, route_difficulty)
    client_data = []
    for i in range(cfg.num_clients):
        y = rng.choice(cfg.num_classes, size=cfg.samples_per_client, p=client_probs[i])
        if cfg.label_noise > 0:
            flip = rng.random(cfg.samples_per_client) < cfg.label_noise
            y[flip] = rng.integers(0, cfg.num_classes, size=int(flip.sum()))
        x = centers[y] + rng.normal(0.0, cfg.feature_noise, size=(cfg.samples_per_client, cfg.feature_dim))
        client_data.append((x.astype(np.float64), y.astype(np.int64)))
    y_test = rng.integers(0, cfg.num_classes, size=cfg.test_samples)
    x_test = centers[y_test] + rng.normal(0.0, cfg.feature_noise, size=(cfg.test_samples, cfg.feature_dim))
    return client_data, (x_test.astype(np.float64), y_test.astype(np.int64)), client_probs


def class_coverage(client_probs: np.ndarray, weights: np.ndarray) -> np.ndarray:
    weights = np.asarray(weights, dtype=float)
    if weights.sum() <= 0:
        return np.full(client_probs.shape[1], 1.0 / client_probs.shape[1])
    weights = weights / weights.sum()
    coverage = weights @ client_probs
    return coverage / max(coverage.sum(), 1e-12)


def js_divergence(p: np.ndarray, q: np.ndarray) -> float:
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    p = p / max(p.sum(), 1e-12)
    q = q / max(q.sum(), 1e-12)
    m = 0.5 * (p + q)

    def kl(a, b):
        mask = a > 0
        ratio = a[mask] / np.clip(b[mask], 1e-12, None)
        return float(np.sum(a[mask] * np.log(np.clip(ratio, 1e-12, None))))

    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def hierarchical_cloud_influence(edge_weights, edge_members, n_clients):
    """Return exact per-client coefficients used by two-level aggregation.

    edge_weights are the unnormalised edge totals used for cloud aggregation.
    edge_members[g] contains (client_id, within_edge_normalised_weight) pairs.
    The returned vector therefore applies both hierarchy levels and sums to one
    whenever at least one edge contributes.
    """
    ew = np.asarray(edge_weights, dtype=float)
    out = np.zeros(int(n_clients), dtype=float)
    if ew.size == 0 or ew.sum() <= 0:
        return out
    ew = ew / ew.sum()
    for edge_coeff, members in zip(ew, edge_members):
        for client, local_coeff in members:
            out[int(client)] += float(edge_coeff) * float(local_coeff)
    return out
