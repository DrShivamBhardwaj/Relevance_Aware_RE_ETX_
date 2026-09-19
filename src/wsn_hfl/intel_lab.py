from collections import defaultdict
from dataclasses import replace
import gzip
import heapq
import math
from pathlib import Path

import numpy as np

from .config import SimConfig
from .data import js_divergence
from .model import cosine_novelty, topk_compress


GATEWAY_MOTES = (10, 26, 48, 38)
_PREP_CACHE = {}


class IntelRoute:
    def __init__(self, nodes, gateway, cost, etx_sum):
        self.nodes = tuple(nodes)
        self.gateway = int(gateway)
        self.cost = float(cost)
        self.etx_sum = float(etx_sum)
        self.hops = max(0, len(self.nodes) - 1)

    @property
    def relays(self):
        return self.nodes[1:-1]


class IntelLabTopology:
    """Routing graph derived from the measured Intel Lab connectivity matrix."""

    def __init__(self, data_dir: Path, cfg: SimConfig):
        self.cfg = cfg
        self.n = 54
        self.gateway_motes = GATEWAY_MOTES
        self.gateway_nodes = tuple(m - 1 for m in self.gateway_motes)
        self.locations = np.loadtxt(data_dir / "mote_locs.txt", dtype=float)
        self.p = np.zeros((self.n, self.n), dtype=float)
        with (data_dir / "connectivity.txt").open() as f:
            for line in f:
                z = line.split()
                if len(z) < 3:
                    continue
                try:
                    s, r, prob = int(z[0]), int(z[1]), float(z[2])
                except ValueError:
                    continue
                if 1 <= s <= self.n and 1 <= r <= self.n and s != r:
                    self.p[s - 1, r - 1] = float(np.clip(prob, 0.0, 1.0))
        self.etx = np.full((self.n, self.n), np.inf, dtype=float)
        for i in range(self.n):
            for j in range(self.n):
                if i == j:
                    continue
                delivery = self.p[i, j] * self.p[j, i]
                if delivery >= 0.01:
                    self.etx[i, j] = min(100.0, 1.0 / delivery)

    def route(self, source: int, residual_energy: np.ndarray, initial_energy: np.ndarray):
        if source in self.gateway_nodes:
            g = self.gateway_nodes.index(source)
            return IntelRoute((source,), g, 0.0, 0.0)
        scarcity = np.maximum(initial_energy / np.maximum(residual_energy, 1e-9) - 1.0, 0.0)
        dist = np.full(self.n, np.inf)
        prev = np.full(self.n, -1, dtype=int)
        dist[source] = 0.0
        heap = [(0.0, source)]
        target = None
        gateway_set = set(self.gateway_nodes)
        while heap:
            du, u = heapq.heappop(heap)
            if du != dist[u]:
                continue
            if u in gateway_set:
                target = u
                break
            for v in range(self.n):
                base = self.etx[u, v]
                if not np.isfinite(base) or residual_energy[v] <= 0:
                    continue
                penalty = 1.0 + self.cfg.etx_energy_weight * 0.5 * (scarcity[u] + scarcity[v])
                nd = du + base * penalty
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))
        if target is None:
            # fallback to the physically nearest gateway if measured connectivity is disconnected
            xy = self.locations[source, 1:3]
            target = min(self.gateway_nodes, key=lambda g: float(np.linalg.norm(xy - self.locations[g, 1:3])))
            return IntelRoute((source, target), self.gateway_nodes.index(target), 100.0, 100.0)
        path = [target]
        cur = target
        while cur != source:
            cur = int(prev[cur])
            if cur < 0:
                raise RuntimeError(f"Broken Intel Lab route from {source+1}")
            path.append(cur)
        path.reverse()
        etx_sum = sum(float(self.etx[u, v]) for u, v in zip(path[:-1], path[1:]))
        return IntelRoute(path, self.gateway_nodes.index(target), float(dist[target]), etx_sum)

    def all_routes(self, residual_energy, initial_energy):
        return [self.route(i, residual_energy, initial_energy) for i in range(self.n)]


def _valid_row(z):
    if len(z) < 8:
        return None
    try:
        epoch = int(float(z[2])); mote = int(float(z[3]))
        temp, hum, light, volt = map(float, z[4:8])
    except ValueError:
        return None
    if not (1 <= mote <= 54):
        return None
    vals = (temp, hum, light, volt)
    if not all(math.isfinite(v) for v in vals):
        return None
    if not (-10 <= temp <= 60 and 0 <= hum <= 100 and 0 <= light <= 200000 and 1.5 <= volt <= 4.0):
        return None
    return epoch, mote - 1, temp, hum, light, volt


def load_intel_sequences(data_dir: Path, max_rows_per_mote=2500, window=16, stride=3):
    by_mote = defaultdict(list)
    with gzip.open(data_dir / "data.txt.gz", "rt", errors="ignore") as f:
        for line in f:
            row = _valid_row(line.split())
            if row is None:
                continue
            epoch, mote, temp, hum, light, volt = row
            if len(by_mote[mote]) < max_rows_per_mote:
                by_mote[mote].append((epoch, temp, hum, light, volt))
    raw = {}
    for mote, rows in by_mote.items():
        rows.sort(key=lambda x: x[0])
        a = np.asarray([[r[1], r[2], math.log1p(r[3]), r[4]] for r in rows], dtype=float)
        if len(a) < max(200, window + 20):
            continue
        x, y = [], []
        for t in range(window, len(a) - 1, stride):
            x.append(a[t-window:t].reshape(-1))
            y.append(a[t, 0])
        raw[mote] = (np.asarray(x, dtype=float), np.asarray(y, dtype=float))
    return raw


def split_and_standardize(raw, gateway_nodes, train_fraction=0.8):
    splits = {}
    train_xs, train_ys = [], []
    for mote, (x, y) in raw.items():
        if mote in gateway_nodes or len(x) < 100:
            continue
        cut = max(50, int(len(x) * train_fraction))
        cut = min(cut, len(x) - 25)
        splits[mote] = [x[:cut], y[:cut], x[cut:], y[cut:]]
        train_xs.append(x[:cut]); train_ys.append(y[:cut])
    X = np.concatenate(train_xs, axis=0)
    Y = np.concatenate(train_ys, axis=0)
    x_mean, x_std = X.mean(axis=0), X.std(axis=0)
    x_std[x_std < 1e-8] = 1.0
    y_mean, y_std = float(Y.mean()), float(Y.std())
    if y_std < 1e-8:
        y_std = 1.0
    for mote in list(splits):
        xtr, ytr, xte, yte = splits[mote]
        splits[mote] = ((xtr-x_mean)/x_std, (ytr-y_mean)/y_std,
                        (xte-x_mean)/x_std, (yte-y_mean)/y_std)
    return splits, (x_mean, x_std, y_mean, y_std)


def prepare_intel_dataset(data_dir: Path, gateway_nodes):
    key = str(Path(data_dir).resolve())
    if key not in _PREP_CACHE:
        raw = load_intel_sequences(Path(data_dir))
        _PREP_CACHE[key] = split_and_standardize(raw, gateway_nodes)
    return _PREP_CACHE[key]


def regression_loss_grad(w, x, y, l2=0.0):
    xb = np.concatenate([x, np.ones((len(x), 1))], axis=1)
    err = xb @ w - y
    loss = 0.5 * float(np.mean(err * err)) + 0.5 * l2 * float(np.sum(w[:-1] ** 2))
    grad = xb.T @ err / len(x)
    grad[:-1] += l2 * w[:-1]
    return loss, grad


def local_regression(w, x, y, steps, lr, l2):
    wl = w.copy()
    before, _ = regression_loss_grad(wl, x, y, l2)
    for _ in range(steps):
        _, g = regression_loss_grad(wl, x, y, l2)
        wl -= lr * g
    after, _ = regression_loss_grad(wl, x, y, l2)
    return wl - w, before, after


def _norm(x):
    x = np.asarray(x, float); lo, hi = float(x.min()), float(x.max())
    return np.full_like(x, 0.5) if hi-lo < 1e-12 else (x-lo)/(hi-lo)


def _jain(x):
    x = np.asarray(x, float); den = len(x)*float(np.sum(x*x))
    return 1.0 if den < 1e-12 else float(np.sum(x)**2/den)


def _adaptive_ratio(cfg, utility, route_cost, scarcity, relay_pressure):
    best = cfg.fixed_compression_ratio; best_obj = float("inf")
    for rho in cfg.compression_candidates:
        network = rho * (route_cost + 0.5*scarcity + cfg.relay_pressure_weight*relay_pressure)
        distortion = cfg.compression_distortion_weight * utility * (1.0-rho)**2
        obj = network + distortion
        if obj < best_obj:
            best_obj, best = obj, float(rho)
    return best


def _schedule(method, cfg, rng, eligible, utility, routes, residual, initial, deficit, relay_queue):
    cand = np.flatnonzero(eligible)
    if not len(cand):
        return [], {}
    k = min(cfg.clients_per_round, len(cand))
    rc = _norm(np.asarray([r.cost for r in routes]))
    scarcity = _norm(np.maximum(initial/np.maximum(residual,1e-9)-1.0, 0.0))
    pressure = np.zeros(cfg.num_clients)
    for i, r in enumerate(routes):
        pressure[i] = sum(relay_queue[j] for j in r.relays)
    pressure = _norm(pressure)
    if method == "proposed_no_relay":
        pressure[:] = 0.0
    util = _norm(utility)
    ratios = {int(i): cfg.fixed_compression_ratio for i in cand}
    if method == "random":
        selected = rng.choice(cand, size=k, replace=False)
    elif method == "resource":
        score = rc + scarcity + pressure
        selected = cand[np.argsort(score[cand])[:k]]
    elif method == "utility":
        selected = cand[np.argsort(-util[cand])[:k]]
    elif method.startswith("proposed"):
        score = np.full(cfg.num_clients, -np.inf)
        for i in cand:
            if method == "proposed_fixed_comp":
                rho = cfg.fixed_compression_ratio
            else:
                rho = _adaptive_ratio(cfg, util[i], rc[i], scarcity[i], pressure[i])
            ratios[int(i)] = rho
            deficit_term = 0.0 if method == "proposed_no_rep" else deficit[i]
            score[i] = cfg.drift_v*util[i] + deficit_term - cfg.drift_v*rho*(rc[i]+0.5*scarcity[i]+cfg.relay_pressure_weight*pressure[i])
        selected = cand[np.argsort(-score[cand])[:k]]
    else:
        raise ValueError(method)
    return [int(i) for i in selected], ratios


def _charge(cfg, topology, route, bits, residual, relay_energy):
    spent = 0.0
    for u, v in zip(route.nodes[:-1], route.nodes[1:]):
        etx = float(topology.etx[u, v]) if np.isfinite(topology.etx[u, v]) else 100.0
        tx = bits*cfg.tx_energy_per_bit_j*etx
        rx = bits*cfg.rx_energy_per_bit_j*etx
        residual[u] -= tx; residual[v] -= rx
        spent += tx + rx
        if u != route.nodes[0]: relay_energy[u] += tx
        if v != route.nodes[-1]: relay_energy[v] += rx
    np.maximum(residual, 0.0, out=residual)
    return spent


def evaluate_regression(w, splits, y_mean, y_std):
    sq, ab, client_rmse = [], [], []
    for _, (_, _, xte, yte) in splits.items():
        xb = np.concatenate([xte, np.ones((len(xte),1))], axis=1)
        pred = (xb @ w)*y_std + y_mean
        true = yte*y_std + y_mean
        err = pred-true
        sq.extend((err*err).tolist()); ab.extend(np.abs(err).tolist())
        client_rmse.append(float(np.sqrt(np.mean(err*err))))
    cr = np.asarray(client_rmse)
    return {
        "rmse_c": float(np.sqrt(np.mean(sq))), "mae_c": float(np.mean(ab)),
        "worst_client_rmse_c": float(cr.max()), "p90_client_rmse_c": float(np.quantile(cr,0.9)),
        "client_rmse_sd_c": float(cr.std()),
    }


def simulate_intel(method, cfg, data_dir: Path, correlation=0.5):
    rng = np.random.default_rng(cfg.seed)
    topo = IntelLabTopology(data_dir, cfg)
    splits, (_, _, y_mean, y_std) = prepare_intel_dataset(data_dir, topo.gateway_nodes)
    client_mask = np.zeros(cfg.num_clients, dtype=bool)
    client_mask[list(splits)] = True
    feat_dim = next(iter(splits.values()))[0].shape[1]
    w = np.zeros(feat_dim+1, dtype=float)
    initial = rng.uniform(cfg.energy_initial_j-cfg.energy_jitter, cfg.energy_initial_j+cfg.energy_jitter, cfg.num_clients)
    residual = initial.copy()
    init_routes = topo.all_routes(residual, initial)

    # Natural statistical rarity; correlation controls whether rare clients also become resource-constrained.
    global_y = np.concatenate([v[1] for v in splits.values()])
    gmean = float(global_y.mean())
    rarity = np.zeros(cfg.num_clients)
    for i, (_, ytr, _, _) in splits.items():
        rarity[i] = abs(float(ytr.mean())-gmean) + 0.25*float(ytr.std())
    rarity = _norm(rarity)
    initial *= (1.0 - 0.35*correlation*rarity)
    residual = initial.copy()
    avail_p = np.clip(cfg.availability_prob - 0.25*correlation*rarity, 0.45, 0.99)

    utility_hist = np.full(cfg.num_clients, 0.5); deficit = np.zeros(cfg.num_clients)
    relay_queue = np.zeros(cfg.num_clients); relay_cum = np.zeros(cfg.num_clients)
    participation = np.zeros(cfg.num_clients); influence = np.zeros(cfg.num_clients); target_cum = np.zeros(cfg.num_clients)
    residual_buf = [np.zeros_like(w) for _ in range(cfg.num_clients)]
    global_update_ema = np.zeros_like(w); pending=[]
    total_eff_bits=total_comp_bits=total_raw_bits=total_energy=0.0
    total_hops=total_etx=0.0; total_updates=0
    full_bits = cfg.header_bits + w.size*(cfg.model_bits+cfg.index_bits)
    history=[]

    for t in range(cfg.rounds):
        routes = topo.all_routes(residual, initial)
        losses = np.zeros(cfg.num_clients)
        for i,(xtr,ytr,_,_) in splits.items():
            losses[i]=regression_loss_grad(w,xtr,ytr,cfg.l2)[0]
        utility = 0.55*_norm(losses) + 0.45*_norm(utility_hist)
        utility[~client_mask]=0.0
        target = utility + 1e-6*client_mask
        target[~client_mask]=0.0
        target /= max(target.sum(),1e-12); target_cum += target
        eligible = client_mask & (residual>0.05) & (rng.random(cfg.num_clients)<avail_p)
        selected, ratios = _schedule(method,cfg,rng,eligible,utility,routes,residual,initial,deficit,relay_queue)
        share=np.zeros(cfg.num_clients)
        if selected: share[selected]=1.0/len(selected)
        deficit=np.maximum(0.0,deficit+target-share)
        relay_round=np.zeros(cfg.num_clients)
        for i in selected:
            participation[i]+=1
            xtr,ytr,_,_=splits[i]
            train_e=cfg.local_steps*cfg.local_step_energy_j
            residual[i]=max(0.0,residual[i]-train_e); total_energy+=train_e
            upd,before,after=local_regression(w,xtr,ytr,cfg.local_steps,cfg.learning_rate,cfg.l2)
            novelty=cosine_novelty(upd,global_update_ema)
            improve=max(before-after,0.0); improve_score=1.0-math.exp(-6.0*improve)
            actual=float(np.clip(0.55*novelty+0.45*improve_score,0,1))
            utility_hist[i]=cfg.utility_ema*utility_hist[i]+(1-cfg.utility_ema)*actual
            rho=float(ratios.get(i,cfg.fixed_compression_ratio))
            comp,new_res,k=topk_compress(upd,rho,residual_buf[i]); residual_buf[i]=new_res
            bits=cfg.header_bits+k*(cfg.model_bits+cfg.index_bits); route=routes[i]
            total_comp_bits+=bits; total_raw_bits+=full_bits; total_eff_bits+=bits*max(route.etx_sum,1.0)
            total_hops+=route.hops; total_etx+=route.etx_sum; total_updates+=1
            total_energy+=_charge(cfg,topo,route,bits,residual,relay_round)
            latency=cfg.local_steps*0.012 + route.hops*cfg.base_hop_delay_s + bits*max(route.etx_sum,1.0)/250000.0
            delay=int(min(cfg.max_staleness,max(0,math.floor(latency/cfg.round_slot_s))))
            if rng.random()>=cfg.dropout_prob:
                pending.append({"arrival":t+delay,"generated":t,"gateway":route.gateway,"client":i,"update":comp,"utility":actual,"samples":len(ytr)})
        relay_cum += relay_round
        relay_queue=np.maximum(0.0,relay_queue+relay_round-cfg.relay_budget_j_per_round)
        arrivals=[e for e in pending if e["arrival"]<=t]; pending=[e for e in pending if e["arrival"]>t]
        by_g=defaultdict(list)
        for e in arrivals:
            if t-e["generated"]<=cfg.max_staleness: by_g[e["gateway"]].append(e)
        edge_delta=[]; edge_weight=[]; accepted=[]
        for g,events in by_g.items():
            rw=[]
            for e in events:
                age=t-e["generated"]; a=math.exp(-cfg.staleness_lambda*age)
                if method.startswith("proposed") and method != "proposed_age_only":
                    a *= 1.0 + cfg.utility_staleness_mu * e["utility"]
                rw.append(a*e["samples"])
            rw=np.asarray(rw,float)
            if rw.sum()<=0: continue
            nw=rw/rw.sum(); edge_delta.append(sum(a*e["update"] for a,e in zip(nw,events))); edge_weight.append(float(rw.sum()))
            accepted.extend((float(a),e) for a,e in zip(nw,events))
        if edge_delta:
            ew=np.asarray(edge_weight); ew/=ew.sum(); cloud=sum(a*d for a,d in zip(ew,edge_delta)); w+=cloud
            global_update_ema=0.7*global_update_ema+0.3*cloud
            for a,e in accepted: influence[e["client"]]+=a
        metrics=evaluate_regression(w,splits,y_mean,y_std)
        history.append({"round":t+1,"method":method,"correlation":correlation,**metrics,
                        "effective_bits":total_eff_bits,"energy_j":total_energy,"representation_js":js_divergence(influence+1e-9,target_cum+1e-9),
                        "participation_jain":_jain(participation[client_mask]),"max_relay_energy_j":float(relay_cum.max()),"min_residual_energy_j":float(residual.min())})
    metrics=evaluate_regression(w,splits,y_mean,y_std)
    summary={"method":method,"seed":cfg.seed,"correlation":correlation,"clients":int(client_mask.sum()),**metrics,
             "effective_bits":total_eff_bits,"compressed_bits":total_comp_bits,"raw_selected_bits":total_raw_bits,
             "mean_selected_hops":total_hops/max(total_updates,1),"mean_selected_etx":total_etx/max(total_updates,1),
             "energy_j":total_energy,"min_residual_energy_j":float(residual.min()),"max_relay_energy_j":float(relay_cum.max()),
             "participation_jain":_jain(participation[client_mask]),"representation_js":js_divergence(influence+1e-9,target_cum+1e-9)}
    return summary, history
