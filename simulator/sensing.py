import numpy as np


class CorrelatedSensingField:
    """
    Spatially and temporally correlated sensing process.

    Background:
        B(t) = phi * B(t-1)
             + sqrt(1-phi^2) * epsilon(t)

    Observation:
        X(t) = B(t) + G(t)

    Event G(t) is NOT recursively fed into the AR background.
    """

    def __init__(
        self,
        config,
        topology
    ):
        self.config = config
        self.topology = topology

        self.num_nodes = int(
            config.num_nodes
        )

        self.phi = float(
            config.temporal_correlation
        )

        self.lambda_s = float(
            config.spatial_correlation_length_m
        )

        self.noise_std = float(
            config.sensing_noise_std
        )

        self.event_probability = float(
            config.event_probability
        )

        self.event_duration_min = int(
            config.event_duration_min
        )

        self.event_duration_max = int(
            config.event_duration_max
        )

        self.event_radius = float(
            config.event_radius_m
        )

        self.event_amplitude = float(
            config.event_amplitude
        )

        if not 0.0 <= self.phi < 1.0:
            raise ValueError(
                "temporal_correlation must be in [0,1)."
            )

        if self.lambda_s <= 0:
            raise ValueError(
                "Spatial correlation length must be positive."
            )

        self.rng = np.random.default_rng(
            config.seed + 4000
        )

        # --------------------------------------
        # Spatial covariance
        # --------------------------------------

        self.spatial_covariance = np.exp(
            -topology.distance_matrix
            / self.lambda_s
        )

        covariance = (
            self.spatial_covariance
            + 1e-10
            * np.eye(
                self.num_nodes
            )
        )

        self.cholesky = np.linalg.cholesky(
            covariance
        )

        # Background process is maintained
        # independently of event observations.
        self.background_state = np.zeros(
            self.num_nodes,
            dtype=np.float64
        )

        self.state = np.zeros(
            self.num_nodes,
            dtype=np.float64
        )

        self.previous_observation = (
            self.state.copy()
        )

        # Event state
        self.event_active = False
        self.event_center = None
        self.event_remaining = 0

        self.current_event_intensity = np.zeros(
            self.num_nodes,
            dtype=np.float64
        )

        self.round_id = 0

    def _start_event(self):
        self.event_center = np.array(
            [
                self.rng.uniform(
                    0.0,
                    self.config.area_width
                ),
                self.rng.uniform(
                    0.0,
                    self.config.area_height
                )
            ],
            dtype=np.float64
        )

        self.event_remaining = int(
            self.rng.integers(
                self.event_duration_min,
                self.event_duration_max + 1
            )
        )

        self.event_active = True

    def _update_event(self):
        if self.event_active:
            self.event_remaining -= 1

            if self.event_remaining <= 0:
                self.event_active = False
                self.event_center = None

        if (
            not self.event_active
            and self.rng.random()
            < self.event_probability
        ):
            self._start_event()

    def _event_profile(self):
        if not self.event_active:
            return np.zeros(
                self.num_nodes,
                dtype=np.float64
            )

        delta = (
            self.topology.positions
            - self.event_center
        )

        distance = np.linalg.norm(
            delta,
            axis=1
        )

        return (
            self.event_amplitude
            * np.exp(
                -0.5
                * (
                    distance
                    / self.event_radius
                ) ** 2
            )
        )

    def step(self):
        self.round_id += 1

        self.previous_observation = (
            self.state.copy()
        )

        independent_noise = self.rng.normal(
            0.0,
            1.0,
            self.num_nodes
        )

        correlated_noise = (
            self.cholesky
            @ independent_noise
        )

        correlated_noise *= (
            self.noise_std
        )

        # AR(1) BACKGROUND ONLY.
        self.background_state = (
            self.phi
            * self.background_state
            + np.sqrt(
                1.0 - self.phi ** 2
            )
            * correlated_noise
        )

        self._update_event()

        self.current_event_intensity = (
            self._event_profile()
        )

        # Event is superimposed on the background;
        # it is not part of next round's AR recursion.
        self.state = (
            self.background_state
            + self.current_event_intensity
        )

        return self.state.copy()

    def event_truth(
        self,
        threshold=0.5
    ):
        return (
            self.current_event_intensity
            >= threshold
        )
