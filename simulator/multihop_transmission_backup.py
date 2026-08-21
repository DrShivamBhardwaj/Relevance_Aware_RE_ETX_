from dataclasses import dataclass


@dataclass
class MultiHopResult:
    success: bool

    airtime: float

    tx_energy: float
    rx_energy: float

    frame_attempts: int
    retransmissions: int
    failed_frame_attempts: int

    hops_completed: int

    propagation_delay: float
    processing_delay: float

    drop_reason: str


class MultiHopTransmitter:
    """
    Store-and-forward fragmented multi-hop transmission.

    Sensor transmit energy:
        counted for every frame attempt.

    Relay receive energy:
        counted for every frame attempt, including corrupted frames.

    Sink energy:
        ignored because the sink is assumed externally powered.

    ACK energy/airtime is not yet modeled.
    """

    def __init__(
        self,
        config,
        radio,
        channel,
        frame_model,
        link_graph
    ):
        self.config = config
        self.radio = radio
        self.channel = channel
        self.frame_model = frame_model
        self.graph = link_graph

        self.sink_id = (
            link_graph.sink_id
        )

        self.max_attempts = (
            int(config.max_retries)
            + 1
        )

    def _link_state(
        self,
        sender,
        receiver
    ):
        if receiver == self.sink_id:
            distance = float(
                self.graph.topology.distance_to_bs[
                    sender
                ]
            )

            snr = float(
                self.graph.bs_snr[
                    sender
                ]
            )

        else:
            distance = float(
                self.graph.sensor_distance[
                    sender,
                    receiver
                ]
            )

            snr = float(
                self.graph.sensor_snr[
                    sender,
                    receiver
                ]
            )

        return distance, snr

    def transmit(
        self,
        network,
        path,
        round_id
    ):
        if path is None:
            return MultiHopResult(
                False,
                0.0,
                0.0,
                0.0,
                0,
                0,
                0,
                0,
                0.0,
                0.0,
                "route"
            )

        airtime = 0.0

        total_tx_energy = 0.0
        total_rx_energy = 0.0

        frame_attempts = 0
        retransmissions = 0
        failed_attempts = 0

        hops_completed = 0

        propagation_delay = 0.0
        processing_delay = 0.0

        # -----------------------------------------
        # Hop-by-hop forwarding
        # -----------------------------------------

        for hop_index in range(
            len(path) - 1
        ):
            sender = int(
                path[hop_index]
            )

            receiver = int(
                path[hop_index + 1]
            )

            # Sender must still be alive.
            if (
                sender != self.sink_id
                and not network.alive[sender]
            ):
                return MultiHopResult(
                    False,
                    airtime,
                    total_tx_energy,
                    total_rx_energy,
                    frame_attempts,
                    retransmissions,
                    failed_attempts,
                    hops_completed,
                    propagation_delay,
                    processing_delay,
                    "energy"
                )

            # Frozen round route may contain a relay
            # that died earlier in this round.
            if (
                receiver != self.sink_id
                and not network.alive[receiver]
            ):
                return MultiHopResult(
                    False,
                    airtime,
                    total_tx_energy,
                    total_rx_energy,
                    frame_attempts,
                    retransmissions,
                    failed_attempts,
                    hops_completed,
                    propagation_delay,
                    processing_delay,
                    "route"
                )

            distance, snr = (
                self._link_state(
                    sender,
                    receiver
                )
            )

            for frame_bits in (
                self.frame_model.fragment_sizes()
            ):
                frame_bits = int(
                    frame_bits
                )

                tx_cost = float(
                    self.radio.tx_energy(
                        frame_bits,
                        distance
                    )
                )

                rx_cost = float(
                    self.radio.rx_energy(
                        frame_bits
                    )
                )

                frame_airtime = (
                    frame_bits
                    / self.config.bit_rate
                )

                delivered = False

                for attempt in range(
                    self.max_attempts
                ):
                    # -----------------------------
                    # Sender energy availability
                    # -----------------------------

                    sender_energy = float(
                        network.energy[
                            sender
                        ]
                    )

                    if (
                        sender_energy
                        + network.energy_epsilon
                        < tx_cost
                    ):
                        if tx_cost > 0:
                            fraction = (
                                sender_energy
                                / tx_cost
                            )
                        else:
                            fraction = 0.0

                        fraction = min(
                            max(
                                fraction,
                                0.0
                            ),
                            1.0
                        )

                        partial_airtime = (
                            frame_airtime
                            * fraction
                        )

                        airtime += (
                            partial_airtime
                        )

                        total_tx_energy += (
                            sender_energy
                        )

                        network.consume_energy(
                            [sender],
                            [sender_energy],
                            round_id=round_id
                        )

                        # Receiver may expend energy
                        # while listening to partial frame.
                        if (
                            receiver
                            != self.sink_id
                            and network.alive[
                                receiver
                            ]
                        ):
                            partial_rx = (
                                rx_cost
                                * fraction
                            )

                            actual_rx = min(
                                float(
                                    network.energy[
                                        receiver
                                    ]
                                ),
                                partial_rx
                            )

                            network.consume_energy(
                                [receiver],
                                [actual_rx],
                                round_id=round_id
                            )

                            total_rx_energy += (
                                actual_rx
                            )

                        return MultiHopResult(
                            False,
                            airtime,
                            total_tx_energy,
                            total_rx_energy,
                            frame_attempts,
                            retransmissions,
                            failed_attempts,
                            hops_completed,
                            propagation_delay,
                            processing_delay,
                            "energy"
                        )

                    # -----------------------------
                    # Receiver energy availability
                    # -----------------------------

                    if receiver != self.sink_id:
                        receiver_energy = float(
                            network.energy[
                                receiver
                            ]
                        )

                        if (
                            receiver_energy
                            + network.energy_epsilon
                            < rx_cost
                        ):
                            # Sender transmits complete frame.
                            network.consume_energy(
                                [sender],
                                [tx_cost],
                                round_id=round_id
                            )

                            total_tx_energy += (
                                tx_cost
                            )

                            network.consume_energy(
                                [receiver],
                                [receiver_energy],
                                round_id=round_id
                            )

                            total_rx_energy += (
                                receiver_energy
                            )

                            airtime += (
                                frame_airtime
                            )

                            frame_attempts += 1

                            return MultiHopResult(
                                False,
                                airtime,
                                total_tx_energy,
                                total_rx_energy,
                                frame_attempts,
                                retransmissions,
                                failed_attempts,
                                hops_completed,
                                propagation_delay,
                                processing_delay,
                                "energy"
                            )

                    # -----------------------------
                    # Complete frame transmission
                    # -----------------------------

                    network.consume_energy(
                        [sender],
                        [tx_cost],
                        round_id=round_id
                    )

                    total_tx_energy += (
                        tx_cost
                    )

                    if receiver != self.sink_id:
                        network.consume_energy(
                            [receiver],
                            [rx_cost],
                            round_id=round_id
                        )

                        total_rx_energy += (
                            rx_cost
                        )

                    airtime += (
                        frame_airtime
                    )

                    frame_attempts += 1

                    if attempt > 0:
                        retransmissions += 1

                    frame_ok = (
                        self.channel.attempt_frame(
                            frame_bits,
                            snr
                        )
                    )

                    if frame_ok:
                        delivered = True
                        break

                    failed_attempts += 1

                if not delivered:
                    return MultiHopResult(
                        False,
                        airtime,
                        total_tx_energy,
                        total_rx_energy,
                        frame_attempts,
                        retransmissions,
                        failed_attempts,
                        hops_completed,
                        propagation_delay,
                        processing_delay,
                        "channel"
                    )

            hops_completed += 1

            propagation_delay += (
                distance
                / self.config.propagation_speed
            )

            processing_delay += (
                self.config.processing_delay
            )

        return MultiHopResult(
            True,
            airtime,
            total_tx_energy,
            total_rx_energy,
            frame_attempts,
            retransmissions,
            failed_attempts,
            hops_completed,
            propagation_delay,
            processing_delay,
            "none"
        )
