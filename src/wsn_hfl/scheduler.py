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


def adaptive_ratio(cfg: SimConfig, utility: float, route_cost: float, scarcity: float, relay_pressure: float) -> float:
    best_rho = cfg.fixed_compression_ratio
    best_obj = float("inf")
    for rho in cfg.compression_candidates:
        if rho < cfg.min_compression_ratio:
            continue
        network_term = rho * (route_cost + 0.5 * scarcity + relay_pressure)
        distortion = cfg.compression_distortion_weight * utility * (1.0 - rho) ** 2
        obj = network_term + distortion
        if obj < best_obj:
            best_obj = obj
            best_rho = float(rho)
    return best_rho
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
):
    candidates = np.flatnonzero(eligible)
    if candidates.size == 0:
        return [], {}
    k = min(cfg.clients_per_round, candidates.size)
    route_cost = _unit_interval(np.array([r.cost for r in routes], dtype=float))
    scarcity = _unit_interval(np.maximum(initial_energy / np.maximum(residual_energy, 1e-9) - 1.0, 0.0))
    pressure = route_pressure(routes, relay_queue, cfg.num_clients)
    util = _unit_interval(utility)
    ratios = {int(i): cfg.fixed_compression_ratio for i in candidates}

    if method == "random":
        selected = rng.choice(candidates, size=k, replace=False)
    elif method == "resource":
        score = route_cost + scarcity + pressure
        selected = candidates[np.argsort(score[candidates])[:k]]
    elif method == "utility":
        selected = candidates[np.argsort(-util[candidates])[:k]]
    elif method == "proposed":
        score = np.full(cfg.num_clients, -np.inf, dtype=float)
        for i in candidates:
            rho = adaptive_ratio(cfg, util[i], route_cost[i], scarcity[i], pressure[i])
            ratios[int(i)] = rho
            comm_penalty = rho * (route_cost[i] + 0.5 * scarcity[i] + pressure[i])
            score[i] = cfg.drift_v * util[i] + deficit_queue[i] - cfg.drift_v * comm_penalty
        selected = candidates[np.argsort(-score[candidates])[:k]]
    else:
        raise ValueError(f"Unknown method: {method}")

    return [int(i) for i in selected], ratios
