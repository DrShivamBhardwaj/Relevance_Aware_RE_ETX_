import numpy as np

from .config import SimConfig


def _unit_interval(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    lo = float(np.min(x))
    hi = float(np.max(x))
    if hi - lo <= 1e-12:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


def route_pressure(routes, relay_queue: np.ndarray, n_clients: int) -> np.ndarray:
    pressure = np.zeros(n_clients, dtype=float)
    for i, route in enumerate(routes):
        if route.relays:
            pressure[i] = float(sum(relay_queue[r] for r in route.relays))
    return _unit_interval(pressure)


def adaptive_ratio(
    cfg: SimConfig,
    utility: float,
    route_cost: float,
    scarcity: float,
    relay_pressure: float,
) -> float:
    """Discrete client-specific Top-k ratio used by the proposed controller.

    The executed scarcity coefficient is 0.5. This function is also reused by
    compression-matched control baselines so that client selection can be
    compared without confounding it with a different compression policy.
    """
    best_rho = cfg.fixed_compression_ratio
    best_obj = float("inf")
    for rho in cfg.compression_candidates:
        if rho < cfg.min_compression_ratio:
            continue
        network_term = rho * (
            route_cost + 0.5 * scarcity + cfg.relay_pressure_weight * relay_pressure
        )
        distortion = cfg.compression_distortion_weight * utility * (1.0 - rho) ** 2
        obj = network_term + distortion
        if obj < best_obj:
            best_obj = obj
            best_rho = float(rho)
    return best_rho


def representative_subset(
    candidates: np.ndarray,
    stat_vectors: np.ndarray,
    k: int,
    capability_cost: np.ndarray,
    cost_weight: float = 0.15,
):
    """Greedy facility-location subset for the FedCG-adapted comparator.

    FedCG selects a gradient-diverse representative subset using submodular
    optimization and then adapts compression to heterogeneous capabilities.
    The original FedCG communication model is not multi-hop HFL, so this
    comparator adapts its representative-gradient principle to the same WSN
    candidate pool and route-capability measurements used by all methods.
    It is intentionally named *adapted*, not an exact reproduction.
    """
    cand = np.asarray(candidates, dtype=int)
    if cand.size <= k:
        return cand.copy()
    V = np.asarray(stat_vectors, dtype=float)[cand]
    V = V.reshape(len(cand), -1)
    norms = np.linalg.norm(V, axis=1, keepdims=True)
    Vn = V / np.maximum(norms, 1e-12)
    sim = np.clip((Vn @ Vn.T + 1.0) * 0.5, 0.0, 1.0)
    costs = _unit_interval(np.asarray(capability_cost, dtype=float))[cand]
    covered = np.zeros(len(cand), dtype=float)
    selected_local = []
    available = set(range(len(cand)))
    # Facility-location gain is O(|C|); scale the capability penalty likewise.
    penalty_scale = cost_weight * len(cand)
    for _ in range(min(k, len(cand))):
        best_j = None
        best_gain = -np.inf
        for j in available:
            gain = float(np.maximum(covered, sim[:, j]).sum() - covered.sum())
            gain -= penalty_scale * float(costs[j])
            if gain > best_gain:
                best_gain = gain
                best_j = j
        selected_local.append(best_j)
        covered = np.maximum(covered, sim[:, best_j])
        available.remove(best_j)
    return cand[np.asarray(selected_local, dtype=int)]


def schedule(
    method: str,
    cfg: SimConfig,
    rng: np.random.Generator,
    eligible: np.ndarray,
    utility: np.ndarray,
    routes,
    residual_energy: np.ndarray,
    initial_energy: np.ndarray,
    deficit_queue: np.ndarray,
    relay_queue: np.ndarray,
    stat_vectors: np.ndarray | None = None,
):
    candidates = np.flatnonzero(eligible)
    if candidates.size == 0:
        return [], {}
    k = min(cfg.clients_per_round, candidates.size)
    route_cost = _unit_interval(np.array([r.cost for r in routes], dtype=float))
    scarcity = _unit_interval(
        np.maximum(initial_energy / np.maximum(residual_energy, 1e-9) - 1.0, 0.0)
    )
    pressure = route_pressure(routes, relay_queue, cfg.num_clients)
    if method == "proposed_no_relay":
        pressure[:] = 0.0
    util = _unit_interval(utility)
    ratios = {int(i): cfg.fixed_compression_ratio for i in candidates}

    base_method = method.removesuffix("_adaptive")
    if base_method == "random":
        selected = rng.choice(candidates, size=k, replace=False)
    elif base_method == "resource":
        score = route_cost + scarcity + pressure
        selected = candidates[np.argsort(score[candidates])[:k]]
    elif base_method == "utility":
        selected = candidates[np.argsort(-util[candidates])[:k]]
    elif method == "fedcg_adapted":
        if stat_vectors is None:
            raise ValueError("fedcg_adapted requires current client gradient/statistical vectors")
        capability = route_cost + scarcity
        selected = representative_subset(candidates, stat_vectors, k, capability)
    elif method.startswith("proposed"):
        score = np.full(cfg.num_clients, -np.inf, dtype=float)
        for i in candidates:
            rho = (
                cfg.fixed_compression_ratio
                if method == "proposed_fixed_comp"
                else adaptive_ratio(cfg, util[i], route_cost[i], scarcity[i], pressure[i])
            )
            ratios[int(i)] = rho
            deficit_term = 0.0 if method == "proposed_no_rep" else deficit_queue[i]
            score[i] = (
                cfg.drift_v * util[i]
                + deficit_term
                - cfg.drift_v
                * rho
                * (
                    route_cost[i]
                    + 0.5 * scarcity[i]
                    + cfg.relay_pressure_weight * pressure[i]
                )
            )
        selected = candidates[np.argsort(-score[candidates])[:k]]
    else:
        raise ValueError(f"Unknown method: {method}")

    if method.endswith("_adaptive"):
        for i in selected:
            ratios[int(i)] = adaptive_ratio(
                cfg, util[i], route_cost[i], scarcity[i], pressure[i]
            )
    elif method == "fedcg_adapted":
        # Capability-aware compression without importing the proposed
        # representation-deficit or relay-queue terms into this comparator.
        for i in selected:
            ratios[int(i)] = adaptive_ratio(
                cfg, util[i], route_cost[i], scarcity[i], 0.0
            )

    return [int(i) for i in selected], ratios
