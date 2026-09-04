#!/bin/bash

set -e

echo "=============================================="
echo "GENERATING ABLATION STATISTICS"
echo "=============================================="

python3 - <<'PY'
from pathlib import Path
import re
import csv
import numpy as np

base = Path("results/ablation")

files = sorted(base.glob("*.txt"))

rows = []

for f in files:
    text = f.read_text()

    def extract(pattern):
        m = re.search(pattern, text)
        return float(m.group(1)) if m else np.nan

    if "C1_RE_ETX" in f.name:
        case = "C1_RE_ETX"
    elif "C2_SEMANTIC_ROUTING" in f.name:
        case = "C2_SEMANTIC_ROUTING"
    else:
        case = "C3_FULL_SEMANTIC"

    seed = int(re.search(r"seed_(\d+)", f.name).group(1))

    rows.append({
        "case": case,
        "seed": seed,
        "FND": extract(r"FND\s*:\s*(\d+)"),
        "HND": extract(r"HND\s*:\s*(\d+)"),
        "LND": extract(r"LND\s*:\s*(\d+)"),
        "PDR": extract(r"PDR \(%\).*:\s*([0-9.]+)"),
        "Payload_reduction": extract(r"Payload reduction \(%\).*:\s*([0-9.]+)"),
        "Compression_ratio": extract(r"Semantic compression ratio.*:\s*([0-9.]+)"),
        "Radio_efficiency": extract(r"Semantic radio efficiency.*:\s*([0-9.]+)")
    })

with open(
    base / "ablation_raw_metrics.csv",
    "w",
    newline=""
) as fp:
    writer = csv.DictWriter(fp, rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)


metrics = [
    "FND",
    "HND",
    "LND",
    "PDR",
    "Payload_reduction",
    "Compression_ratio",
    "Radio_efficiency"
]

with open(
    base / "ablation_mean_std.csv",
    "w",
    newline=""
) as fp:
    writer = csv.writer(fp)
    writer.writerow(
        ["case","metric","mean","std"]
    )

    for case in sorted(set(r["case"] for r in rows)):
        subset = [
            r for r in rows
            if r["case"] == case
        ]

        for m in metrics:
            vals = [
                r[m] for r in subset
                if not np.isnan(r[m])
            ]

            writer.writerow([
                case,
                m,
                np.mean(vals),
                np.std(vals, ddof=1)
            ])

print("Created:")
print(base / "ablation_raw_metrics.csv")
print(base / "ablation_mean_std.csv")

PY

echo "DONE"
