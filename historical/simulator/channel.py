import numpy as np
from scipy.special import erfc


class WirelessChannel:
    """
    Generic log-distance wireless channel with:
      - log-normal slow shadowing
      - BPSK-equivalent independent frame errors

    This is not claimed as an exact IEEE 802.15.4 PHY model.
    """

    def __init__(self, config):
        self.config = config

        self.frequency = float(
            config.carrier_frequency_hz
        )

        self.tx_power_dbm = float(
            config.tx_power_dbm
        )

        self.reference_distance = float(
            config.reference_distance_m
        )

        self.path_loss_exponent = float(
            config.path_loss_exponent
        )

        self.shadowing_sigma_db = float(
            config.shadowing_sigma_db
        )

        self.noise_floor_dbm = float(
            config.noise_floor_dbm
        )

        self.propagation_speed = float(
            config.propagation_speed
        )

        if self.frequency <= 0:
            raise ValueError(
                "Carrier frequency must be positive."
            )

        if self.reference_distance <= 0:
            raise ValueError(
                "Reference distance must be positive."
            )

        if self.path_loss_exponent <= 0:
            raise ValueError(
                "Path-loss exponent must be positive."
            )

        if self.shadowing_sigma_db < 0:
            raise ValueError(
                "Shadowing sigma cannot be negative."
            )

        # Independent random streams improve reproducibility.
        self.shadow_rng = np.random.default_rng(
            config.seed + 1000
        )

        self.error_rng = np.random.default_rng(
            config.seed + 2000
        )

        wavelength = (
            self.propagation_speed
            / self.frequency
        )

        self.reference_path_loss_db = (
            20.0
            * np.log10(
                (
                    4.0
                    * np.pi
                    * self.reference_distance
                )
                / wavelength
            )
        )

    def sample_static_shadowing(self, size):
        return self.shadow_rng.normal(
            loc=0.0,
            scale=self.shadowing_sigma_db,
            size=size
        )

    def path_loss_db(
        self,
        distance,
        shadowing_db=0.0
    ):
        distance = np.asarray(
            distance,
            dtype=np.float64
        )

        shadowing_db = np.asarray(
            shadowing_db,
            dtype=np.float64
        )

        if np.any(distance < 0):
            raise ValueError(
                "Distance cannot be negative."
            )

        effective_distance = np.maximum(
            distance,
            self.reference_distance
        )

        return (
            self.reference_path_loss_db
            + 10.0
            * self.path_loss_exponent
            * np.log10(
                effective_distance
                / self.reference_distance
            )
            + shadowing_db
        )

    def received_power_dbm(
        self,
        distance,
        shadowing_db=0.0
    ):
        return (
            self.tx_power_dbm
            - self.path_loss_db(
                distance,
                shadowing_db
            )
        )

    def snr_db(
        self,
        distance,
        shadowing_db=0.0
    ):
        return (
            self.received_power_dbm(
                distance,
                shadowing_db
            )
            - self.noise_floor_dbm
        )

    @staticmethod
    def snr_linear(snr_db):
        snr_db = np.asarray(
            snr_db,
            dtype=np.float64
        )

        return (
            10.0 ** (
                snr_db / 10.0
            )
        )

    def bit_error_rate(self, snr_db):
        gamma = self.snr_linear(
            snr_db
        )

        return (
            0.5
            * erfc(
                np.sqrt(gamma)
            )
        )

    def frame_success_probability(
        self,
        frame_bits,
        snr_db
    ):
        frame_bits = np.asarray(
            frame_bits,
            dtype=np.float64
        )

        if np.any(frame_bits <= 0):
            raise ValueError(
                "Frame size must be positive."
            )

        ber = self.bit_error_rate(
            snr_db
        )

        ber = np.clip(
            ber,
            0.0,
            1.0 - 1e-15
        )

        probability = np.exp(
            frame_bits
            * np.log1p(
                -ber
            )
        )

        return np.clip(
            probability,
            0.0,
            1.0
        )

    def message_success_probability(
        self,
        frame_sizes,
        snr_db
    ):
        frame_sizes = np.asarray(
            frame_sizes,
            dtype=np.float64
        )

        probabilities = (
            self.frame_success_probability(
                frame_sizes,
                snr_db
            )
        )

        return float(
            np.prod(probabilities)
        )

    def attempt_frame(
        self,
        frame_bits,
        snr_db
    ):
        probability = float(
            self.frame_success_probability(
                frame_bits,
                snr_db
            )
        )

        return bool(
            self.error_rng.random()
            < probability
        )
