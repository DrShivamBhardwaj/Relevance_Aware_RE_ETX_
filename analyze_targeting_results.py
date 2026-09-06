import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

INPUT = Path(
    "results/master_validation/statistics/"
    "within_round_targeting_multiseed.csv"
)

OUTDIR = Path(
    "results/master_validation/statistics"
)

df = pd.read_csv(INPUT)

assert len(df) == 40, f"Expected 40 rows, found {len(df)}"

for mode in ["C3", "C5", "C6", "C7"]:
    sub = df[df["mode"] == mode]
    assert len(sub) == 10
    assert sub["seed"].nunique() == 10


def holm_adjust(pvalues):
    pvalues = np.asarray(pvalues, dtype=float)
    n = len(pvalues)
    order = np.argsort(pvalues)

    adjusted = np.empty(n)
    running = 0.0

    for rank, idx in enumerate(order):
        candidate = (n - rank) * pvalues[idx]
        running = max(running, candidate)
        adjusted[idx] = min(running, 1.0)

    return adjusted


metric = "within_round_targeting_gap_bits"

summary_rows = []

for mode in ["C3", "C5", "C6", "C7"]:
    values = (
        df[df["mode"] == mode][metric]
        .astype(float)
        .to_numpy()
    )

    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1))
    sem = sd / math.sqrt(len(values))
    tcrit = stats.t.ppf(0.975, len(values) - 1)

    summary_rows.append({
        "mode": mode,
        "n": len(values),
        "mean_within_round_gap_bits": mean,
        "sd": sd,
        "ci95_low": mean - tcrit * sem,
        "ci95_high": mean + tcrit * sem,
    })

summary = pd.DataFrame(summary_rows)

summary.to_csv(
    OUTDIR / "within_round_targeting_summary.csv",
    index=False,
)


contrasts = [
    ("C5", "C3", "C5_to_C3"),
    ("C6", "C3", "C6_to_C3"),
    ("C3", "C7", "C3_to_C7"),
]

test_rows = []

for baseline, treatment, name in contrasts:

    a = (
        df[df["mode"] == baseline]
        .sort_values("seed")
    )

    b = (
        df[df["mode"] == treatment]
        .sort_values("seed")
    )

    assert np.array_equal(
        a["seed"].to_numpy(),
        b["seed"].to_numpy(),
    )

    x = a[metric].astype(float).to_numpy()
    y = b[metric].astype(float).to_numpy()
    d = y - x

    n = len(d)
    mean_diff = float(np.mean(d))
    sd_diff = float(np.std(d, ddof=1))
    sem = sd_diff / math.sqrt(n)
    tcrit = stats.t.ppf(0.975, n - 1)

    ttest = stats.ttest_rel(y, x)

    try:
        wilcoxon_p = float(
            stats.wilcoxon(
                y,
                x,
                alternative="two-sided",
            ).pvalue
        )
    except ValueError:
        wilcoxon_p = np.nan

    dz = (
        mean_diff / sd_diff
        if sd_diff > 0
        else np.nan
    )

    test_rows.append({
        "contrast": name,
        "baseline": baseline,
        "treatment": treatment,
        "baseline_mean": float(np.mean(x)),
        "treatment_mean": float(np.mean(y)),
        "mean_difference": mean_diff,
        "ci95_low": mean_diff - tcrit * sem,
        "ci95_high": mean_diff + tcrit * sem,
        "paired_t_p": float(ttest.pvalue),
        "wilcoxon_p": wilcoxon_p,
        "cohen_dz": dz,
    })

tests = pd.DataFrame(test_rows)

tests["holm_p"] = holm_adjust(
    tests["paired_t_p"].to_numpy()
)

tests["holm_significant_0.05"] = (
    tests["holm_p"] < 0.05
)

tests.to_csv(
    OUTDIR / "within_round_targeting_paired_tests.csv",
    index=False,
)


print()
print("=" * 105)
print("WITHIN-ROUND TARGETING GAP — 10-SEED SUMMARY")
print("=" * 105)
print(
    summary.round(4).to_string(
        index=False
    )
)

print()
print("=" * 105)
print("PAIRED TESTS — WITHIN-ROUND TARGETING GAP")
print("=" * 105)
print(
    tests[
        [
            "contrast",
            "baseline_mean",
            "treatment_mean",
            "mean_difference",
            "ci95_low",
            "ci95_high",
            "holm_p",
            "holm_significant_0.05",
            "cohen_dz",
        ]
    ].to_string(
        index=False
    )
)

print()
print("SAVED:")
print(
    "results/master_validation/statistics/"
    "within_round_targeting_summary.csv"
)
print(
    "results/master_validation/statistics/"
    "within_round_targeting_paired_tests.csv"
)
