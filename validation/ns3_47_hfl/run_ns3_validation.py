import argparse
import csv
import json
import subprocess
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from wsn_hfl.config import EVALUATION_SEEDS

ROOT = Path(__file__).resolve().parents[2]
VAL = Path(__file__).resolve().parent
NS3_BIN = Path("/Users/shivambhardwaj/ns3-validation/ns-3.47/build/scratch/ns3.47-hfl-lrwpan-load-validation-optimized")
AGG = ROOT / "results" / "aggregate_summary.csv"
SEEDS = list(EVALUATION_SEEDS)
CONDITIONS = [
    ("dense_fast", 12, 0.5),
    ("dense_nominal", 12, 1.0),
    ("dense_relaxed", 12, 2.0),
    ("light_nominal", 6, 1.0),
    ("scale_nominal", 24, 1.0),
]
SIM_TIME = 20.0
CORRELATION = 0.9


def policy_loads(mapping):
    with AGG.open(newline="") as f:
        rows = list(csv.DictReader(f))
    loads = {}
    for r in rows:
        if abs(float(r["correlation"]) - CORRELATION) > 1e-9:
            continue
        method = r["method"]
        compressed_per_update = float(r["compressed_bits_mean"]) / (40.0 * 6.0)
        mean_hops = float(r["mean_selected_hops_mean"])
        effective_per_update = float(r["effective_bits_mean"]) / (40.0 * 6.0)
        logical_air_bits = compressed_per_update * mean_hops
        payload = logical_air_bits if mapping == "hop" else effective_per_update
        loads[method] = {
            "compressed_bits_per_update": compressed_per_update,
            "mean_selected_hops": mean_hops,
            "mean_selected_etx": float(r["mean_selected_etx_mean"]),
            "effective_bits_per_update": effective_per_update,
            "mapped_payload_bits": payload,
        }
    return loads


def run(mapping):
    if not NS3_BIN.exists():
        raise FileNotFoundError(NS3_BIN)
    loads = policy_loads(mapping)
    out_dir = VAL / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"ns3_hfl_{mapping}_equivalent_sweep.csv"
    records = []
    for condition, n_sensors, period in CONDITIONS:
        for method, meta in loads.items():
            payload_bits = max(800.0, round(meta["mapped_payload_bits"]))
            for seed in SEEDS:
                cmd = [
                    str(NS3_BIN), f"--mode={method}", f"--payloadBits={payload_bits}",
                    f"--reportPeriod={period}", f"--nSensors={n_sensors}",
                    f"--simTime={SIM_TIME}", f"--seed={seed}", "--header=1",
                ]
                p = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
                lines = [line for line in p.stdout.splitlines() if line.strip()]
                parsed = list(csv.DictReader(lines[-2:]))[0]
                parsed.update({
                    "condition": condition, "mapping": mapping,
                    "mapped_payload_bits": payload_bits,
                    "compressed_bits_per_update": meta["compressed_bits_per_update"],
                    "mean_selected_hops_from_hfl": meta["mean_selected_hops"],
                    "mean_selected_etx_from_hfl": meta["mean_selected_etx"],
                    "effective_bits_per_update_from_hfl": meta["effective_bits_per_update"],
                })
                records.append(parsed)
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    manifest = {
        "mapping": mapping, "ns3_binary": str(NS3_BIN), "correlation_source": CORRELATION,
        "seeds": SEEDS, "conditions": CONDITIONS, "sim_time_s": SIM_TIME,
        "policy_load_mapping": loads,
        "mapping_note": (
            "hop: compressed update bits x mean selected hop count; "
            "etx: HFL effective bits/update including route ETX expectation. "
            "ns-3 then applies LR-WPAN CSMA/CA and MAC retries."
        ),
    }
    (out_dir / f"NS3_{mapping.upper()}_EXECUTION_MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    print(f"Wrote {len(records)} {mapping}-equivalent runs to {out}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mapping", choices=["hop", "etx"], default="hop")
    args = parser.parse_args()
    run(args.mapping)


if __name__ == "__main__":
    main()
