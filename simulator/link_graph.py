import numpy as np


class LinkGraph:
    """
    Static WSN link-quality graph.

    Sensor-to-sensor links use:
        - pairwise distance
        - symmetric static log-normal shadowing
        - SNR
        - one-attempt fragmented-message success probability

    Sensor-to-BS links reuse the same deterministic BS-shadowing
    stream used by the previous direct-to-BS lossy baseline.
    """

    def __init__(
        self,
        config,
        topology,
        channel,
        frame_model
    ):
        self.config = config
        self.topology = topology
        self.channel = channel
        self.frame_model = frame_model

        self.num_nodes = int(
            config.num_nodes
        )

        self.sink_id = (
            self.num_nodes
        )

        self.max_sensor_distance = float(
            config.max_sensor_link_distance_m
        )

        self.min_link_success = float(
            config.min_link_success
        )

        self.etx_epsilon = float(
            config.etx_epsilon
        )

        # ----------------------------------------
        # Sensor-to-sensor geometry
        # ----------------------------------------

        self.sensor_distance = (
            topology.distance_matrix.copy()
        )

        # Separate deterministic random stream for
        # reciprocal sensor-to-sensor slow shadowing.
        pair_rng = np.random.default_rng(
            config.seed + 3000
        )

        self.sensor_shadowing = np.zeros(
            (
                self.num_nodes,
                self.num_nodes
            ),
            dtype=np.float64
        )

        upper = np.triu_indices(
            self.num_nodes,
            k=1
        )

        upper_values = pair_rng.normal(
            loc=0.0,
            scale=config.shadowing_sigma_db,
            size=len(upper[0])
        )

        self.sensor_shadowing[
            upper
        ] = upper_values

        self.sensor_shadowing[
            (
                upper[1],
                upper[0]
            )
        ] = upper_values

        # ----------------------------------------
        # Sensor-to-sensor SNR
        # ----------------------------------------

        self.sensor_snr = (
            channel.snr_db(
                self.sensor_distance,
                self.sensor_shadowing
            )
        )

        # ----------------------------------------
        # One-attempt fragmented-message success
        # ----------------------------------------

        self.sensor_message_success = (
            self._message_success_matrix(
                self.sensor_snr
            )
        )

        np.fill_diagonal(
            self.sensor_message_success,
            0.0
        )

        # ----------------------------------------
        # Neighbor eligibility
        # ----------------------------------------

        distance_ok = (
            self.sensor_distance
            <= self.max_sensor_distance
        )

        quality_ok = (
            self.sensor_message_success
            >= self.min_link_success
        )

        self.neighbor_mask = (
            distance_ok
            & quality_ok
        )

        np.fill_diagonal(
            self.neighbor_mask,
            False
        )

        # ----------------------------------------
        # ETX matrix
        #
        # ETX = 1 / P_message
        # ----------------------------------------

        self.sensor_etx = np.full(
            (
                self.num_nodes,
                self.num_nodes
            ),
            np.inf,
            dtype=np.float64
        )

        valid_probabilities = np.maximum(
            self.sensor_message_success,
            self.etx_epsilon
        )

        self.sensor_etx[
            self.neighbor_mask
        ] = (
            1.0
            / valid_probabilities[
                self.neighbor_mask
            ]
        )

        # ----------------------------------------
        # Sensor-to-BS links
        #
        # Calling this first on a newly created
        # WirelessChannel reproduces the BS shadowing
        # used in the earlier direct-to-BS experiment.
        # ----------------------------------------

        self.bs_shadowing = (
            channel.sample_static_shadowing(
                self.num_nodes
            )
        )

        self.bs_snr = (
            channel.snr_db(
                topology.distance_to_bs,
                self.bs_shadowing
            )
        )

        self.bs_message_success = (
            self._message_success_vector(
                self.bs_snr
            )
        )

        self.bs_link_mask = (
            self.bs_message_success
            >= self.min_link_success
        )

        self.bs_etx = np.full(
            self.num_nodes,
            np.inf,
            dtype=np.float64
        )

        valid_bs = np.maximum(
            self.bs_message_success,
            self.etx_epsilon
        )

        self.bs_etx[
            self.bs_link_mask
        ] = (
            1.0
            / valid_bs[
                self.bs_link_mask
            ]
        )

    def _message_success_matrix(
        self,
        snr_matrix
    ):
        probability = np.ones_like(
            snr_matrix,
            dtype=np.float64
        )

        for frame_bits in (
            self.frame_model.fragment_sizes()
        ):
            probability *= (
                self.channel.frame_success_probability(
                    int(frame_bits),
                    snr_matrix
                )
            )

        return np.clip(
            probability,
            0.0,
            1.0
        )

    def _message_success_vector(
        self,
        snr_vector
    ):
        probability = np.ones_like(
            snr_vector,
            dtype=np.float64
        )

        for frame_bits in (
            self.frame_model.fragment_sizes()
        ):
            probability *= (
                self.channel.frame_success_probability(
                    int(frame_bits),
                    snr_vector
                )
            )

        return np.clip(
            probability,
            0.0,
            1.0
        )

    def neighbors(
        self,
        node_id
    ):
        return np.flatnonzero(
            self.neighbor_mask[
                node_id
            ]
        )

    def degree(
        self,
        node_id
    ):
        return int(
            np.sum(
                self.neighbor_mask[
                    node_id
                ]
            )
        )

    @property
    def sensor_edge_count(self):
        return int(
            np.sum(
                np.triu(
                    self.neighbor_mask,
                    k=1
                )
            )
        )

    @property
    def bs_edge_count(self):
        return int(
            np.sum(
                self.bs_link_mask
            )
        )
