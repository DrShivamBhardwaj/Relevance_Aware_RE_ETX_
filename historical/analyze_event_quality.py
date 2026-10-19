import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

INPUT = Path(
    "results/master_validation/statistics/event_quality_multiseed_raw.csv"
)

OUTDIR = Path(
    "results/master_validation/statistics"
)

df = pd.read_csv(INPUT)

MODES = ["C1", "C2", "C3", "C4", "C5", "C6", "C7"]

METRICS = [
    "event_report_delivery_ratio",
    "event_mean_payload_bits",
    "non_event_mean_payload_bits",
    "payload_targeting_gap_bits",
    "event_payload_preservation",
    "event_payload_delivery_ratio",
]

CONTRASTS = [
    ("C5", "C3", "C5_to_C3"),
    ("C6", "C3", "C6_to_C3"),
    ("C3", "C7", "C3_to_C7"),
]


def holm(pvalues):
    pvalues = np.asarray(pvalues, dtype=float)
    order = np.argsort(pvalues)
    n = len(pvalues)

    adjusted = np.empty(n)
    running = 0.0

    for rank, idx in enumerate(order):
        value = (n - rank) * pvalues[idx]
        running = max(running, value)
        adjusted[idx] = min(running, 1.0)

    return adjusted


# ---------------------------------------------------------
# Descriptive statistics
# ---------------------------------------------------------

summary_rows = []

for mode in MODES:
    sub = df[df["mode"] == mode]

    for metric in METRICS:
        values = sub[metric].astype(float).to_numpy()

        mean = float(np.mean(values))
        sd = float(np.std(values, ddof=1))
        sem = sd / math.sqrt(len(values))

        tcrit = stats.t.ppf(
            0.975,
            len(values) - 1
        )

        summary_rows.append({
            "mode": mode,
            "metric": metric,
            "mean": mean,
            "sd": sd,
            "ci95_low": mean - tcrit * sem,
            "ci95_high": mean + tcrit * sem,
        })

summary = pd.DataFrame(summary_rows)

summary.to_csv(
    OUTDIR / "event_quality_summary.csv",
    index=False
)


# ---------------------------------------------------------
# Paired tests
# ---------------------------------------------------------

test_rows = []

for baseline, treatment, contrast in CONTRASTS:

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
        b["seed"].to_numpy()
    )

    for metric in METRICS:

        x = a[metric].astype(float).to_numpy()
        y = b[metric].astype(float).to_numpy()

        diff = y - x

        n = len(diff)

        mean_diff = float(
            np.mean(diff)
        )

        sd_diff = float(
            np.std(diff, ddof=1)
        )

        sem = sd_diff / math.sqrt(n)

        tcrit = stats.t.ppf(
            0.975,
            n - 1
        )

        if sd_diff > 0:
            dz = mean_diff / sd_diff
        else:
            dz = np.nan

        ttest = stats.ttest_rel(
            y,
            x
        )

        try:
            wilcoxon_p = stats.wilcoxon(
                y,
                x,
                alternative="two-sided"
            ).pvalue
        except ValueError:
            wilcoxon_p = np.nan

        test_rows.append({
            "contrast": contrast,
            "baseline": baseline,
            "treatment": treatment,
            "metric": metric,
            "baseline_mean": float(np.mean(x)),
            "treatment_mean": float(np.mean(y)),
            "mean_difference": mean_diff,
            "ci95_low": mean_diff - tcrit * sem,
            "ci95_high": mean_diff + tcrit * sem,
            "paired_t_p": float(ttest.pvalue),
            "wilcoxon_p": float(wilcoxon_p)
                if np.isfinite(wilcoxon_p)
                else np.nan,
            "cohen_dz": dz,
        })

tests = pd.DataFrame(test_rows)

tests["holm_p"] = np.nan

for contrast in tests["contrast"].unique():
    idx = tests[
        tests["contrast"] == contrast
    ].index

    tests.loc[
        idx,
        "holm_p"
    ] = holm(
        tests.loc[
            idx,
            "paired_t_p"
        ].to_numpy()
    )

tests[
    "holm_significant_0.05"
] = tests["holm_p"] < 0.05

tests.to_csv(
    OUTDIR / "event_quality_paired_tests.csv",
    index=False
)


# ---------------------------------------------------------
# Human-readable journal table
# ---------------------------------------------------------

means = (
    df.groupby("mode")[METRICS]
      .mean()
      .round(4)
)

print()
print("=" * 125)
print("EVENT-QUALITY MEANS OVER 10 SEEDS")
print("=" * 125)
print(means.to_string())

print()
print("=" * 125)
print("PRIMARY SEMANTIC-CONTROL PAIRED TESTS")
print("=" * 125)

primary_metrics = [
    "payload_targeting_gap_bits",
    "event_payload_preservation",
    "event_payload_delivery_ratio",
    "event_report_delivery_ratio",
]

view = tests[
    tests["metric"].isin(primary_metrics)
][
    [
        "contrast",
        "metric",
        "baseline_mean",
        "treatment_mean",
        "mean_difference",
        "ci95_low",
        "ci95_high",
        "holm_p",
        "holm_significant_0.05",
        "cohen_dz",
    ]
]

pd.set_option("display.width", 220)
pd.set_option("display.max_rows", 100)

print(
    view.to_string(
        index=False
    )
)

print()
print("SAVED:")
print(
    "results/master_validation/statistics/"
    "event_quality_summary.csv"
)
print(
    "results/master_validation/statistics/"
    "event_quality_paired_tests.csv"
)
