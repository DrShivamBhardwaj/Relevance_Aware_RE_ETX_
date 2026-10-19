import numpy as np


class RadioEnergyModel:
    """
    First-order radio energy model.

    TX:
        E_TX(k,d) = k*E_elec + k*epsilon_fs*d^2,  d < d0
        E_TX(k,d) = k*E_elec + k*epsilon_mp*d^4,  d >= d0

    RX:
        E_RX(k) = k*E_elec

    Aggregation:
        E_DA(k) = k*E_DA
    """

    def __init__(self, config):
        self.e_elec = float(config.e_elec)
        self.e_fs = float(config.e_fs)
        self.e_mp = float(config.e_mp)
        self.e_da = float(config.e_da)

        if self.e_fs <= 0 or self.e_mp <= 0:
            raise ValueError(
                "Amplifier energy parameters must be positive."
            )

        self.d0 = np.sqrt(
            self.e_fs / self.e_mp
        )

    def tx_energy(self, bits, distance):
        bits = np.asarray(
            bits,
            dtype=np.float64
        )

        distance = np.asarray(
            distance,
            dtype=np.float64
        )

        if np.any(bits < 0):
            raise ValueError(
                "Packet size cannot be negative."
            )

        if np.any(distance < 0):
            raise ValueError(
                "Transmission distance cannot be negative."
            )

        electronics = bits * self.e_elec

        free_space = (
            electronics
            + bits * self.e_fs * distance**2
        )

        multipath = (
            electronics
            + bits * self.e_mp * distance**4
        )

        return np.where(
            distance < self.d0,
            free_space,
            multipath
        )

    def rx_energy(self, bits):
        bits = np.asarray(
            bits,
            dtype=np.float64
        )

        if np.any(bits < 0):
            raise ValueError(
                "Packet size cannot be negative."
            )

        return bits * self.e_elec

    def aggregation_energy(self, bits):
        bits = np.asarray(
            bits,
            dtype=np.float64
        )

        if np.any(bits < 0):
            raise ValueError(
                "Packet size cannot be negative."
            )

        return bits * self.e_da
