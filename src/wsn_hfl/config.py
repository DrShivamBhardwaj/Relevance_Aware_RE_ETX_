from dataclasses import dataclass


@dataclass(frozen=True)
class SimConfig:
    seed: int = 7
    num_clients: int = 24
    num_gateways: int = 4
    num_classes: int = 5
    feature_dim: int = 24
    samples_per_client: int = 96
    test_samples: int = 1000
    rounds: int = 40
    clients_per_round: int = 6
    local_steps: int = 4
    learning_rate: float = 0.14
    l2: float = 1e-3
    area_size: float = 1.0
    sensor_radius: float = 0.34
    gateway_radius: float = 0.28
    energy_initial_j: float = 10.0
    energy_jitter: float = 1.5
    local_step_energy_j: float = 0.004
    tx_energy_per_bit_j: float = 1.5e-6
    rx_energy_per_bit_j: float = 8.0e-7
    bandwidth_bps: float = 2.0e5
    base_hop_delay_s: float = 0.025
    round_slot_s: float = 0.20
    etx_energy_weight: float = 0.65
    min_compression_ratio: float = 0.15
    fixed_compression_ratio: float = 0.50
    staleness_lambda: float = 0.35
    utility_staleness_mu: float = 0.80
    max_staleness: int = 4
    drift_v: float = 0.5
    relay_budget_j_per_round: float = 0.004
    utility_ema: float = 0.65
    compression_distortion_weight: float = 1.20
    compression_candidates: tuple = (0.15, 0.30, 0.50, 0.75, 1.0)
    model_bits: int = 32
    index_bits: int = 16
    header_bits: int = 96
    correlation: float = 0.75
    noniid_alpha: float = 0.35
    rare_class_boost: float = 5.5
    class_separation: float = 1.10
    feature_noise: float = 1.60
    label_noise: float = 0.04
    availability_prob: float = 0.90
    dropout_prob: float = 0.03


METHODS = ("random", "resource", "utility", "proposed")
