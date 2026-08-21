import numpy as np


class SensorNetwork:
    """
    Dynamic energy and alive/dead state of WSN nodes.
    """

    def __init__(self, config, topology):
        self.config = config
        self.topology = topology

        self.num_nodes = int(
            config.num_nodes
        )

        self.energy_epsilon = float(
            config.energy_epsilon
        )

        self.energy = np.full(
            self.num_nodes,
            config.initial_energy,
            dtype=np.float64
        )

        self.alive = np.ones(
            self.num_nodes,
            dtype=bool
        )

        self.death_round = np.full(
            self.num_nodes,
            -1,
            dtype=np.int64
        )

        self.cumulative_energy_consumed = 0.0

    @property
    def num_alive(self):
        return int(
            np.sum(self.alive)
        )

    @property
    def num_dead(self):
        return int(
            self.num_nodes
            - self.num_alive
        )

    @property
    def total_residual_energy(self):
        return float(
            np.sum(self.energy)
        )

    @property
    def dead_fraction(self):
        return (
            self.num_dead
            / self.num_nodes
        )

    def consume_energy(
        self,
        node_ids,
        energy_cost,
        round_id
    ):
        node_ids = np.atleast_1d(
            np.asarray(
                node_ids,
                dtype=np.int64
            )
        )

        energy_cost = np.atleast_1d(
            np.asarray(
                energy_cost,
                dtype=np.float64
            )
        )

        if (
            energy_cost.size == 1
            and node_ids.size > 1
        ):
            energy_cost = np.full(
                node_ids.shape,
                energy_cost.item(),
                dtype=np.float64
            )

        if (
            node_ids.size
            != energy_cost.size
        ):
            raise ValueError(
                "node_ids and energy_cost must "
                "have equal length."
            )

        if (
            np.any(node_ids < 0)
            or np.any(
                node_ids >= self.num_nodes
            )
        ):
            raise IndexError(
                "Invalid node ID."
            )

        if np.any(
            energy_cost < 0
        ):
            raise ValueError(
                "Energy cost cannot be negative."
            )

        active_mask = (
            self.alive[
                node_ids
            ]
        )

        active_ids = (
            node_ids[
                active_mask
            ]
        )

        active_costs = (
            energy_cost[
                active_mask
            ]
        )

        if active_ids.size == 0:
            return np.array(
                [],
                dtype=np.int64
            )

        total_cost_per_node = (
            np.bincount(
                active_ids,
                weights=active_costs,
                minlength=self.num_nodes
            )
        )

        actual_consumption = (
            np.minimum(
                self.energy,
                total_cost_per_node
            )
        )

        self.energy -= (
            total_cost_per_node
        )

        # Clamp true negative values.
        self.energy = np.maximum(
            self.energy,
            0.0
        )

        # Eliminate floating-point residual energy.
        near_zero = (
            self.energy
            <= self.energy_epsilon
        )

        self.energy[
            near_zero
        ] = 0.0

        self.cumulative_energy_consumed += float(
            np.sum(
                actual_consumption
            )
        )

        newly_dead_mask = (
            self.alive
            & (
                self.energy
                <= self.energy_epsilon
            )
        )

        newly_dead_ids = (
            np.flatnonzero(
                newly_dead_mask
            )
        )

        if (
            newly_dead_ids.size
            > 0
        ):
            self.death_round[
                newly_dead_ids
            ] = round_id

            self.alive[
                newly_dead_ids
            ] = False

        return newly_dead_ids

    def reset(self):
        self.energy.fill(
            self.config.initial_energy
        )

        self.alive.fill(
            True
        )

        self.death_round.fill(
            -1
        )

        self.cumulative_energy_consumed = 0.0
