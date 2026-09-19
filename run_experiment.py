import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from wsn_hfl import METHODS, SimConfig, simulate_many


def aggregate(rows):
    numeric = [
        "accuracy", "macro_f1", "effective_bits", "compressed_bits", "raw_selected_bits",
        "mean_selected_hops", "mean_selected_etx",
        "compression_saving", "energy_j", "min_residual_energy_j",
        "participation_jain", "representation_js", "class_coverage_js",
        "mean_route_cost", "mean_route_hops", "max_relay_queue", "max_relay_energy_j",
    ]
    out = {"method": rows[0]["method"], "correlation": rows[0]["correlation"], "n": len(rows)}
    for key in numeric:
        vals = [float(r[key]) for r in rows]
        out[key + "_mean"] = statistics.fmean(vals)
        out[key + "_sd"] = statistics.stdev(vals) if len(vals) > 1 else 0.0
    return out


def write_csv(path, rows):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="short smoke experiment")
    parser.add_argument("--correlations", nargs="*", type=float, default=[0.0, 0.5, 0.9])
    parser.add_argument("--methods", nargs="*", default=list(METHODS))
    parser.add_argument("--seeds", nargs="*", type=int, default=[7, 11, 19])
    parser.add_argument("--out", default="results")
    args = parser.parse_args()

    cfg = SimConfig()
    if args.quick:
        cfg = replace(
            cfg,
            rounds=8,
            num_clients=12,
            clients_per_round=4,
            samples_per_client=48,
            test_samples=400,
        )

    out_dir = ROOT / args.out
    raw_rows = []
    history_rows = []
    aggregate_rows = []

    for corr in args.correlations:
        for method in args.methods:
            run_cfg = replace(cfg, correlation=float(corr))
            summaries, histories = simulate_many(method, run_cfg, args.seeds)
            raw_rows.extend([{k: v for k, v in s.items() if k != "config"} for s in summaries])
            for seed, hist in zip(args.seeds, histories):
                for row in hist:
                    history_rows.append({"seed": seed, "correlation": corr, **row})
            aggregate_rows.append(aggregate(summaries))
            print(
                f"corr={corr:.2f} method={method:8s} "
                f"acc={aggregate_rows[-1]['accuracy_mean']:.4f} "
                f"F1={aggregate_rows[-1]['macro_f1_mean']:.4f} "
                f"repJS={aggregate_rows[-1]['representation_js_mean']:.4f}"
            )
    write_csv(out_dir / "raw_summary.csv", raw_rows)
    write_csv(out_dir / "round_history.csv", history_rows)
    write_csv(out_dir / "aggregate_summary.csv", aggregate_rows)
    manifest = {
        "methods": args.methods,
        "correlations": args.correlations,
        "seeds": args.seeds,
        "quick": args.quick,
        "config": cfg.__dict__,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "run_manifest.json").open("w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nWrote results to {out_dir}")


if __name__ == "__main__":
    main()
