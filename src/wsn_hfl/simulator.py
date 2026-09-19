from collections import defaultdict
from dataclasses import asdict, replace
import math
import numpy as np

from .config import SimConfig
from .data import class_coverage, js_divergence, make_synthetic_data
from .model import accuracy, cosine_novelty, local_train, loss_and_grad, macro_f1, topk_compress
from .scheduler import schedule
from .topology import WSNTopology


def _norm(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    lo = float(x.min())
    hi = float(x.max())
    if hi - lo <= 1e-12:
        return np.full_like(x, 0.5)
    return (x - lo) / (hi - lo)


def _jain(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    den = len(x) * float(np.sum(x * x))
    if den <= 1e-12:
        return 1.0
    return float(np.sum(x) ** 2 / den)


def _link_etx(topology: WSNTopology, u: int, v: int) -> float:
    if v < topology.n:
        return float(topology.sensor_etx[u, v])
    return float(topology.gateway_etx[u, v - topology.n])


def _charge_path(cfg, topology, route, bits, residual_energy, relay_energy):
    spent = 0.0
    for u, v in zip(route.nodes[:-1], route.nodes[1:]):
        etx = _link_etx(topology, u, v)
        if u < topology.n:
            e_tx = bits * cfg.tx_energy_per_bit_j * etx
            residual_energy[u] -= e_tx
            spent += e_tx
            if u != route.nodes[0]:
                relay_energy[u] += e_tx
        if v < topology.n:
            e_rx = bits * cfg.rx_energy_per_bit_j * etx
            residual_energy[v] -= e_rx
            spent += e_rx
            relay_energy[v] += e_rx
    np.maximum(residual_energy, 0.0, out=residual_energy)
    return spent
def simulate(method: str, cfg: SimConfig):
    rng = np.random.default_rng(cfg.seed)
    topology = WSNTopology(cfg, rng)
    initial_energy = rng.uniform(
        cfg.energy_initial_j - cfg.energy_jitter,
        cfg.energy_initial_j + cfg.energy_jitter,
        size=cfg.num_clients,
    )
    residual_energy = initial_energy.copy()
    initial_routes = topology.all_routes(residual_energy, initial_energy)
    difficulty = np.array([r.cost for r in initial_routes], dtype=float)
    client_data, test_data, client_probs = make_synthetic_data(cfg, rng, difficulty)

    w = np.zeros((cfg.feature_dim + 1, cfg.num_classes), dtype=float)
    error_feedback = [np.zeros_like(w) for _ in range(cfg.num_clients)]
    utility_history = np.full(cfg.num_clients, 0.5, dtype=float)
    deficit_queue = np.zeros(cfg.num_clients, dtype=float)
    relay_queue = np.zeros(cfg.num_clients, dtype=float)
    relay_energy_cumulative = np.zeros(cfg.num_clients, dtype=float)
    participation = np.zeros(cfg.num_clients, dtype=float)
    influence = np.zeros(cfg.num_clients, dtype=float)
    target_cumulative = np.zeros(cfg.num_clients, dtype=float)
    global_update_ema = np.zeros_like(w)
    pending = []
    total_effective_bits = 0.0
    total_raw_payload_bits = 0.0
    total_energy = 0.0
    history = []

    model_params = w.size
    full_update_bits = cfg.header_bits + model_params * (cfg.model_bits + cfg.index_bits)

    for t in range(cfg.rounds):
        routes = topology.all_routes(residual_energy, initial_energy)
        local_losses = np.array([
            loss_and_grad(w, x, y, cfg.l2)[0] for x, y in client_data
        ])
        utility_signal = 0.55 * _norm(local_losses) + 0.45 * _norm(utility_history)
        target = utility_signal + 1e-6
        target /= target.sum()
        target_cumulative += target

        alive = residual_energy > 0.05
        available = rng.random(cfg.num_clients) < cfg.availability_prob
        eligible = alive & available
        selected, ratios = schedule(
            method, cfg, rng, eligible, utility_signal, routes,
            residual_energy, initial_energy, deficit_queue, relay_queue,
        )
        selected_share = np.zeros(cfg.num_clients, dtype=float)
        if selected:
            selected_share[selected] = 1.0 / len(selected)
        deficit_queue = np.maximum(0.0, deficit_queue + target - selected_share)
        relay_energy_round = np.zeros(cfg.num_clients, dtype=float)

        for i in selected:
            participation[i] += 1.0
            x_i, y_i = client_data[i]
            train_energy = cfg.local_steps * cfg.local_step_energy_j
            residual_energy[i] = max(0.0, residual_energy[i] - train_energy)
            total_energy += train_energy

            update, before, after = local_train(
                w, x_i, y_i, cfg.local_steps, cfg.learning_rate, cfg.l2
            )
            novelty = cosine_novelty(update, global_update_ema)
            improvement = max(before - after, 0.0)
            improvement_score = 1.0 - math.exp(-6.0 * improvement)
            actual_utility = float(np.clip(0.55 * novelty + 0.45 * improvement_score, 0.0, 1.0))
            utility_history[i] = (
                cfg.utility_ema * utility_history[i]
                + (1.0 - cfg.utility_ema) * actual_utility
            )

            rho = float(ratios.get(i, cfg.fixed_compression_ratio))
            compressed, new_residual, k_nonzero = topk_compress(
                update, rho, error_feedback[i]
            )
            error_feedback[i] = new_residual
            bits = cfg.header_bits + k_nonzero * (cfg.model_bits + cfg.index_bits)
            route = routes[i]
            effective_bits = bits * route.etx_sum
            total_effective_bits += effective_bits
            total_raw_payload_bits += full_update_bits
            total_energy += _charge_path(
                cfg, topology, route, bits, residual_energy, relay_energy_round
            )

            tx_time = effective_bits / cfg.bandwidth_bps
            route_time = route.hops * cfg.base_hop_delay_s
            compute_time = cfg.local_steps * 0.012
            latency = compute_time + route_time + tx_time
            delay_rounds = int(min(cfg.max_staleness, max(0, math.floor(latency / cfg.round_slot_s))))
            if rng.random() >= cfg.dropout_prob:
                pending.append({
                    "arrival": t + delay_rounds,
                    "generated": t,
                    "gateway": route.gateway,
                    "client": i,
                    "update": compressed,
                    "utility": actual_utility,
                    "samples": len(y_i),
                })
        relay_energy_cumulative += relay_energy_round
        relay_queue = np.maximum(
            0.0, relay_queue + relay_energy_round - cfg.relay_budget_j_per_round
        )

        arrivals = [e for e in pending if e["arrival"] <= t]
        pending = [e for e in pending if e["arrival"] > t]
        by_gateway = defaultdict(list)
        for event in arrivals:
            age = t - event["generated"]
            if age <= cfg.max_staleness:
                by_gateway[event["gateway"]].append(event)

        edge_deltas = []
        edge_weights = []
        accepted_events = []
        for gateway, events in by_gateway.items():
            raw_weights = []
            for event in events:
                age = t - event["generated"]
                stale = math.exp(-cfg.staleness_lambda * age)
                if method == "proposed":
                    stale *= 1.0 + cfg.utility_staleness_mu * event["utility"]
                raw_weights.append(stale * event["samples"])
            raw_weights = np.asarray(raw_weights, dtype=float)
            if raw_weights.sum() <= 0:
                continue
            norm_weights = raw_weights / raw_weights.sum()
            delta = sum(wgt * ev["update"] for wgt, ev in zip(norm_weights, events))
            edge_deltas.append(delta)
            edge_weights.append(float(raw_weights.sum()))
            for wgt, ev in zip(norm_weights, events):
                accepted_events.append((float(wgt), ev))

        if edge_deltas:
            edge_weights_arr = np.asarray(edge_weights, dtype=float)
            edge_weights_arr /= edge_weights_arr.sum()
            cloud_delta = sum(a * d for a, d in zip(edge_weights_arr, edge_deltas))
            w += cloud_delta
            global_update_ema = 0.70 * global_update_ema + 0.30 * cloud_delta
            for local_w, ev in accepted_events:
                influence[ev["client"]] += local_w
        x_test, y_test = test_data
        acc = accuracy(w, x_test, y_test)
        f1 = macro_f1(w, x_test, y_test, cfg.num_classes)
        rep_js = js_divergence(influence + 1e-9, target_cumulative + 1e-9)
        global_class = client_probs.mean(axis=0)
        learned_coverage = class_coverage(client_probs, influence + 1e-9)
        coverage_js = js_divergence(learned_coverage, global_class)
        history.append({
            "round": t + 1,
            "method": method,
            "accuracy": acc,
            "macro_f1": f1,
            "effective_bits": total_effective_bits,
            "raw_selected_bits": total_raw_payload_bits,
            "energy_j": total_energy,
            "min_residual_energy_j": float(residual_energy.min()),
            "mean_residual_energy_j": float(residual_energy.mean()),
            "participation_jain": _jain(participation),
            "representation_js": rep_js,
            "class_coverage_js": coverage_js,
            "relay_queue_max": float(relay_queue.max()),
            "relay_energy_max_j": float(relay_energy_cumulative.max()),
            "selected": len(selected),
            "accepted_updates": len(accepted_events),
        })

    x_test, y_test = test_data
    summary = {
        "method": method,
        "seed": cfg.seed,
        "correlation": cfg.correlation,
        "accuracy": accuracy(w, x_test, y_test),
        "macro_f1": macro_f1(w, x_test, y_test, cfg.num_classes),
        "effective_bits": total_effective_bits,
        "raw_selected_bits": total_raw_payload_bits,
        "compression_saving": 1.0 - total_effective_bits / max(
            total_raw_payload_bits * max(np.mean([r.etx_sum for r in initial_routes]), 1.0), 1e-12
        ),
        "energy_j": total_energy,
        "min_residual_energy_j": float(residual_energy.min()),
        "participation_jain": _jain(participation),
        "representation_js": js_divergence(influence + 1e-9, target_cumulative + 1e-9),
        "class_coverage_js": js_divergence(
            class_coverage(client_probs, influence + 1e-9), client_probs.mean(axis=0)
        ),
        "mean_route_cost": float(np.mean(difficulty)),
        "mean_route_hops": float(np.mean([r.hops for r in initial_routes])),
        "max_relay_queue": float(relay_queue.max()),
        "max_relay_energy_j": float(relay_energy_cumulative.max()),
        "config": asdict(cfg),
    }
    return summary, history
def simulate_many(method: str, cfg: SimConfig, seeds):
    outputs = []
    histories = []
    for seed in seeds:
        summary, history = simulate(method, replace(cfg, seed=int(seed)))
        outputs.append(summary)
        histories.append(history)
    return outputs, histories
