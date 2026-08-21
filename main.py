import csv
import os

import numpy as np

from config import SimulationConfig
from simulator.topology import Topology
from simulator.energy import RadioEnergyModel
from simulator.network import SensorNetwork
from simulator.metrics import PerformanceMetrics
from simulator.mac import TDMAScheduler


def run_direct_to_bs():
    config = SimulationConfig()

    topology = Topology(config)
    radio = RadioEnergyModel(config)

    network = SensorNetwork(
        config,
        topology
    )

    mac = TDMAScheduler(config)

    metrics = PerformanceMetrics()

    fnd = None
    hnd = None
    lnd = None

    elapsed_channel_time = 0.0

    round_records = []

    os.makedirs(
        "results",
        exist_ok=True
    )

    for round_id in range(
        1,
        config.max_rounds + 1
    ):

        alive_ids = np.flatnonzero(
            network.alive
        )

        if alive_ids.size == 0:
            break

        # ==========================================
        # Application message generation
        # ==========================================

        metrics.register_generated(
            alive_ids.size
        )

        metrics.register_attempted(
            alive_ids.size
        )

        # ==========================================
        # TDMA scheduling
        # ==========================================

        (
            scheduled_ids,
            completion_times,
            round_airtime
        ) = mac.schedule(
            alive_ids
        )

        distances = (
            topology.distance_to_bs[
                scheduled_ids
            ]
        )

        required_energy = (
            radio.tx_energy(
                config.packet_size,
                distances
            )
        )

        residual_before = (
            network.energy[
                scheduled_ids
            ].copy()
        )

        # A complete application message is delivered
        # only if sufficient transmission energy exists.
        success_mask = (
            residual_before
            >= required_energy
        )

        success_ids = (
            scheduled_ids[
                success_mask
            ]
        )

        failed_ids = (
            scheduled_ids[
                ~success_mask
            ]
        )

        success_distances = (
            distances[
                success_mask
            ]
        )

        success_completion_times = (
            completion_times[
                success_mask
            ]
        )

        # ==========================================
        # End-to-end one-hop packet latency
        #
        # Includes:
        #   TDMA waiting
        # + transmission
        # + propagation
        # + receiver processing
        # ==========================================

        packet_delays = (
            success_completion_times
            + (
                success_distances
                / config.propagation_speed
            )
            + config.processing_delay
        )

        metrics.register_delivered(
            count=success_ids.size,
            packet_size=config.packet_size,
            delays=packet_delays
        )

        metrics.register_energy_drop(
            failed_ids.size
        )

        # ==========================================
        # Energy depletion
        # ==========================================

        network.consume_energy(
            node_ids=scheduled_ids,
            energy_cost=required_energy,
            round_id=round_id
        )

        # Channel remains reserved for every scheduled
        # slot, including the slot of a node that dies
        # during an incomplete transmission attempt.
        elapsed_channel_time += (
            round_airtime
        )

        dead = network.num_dead

        if (
            fnd is None
            and dead >= 1
        ):
            fnd = round_id

        if (
            hnd is None
            and dead >= (
                config.num_nodes / 2
            )
        ):
            hnd = round_id

        if dead == config.num_nodes:
            lnd = round_id

        current_throughput = (
            metrics.throughput(
                elapsed_channel_time
            )
        )

        round_records.append({
            "round":
                round_id,

            "round_airtime_s":
                round_airtime,

            "elapsed_channel_time_s":
                elapsed_channel_time,

            "alive_nodes":
                network.num_alive,

            "dead_nodes":
                network.num_dead,

            "residual_energy_j":
                network.total_residual_energy,

            "generated_packets":
                metrics.generated_packets,

            "delivered_packets":
                metrics.delivered_packets,

            "energy_drops":
                metrics.energy_dropped_packets,

            "pdr":
                metrics.pdr,

            "avg_delay_s":
                metrics.average_delay,

            "throughput_bps":
                current_throughput
        })

        if lnd is not None:
            break

    output_path = (
        "results/"
        "direct_to_bs_tdma_metrics.csv"
    )

    with open(
        output_path,
        "w",
        newline=""
    ) as csvfile:

        fieldnames = list(
            round_records[0].keys()
        )

        writer = csv.DictWriter(
            csvfile,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            round_records
        )

    final_throughput = (
        metrics.throughput(
            elapsed_channel_time
        )
    )

    if metrics.delivered_packets > 0:
        energy_per_packet = (
            network.cumulative_energy_consumed
            / metrics.delivered_packets
        )
    else:
        energy_per_packet = 0.0

    print("=" * 70)
    print("DIRECT-TO-BS TDMA BASELINE")
    print("=" * 70)

    print(
        f"PHY bit rate              : "
        f"{config.bit_rate:.0f} bit/s"
    )

    print(
        f"TDMA slot duration        : "
        f"{mac.slot_duration:.6f} s"
    )

    print(
        f"FND                       : "
        f"{fnd}"
    )

    print(
        f"HND                       : "
        f"{hnd}"
    )

    print(
        f"LND                       : "
        f"{lnd}"
    )

    print(
        f"Generated messages        : "
        f"{metrics.generated_packets}"
    )

    print(
        f"Attempted messages        : "
        f"{metrics.attempted_packets}"
    )

    print(
        f"Delivered messages        : "
        f"{metrics.delivered_packets}"
    )

    print(
        f"Energy-related drops      : "
        f"{metrics.energy_dropped_packets}"
    )

    print(
        f"PDR                       : "
        f"{metrics.pdr:.9f}"
    )

    print(
        f"PDR (%)                   : "
        f"{metrics.pdr * 100:.6f}"
    )

    print(
        f"Average end-to-end delay  : "
        f"{metrics.average_delay:.9f} s"
    )

    print(
        f"Average end-to-end delay  : "
        f"{metrics.average_delay * 1000:.3f} ms"
    )

    print(
        f"Channel elapsed time      : "
        f"{elapsed_channel_time:.6f} s"
    )

    print(
        f"Aggregate goodput         : "
        f"{final_throughput:.3f} bit/s"
    )

    print(
        f"Aggregate goodput         : "
        f"{final_throughput / 1000:.3f} kbps"
    )

    print(
        f"Residual energy           : "
        f"{network.total_residual_energy:.9f} J"
    )

    print(
        f"Cumulative energy used    : "
        f"{network.cumulative_energy_consumed:.9f} J"
    )

    print(
        f"Energy/delivered message  : "
        f"{energy_per_packet:.12f} J"
    )

    print(
        f"CSV output                : "
        f"{output_path}"
    )

    # =================================================
    # Validation invariants
    # =================================================

    assert (
        metrics.generated_packets
        == metrics.attempted_packets
    )

    assert (
        metrics.delivered_packets
        + metrics.energy_dropped_packets
        == metrics.generated_packets
    )

    assert (
        0.0
        <= metrics.pdr
        <= 1.0
    )

    assert (
        final_throughput
        <= config.bit_rate + 1e-9
    ), (
        "Aggregate goodput exceeds configured "
        "single-channel PHY rate."
    )

    assert (
        metrics.average_delay
        >= mac.slot_duration
    )

    assert (
        network.num_dead
        == config.num_nodes
    )

    assert np.all(
        network.energy >= 0.0
    )

    assert np.isclose(
        network.cumulative_energy_consumed,
        (
            config.num_nodes
            * config.initial_energy
        )
    )

    assert (
        fnd == 168
    )

    assert (
        hnd == 637
    )

    assert (
        lnd == 1595
    )

    print()
    print(
        "All TDMA packet-level checks PASSED."
    )


if __name__ == "__main__":
    run_direct_to_bs()
