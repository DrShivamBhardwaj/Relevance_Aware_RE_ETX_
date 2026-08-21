import numpy as np


class TDMAScheduler:
    """
    Simple single-channel deterministic TDMA scheduler.

    Each active node receives one transmission slot per round.
    Nodes are ordered by node ID for reproducibility.

    This is a baseline MAC model, not a claim of a complete
    IEEE 802.15.4 implementation.
    """

    def __init__(self, config):
        self.packet_size = int(config.packet_size)
        self.bit_rate = float(config.bit_rate)

        if self.packet_size <= 0:
            raise ValueError(
                "packet_size must be positive."
            )

        if self.bit_rate <= 0:
            raise ValueError(
                "bit_rate must be positive."
            )

        self.slot_duration = (
            self.packet_size
            / self.bit_rate
        )

    def schedule(self, node_ids):
        """
        Parameters
        ----------
        node_ids : array-like
            Nodes attempting transmission in the round.

        Returns
        -------
        ordered_ids : np.ndarray
            Deterministic transmission order.

        completion_times : np.ndarray
            Packet transmission completion time relative
            to the beginning of the current round.

        round_airtime : float
            Total channel occupancy for the round.
        """

        ordered_ids = np.sort(
            np.asarray(
                node_ids,
                dtype=np.int64
            )
        )

        number_of_slots = (
            ordered_ids.size
        )

        completion_times = (
            np.arange(
                1,
                number_of_slots + 1,
                dtype=np.float64
            )
            * self.slot_duration
        )

        round_airtime = (
            number_of_slots
            * self.slot_duration
        )

        return (
            ordered_ids,
            completion_times,
            round_airtime
        )
