#!/bin/bash

set -e

echo "=============================================="
echo "GENERATING PAPER TABLES"
echo "=============================================="

python3 - <<'PY'
from pathlib import Path
import pandas as pd

base = Path("results/ablation")

df = pd.read_csv(
    base / "ablation_mean_std.csv"
)

# Pivot helper

def make_table(metrics, filename):
    rows=[]

    for case in df.case.unique():
        row={"Configuration":case}

        for metric in metrics:
            x=df[
                (df.case==case)
                &
                (df.metric==metric)
            ]

            if len(x):
                row[metric]=(
                    f"{x.iloc[0]['mean']:.3f}"
                    " ± "
                    f"{x.iloc[0]['std']:.3f}"
                )

        rows.append(row)

    pd.DataFrame(rows).to_csv(
        base / filename,
        index=False
    )


# Table I
make_table(
    [
        "FND",
        "HND",
        "LND"
    ],
    "Table_I_Lifetime.csv"
)


# Table II
make_table(
    [
        "PDR"
    ],
    "Table_II_Reliability.csv"
)


# Table III
make_table(
    [
        "Payload_reduction",
        "Compression_ratio",
        "Radio_efficiency"
    ],
    "Table_III_Semantic_Efficiency.csv"
)


# Table IV
make_table(
    [
        "FND",
        "LND",
        "PDR",
        "Payload_reduction"
    ],
    "Table_IV_Ablation.csv"
)


print("Created:")
for f in [
    "Table_I_Lifetime.csv",
    "Table_II_Reliability.csv",
    "Table_III_Semantic_Efficiency.csv",
    "Table_IV_Ablation.csv"
]:
    print(base/f)

PY

echo "DONE"

