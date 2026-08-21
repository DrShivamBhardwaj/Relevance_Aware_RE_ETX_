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
from simulator.link_graph import LinkGraph
from simulator.routing_re_etx import ResidualEnergyETXRouter
from simulator.multihop_transmission import MultiHopTransmitter


ENERGY_WEIGHTS = [
    0.0,
    0.25,
    0.5,
    1.0,
    2.0,
    4.0
]


def rotate_schedule(node_ids, round_id):
    if node_ids.size <= 1:
        return node_ids

    shift = (
        (round_id - 1)
        % node_ids.size
    )

    return np.roll(
        node_ids,
        -shift
    )


def safe_weight_name(weight):
    return (
        f"{weight:.2f}"
        .replace(".", "p")
    )


def run_single_weight(
    energy_weight,
    seed=None
):
    config = SimulationConfig()

    if seed is not None:
        config.seed = int(seed)

    # --------------------------------------------
    # IMPORTANT:
    # Every lambda starts from exactly the same
    # topology, shadowing realization and RNG seed.
    # --------------------------------------------

    topology = Topology(
        config
    )

    radio = RadioEnergyModel(
        config
    )

    network = SensorNetwork(
        config,
        topology
    )

    channel = WirelessChannel(
        config
    )

    frame = FrameModel(
        config
    )

    graph = LinkGraph(
        config,
        topology,
        channel,
        frame
    )

    transmitter = MultiHopTransmitter(
        config,
        radio,
        channel,
        frame,
        graph
    )

    metrics = PerformanceMetrics()

    # --------------------------------------------
    # Routing statistics
    # --------------------------------------------

    direct_route_assignments = 0
    multihop_route_assignments = 0
    fallback_direct_assignments = 0

    delivered_hop_sum = 0
    delivered_hop_max = 0

    relay_route_usage = np.zeros(
        config.num_nodes,
        dtype=np.int64
    )

    route_changes = 0

    previous_next_hop = np.full(
        config.num_nodes,
        -1,
        dtype=np.int64
    )

    fnd = None
    hnd = None
    lnd = None

    elapsed_channel_time = 0.0

    records = []

    # --------------------------------------------
    # Simulation
    # --------------------------------------------

    for round_id in range(
        1,
        config.max_rounds + 1
    ):

        alive_at_start = np.flatnonzero(
            network.alive
        )

        if alive_at_start.size == 0:
            break

        router = ResidualEnergyETXRouter(
            graph,
            residual_energy=
                network.energy,
            initial_energy=
                config.initial_energy,
            alive_mask=
                network.alive,
            energy_weight=
                energy_weight,
            epsilon=
                config.energy_epsilon
        )

        # ----------------------------------------
        # Measure routing adaptation
        # ----------------------------------------

        for node_id in alive_at_start:
            node_id = int(node_id)

            path = router.route(
                node_id
            )

            if (
                path is not None
                and len(path) >= 2
            ):
                current_next_hop = (
                    path[1]
                )
            else:
                current_next_hop = -1

            if (
                previous_next_hop[node_id] >= 0
                and current_next_hop >= 0
                and previous_next_hop[node_id]
                    != current_next_hop
            ):
                route_changes += 1

            previous_next_hop[
                node_id
            ] = current_next_hop

        schedule = rotate_schedule(
            alive_at_start,
            round_id
        )

        generated_round = int(
            schedule.size
        )

        delivered_round = 0
        channel_drops_round = 0
        energy_drops_round = 0
        route_drops_round = 0
        fallback_round = 0

        round_airtime = 0.0

        metrics.register_generated(
            generated_round
        )

        # ----------------------------------------
        # Process all source messages
        # ----------------------------------------

        for source in schedule:
            source = int(source)

            # Source may die earlier in the same
            # round while serving as a relay.
            if not network.alive[source]:
                metrics.register_energy_drop(
                    1
                )

                energy_drops_round += 1
                continue

            path = router.route(
                source
            )

            # ------------------------------------
            # Direct fallback if the quality-
            # constrained routing graph becomes
            # temporarily disconnected.
            # ------------------------------------

            if path is None:
                path = [
                    source,
                    graph.sink_id
                ]

                fallback_direct_assignments += 1
                fallback_round += 1

            metrics.register_attempted(
                1
            )

            hops = (
                len(path) - 1
            )

            if hops == 1:
                direct_route_assignments += 1
            else:
                multihop_route_assignments += 1

                for relay in path[
                    1:-1
                ]:
                    relay_route_usage[
                        int(relay)
                    ] += 1

            start_time = (
                round_airtime
            )

            result = transmitter.transmit(
                network,
                path,
                round_id=round_id
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

            if result.success:
                delay = (
                    start_time
                    + result.airtime
                    + result.propagation_delay
                    + result.processing_delay
                )

                metrics.register_delivered(
                    count=1,
                    packet_size=
                        config.packet_size,
                    delays=[delay]
                )

                delivered_round += 1

                delivered_hop_sum += (
                    result.hops_completed
                )

                delivered_hop_max = max(
                    delivered_hop_max,
                    result.hops_completed
                )

            elif (
                result.drop_reason
                == "channel"
            ):
                metrics.register_channel_drop(
                    1
                )

                channel_drops_round += 1

            elif (
                result.drop_reason
                == "energy"
            ):
                metrics.register_energy_drop(
                    1
                )

                energy_drops_round += 1

            elif (
                result.drop_reason
                == "route"
            ):
                metrics.register_route_drop(
                    1
                )

                route_drops_round += 1

            else:
                raise RuntimeError(
                    "Unknown drop reason."
                )

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
            and dead
            >= config.num_nodes / 2
        ):
            hnd = round_id

        if (
            dead
            == config.num_nodes
        ):
            lnd = round_id

        # ----------------------------------------
        # Residual-energy balance among alive nodes
        # ----------------------------------------

        alive_energy = network.energy[
            network.alive
        ]

        if alive_energy.size > 0:
            mean_alive_energy = float(
                np.mean(alive_energy)
            )

            std_alive_energy = float(
                np.std(alive_energy)
            )

            # Jain fairness over residual energy.
            denominator = (
                alive_energy.size
                * np.sum(
                    alive_energy ** 2
                )
            )

            if denominator > 0:
                jain_energy = float(
                    (
                        np.sum(
                            alive_energy
                        ) ** 2
                    )
                    / denominator
                )
            else:
                jain_energy = 0.0

        else:
            mean_alive_energy = 0.0
            std_alive_energy = 0.0
            jain_energy = 0.0

        records.append({
            "round":
                round_id,

            "lambda_energy":
                energy_weight,

            "alive_nodes":
                network.num_alive,

            "dead_nodes":
                network.num_dead,

            "generated_round":
                generated_round,

            "delivered_round":
                delivered_round,

            "channel_drops_round":
                channel_drops_round,

            "energy_drops_round":
                energy_drops_round,

            "route_drops_round":
                route_drops_round,

            "fallback_direct_round":
                fallback_round,

            "round_airtime_s":
                round_airtime,

            "elapsed_channel_time_s":
                elapsed_channel_time,

            "pdr":
                metrics.pdr,

            "goodput_bps":
                metrics.throughput(
                    elapsed_channel_time
                ),

            "average_delay_s":
                metrics.average_delay,

            "residual_energy_j":
                network.total_residual_energy,

            "mean_alive_energy_j":
                mean_alive_energy,

            "std_alive_energy_j":
                std_alive_energy,

            "jain_energy_fairness":
                jain_energy,

            "route_changes_total":
                route_changes
        })

        if lnd is not None:
            break

    # --------------------------------------------
    # Derived final statistics
    # --------------------------------------------

    goodput = metrics.throughput(
        elapsed_channel_time
    )

    if (
        metrics.delivered_packets
        > 0
    ):
        average_hops = (
            delivered_hop_sum
            / metrics.delivered_packets
        )

        energy_per_delivered = (
            network.cumulative_energy_consumed
            / metrics.delivered_packets
        )
    else:
        average_hops = 0.0
        energy_per_delivered = 0.0

    relay_total = int(
        np.sum(
            relay_route_usage
        )
    )

    if relay_total > 0:
        relay_shares = (
            relay_route_usage[
                relay_route_usage > 0
            ]
            / relay_total
        )

        relay_hhi = float(
            np.sum(
                relay_shares ** 2
            )
        )

        max_relay_share = float(
            np.max(
                relay_shares
            )
        )
    else:
        relay_hhi = 0.0
        max_relay_share = 0.0

    # Generated messages also represents
    # alive-node-rounds because every alive node
    # generates exactly one message per round.
    alive_node_rounds = (
        metrics.generated_packets
    )

    rounds_executed = (
        records[-1]["round"]
    )

    mean_alive_fraction = (
        alive_node_rounds
        / (
            config.num_nodes
            * rounds_executed
        )
    )

    accounted = (
        metrics.delivered_packets
        + metrics.channel_dropped_packets
        + metrics.energy_dropped_packets
        + metrics.route_dropped_packets
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

    assert np.all(
        network.energy >= 0.0
    )

    # --------------------------------------------
    # Save per-round file
    # --------------------------------------------

    os.makedirs(
        "results/re_etx_sweep",
        exist_ok=True
    )

    name = safe_weight_name(
        energy_weight
    )

    per_round_path = (
        "results/re_etx_sweep/"
        f"seed_{config.seed}_lambda_{name}.csv"
    )

    with open(
        per_round_path,
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

    return {
        "seed":
            config.seed,

        "lambda_energy":
            energy_weight,

        "FND":
            fnd,

        "HND":
            hnd,

        "LND":
            lnd,

        "generated_messages":
            metrics.generated_packets,

        "attempted_messages":
            metrics.attempted_packets,

        "delivered_messages":
            metrics.delivered_packets,

        "channel_drops":
            metrics.channel_dropped_packets,

        "energy_drops":
            metrics.energy_dropped_packets,

        "route_drops":
            metrics.route_dropped_packets,

        "PDR":
            metrics.pdr,

        "PDR_percent":
            metrics.pdr * 100.0,

        "frame_attempts":
            metrics.total_frame_attempts,

        "retransmissions":
            metrics.total_retransmissions,

        "failed_frame_attempts":
            metrics.failed_frame_attempts,

        "direct_assignments":
            direct_route_assignments,

        "multihop_assignments":
            multihop_route_assignments,

        "fallback_assignments":
            fallback_direct_assignments,

        "average_hops":
            average_hops,

        "maximum_hops":
            delivered_hop_max,

        "average_delay_ms":
            metrics.average_delay
            * 1000.0,

        "goodput_kbps":
            goodput
            / 1000.0,

        "energy_per_delivered_j":
            energy_per_delivered,

        "route_changes":
            route_changes,

        "relay_HHI":
            relay_hhi,

        "max_relay_share":
            max_relay_share,

        "alive_node_rounds":
            alive_node_rounds,

        "mean_alive_fraction":
            mean_alive_fraction,

        "per_round_csv":
            per_round_path
    }


def main():
    summaries = []

    print("=" * 96)
    print("RESIDUAL-ENERGY-AWARE ETX PARAMETER SWEEP")
    print("=" * 96)

    for weight in ENERGY_WEIGHTS:
        print()
        print(
            f"Running lambda_E = {weight} ..."
        )

        result = run_single_weight(
            weight
        )

        summaries.append(
            result
        )

        print(
            f"  FND/HND/LND     : "
            f"{result['FND']} / "
            f"{result['HND']} / "
            f"{result['LND']}"
        )

        print(
            f"  PDR             : "
            f"{result['PDR_percent']:.3f}%"
        )

        print(
            f"  Delivered       : "
            f"{result['delivered_messages']}"
        )

        print(
            f"  Retransmissions : "
            f"{result['retransmissions']}"
        )

        print(
            f"  Avg hops        : "
            f"{result['average_hops']:.4f}"
        )

        print(
            f"  Delay           : "
            f"{result['average_delay_ms']:.3f} ms"
        )

        print(
            f"  Goodput         : "
            f"{result['goodput_kbps']:.3f} kbps"
        )

        print(
            f"  Relay HHI       : "
            f"{result['relay_HHI']:.6f}"
        )

        print(
            f"  Mean alive frac : "
            f"{result['mean_alive_fraction']:.4f}"
        )

    # --------------------------------------------
    # Save summary CSV
    # --------------------------------------------

    summary_path = (
        "results/"
        "re_etx_lambda_summary.csv"
    )

    with open(
        summary_path,
        "w",
        newline=""
    ) as csvfile:

        writer = csv.DictWriter(
            csvfile,
            fieldnames=list(
                summaries[0].keys()
            )
        )

        writer.writeheader()
        writer.writerows(
            summaries
        )

    print()
    print("=" * 96)
    print("SWEEP SUMMARY")
    print("=" * 96)

    header = (
        f"{'lambda':>7} "
        f"{'FND':>6} "
        f"{'HND':>6} "
        f"{'LND':>6} "
        f"{'PDR%':>9} "
        f"{'Delivered':>11} "
        f"{'Retry':>8} "
        f"{'Delay(ms)':>11} "
        f"{'Goodput':>10} "
        f"{'HHI':>9} "
        f"{'AliveFrac':>10}"
    )

    print(header)
    print("-" * len(header))

    for r in summaries:
        print(
            f"{r['lambda_energy']:7.2f} "
            f"{str(r['FND']):>6} "
            f"{str(r['HND']):>6} "
            f"{str(r['LND']):>6} "
            f"{r['PDR_percent']:9.3f} "
            f"{r['delivered_messages']:11d} "
            f"{r['retransmissions']:8d} "
            f"{r['average_delay_ms']:11.3f} "
            f"{r['goodput_kbps']:10.3f} "
            f"{r['relay_HHI']:9.5f} "
            f"{r['mean_alive_fraction']:10.4f}"
        )

    print()
    print(
        "Summary CSV:",
        summary_path
    )

    print(
        "Per-round CSV directory:",
        "results/re_etx_sweep/"
    )


if __name__ == "__main__":
    main()
