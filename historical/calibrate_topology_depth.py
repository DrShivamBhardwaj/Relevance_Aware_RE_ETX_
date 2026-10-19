from dataclasses import replace
import numpy as np

from config import SimulationConfig
from simulator.topology import Topology
from simulator.energy import RadioEnergyModel
from simulator.network import SensorNetwork
from simulator.channel import WirelessChannel
from simulator.frame import FrameModel
from simulator.link_graph import LinkGraph
from simulator.routing_semantic_re_etx import (
    SemanticResidualEnergyETXRouter,
)

SEEDS = [11, 23, 42, 67, 101, 137, 173, 211, 257, 307]

# Keep 100 nodes and 100 m field width.
# Increase field depth while keeping the BS 50 m above
# the upper field boundary. This creates deeper multi-hop
# paths without artificially moving the BS out of radio range.
HEIGHTS = [450, 500, 550, 600, 650]
RADII = [35, 40, 45, 50, 55, 60]


def evaluate(seed, height, radius):
    base = SimulationConfig()

    cfg = replace(
        base,
        seed=seed,
        num_nodes=100,
        area_width=100.0,
        area_height=float(height),
        bs_x=50.0,
        bs_y=float(height + 50),
        max_sensor_link_distance_m=float(radius),
    )

    topology = Topology(cfg)
    network = SensorNetwork(cfg, topology)
    channel = WirelessChannel(cfg)
    frame = FrameModel(cfg)

    graph = LinkGraph(
        cfg,
        topology,
        channel,
        frame,
    )

    router = SemanticResidualEnergyETXRouter(
        graph,
        network.energy,
        cfg.initial_energy,
        alive_mask=network.alive,
        energy_weight=0.25,
        semantic_weight=0.0,
        semantic_age=np.zeros(
            cfg.num_nodes,
            dtype=float,
        ),
    )

    hops = []
    direct = 0
    no_route = 0

    for node in range(cfg.num_nodes):
        path = router.route(node)

        if path is None:
            no_route += 1
            continue

        h = len(path) - 1
        hops.append(h)

        if h == 1:
            direct += 1

    if hops:
        mean_hops = float(np.mean(hops))
        p90_hops = float(np.percentile(hops, 90))
        max_hops = int(np.max(hops))
    else:
        mean_hops = np.nan
        p90_hops = np.nan
        max_hops = 0

    coverage = (
        (cfg.num_nodes - no_route)
        / cfg.num_nodes
    )

    return {
        "mean_hops": mean_hops,
        "p90_hops": p90_hops,
        "max_hops": max_hops,
        "coverage": coverage,
        "direct_fraction": direct / cfg.num_nodes,
        "sensor_edges": graph.sensor_edge_count,
    }


print()
print("=" * 112)
print("ELONGATED-FIELD TOPOLOGY-DEPTH CALIBRATION — 10 SEEDS")
print("=" * 112)

print(
    f"{'HEIGHT':>7} "
    f"{'BS_Y':>7} "
    f"{'RADIUS':>7} "
    f"{'MEAN_HOPS':>10} "
    f"{'P90_HOPS':>9} "
    f"{'MAX':>6} "
    f"{'COVERAGE_%':>11} "
    f"{'DIRECT_%':>9} "
    f"{'EDGES':>9}"
)

print("-" * 112)

results = []

for height in HEIGHTS:
    for radius in RADII:
        runs = [
            evaluate(
                seed,
                height,
                radius,
            )
            for seed in SEEDS
        ]

        valid_hops = [
            x["mean_hops"]
            for x in runs
            if np.isfinite(x["mean_hops"])
        ]

        valid_p90 = [
            x["p90_hops"]
            for x in runs
            if np.isfinite(x["p90_hops"])
        ]

        mean_hops = (
            float(np.mean(valid_hops))
            if valid_hops
            else np.nan
        )

        p90_hops = (
            float(np.mean(valid_p90))
            if valid_p90
            else np.nan
        )

        max_hops = max(
            x["max_hops"]
            for x in runs
        )

        coverage = 100.0 * np.mean(
            [x["coverage"] for x in runs]
        )

        direct_fraction = 100.0 * np.mean(
            [x["direct_fraction"] for x in runs]
        )

        edges = np.mean(
            [x["sensor_edges"] for x in runs]
        )

        results.append({
            "height": height,
            "bs_y": height + 50,
            "radius": radius,
            "mean_hops": mean_hops,
            "coverage": coverage,
        })

        print(
            f"{height:7.0f} "
            f"{height + 50:7.0f} "
            f"{radius:7.0f} "
            f"{mean_hops:10.3f} "
            f"{p90_hops:9.3f} "
            f"{max_hops:6d} "
            f"{coverage:11.2f} "
            f"{direct_fraction:9.2f} "
            f"{edges:9.1f}"
        )

print()
print("=" * 112)
print("BEST >=95% COVERAGE CANDIDATES")
print("=" * 112)

valid = [
    x
    for x in results
    if (
        x["coverage"] >= 95.0
        and np.isfinite(x["mean_hops"])
    )
]

for target in [4.0, 4.5, 5.0]:
    best = min(
        valid,
        key=lambda x: abs(
            x["mean_hops"] - target
        ),
    )

    print(
        f"Target ~{target:.1f} hops -> "
        f"height={best['height']} m, "
        f"BS_Y={best['bs_y']} m, "
        f"radius={best['radius']} m, "
        f"mean={best['mean_hops']:.3f}, "
        f"coverage={best['coverage']:.2f}%"
    )
