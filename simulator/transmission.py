from dataclasses import dataclass


@dataclass
class TransmissionResult:
    success: bool
    energy_used: float
    airtime: float
    frame_attempts: int
    retransmissions: int
    failed_frame_attempts: int
    completed_frames: int
    drop_reason: str


class FragmentedLinkTransmitter:
    """
    Sends one fragmented application message over one wireless link.

    Each fragment can be retransmitted up to max_retries times.

    max_retries = 3 means:
        1 initial attempt + 3 retries = 4 maximum attempts/frame.
    """

    def __init__(
        self,
        config,
        radio,
        channel,
        frame_model
    ):
        self.config = config
        self.radio = radio
        self.channel = channel
        self.frame_model = frame_model

        self.max_attempts = (
            int(config.max_retries)
            + 1
        )

        if self.max_attempts <= 0:
            raise ValueError(
                "Maximum attempts must be positive."
            )

    def transmit_message(
        self,
        residual_energy,
        distance,
        snr_db
    ):
        remaining_energy = float(
            residual_energy
        )

        if remaining_energy < 0:
            raise ValueError(
                "Residual energy cannot be negative."
            )

        energy_used = 0.0
        airtime = 0.0

        frame_attempts = 0
        retransmissions = 0
        failed_frame_attempts = 0
        completed_frames = 0

        frame_sizes = (
            self.frame_model.fragment_sizes()
        )

        for frame_bits in frame_sizes:
            frame_bits = int(frame_bits)

            tx_energy = float(
                self.radio.tx_energy(
                    frame_bits,
                    distance
                )
            )

            frame_airtime = (
                frame_bits
                / self.config.bit_rate
            )

            frame_delivered = False

            for attempt in range(
                self.max_attempts
            ):
                # Node cannot complete the next transmission.
                if remaining_energy < tx_energy:
                    if tx_energy > 0:
                        fraction = (
                            remaining_energy
                            / tx_energy
                        )
                    else:
                        fraction = 0.0

                    airtime += (
                        frame_airtime
                        * fraction
                    )

                    energy_used += (
                        remaining_energy
                    )

                    remaining_energy = 0.0

                    return TransmissionResult(
                        success=False,
                        energy_used=energy_used,
                        airtime=airtime,
                        frame_attempts=frame_attempts,
                        retransmissions=retransmissions,
                        failed_frame_attempts=
                            failed_frame_attempts,
                        completed_frames=
                            completed_frames,
                        drop_reason="energy"
                    )

                # Complete frame attempt.
                remaining_energy -= (
                    tx_energy
                )

                energy_used += (
                    tx_energy
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
                        snr_db
                    )
                )

                if frame_ok:
                    frame_delivered = True
                    completed_frames += 1
                    break

                failed_frame_attempts += 1

            if not frame_delivered:
                return TransmissionResult(
                    success=False,
                    energy_used=energy_used,
                    airtime=airtime,
                    frame_attempts=frame_attempts,
                    retransmissions=retransmissions,
                    failed_frame_attempts=
                        failed_frame_attempts,
                    completed_frames=
                        completed_frames,
                    drop_reason="channel"
                )

        return TransmissionResult(
            success=True,
            energy_used=energy_used,
            airtime=airtime,
            frame_attempts=frame_attempts,
            retransmissions=retransmissions,
            failed_frame_attempts=
                failed_frame_attempts,
            completed_frames=completed_frames,
            drop_reason="none"
        )
