import csv
import hashlib
import json
import math
import statistics
import sys
import time
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))

from wsn_hfl.config import EVALUATION_SEEDS, TUNING_SEEDS, SimConfig
from wsn_hfl.intel_lab import simulate_intel

METHODS = (
    'random','resource','utility',
    'random_adaptive','resource_adaptive','utility_adaptive',
    'proposed_fixed_comp','fedcg_adapted','proposed'
)
SEEDS = EVALUATION_SEEDS
CORRELATIONS = (0.0, 0.5, 0.9)


def mean_sd_ci(vals):
    vals = [float(x) for x in vals]
    mean = statistics.fmean(vals)
    sd = statistics.stdev(vals) if len(vals) > 1 else 0.0
    ci = 1.96 * sd / math.sqrt(len(vals)) if len(vals) > 1 else 0.0
    return mean, sd, ci


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)


def main():
    data_dir = ROOT / 'data' / 'intel_lab'
    out_dir = ROOT / 'results' / 'intel_lab'
    cfg = replace(
        SimConfig(), num_clients=54, num_gateways=4, rounds=30,
        clients_per_round=10, local_steps=1, learning_rate=0.010, l2=0.010,
        round_slot_s=0.20, relay_budget_j_per_round=0.004,
        relay_pressure_weight=5.0,
        compression_distortion_weight=0.10,
    )
    raw, history = [], []
    start = time.time()
    for corr in CORRELATIONS:
        for method in METHODS:
            for seed in SEEDS:
                summary, hist = simulate_intel(method, replace(cfg, seed=seed), data_dir, corr)
                raw.append(summary)
                history.extend({'seed':seed, **r} for r in hist)
            group = [r for r in raw if r['method']==method and r['correlation']==corr]
            print(
                f"corr={corr:.1f} method={method:19s} "
                f"RMSE={statistics.fmean(r['rmse_c'] for r in group):.3f}C "
                f"utilityJS={statistics.fmean(r['utility_target_js'] for r in group):.4f}"
            )
    numeric = [
        'rmse_c','mae_c','worst_client_rmse_c','p90_client_rmse_c','client_rmse_sd_c',
        'effective_bits','compressed_bits','raw_selected_bits','mean_selected_hops','mean_selected_etx',
        'energy_j','min_residual_energy_j','max_relay_energy_j','participation_jain',
        'utility_target_js','temperature_coverage_js'
    ]
    agg=[]
    for corr in CORRELATIONS:
        for method in METHODS:
            rows=[r for r in raw if r['method']==method and r['correlation']==corr]
            out={'method':method,'correlation':corr,'n':len(rows),'clients':rows[0]['clients']}
            for key in numeric:
                mean,sd,ci=mean_sd_ci([r[key] for r in rows])
                out[key+'_mean']=mean; out[key+'_sd']=sd; out[key+'_ci95']=ci
            agg.append(out)
    write_csv(out_dir/'raw_summary.csv', raw)
    write_csv(out_dir/'round_history.csv', history)
    write_csv(out_dir/'aggregate_summary.csv', agg)
    manifest={
        'dataset':'Intel Berkeley Research Lab sensor data',
        'source':'https://db.csail.mit.edu/labdata/labdata.html',
        'task':'per-mote next-temperature regression from 16-step windows of temperature, humidity, log-light and voltage',
        'gateway_motes':[10,26,48,38],
        'methods':METHODS,
        'evaluation_seeds':SEEDS,
        'tuning_seeds':TUNING_SEEDS,
        'seed_protocol':'controller parameters tuned only on tuning_seeds; all final comparisons/statistics use disjoint evaluation_seeds',
        'correlations':CORRELATIONS,
        'config':cfg.__dict__, 'runtime_s':time.time()-start,
        'checksums':{}
    }
    for name in ('data.txt.gz','mote_locs.txt','connectivity.txt'):
        p=data_dir/name
        manifest['checksums'][name]=hashlib.sha256(p.read_bytes()).hexdigest()
    (out_dir/'run_manifest.json').write_text(json.dumps(manifest,indent=2,default=list))
    print(f"completed in {manifest['runtime_s']:.2f}s; wrote {out_dir}")


if __name__=='__main__':
    main()
