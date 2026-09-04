#!/bin/bash

set -e

OUTDIR="results/semantic_multiseed"

echo "=============================================="
echo "GENERATING SEMANTIC MULTI-SEED STATISTICS"
echo "=============================================="

python3 - <<'PY'
from pathlib import Path
import re
import csv
import numpy as np

folder = Path("results/semantic_multiseed")

files = sorted(folder.glob("seed_*.txt"))

rows = []

patterns = {
    "FND": r"FND\s*:\s*(\d+)",
    "HND": r"HND\s*:\s*(\d+)",
    "LND": r"LND\s*:\s*(\d+)",
    "PDR": r"PDR \(%\)\s*:\s*([0-9.]+)",
    "Goodput_kbps": r"Application goodput\s*:\s*([0-9.]+)",
    "Energy_per_packet": r"Energy/delivered message\s*:\s*([0-9.]+)",
    "Payload_reduction": r"Payload reduction \(%\)\s*:\s*([0-9.]+)",
    "Semantic_efficiency": r"Semantic efficiency\s*:\s*([0-9.]+)",
}

for file in files:

    text = file.read_text()

    row = {
        "seed": file.stem.replace("seed_", "")
    }

    for key, pattern in patterns.items():

        match = re.search(pattern, text)

        if match:
            row[key] = float(match.group(1))
        else:
            row[key] = np.nan

    rows.append(row)


raw = folder / "semantic_raw_metrics.csv"

with open(raw, "w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=rows[0].keys()
    )

    writer.writeheader()
    writer.writerows(rows)


summary = folder / "semantic_mean_std.csv"

metrics = list(rows[0].keys())[1:]

with open(summary, "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow(
        [
            "metric",
            "mean",
            "std"
        ]
    )

    for metric in metrics:

        values = [
            r[metric]
            for r in rows
            if not np.isnan(r[metric])
        ]

        writer.writerow(
            [
                metric,
                np.mean(values),
                np.std(values, ddof=1)
            ]
        )


print("Created:")
print(raw)
print(summary)

PY

echo ""
echo "Files:"
ls -lh "$OUTDIR"/semantic_*.csv

echo "DONE"

