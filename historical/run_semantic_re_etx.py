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
from simulator.routing_semantic_re_etx import SemanticResidualEnergyETXRouter
from simulator.multihop_transmission import MultiHopTransmitter
from simulator.sensing import CorrelatedSensingField
from simulator.semantic_relevance import SemanticRelevanceEstimator
from simulator.semantic_age import SemanticAgeTracker
from simulator.semantic_payload import SemanticPayloadController


def rotate_schedule(
    node_ids,
    round_id
):
    """
    Rotate source ordering between rounds so low node IDs
    do not permanently receive preferential service.
    """

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


def run():
    config = SimulationConfig()

    mode = config.experiment_mode

    valid_modes = {
        "LEGACY",
        "C1",
        "C2",
        "C3",
        "C4",
        "C5",
        "C6",
        "C7",
    }

    if mode not in valid_modes:
        raise ValueError(
            f"Invalid EXPERIMENT_MODE={mode}. "
            f"Choose from {sorted(valid_modes)}"
        )

    if mode == "LEGACY":
        routing_enabled = bool(
            config.semantic_routing_enabled
        )

        payload_mode = (
            "adaptive"
            if config.semantic_payload_enabled
            else "fixed_full"
        )

        temporal_weight = 0.6
        spatial_weight = 0.4

    else:
        routing_enabled = mode in {
            "C2",
            "C4",
        }

        payload_mode = {
            "C1": "fixed_full",
            "C2": "fixed_full",
            "C3": "adaptive",
            "C4": "adaptive",
            "C5": "equal_budget",
            "C6": "shuffled",
            "C7": "adaptive",
        }[mode]

        if mode == "C7":
            temporal_weight = 1.0
            spatial_weight = 0.0
        else:
            temporal_weight = 0.6
            spatial_weight = 0.4

    if mode == "C5":
        if not (
            8
            <= config.equal_budget_payload_bits
            <= config.packet_size
        ):
            raise ValueError(
                "EQUAL_BUDGET_PAYLOAD_BITS is outside "
                "the allowed payload range."
            )

        if config.equal_budget_payload_bits % 8 != 0:
            raise ValueError(
                "EQUAL_BUDGET_PAYLOAD_BITS must be "
                "byte aligned."
            )

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


    sensing = CorrelatedSensingField(
        config,
        topology
    )

    semantic_estimator = SemanticRelevanceEstimator(
        topology,
        temporal_weight=temporal_weight,
        spatial_weight=spatial_weight,
    )

    shuffle_rng = np.random.default_rng(
        config.seed
        + config.shuffle_seed_offset
    )

    semantic_tracker = SemanticAgeTracker(
        config.num_nodes
    )

    semantic_payload_controller = None

    if payload_mode in {
        "adaptive",
        "shuffled",
    }:
        semantic_payload_controller = SemanticPayloadController(
            config
        )

    transmitter = MultiHopTransmitter(
        config,
        radio,
        channel,
        frame,
        graph
    )

    metrics = PerformanceMetrics()

    # ------------------------------------------------
    # Routing / load statistics
    # ------------------------------------------------

    direct_route_assignments = 0
    multihop_route_assignments = 0
    fallback_direct_assignments = 0

    delivered_hop_sum = 0
    delivered_hop_max = 0

    relay_route_usage = np.zeros(
        config.num_nodes,
        dtype=np.int64
    )

    fnd = None
    hnd = None
    lnd = None

    elapsed_channel_time = 0.0

    records = []

    payload_bits_history = []

    total_semantic_payload_bits = 0
    total_full_payload_bits = 0
    total_radio_bits = 0

    semantic_mean_history = []
    semantic_max_history = []

    # ------------------------------------------------
    # Ground-truth event evaluation counters.
    #
    # Event truth is used ONLY for offline evaluation;
    # it is never supplied to routing, relevance,
    # payload adaptation, or transmission decisions.
    # ------------------------------------------------
    event_generated_reports = 0
    event_attempted_reports = 0
    event_delivered_reports = 0
    event_attempted_payload_bits = 0
    event_delivered_payload_bits = 0

    non_event_attempted_reports = 0
    non_event_attempted_payload_bits = 0

    # Within-round event targeting removes the
    # confounding effect that event-active rounds
    # can have a larger payload multiset overall.
    within_round_targeting_gaps = []

    os.makedirs(
        "results",
        exist_ok=True
    )

    # ------------------------------------------------
    # Simulation
    # ------------------------------------------------

    for round_id in range(
        1,
        config.max_rounds + 1
    ):

        alive_at_start = np.flatnonzero(
            network.alive
        )

        if alive_at_start.size == 0:
            break

        # --------------------------------------------
        # Route recomputation once per round.
        #
        # This adapts to node deaths without assuming
        # unrealistically instantaneous route updates
        # after every packet.
        # --------------------------------------------

        current_observation = sensing.step()

        semantic_output = semantic_estimator.compute(
            current_observation,
            sensing.previous_observation
        )

        relevance = semantic_output["relevance"]

        # Evaluation-only ground truth.
        # This variable must never affect any network decision.
        event_truth = sensing.event_truth()

        semantic_age = semantic_tracker.semantic_age(
            relevance
        )

        if payload_mode in {
            "adaptive",
            "shuffled",
        }:
            semantic_payload_bits = (
                semantic_payload_controller.payload_bits(
                    relevance
                )
            )

            if payload_mode == "shuffled":
                shuffled_payload_bits = (
                    semantic_payload_bits.copy()
                )

                if alive_at_start.size > 1:
                    permuted_sources = (
                        shuffle_rng.permutation(
                            alive_at_start
                        )
                    )

                    shuffled_payload_bits[
                        alive_at_start
                    ] = semantic_payload_bits[
                        permuted_sources
                    ]

                semantic_payload_bits = (
                    shuffled_payload_bits
                )

        elif payload_mode == "equal_budget":
            semantic_payload_bits = np.full(
                config.num_nodes,
                config.equal_budget_payload_bits,
                dtype=np.int64
            )

        else:
            semantic_payload_bits = np.full(
                config.num_nodes,
                config.packet_size,
                dtype=np.int64
            )

        payload_bits_history.extend(
            semantic_payload_bits.tolist()
        )



        semantic_mean_history.append(
            float(np.mean(semantic_age))
        )

        semantic_max_history.append(
            float(np.max(semantic_age))
        )


        router = SemanticResidualEnergyETXRouter(
            graph,
            network.energy,
            config.initial_energy,
            alive_mask=network.alive,
            energy_weight=0.25,
            semantic_weight=(
                1.00
                if routing_enabled
                else 0.0
            ),
            semantic_age=(
                semantic_age
                if routing_enabled
                else np.zeros(
                    config.num_nodes
                )
            )
        )

        schedule = rotate_schedule(
            alive_at_start,
            round_id
        )

        generated_round = int(
            schedule.size
        )

        event_generated_reports += int(
            np.count_nonzero(
                event_truth[schedule]
            )
        )

        delivered_round = 0

        event_attempted_round = 0
        event_payload_bits_round = 0
        non_event_attempted_round = 0
        non_event_payload_bits_round = 0

        delivered_mask = np.zeros(
            config.num_nodes,
            dtype=bool
        )
        channel_drops_round = 0
        energy_drops_round = 0
        route_drops_round = 0

        fallback_round = 0

        round_airtime = 0.0

        metrics.register_generated(
            generated_round
        )

        # --------------------------------------------
        # Process each source sequentially on one
        # shared channel.
        # --------------------------------------------

        for source in schedule:
            source = int(source)

            # Node may have died earlier in this round
            # while acting as a relay.
            if not network.alive[source]:
                metrics.register_energy_drop(
                    1
                )

                energy_drops_round += 1

                continue

            path = router.route(
                source
            )

            # ----------------------------------------
            # Emergency direct fallback
            #
            # If quality-filtered multi-hop topology is
            # partitioned after relay deaths, the node
            # may still physically attempt its direct BS
            # link. This avoids immortal isolated nodes.
            #
            # The fallback is tracked separately.
            # ----------------------------------------

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

            if event_truth[source]:
                event_attempted_reports += 1
                event_attempted_round += 1
            else:
                non_event_attempted_reports += 1
                non_event_attempted_round += 1

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

            # Waiting time in the current global
            # serialized MAC schedule.
            start_time = (
                round_airtime
            )

            result = transmitter.transmit(
                network,
                path,
                round_id=round_id,
                app_bits=int(
                    semantic_payload_bits[source]
                )
            )

            round_airtime += (
                result.airtime
            )

            total_radio_bits += int(
                result.radio_bits
            )

            total_full_payload_bits += int(
                config.packet_size
            )

            total_semantic_payload_bits += int(
                semantic_payload_bits[source]
            )

            if event_truth[source]:
                event_attempted_payload_bits += int(
                    semantic_payload_bits[source]
                )
                event_payload_bits_round += int(
                    semantic_payload_bits[source]
                )
            else:
                non_event_attempted_payload_bits += int(
                    semantic_payload_bits[source]
                )
                non_event_payload_bits_round += int(
                    semantic_payload_bits[source]
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
                
                delivered_mask[
                    source
                ] = True

                delay = (
                    start_time
                    + result.airtime
                    + result.propagation_delay
                    + result.processing_delay
                )

                metrics.register_delivered(
                    count=1,
                    packet_size=
                        int(
                            semantic_payload_bits[source]
                        ),
                    delays=[delay]
                )

                if event_truth[source]:
                    event_delivered_reports += 1
                    event_delivered_payload_bits += int(
                        semantic_payload_bits[source]
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
                    "Unknown transmission drop reason."
                )

        if (
            event_attempted_round > 0
            and non_event_attempted_round > 0
        ):
            event_mean_round = (
                event_payload_bits_round
                / event_attempted_round
            )
            non_event_mean_round = (
                non_event_payload_bits_round
                / non_event_attempted_round
            )
            within_round_targeting_gaps.append(
                event_mean_round
                - non_event_mean_round
            )

        elapsed_channel_time += (
            round_airtime
        )

        # --------------------------------------------
        # Lifetime metrics
        # --------------------------------------------

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

        goodput = metrics.throughput(
            elapsed_channel_time
        )

        semantic_tracker.update(
            delivered_mask
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

            "route_drops_round":
                route_drops_round,

            "fallback_direct_round":
                fallback_round,

            "generated_total":
                metrics.generated_packets,

            "attempted_total":
                metrics.attempted_packets,

            "delivered_total":
                metrics.delivered_packets,

            "channel_drops_total":
                metrics.channel_dropped_packets,

            "energy_drops_total":
                metrics.energy_dropped_packets,

            "route_drops_total":
                metrics.route_dropped_packets,

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

    # ------------------------------------------------
    # Save results
    # ------------------------------------------------

    output_path = (
        "results/"
        "minimum_etx_multihop.csv"
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

        writer.writerows(
            records
        )

    goodput = metrics.throughput(
        elapsed_channel_time
    )

    ideal_application_limit = (
        config.bit_rate
        * frame.efficiency
    )

    if (
        metrics.delivered_packets
        > 0
    ):
        average_delivered_hops = (
            delivered_hop_sum
            / metrics.delivered_packets
        )

        energy_per_delivered = (
            network.cumulative_energy_consumed
            / metrics.delivered_packets
        )
    else:
        average_delivered_hops = 0.0
        energy_per_delivered = 0.0

    # --------------------------------------------
    # Relay concentration statistics
    # --------------------------------------------

    top_relays = np.argsort(
        relay_route_usage
    )[::-1][:10]

    # ------------------------------------------------
    # Event-aware evaluation metrics.
    #
    # These are offline diagnostics only. Ground-truth
    # event labels never participate in the algorithm.
    # ------------------------------------------------
    if event_attempted_reports > 0:
        event_mean_payload_bits = (
            event_attempted_payload_bits
            / event_attempted_reports
        )
        event_payload_preservation_ratio = (
            event_attempted_payload_bits
            / (
                event_attempted_reports
                * config.packet_size
            )
        )
    else:
        event_mean_payload_bits = 0.0
        event_payload_preservation_ratio = 0.0

    if non_event_attempted_reports > 0:
        non_event_mean_payload_bits = (
            non_event_attempted_payload_bits
            / non_event_attempted_reports
        )
    else:
        non_event_mean_payload_bits = 0.0

    payload_targeting_gap_bits = (
        event_mean_payload_bits
        - non_event_mean_payload_bits
    )

    if event_generated_reports > 0:
        event_report_delivery_ratio = (
            event_delivered_reports
            / event_generated_reports
        )
        event_payload_delivery_ratio = (
            event_delivered_payload_bits
            / (
                event_generated_reports
                * config.packet_size
            )
        )
    else:
        event_report_delivery_ratio = 0.0
        event_payload_delivery_ratio = 0.0

    if within_round_targeting_gaps:
        within_round_targeting_gap_bits = float(
            np.mean(
                within_round_targeting_gaps
            )
        )
        event_rounds_evaluated = len(
            within_round_targeting_gaps
        )
    else:
        within_round_targeting_gap_bits = 0.0
        event_rounds_evaluated = 0

    # ------------------------------------------------
    # Final summary
    # ------------------------------------------------

    print("=" * 78)
    print("DYNAMIC MINIMUM-ETX MULTI-HOP BASELINE")
    print("=" * 78)

    print(
        f"FND                         : {fnd}"
    )

    print(
        f"HND                         : {hnd}"
    )

    print(
        f"LND                         : {lnd}"
    )

    print(
        f"Generated messages          : "
        f"{metrics.generated_packets}"
    )

    print(
        f"Attempted messages          : "
        f"{metrics.attempted_packets}"
    )

    print(
        f"Delivered messages          : "
        f"{metrics.delivered_packets}"
    )

    print(
        f"Channel-related drops       : "
        f"{metrics.channel_dropped_packets}"
    )

    print(
        f"Energy-related drops        : "
        f"{metrics.energy_dropped_packets}"
    )

    print(
        f"Route-related drops         : "
        f"{metrics.route_dropped_packets}"
    )

    print(
        f"Direct fallback assignments : "
        f"{fallback_direct_assignments}"
    )

    print(
        f"PDR                         : "
        f"{metrics.pdr:.6f}"
    )

    print(
        f"PDR (%)                     : "
        f"{metrics.pdr * 100:.3f}"
    )

    print(
        f"Frame attempts              : "
        f"{metrics.total_frame_attempts}"
    )

    print(
        f"Retransmissions             : "
        f"{metrics.total_retransmissions}"
    )

    print(
        f"Failed frame attempts       : "
        f"{metrics.failed_frame_attempts}"
    )

    print(
        f"Direct route assignments    : "
        f"{direct_route_assignments}"
    )

    print(
        f"Multi-hop route assignments : "
        f"{multihop_route_assignments}"
    )

    print(
        f"Average delivered hops      : "
        f"{average_delivered_hops:.4f}"
    )

    print(
        f"Maximum delivered hops      : "
        f"{delivered_hop_max}"
    )

    print(
        f"Average delay               : "
        f"{metrics.average_delay * 1000:.3f} ms"
    )

    print(
        f"Channel elapsed time        : "
        f"{elapsed_channel_time:.6f} s"
    )

    print(
        f"Application goodput         : "
        f"{goodput / 1000:.3f} kbps"
    )

    print(
        f"Ideal 1-hop upper bound     : "
        f"{ideal_application_limit / 1000:.3f} kbps"
    )

    print(
        f"Energy/delivered message    : "
        f"{energy_per_delivered:.9f} J"
    )

    print(
        f"Mean semantic age           : "
        f"{np.mean(semantic_mean_history):.6f}"
    )

    print(
        f"Maximum semantic age        : "
        f"{np.max(semantic_max_history):.6f}"
    )

    print(
        f"Residual network energy     : "
        f"{network.total_residual_energy:.9f} J"
    )

    if payload_bits_history:
        print(
            f"Average semantic payload bits : "
            f"{np.mean(payload_bits_history):.2f}"
        )

        print(
            f"Minimum semantic payload bits : "
            f"{np.min(payload_bits_history)}"
        )

        print(
            f"Maximum semantic payload bits : "
            f"{np.max(payload_bits_history)}"
        )

        print(
            f"Payload reduction (%)         : "
            f"{(1 - np.mean(payload_bits_history)/config.packet_size)*100:.2f}"
        )

        if total_full_payload_bits > 0:
            semantic_compression_ratio = (
                total_semantic_payload_bits
                /
                total_full_payload_bits
            )

            print(
                f"Semantic compression ratio   : "
                f"{semantic_compression_ratio:.6f}"
            )

        if total_radio_bits > 0:
            semantic_radio_efficiency = (
                total_semantic_payload_bits
                /
                total_radio_bits
            )

            print(
                f"Semantic radio efficiency    : "
                f"{semantic_radio_efficiency:.6f}"
            )



    print(
        f"Cumulative energy used      : "
        f"{network.cumulative_energy_consumed:.9f} J"
    )

    print(
        f"Event generated reports     : "
        f"{event_generated_reports}"
    )

    print(
        f"Event attempted reports     : "
        f"{event_attempted_reports}"
    )

    print(
        f"Event delivered reports     : "
        f"{event_delivered_reports}"
    )

    print(
        f"Event report delivery ratio : "
        f"{event_report_delivery_ratio:.6f}"
    )

    print(
        f"Event mean payload bits     : "
        f"{event_mean_payload_bits:.3f}"
    )

    print(
        f"Non-event mean payload bits : "
        f"{non_event_mean_payload_bits:.3f}"
    )

    print(
        f"Payload targeting gap bits  : "
        f"{payload_targeting_gap_bits:.3f}"
    )

    print(
        f"Event payload preservation  : "
        f"{event_payload_preservation_ratio:.6f}"
    )

    print(
        f"Event payload delivery ratio: "
        f"{event_payload_delivery_ratio:.6f}"
    )

    print(
        f"Event rounds evaluated       : "
        f"{event_rounds_evaluated}"
    )

    print(
        f"Within-round targeting gap   : "
        f"{within_round_targeting_gap_bits:.3f}"
    )

    print()
    print("Most frequently selected relays")
    print("-" * 78)

    for relay in top_relays:
        count = int(
            relay_route_usage[
                relay
            ]
        )

        if count <= 0:
            continue

        print(
            f"Node {relay:3d} : "
            f"{count} route selections"
        )

    print()

    print(
        f"CSV output                  : "
        f"{output_path}"
    )

    # ------------------------------------------------
    # Validation
    # ------------------------------------------------

    accounted = (
        metrics.delivered_packets
        + metrics.channel_dropped_packets
        + metrics.energy_dropped_packets
        + metrics.route_dropped_packets
    )

    assert (
        accounted
        == metrics.generated_packets
    ), (
        "Generated-message accounting mismatch."
    )

    assert (
        metrics.attempted_packets
        <= metrics.generated_packets
    )

    assert (
        0.0
        <= metrics.pdr
        <= 1.0
    )

    assert (
        goodput
        <= ideal_application_limit
        + 1e-9
    )

    assert np.all(
        network.energy >= 0.0
    )

    if lnd is not None:
        assert (
            network.num_dead
            == config.num_nodes
        )

    print()
    print(
        "All dynamic minimum-ETX checks PASSED."
    )


if __name__ == "__main__":
    run()
