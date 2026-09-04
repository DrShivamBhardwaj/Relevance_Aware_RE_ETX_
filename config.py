import os

from dataclasses import dataclass


@dataclass
class SimulationConfig:
    # Reproducibility
    seed: int = int(
        os.environ.get(
            "SEMANTIC_SEED",
            42
        )
    )

    # Network
    num_nodes: int = 100
    area_width: float = 100.0
    area_height: float = 100.0

    # Base station
    bs_x: float = 50.0
    bs_y: float = 150.0

    # Node energy
    initial_energy: float = 0.5
    energy_epsilon: float = 1e-12

    # Application message
    packet_size: int = 4000

    # Fragmentation abstraction
    mac_payload_bits: int = 800
    mac_overhead_bits: int = 216

    # First-order radio-energy model
    e_elec: float = 50e-9
    e_fs: float = 10e-12
    e_mp: float = 0.0013e-12
    e_da: float = 5e-9

    # PHY / timing
    bit_rate: float = 250000.0
    propagation_speed: float = 3e8
    processing_delay: float = 0.001

    # Channel model
    carrier_frequency_hz: float = 2.4e9
    tx_power_dbm: float = 0.0
    reference_distance_m: float = 1.0
    path_loss_exponent: float = 2.4
    shadowing_sigma_db: float = 4.0
    noise_floor_dbm: float = -100.0

    # Retransmission parameters
    max_retries: int = 3

    # Correlated IoT sensing model
    temporal_correlation: float = 0.85
    spatial_correlation_length_m: float = 25.0
    sensing_noise_std: float = 0.10

    event_probability: float = 0.03
    event_duration_min: int = 4
    event_duration_max: int = 10
    event_radius_m: float = 18.0
    event_amplitude: float = 3.0

    # Semantic payload / priority model
    semantic_min_payload_ratio: float = 0.25
    semantic_high_recall_threshold: float = 0.50
    semantic_high_confidence_threshold: float = 0.85
    semantic_high_recall_min_ratio: float = 0.75

    # Ablation control switches
    semantic_routing_enabled: bool = (
        os.environ.get(
            "SEMANTIC_ROUTING_ENABLED",
            "true"
        ).lower()
        == "true"
    )

    semantic_payload_enabled: bool = (
        os.environ.get(
            "SEMANTIC_PAYLOAD_ENABLED",
            "true"
        ).lower()
        == "true"
    )

    # Multi-hop neighbor / routing model
    max_sensor_link_distance_m: float = 30.0
    min_link_success: float = 0.90
    etx_epsilon: float = 1e-12

    # Simulation
    max_rounds: int = 5000
