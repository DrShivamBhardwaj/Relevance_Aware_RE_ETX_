import numpy as np


class FrameModel:
    """
    Protocol-abstract fragmentation model.

    Default application message:
        config.packet_size bits

    Each MAC fragment carries at most:
        config.mac_payload_bits payload bits

    Every fragment adds:
        config.mac_overhead_bits overhead bits

    This is NOT a complete IEEE 802.15.4 implementation.
    """

    def __init__(
        self,
        config
    ):
        self.config = config

        self.app_bits = int(
            config.packet_size
        )

        self.payload_bits = int(
            config.mac_payload_bits
        )

        self.overhead_bits = int(
            config.mac_overhead_bits
        )

        if self.app_bits <= 0:
            raise ValueError(
                "Application packet size must be positive."
            )

        if self.payload_bits <= 0:
            raise ValueError(
                "MAC payload size must be positive."
            )

        if self.overhead_bits < 0:
            raise ValueError(
                "MAC overhead cannot be negative."
            )

    def fragment_payloads(
        self,
        app_bits=None
    ):
        if app_bits is None:
            app_bits = self.app_bits

        app_bits = int(
            app_bits
        )

        if app_bits <= 0:
            raise ValueError(
                "Application payload must be positive."
            )

        full_frames, remainder = divmod(
            app_bits,
            self.payload_bits
        )

        payloads = [
            self.payload_bits
        ] * full_frames

        if remainder > 0:
            payloads.append(
                remainder
            )

        return np.asarray(
            payloads,
            dtype=np.int64
        )

    def fragment_sizes(
        self,
        app_bits=None
    ):
        payloads = (
            self.fragment_payloads(
                app_bits
            )
        )

        return (
            payloads
            + self.overhead_bits
        ).astype(
            np.int64
        )

    def frame_count(
        self,
        app_bits=None
    ):
        return int(
            len(
                self.fragment_sizes(
                    app_bits
                )
            )
        )

    def radio_bits(
        self,
        app_bits=None
    ):
        return int(
            np.sum(
                self.fragment_sizes(
                    app_bits
                )
            )
        )

    def efficiency_for(
        self,
        app_bits=None
    ):
        if app_bits is None:
            app_bits = self.app_bits

        app_bits = int(
            app_bits
        )

        return (
            app_bits
            / self.radio_bits(
                app_bits
            )
        )

    @property
    def efficiency(self):
        return self.efficiency_for(
            self.app_bits
        )
