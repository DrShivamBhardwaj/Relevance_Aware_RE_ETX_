#!/bin/bash

set -e

echo "=============================================="
echo "GENERATING PAPER FIGURES"
echo "=============================================="

python3 - <<'PY'
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

base = Path("results/ablation")

df = pd.read_csv(
    base / "ablation_raw_metrics.csv"
)


# -----------------------------
# Lifetime milestone comparison
# -----------------------------

life = df.groupby("case")[["FND","HND","LND"]].mean()

ax = life.plot(
    kind="bar",
    figsize=(8,5)
)

ax.set_ylabel(
    "Rounds"
)

ax.set_xlabel(
    "Configuration"
)

ax.set_title(
    "Network Lifetime Comparison"
)

plt.tight_layout()

plt.savefig(
    base / "Fig1_Lifetime_Comparison.png",
    dpi=300
)

plt.close()


# -----------------------------
# PDR comparison
# -----------------------------

pdr = df.groupby("case")["PDR"].mean()

plt.figure(figsize=(7,4))

plt.bar(
    pdr.index,
    pdr.values
)

plt.ylabel(
    "PDR (%)"
)

plt.title(
    "Packet Delivery Ratio Comparison"
)

plt.xticks(
    rotation=20
)

plt.tight_layout()

plt.savefig(
    base / "Fig2_PDR_Comparison.png",
    dpi=300
)

plt.close()


# -----------------------------
# Semantic metrics
# -----------------------------

sem = df.groupby("case")[
    [
        "Payload_reduction",
        "Compression_ratio",
        "Radio_efficiency"
    ]
].mean()


ax = sem.plot(
    kind="bar",
    figsize=(8,5)
)

ax.set_ylabel(
    "Value"
)

ax.set_title(
    "Semantic Communication Efficiency"
)

plt.xticks(
    rotation=20
)

plt.tight_layout()

plt.savefig(
    base / "Fig3_Semantic_Efficiency.png",
    dpi=300
)

plt.close()


print("Figures created")

PY

echo "DONE"

