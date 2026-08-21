import numpy as np


class SemanticRelevanceEstimator:
    """
    Stateful semantic-relevance estimator.

    Relevance is measured relative to a historical baseline,
    rather than normalizing independently within every round.

    Features:
      - temporal innovation
      - spatial deviation from neighborhood median

    Ground-truth event information is never used.
    """

    def __init__(
        self,
        topology,
        neighbor_radius=20.0,
        temporal_weight=0.6,
        spatial_weight=0.4,
        warmup_rounds=50,
        ewma_alpha=0.02,
        baseline_clip_sigma=3.0,
        z_clip=8.0,
        epsilon=1e-9
    ):
        self.topology = topology

        self.num_nodes = int(
            topology.positions.shape[0]
        )

        self.neighbor_radius = float(
            neighbor_radius
        )

        self.temporal_weight = float(
            temporal_weight
        )

        self.spatial_weight = float(
            spatial_weight
        )

        self.warmup_rounds = int(
            warmup_rounds
        )

        self.ewma_alpha = float(
            ewma_alpha
        )

        self.baseline_clip_sigma = float(
            baseline_clip_sigma
        )

        self.z_clip = float(
            z_clip
        )

        self.epsilon = float(
            epsilon
        )

        distance = (
            topology.distance_matrix
        )

        self.neighbor_mask = (
            distance
            <= self.neighbor_radius
        )

        np.fill_diagonal(
            self.neighbor_mask,
            False
        )

        self.round_count = 0

        # Warm-up accumulators.
        self.temp_sum = np.zeros(
            self.num_nodes
        )

        self.temp_sq_sum = np.zeros(
            self.num_nodes
        )

        self.spatial_sum = np.zeros(
            self.num_nodes
        )

        self.spatial_sq_sum = np.zeros(
            self.num_nodes
        )

        # Adaptive baseline statistics.
        self.temp_mean = np.zeros(
            self.num_nodes
        )

        self.temp_var = np.full(
            self.num_nodes,
            1e-6
        )

        self.spatial_mean = np.zeros(
            self.num_nodes
        )

        self.spatial_var = np.full(
            self.num_nodes,
            1e-6
        )

        self.baseline_ready = False

    def _spatial_feature(
        self,
        current
    ):
        reference = np.empty(
            self.num_nodes,
            dtype=np.float64
        )

        for i in range(
            self.num_nodes
        ):
            neighbors = np.flatnonzero(
                self.neighbor_mask[i]
            )

            if neighbors.size > 0:
                reference[i] = float(
                    np.median(
                        current[
                            neighbors
                        ]
                    )
                )
            else:
                reference[i] = (
                    current[i]
                )

        return np.abs(
            current - reference
        )

    def _finish_warmup(self):
        n = float(
            self.warmup_rounds
        )

        self.temp_mean = (
            self.temp_sum / n
        )

        self.spatial_mean = (
            self.spatial_sum / n
        )

        self.temp_var = np.maximum(
            self.temp_sq_sum / n
            - self.temp_mean ** 2,
            1e-8
        )

        self.spatial_var = np.maximum(
            self.spatial_sq_sum / n
            - self.spatial_mean ** 2,
            1e-8
        )

        self.baseline_ready = True

    def _update_baseline(
        self,
        temporal,
        spatial
    ):
        temp_std = np.sqrt(
            self.temp_var
        )

        spatial_std = np.sqrt(
            self.spatial_var
        )

        # Prevent strong events from rapidly contaminating
        # the normal-behavior baseline.
        clipped_temporal = np.minimum(
            temporal,
            self.temp_mean
            + self.baseline_clip_sigma
            * temp_std
        )

        clipped_spatial = np.minimum(
            spatial,
            self.spatial_mean
            + self.baseline_clip_sigma
            * spatial_std
        )

        alpha = (
            self.ewma_alpha
        )

        temp_delta = (
            clipped_temporal
            - self.temp_mean
        )

        spatial_delta = (
            clipped_spatial
            - self.spatial_mean
        )

        self.temp_mean = (
            (1.0 - alpha)
            * self.temp_mean
            + alpha
            * clipped_temporal
        )

        self.spatial_mean = (
            (1.0 - alpha)
            * self.spatial_mean
            + alpha
            * clipped_spatial
        )

        self.temp_var = (
            (1.0 - alpha)
            * self.temp_var
            + alpha
            * temp_delta ** 2
        )

        self.spatial_var = (
            (1.0 - alpha)
            * self.spatial_var
            + alpha
            * spatial_delta ** 2
        )

        self.temp_var = np.maximum(
            self.temp_var,
            1e-8
        )

        self.spatial_var = np.maximum(
            self.spatial_var,
            1e-8
        )

    def compute(
        self,
        current,
        previous
    ):
        current = np.asarray(
            current,
            dtype=np.float64
        )

        previous = np.asarray(
            previous,
            dtype=np.float64
        )

        temporal = np.abs(
            current - previous
        )

        spatial = (
            self._spatial_feature(
                current
            )
        )

        self.round_count += 1

        # --------------------------------------
        # Calibration period
        # --------------------------------------

        if not self.baseline_ready:
            self.temp_sum += (
                temporal
            )

            self.temp_sq_sum += (
                temporal ** 2
            )

            self.spatial_sum += (
                spatial
            )

            self.spatial_sq_sum += (
                spatial ** 2
            )

            if (
                self.round_count
                >= self.warmup_rounds
            ):
                self._finish_warmup()

            return {
                "relevance":
                    np.zeros(
                        self.num_nodes,
                        dtype=np.float64
                    ),

                "temporal_novelty":
                    np.zeros(
                        self.num_nodes,
                        dtype=np.float64
                    ),

                "spatial_novelty":
                    np.zeros(
                        self.num_nodes,
                        dtype=np.float64
                    ),

                "baseline_ready":
                    self.baseline_ready
            }

        # --------------------------------------
        # Score BEFORE updating baseline
        # --------------------------------------

        temp_std = np.sqrt(
            self.temp_var
        )

        spatial_std = np.sqrt(
            self.spatial_var
        )

        z_temporal = (
            temporal
            - self.temp_mean
        ) / (
            temp_std
            + self.epsilon
        )

        z_spatial = (
            spatial
            - self.spatial_mean
        ) / (
            spatial_std
            + self.epsilon
        )

        z_temporal = np.clip(
            z_temporal,
            0.0,
            self.z_clip
        )

        z_spatial = np.clip(
            z_spatial,
            0.0,
            self.z_clip
        )

        combined = (
            self.temporal_weight
            * z_temporal
            + self.spatial_weight
            * z_spatial
        )

        relevance = (
            1.0
            - np.exp(
                -combined
            )
        )

        relevance = np.clip(
            relevance,
            0.0,
            1.0
        )

        # Baseline adaptation occurs only after scoring.
        self._update_baseline(
            temporal,
            spatial
        )

        return {
            "relevance":
                relevance,

            "temporal_novelty":
                z_temporal,

            "spatial_novelty":
                z_spatial,

            "baseline_ready":
                True
        }
