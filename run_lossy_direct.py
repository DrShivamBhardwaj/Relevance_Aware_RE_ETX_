import csv
import os

import numpy as np

from config import SimulationConfig
from simulator.topology import Topology
from simulator.energy import RadioEnergyModel
from simulator.network import SensorNetwork
from simulator.metrics import PerformanceMetrics
from simulator.channel import WirelessChannel
from simulator.frame import FrameModel
from simulator.transmission import (
    FragmentedLinkTransmitter
)


def rotate_schedule(
    alive_ids,
    round_id
):
    if alive_ids.size <= 1:
        return alive_ids

    shift = (
        (round_id - 1)
        % alive_ids.size
    )

    return np.roll(
        alive_ids,
        -shift
    )


def run():
    config = SimulationConfig()

    topology = Topology(config)

    radio = RadioEnergyModel(config)

    network = SensorNetwork(
        config,
        topology
    )

    channel = WirelessChannel(config)

    frame_model = FrameModel(config)

    transmitter = FragmentedLinkTransmitter(
        config,
        radio,
        channel,
        frame_model
    )

    metrics = PerformanceMetrics()

    shadowing = (
        channel.sample_static_shadowing(
            config.num_nodes
        )
    )

    node_snr = channel.snr_db(
        topology.distance_to_bs,
        shadowing
    )

    fnd = None
    hnd = None
    lnd = None

    elapsed_channel_time = 0.0

    records = []

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

        schedule = rotate_schedule(
            alive_ids,
            round_id
        )

        round_airtime = 0.0

        generated_round = (
            schedule.size
        )

        delivered_round = 0
        channel_drops_round = 0
        energy_drops_round = 0

        metrics.register_generated(
            generated_round
        )

        metrics.register_attempted(
            generated_round
        )

        for node_id in schedule:
            node_id = int(node_id)

            distance = float(
                topology.distance_to_bs[
                    node_id
                ]
            )

            snr = float(
                node_snr[
                    node_id
                ]
            )

            result = (
                transmitter.transmit_message(
                    residual_energy=
                        network.energy[node_id],
                    distance=distance,
                    snr_db=snr
                )
            )

            # Waiting time before this node starts
            # its TDMA service in the current round.
            start_time = (
                round_airtime
            )

            round_airtime += (
                result.airtime
            )

            metrics.register_frame_stats(
                attempts=
                    result.frame_attempts,
                retransmissions=
                    result.retransmissions,
                failed_attempts=
                    result.failed_frame_attempts
            )

            network.consume_energy(
                node_ids=[node_id],
                energy_cost=[
                    result.energy_used
                ],
                round_id=round_id
            )

            if result.success:
                propagation_delay = (
                    distance
                    / config.propagation_speed
                )

                delay = (
                    start_time
                    + result.airtime
                    + propagation_delay
                    + config.processing_delay
                )

                metrics.register_delivered(
                    count=1,
                    packet_size=
                        config.packet_size,
                    delays=[delay]
                )

                delivered_round += 1

            elif result.drop_reason == "channel":
                metrics.register_channel_drop(
                    1
                )

                channel_drops_round += 1

            elif result.drop_reason == "energy":
                metrics.register_energy_drop(
                    1
                )

                energy_drops_round += 1

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

        goodput = metrics.throughput(
            elapsed_channel_time
        )

        records.append({
            "round":
                round_id,

            "alive_nodes":
                network.num_alive,

            "dead_nodes":
                network.num_dead,

            "round_airtime_s":
                round_airtime,

            "elapsed_channel_time_s":
                elapsed_channel_time,

            "generated_round":
                generated_round,

            "delivered_round":
                delivered_round,

            "channel_drops_round":
                channel_drops_round,

            "energy_drops_round":
                energy_drops_round,

            "generated_total":
                metrics.generated_packets,

            "delivered_total":
                metrics.delivered_packets,

            "channel_drops_total":
                metrics.channel_dropped_packets,

            "energy_drops_total":
                metrics.energy_dropped_packets,

            "pdr":
                metrics.pdr,

            "goodput_bps":
                goodput,

            "average_delay_s":
                metrics.average_delay,

            "frame_attempts":
                metrics.total_frame_attempts,

            "retransmissions":
                metrics.total_retransmissions,

            "residual_energy_j":
                network.total_residual_energy
        })

        if lnd is not None:
            break

    output_path = (
        "results/"
        "lossy_direct_to_bs.csv"
    )

    with open(
        output_path,
        "w",
        newline=""
    ) as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=list(
                records[0].keys()
            )
        )

        writer.writeheader()
        writer.writerows(records)

    goodput = metrics.throughput(
        elapsed_channel_time
    )

    ideal_app_goodput_limit = (
        config.bit_rate
        * frame_model.efficiency
    )

    print("=" * 76)
    print("LOSSY FRAGMENTED DIRECT-TO-BS BASELINE")
    print("=" * 76)

    print(
        f"FND                       : {fnd}"
    )

    print(
        f"HND                       : {hnd}"
    )

    print(
        f"LND                       : {lnd}"
    )

    print(
        f"Generated messages        : "
        f"{metrics.generated_packets}"
    )

    print(
        f"Delivered messages        : "
        f"{metrics.delivered_packets}"
    )

    print(
        f"Channel-related drops     : "
        f"{metrics.channel_dropped_packets}"
    )

    print(
        f"Energy-related drops      : "
        f"{metrics.energy_dropped_packets}"
    )

    print(
        f"PDR                       : "
        f"{metrics.pdr:.6f}"
    )

    print(
        f"PDR (%)                   : "
        f"{metrics.pdr * 100:.3f}"
    )

    print(
        f"Frame attempts            : "
        f"{metrics.total_frame_attempts}"
    )

    print(
        f"Retransmissions           : "
        f"{metrics.total_retransmissions}"
    )

    print(
        f"Failed frame attempts     : "
        f"{metrics.failed_frame_attempts}"
    )

    print(
        f"Average delay             : "
        f"{metrics.average_delay * 1000:.3f} ms"
    )

    print(
        f"Channel elapsed time      : "
        f"{elapsed_channel_time:.6f} s"
    )

    print(
        f"Application goodput       : "
        f"{goodput / 1000:.3f} kbps"
    )

    print(
        f"Ideal goodput upper bound : "
        f"{ideal_app_goodput_limit / 1000:.3f} kbps"
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
        f"CSV output                : "
        f"{output_path}"
    )

    accounted = (
        metrics.delivered_packets
        + metrics.channel_dropped_packets
        + metrics.energy_dropped_packets
    )

    assert (
        accounted
        == metrics.generated_packets
    )

    assert (
        0.0
        <= metrics.pdr
        <= 1.0
    )

    assert (
        goodput
        <= ideal_app_goodput_limit
        + 1e-9
    )

    assert np.all(
        network.energy >= 0.0
    )

    print()
    print(
        "All lossy-channel baseline checks PASSED."
    )


if __name__ == "__main__":
    run()
