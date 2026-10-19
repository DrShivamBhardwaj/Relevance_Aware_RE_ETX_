import numpy as np


class Topology:
    def __init__(self, config):
        self.config = config
        self.rng = np.random.default_rng(config.seed)

        # Deploy sensor nodes
        self.positions = self._deploy_nodes()

        # Base station coordinate
        self.base_station = np.array(
            [config.bs_x, config.bs_y],
            dtype=np.float64
        )

        # Pre-compute distances
        self.distance_matrix = self._calculate_distance_matrix()
        self.distance_to_bs = self._calculate_distance_to_bs()

    def _deploy_nodes(self):
        x = self.rng.uniform(
            0.0,
            self.config.area_width,
            self.config.num_nodes
        )

        y = self.rng.uniform(
            0.0,
            self.config.area_height,
            self.config.num_nodes
        )

        return np.column_stack((x, y))

    def _calculate_distance_matrix(self):
        delta = (
            self.positions[:, None, :]
            - self.positions[None, :, :]
        )

        return np.linalg.norm(delta, axis=2)

    def _calculate_distance_to_bs(self):
        delta = self.positions - self.base_station

        return np.linalg.norm(delta, axis=1)
