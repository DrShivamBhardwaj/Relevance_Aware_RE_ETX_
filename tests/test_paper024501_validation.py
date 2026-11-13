import numpy as np
from config import SimulationConfig
from simulator.energy import RadioEnergyModel
from simulator.semantic_payload import SemanticPayloadController
from reviewer_audit.PAPER024501.receiver_reference_codec import ReceiverReferenceCodec
from reviewer_audit.PAPER024501.energy_profile import ExtendedEnergyProfile
from simulator.topology import Topology
from simulator.network import SensorNetwork


def test_threshold_safeguards_are_3000_and_4000_bits():
    codec = SemanticPayloadController(SimulationConfig())
    assert int(codec.payload_bits([0.50])[0]) == 3000
    assert int(codec.payload_bits([0.85])[0]) == 4000


def test_reference_decoder_progressive_and_deterministic():
    low = ReceiverReferenceCodec(1, seed=42)
    high = ReceiverReferenceCodec(1, seed=42)
    low.record(0, 1, .65, True, 1000, True)
    high.record(0, 1, .65, True, 4000, True)
    assert high.results()["rmse"] <= low.results()["rmse"] + 1e-12
    same = ReceiverReferenceCodec(1, seed=42)
    same.record(0, 1, .65, True, 1000, True)
    assert np.array_equal(low.last, same.last)


def test_missing_packet_holds_last_receiver_value():
    codec = ReceiverReferenceCodec(1, seed=23)
    codec.record(0, 1, .8, True, 4000, True)
    prior = codec.last.copy()
    codec.record(0, 2, .2, False, 1000, False)
    assert np.array_equal(codec.last, prior)
    assert codec.results()["received"] == 1


def test_zero_extra_energy_does_not_change_node_state(monkeypatch):
    for k in ("REVIEW_SENSING_UJ", "REVIEW_CPU_UJ", "REVIEW_IDLE_UJ",
              "REVIEW_CONTEXT_BITS", "REVIEW_ROUTING_BITS", "REVIEW_ACK_BITS"):
        monkeypatch.setenv(k, "0")
    cfg = SimulationConfig()
    cfg.num_nodes = 5
    topo = Topology(cfg)
    net = SensorNetwork(cfg, topo)
    profile = ExtendedEnergyProfile(cfg, RadioEnergyModel(cfg), topo)
    before = net.total_residual_energy
    profile.round_cost(net, 1)
    assert net.total_residual_energy == before


def test_nonzero_idle_energy_reduces_battery(monkeypatch):
    monkeypatch.setenv("REVIEW_IDLE_UJ", "5")
    for k in ("REVIEW_SENSING_UJ", "REVIEW_CPU_UJ",
              "REVIEW_CONTEXT_BITS", "REVIEW_ROUTING_BITS", "REVIEW_ACK_BITS"):
        monkeypatch.setenv(k, "0")
    cfg = SimulationConfig()
    cfg.num_nodes = 5
    topo = Topology(cfg)
    net = SensorNetwork(cfg, topo)
    profile = ExtendedEnergyProfile(cfg, RadioEnergyModel(cfg), topo)
    before = net.total_residual_energy
    profile.round_cost(net, 1)
    assert np.isclose(before-net.total_residual_energy, 5*5e-6)
