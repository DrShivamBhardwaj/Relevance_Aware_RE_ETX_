import heapq
import numpy as np


class MinimumETXRouter:
    """
    Minimum cumulative ETX routing toward a single sink.

    Dead nodes can be excluded through alive_mask.
    """

    def __init__(
        self,
        link_graph,
        alive_mask=None
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

        if alive_mask is None:
            self.alive_mask = np.ones(
                self.num_nodes,
                dtype=bool
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

        self.adjacency = (
            self._build_adjacency()
        )

        (
            self.path_cost,
            self.next_hop
        ) = self._run_dijkstra()

    def _build_adjacency(self):
        adjacency = [
            []
            for _ in range(
                self.total_vertices
            )
        ]

        # Sensor-to-sensor links
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

                weight = float(
                    self.graph.sensor_etx[
                        i,
                        j
                    ]
                )

                adjacency[i].append(
                    (j, weight)
                )

                adjacency[j].append(
                    (i, weight)
                )

        # Sensor-to-BS links
        for node_id in range(
            self.num_nodes
        ):
            if not self.alive_mask[
                node_id
            ]:
                continue

            if not self.graph.bs_link_mask[
                node_id
            ]:
                continue

            weight = float(
                self.graph.bs_etx[
                    node_id
                ]
            )

            adjacency[node_id].append(
                (
                    self.sink_id,
                    weight
                )
            )

            adjacency[
                self.sink_id
            ].append(
                (
                    node_id,
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

        return distance, next_hop

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
