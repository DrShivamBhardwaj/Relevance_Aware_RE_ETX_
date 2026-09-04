#!/bin/bash

set -e

echo "=============================================="
echo "GENERATING ABLATION SIGNIFICANCE ANALYSIS"
echo "=============================================="

python3 - <<'PY'
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind, t

base = Path("results/ablation")

df = pd.read_csv(
    base / "ablation_raw_metrics.csv"
)

metrics = [
    "FND",
    "HND",
    "LND",
    "PDR",
    "Payload_reduction",
    "Compression_ratio",
    "Radio_efficiency"
]

comparisons = [
    ("C1_RE_ETX", "C2_SEMANTIC_ROUTING"),
    ("C2_SEMANTIC_ROUTING", "C3_FULL_SEMANTIC"),
    ("C1_RE_ETX", "C3_FULL_SEMANTIC")
]


def cohens_d(a, b):
    na = len(a)
    nb = len(b)

    pooled = np.sqrt(
        (
            (na-1)*np.var(a, ddof=1)
            +
            (nb-1)*np.var(b, ddof=1)
        )
        /
        (na+nb-2)
    )

    if pooled == 0:
        return np.nan

    return (
        np.mean(a)-np.mean(b)
    ) / pooled


def confidence_interval(values):

    n = len(values)
    mean = np.mean(values)
    std = np.std(values, ddof=1)

    margin = (
        t.ppf(
            0.975,
            n-1
        )
        *
        std
        /
        np.sqrt(n)
    )

    return (
        mean-margin,
        mean+margin
    )


# Confidence intervals

ci_rows=[]

for case in df.case.unique():

    subset=df[df.case==case]

    for metric in metrics:

        vals=subset[metric].dropna()

        low,high=confidence_interval(vals)

        ci_rows.append({
            "case":case,
            "metric":metric,
            "mean":vals.mean(),
            "CI_low":low,
            "CI_high":high
        })


pd.DataFrame(ci_rows).to_csv(
    base/"confidence_intervals.csv",
    index=False
)


# Statistical tests

test_rows=[]

for a,b in comparisons:

    for metric in metrics:

        x=df[df.case==a][metric]
        y=df[df.case==b][metric]

        if (
            np.std(x, ddof=1) == 0
            and np.std(y, ddof=1) == 0
        ):
            stat = np.nan
            p = np.nan
        else:
            stat,p=ttest_ind(
                x,
                y,
                equal_var=False
            )

        d=cohens_d(
            x.values,
            y.values
        )

        test_rows.append({
            "comparison":f"{a}_vs_{b}",
            "metric":metric,
            "t_stat":stat,
            "p_value":p,
            "cohens_d":d
        })


pd.DataFrame(test_rows).to_csv(
    base/"statistical_tests.csv",
    index=False
)


print("Created:")
print(base/"confidence_intervals.csv")
print(base/"statistical_tests.csv")

PY

echo "DONE"

