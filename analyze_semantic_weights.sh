#!/bin/bash

set -e

OUT="results/semantic_weight_comparison.csv"

echo "Creating semantic weight comparison..."

python3 - <<'PY'
from pathlib import Path
import re
import csv

files = {
    "0.25": "results/semantic_w025.txt",
    "0.50": "results/semantic_w050.txt",
    "1.00": "results/semantic_w100.txt",
}

metrics = [
    "FND",
    "HND",
    "LND",
    "PDR",
    "Application goodput",
    "Energy/delivered message",
    "Average delivered hops",
    "Average delay"
]

rows = []

for weight, filename in files.items():

    path = Path(filename)

    if not path.exists():
        print(f"Missing: {filename}")
        continue

    text = path.read_text()

    row = {
        "semantic_weight": weight
    }

    patterns = {
        "FND": r"FND\s*:\s*(\d+)",
        "HND": r"HND\s*:\s*(\d+)",
        "LND": r"LND\s*:\s*(\d+)",
        "PDR": r"PDR \(%\)\s*:\s*([0-9.]+)",
        "Application goodput": r"Application goodput\s*:\s*([0-9.]+)",
        "Energy/delivered message": r"Energy/delivered message\s*:\s*([0-9.]+)",
        "Average delivered hops": r"Average delivered hops\s*:\s*([0-9.]+)",
        "Average delay": r"Average delay\s*:\s*([0-9.]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text)

        if match:
            row[key] = match.group(1)
        else:
            row[key] = "NA"

    rows.append(row)


if rows:

    with open(
        "results/semantic_weight_comparison.csv",
        "w",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(rows)

    print("Created:")
    print("results/semantic_weight_comparison.csv")

else:
    print("No result files found")

PY

echo "Done"
