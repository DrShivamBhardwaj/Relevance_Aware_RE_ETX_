from dataclasses import dataclass
import heapq
import math
import numpy as np

from .config import SimConfig


@dataclass(frozen=True)
class Route:
    nodes: tuple
    gateway: int
    cost: float
    etx_sum: float
    hops: int

    @property
    def relays(self):
        return self.nodes[1:-1]


class WSNTopology:
    """Multi-hop WSN substrate. RE-ETX-like cost is prior infrastructure."""

    def __init__(self, cfg: SimConfig, rng: np.random.Generator):
        self.cfg = cfg
        self.n = cfg.num_clients
        self.g = cfg.num_gateways
        self.client_xy = rng.uniform(0.05, 0.95, size=(self.n, 2))
        base_gateways = np.array([[0.18, 0.18], [0.82, 0.18], [0.18, 0.82], [0.82, 0.82]])
        if self.g <= 4:
            self.gateway_xy = base_gateways[: self.g].copy()
        else:
            self.gateway_xy = rng.uniform(0.10, 0.90, size=(self.g, 2))
        self.sensor_etx = np.full((self.n, self.n), np.inf, dtype=float)
        self.gateway_etx = np.full((self.n, self.g), np.inf, dtype=float)
        self._build_links(rng)

    @staticmethod
    def _link_p(distance: float, jitter: float = 1.0) -> float:
        p = math.exp(-3.7 * distance) * jitter
        return float(np.clip(p, 0.08, 0.985))
    def _build_links(self, rng: np.random.Generator):
        for i in range(self.n):
            for j in range(i + 1, self.n):
                d = float(np.linalg.norm(self.client_xy[i] - self.client_xy[j]))
                if d <= self.cfg.sensor_radius:
                    jitter = float(rng.uniform(0.90, 1.08))
                    p = self._link_p(d, jitter)
                    etx = 1.0 / p
                    self.sensor_etx[i, j] = etx
                    self.sensor_etx[j, i] = etx
            for g in range(self.g):
                d = float(np.linalg.norm(self.client_xy[i] - self.gateway_xy[g]))
                # Gateways remain reachable even when distant; poor direct links get high ETX.
                jitter = float(rng.uniform(0.92, 1.05))
                p = self._link_p(d, jitter)
                if d > self.cfg.gateway_radius:
                    p *= 0.10
                self.gateway_etx[i, g] = 1.0 / max(p, 0.05)

    def route(self, source: int, residual_energy: np.ndarray, initial_energy: np.ndarray) -> Route:
        scarcity = np.maximum(initial_energy / np.maximum(residual_energy, 1e-9) - 1.0, 0.0)
        total = self.n + self.g
        dist = np.full(total, np.inf)
        prev = np.full(total, -1, dtype=int)
        dist[source] = 0.0
        heap = [(0.0, source)]

        while heap:
            d_u, u = heapq.heappop(heap)
            if d_u != dist[u]:
                continue
            if u >= self.n:
                continue
            for v in range(self.n):
                base = self.sensor_etx[u, v]
                if not np.isfinite(base) or residual_energy[v] <= 0:
                    continue
                penalty = 1.0 + self.cfg.etx_energy_weight * 0.5 * (scarcity[u] + scarcity[v])
                nd = d_u + base * penalty
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
            for g in range(self.g):
                v = self.n + g
                base = self.gateway_etx[u, g]
                penalty = 1.0 + self.cfg.etx_energy_weight * 0.5 * scarcity[u]
                nd = d_u + base * penalty
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))

        targets = np.arange(self.n, total)
        target = int(targets[np.argmin(dist[targets])])
        if not np.isfinite(dist[target]):
            raise RuntimeError(f"No gateway route for client {source}")
        path = [target]
        cur = target
        while cur != source:
            cur = int(prev[cur])
            if cur < 0:
                raise RuntimeError("Broken predecessor chain")
            path.append(cur)
        path.reverse()

        etx_sum = 0.0
        for u, v in zip(path[:-1], path[1:]):
            if v < self.n:
                etx_sum += float(self.sensor_etx[u, v])
            else:
                etx_sum += float(self.gateway_etx[u, v - self.n])
        return Route(tuple(path), target - self.n, float(dist[target]), etx_sum, len(path) - 1)

    def all_routes(self, residual_energy: np.ndarray, initial_energy: np.ndarray):
        return [self.route(i, residual_energy, initial_energy) for i in range(self.n)]
