import heapq
import numpy as np


class ResidualEnergyETXRouter:
    """
    Residual-Energy-Aware ETX routing.

    Dynamic link cost:

        C_ij = ETX_ij *
               [1 + lambda_E * (phi_i + phi_j)/2]

    where:

        phi_i = 1 / normalized_residual_energy_i - 1

    Dead nodes are excluded from the routing graph.
    """

    def __init__(
        self,
        link_graph,
        residual_energy,
        initial_energy,
        alive_mask=None,
        energy_weight=1.0,
        epsilon=1e-12
    ):
        self.graph = link_graph

        self.num_nodes = (
            link_graph.num_nodes
        )

        self.sink_id = (
            link_graph.sink_id
        )

        self.total_vertices = (
            self.num_nodes + 1
        )

        self.energy_weight = float(
            energy_weight
        )

        self.epsilon = float(
            epsilon
        )

        self.residual_energy = np.asarray(
            residual_energy,
            dtype=np.float64
        ).copy()

        if (
            self.residual_energy.shape
            != (self.num_nodes,)
        ):
            raise ValueError(
                "Residual-energy vector has invalid shape."
            )

        if alive_mask is None:
            self.alive_mask = (
                self.residual_energy
                > self.epsilon
            )
        else:
            self.alive_mask = np.asarray(
                alive_mask,
                dtype=bool
            ).copy()

        if (
            self.alive_mask.shape
            != (self.num_nodes,)
        ):
            raise ValueError(
                "alive_mask has invalid shape."
            )

        self.initial_energy = float(
            initial_energy
        )

        if self.initial_energy <= 0:
            raise ValueError(
                "Initial energy must be positive."
            )

        # --------------------------------------
        # Normalized energy
        # --------------------------------------

        normalized_energy = (
            self.residual_energy
            / self.initial_energy
        )

        normalized_energy = np.clip(
            normalized_energy,
            self.epsilon,
            1.0
        )

        # Energy scarcity:
        #
        # full energy -> 0
        # 50% energy  -> 1
        # 25% energy  -> 3
        #
        self.energy_scarcity = (
            1.0
            / normalized_energy
            - 1.0
        )

        self.adjacency = (
            self._build_adjacency()
        )

        (
            self.path_cost,
            self.next_hop
        ) = self._run_dijkstra()

    def _sensor_link_cost(
        self,
        i,
        j
    ):
        base_etx = float(
            self.graph.sensor_etx[
                i,
                j
            ]
        )

        scarcity = (
            self.energy_scarcity[i]
            + self.energy_scarcity[j]
        ) / 2.0

        return (
            base_etx
            * (
                1.0
                + self.energy_weight
                * scarcity
            )
        )

    def _sink_link_cost(
        self,
        i
    ):
        base_etx = float(
            self.graph.bs_etx[i]
        )

        # Sink is externally powered:
        # scarcity_sink = 0.
        scarcity = (
            self.energy_scarcity[i]
            / 2.0
        )

        return (
            base_etx
            * (
                1.0
                + self.energy_weight
                * scarcity
            )
        )

    def _build_adjacency(self):
        adjacency = [
            []
            for _ in range(
                self.total_vertices
            )
        ]

        # --------------------------------------
        # Sensor-to-sensor links
        # --------------------------------------

        for i in range(
            self.num_nodes
        ):
            if not self.alive_mask[i]:
                continue

            neighbors = np.flatnonzero(
                self.graph.neighbor_mask[i]
            )

            for j in neighbors:
                j = int(j)

                if j <= i:
                    continue

                if not self.alive_mask[j]:
                    continue

                weight = (
                    self._sensor_link_cost(
                        i,
                        j
                    )
                )

                adjacency[i].append(
                    (
                        j,
                        weight
                    )
                )

                adjacency[j].append(
                    (
                        i,
                        weight
                    )
                )

        # --------------------------------------
        # Sensor-to-sink links
        # --------------------------------------

        for i in range(
            self.num_nodes
        ):
            if not self.alive_mask[i]:
                continue

            if not self.graph.bs_link_mask[i]:
                continue

            weight = (
                self._sink_link_cost(i)
            )

            adjacency[i].append(
                (
                    self.sink_id,
                    weight
                )
            )

            adjacency[
                self.sink_id
            ].append(
                (
                    i,
                    weight
                )
            )

        return adjacency

    def _run_dijkstra(self):
        distance = np.full(
            self.total_vertices,
            np.inf,
            dtype=np.float64
        )

        next_hop = np.full(
            self.total_vertices,
            -1,
            dtype=np.int64
        )

        distance[
            self.sink_id
        ] = 0.0

        queue = [
            (
                0.0,
                self.sink_id
            )
        ]

        visited = np.zeros(
            self.total_vertices,
            dtype=bool
        )

        while queue:
            current_cost, current = (
                heapq.heappop(queue)
            )

            if visited[current]:
                continue

            visited[current] = True

            for neighbor, weight in (
                self.adjacency[current]
            ):
                candidate = (
                    current_cost
                    + weight
                )

                if (
                    candidate
                    < distance[neighbor]
                ):
                    distance[
                        neighbor
                    ] = candidate

                    next_hop[
                        neighbor
                    ] = current

                    heapq.heappush(
                        queue,
                        (
                            candidate,
                            neighbor
                        )
                    )

        next_hop[
            self.sink_id
        ] = self.sink_id

        return (
            distance,
            next_hop
        )

    def has_route(
        self,
        node_id
    ):
        if (
            node_id < self.num_nodes
            and not self.alive_mask[node_id]
        ):
            return False

        return bool(
            np.isfinite(
                self.path_cost[
                    node_id
                ]
            )
        )

    def route(
        self,
        node_id
    ):
        if not self.has_route(
            node_id
        ):
            return None

        path = [
            int(node_id)
        ]

        current = int(
            node_id
        )

        visited = set(path)

        while (
            current
            != self.sink_id
        ):
            next_node = int(
                self.next_hop[
                    current
                ]
            )

            if next_node < 0:
                return None

            if (
                next_node in visited
                and next_node
                != self.sink_id
            ):
                raise RuntimeError(
                    "Routing loop detected."
                )

            path.append(
                next_node
            )

            visited.add(
                next_node
            )

            current = next_node

        return path

    def hop_count(
        self,
        node_id
    ):
        path = self.route(
            node_id
        )

        if path is None:
            return None

        return (
            len(path) - 1
        )
