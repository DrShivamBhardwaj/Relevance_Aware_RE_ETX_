from dataclasses import replace
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from wsn_hfl.config import SimConfig
from wsn_hfl.model import topk_compress
from wsn_hfl.simulator import simulate
from wsn_hfl.topology import WSNTopology


def test_topology_routes_reach_gateways():
    cfg = replace(SimConfig(), num_clients=10, num_gateways=2)
    rng = np.random.default_rng(3)
    topo = WSNTopology(cfg, rng)
    e0 = np.full(cfg.num_clients, cfg.energy_initial_j)
    routes = topo.all_routes(e0, e0)
    assert len(routes) == cfg.num_clients
    assert all(r.hops >= 1 for r in routes)
    assert all(0 <= r.gateway < cfg.num_gateways for r in routes)


def test_topk_compression_shape_and_residual():
    update = np.arange(20, dtype=float).reshape(4, 5)
    residual = np.zeros_like(update)
    compressed, new_residual, k = topk_compress(update, 0.25, residual)
    assert compressed.shape == update.shape
    assert new_residual.shape == update.shape
    assert k == 5
    np.testing.assert_allclose(compressed + new_residual, update)
def test_smoke_simulation_produces_metrics():
    cfg = replace(
        SimConfig(),
        seed=5,
        num_clients=8,
        num_gateways=2,
        rounds=4,
        clients_per_round=3,
        samples_per_client=32,
        test_samples=120,
        feature_dim=8,
        num_classes=4,
    )
    summary, history = simulate("proposed", cfg)
    assert len(history) == cfg.rounds
    assert 0.0 <= summary["accuracy"] <= 1.0
    assert 0.0 <= summary["macro_f1"] <= 1.0
    assert summary["effective_bits"] > 0
    assert summary["energy_j"] > 0
    assert summary["representation_js"] >= 0
    assert summary["participation_jain"] > 0
