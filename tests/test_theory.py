from dataclasses import replace
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wsn_hfl.config import SimConfig
from wsn_hfl.model import topk_compress
from wsn_hfl.scheduler import adaptive_ratio, schedule


class Route:
    def __init__(self, cost, relays=()):
        self.cost = float(cost)
        self.relays = tuple(relays)


def test_participation_queue_finite_horizon_bound():
    pi = np.array([
        [0.50, 0.30, 0.20],
        [0.40, 0.35, 0.25],
        [0.30, 0.40, 0.30],
        [0.45, 0.25, 0.30],
    ])
    a = np.array([
        [0.50, 0.50, 0.00],
        [0.50, 0.00, 0.50],
        [0.00, 0.50, 0.50],
        [0.50, 0.50, 0.00],
    ])
    q = np.zeros(3)
    q0 = q.copy()
    for t in range(len(pi)):
        q = np.maximum(0.0, q + pi[t] - a[t])
    lhs = np.sum(pi - a, axis=0)
    np.testing.assert_array_less(lhs - (q - q0), np.full(3, 1e-12))


def test_relay_queue_finite_horizon_bound():
    budget = np.array([0.20, 0.10])
    energy = np.array([
        [0.25, 0.05],
        [0.10, 0.12],
        [0.30, 0.08],
        [0.05, 0.15],
    ])
    z = np.zeros(2)
    z0 = z.copy()
    for e in energy:
        z = np.maximum(0.0, z + e - budget)
    lhs = np.sum(energy - budget, axis=0)
    np.testing.assert_array_less(lhs - (z - z0), np.full(2, 1e-12))


def test_adaptive_ratio_is_exact_finite_set_minimizer():
    cfg = SimConfig()
    utility = 0.73
    route_cost = 0.62
    scarcity = 0.35
    pressure = 0.48
    chosen = adaptive_ratio(cfg, utility, route_cost, scarcity, pressure)
    objectives = {}
    for rho in cfg.compression_candidates:
        network = rho * (
            route_cost + 0.5 * scarcity + cfg.relay_pressure_weight * pressure
        )
        distortion = cfg.compression_distortion_weight * utility * (1.0 - rho) ** 2
        objectives[float(rho)] = network + distortion
    exact = min(objectives, key=objectives.get)
    assert chosen == exact


def test_scheduler_returns_top_k_of_implemented_score():
    cfg = replace(SimConfig(), num_clients=4, clients_per_round=2)
    rng = np.random.default_rng(1)
    eligible = np.array([True, True, True, True])
    utility = np.array([0.2, 0.9, 0.6, 0.4])
    routes = [Route(1.0), Route(2.0), Route(1.4), Route(3.0)]
    residual = np.array([9.0, 9.0, 9.0, 9.0])
    initial = np.array([10.0, 10.0, 10.0, 10.0])
    deficit = np.array([0.2, 0.1, 0.8, 0.0])
    relay_queue = np.zeros(4)

    selected, ratios = schedule(
        "proposed", cfg, rng, eligible, utility, routes,
        residual, initial, deficit, relay_queue,
    )

    route_cost = (np.array([r.cost for r in routes]) - 1.0) / 2.0
    scarcity_raw = initial / residual - 1.0
    scarcity = np.zeros_like(scarcity_raw)  # all clients have equal scarcity
    util = (utility - utility.min()) / (utility.max() - utility.min())
    scores = []
    for i in range(4):
        rho = ratios[i]
        comm = rho * (route_cost[i] + 0.5 * scarcity[i])
        scores.append(cfg.drift_v * util[i] + deficit[i] - cfg.drift_v * comm)
    expected = set(np.argsort(-np.asarray(scores))[:2].tolist())
    assert set(selected) == expected


def test_error_feedback_conservation_identity():
    updates = [
        np.arange(12, dtype=float).reshape(3, 4),
        np.flip(np.arange(12, dtype=float)).reshape(3, 4) * 0.25,
        np.ones((3, 4), dtype=float) * 0.4,
    ]
    residual = np.zeros((3, 4), dtype=float)
    transmitted_sum = np.zeros_like(residual)
    raw_sum = np.zeros_like(residual)
    initial_residual = residual.copy()
    for update in updates:
        compressed, residual, _ = topk_compress(update, 0.30, residual)
        transmitted_sum += compressed
        raw_sum += update
    np.testing.assert_allclose(
        transmitted_sum,
        raw_sum + initial_residual - residual,
        rtol=0,
        atol=1e-12,
    )
