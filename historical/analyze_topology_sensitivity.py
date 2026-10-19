import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

INPUT = Path(
    "results/master_validation/statistics/topology_sensitivity_raw.csv"
)

OUTDIR = Path(
    "results/master_validation/statistics"
)

df = pd.read_csv(INPUT)

assert len(df) == 90, f"Expected 90 runs, found {len(df)}"

PROFILES = ["shallow", "medium", "deep"]
MODES = ["C1", "C3", "C5"]

for profile in PROFILES:
    for mode in MODES:
        sub = df[
            (df["profile"] == profile)
            & (df["mode"] == mode)
        ]
        assert len(sub) == 10, (
            f"{profile} {mode}: expected 10 runs, "
            f"found {len(sub)}"
        )
        assert sub["seed"].nunique() == 10


METRICS = [
    "FND",
    "HND",
    "LND",
    "PDR_percent",
    "average_delivered_hops",
    "average_delay_ms",
    "energy_per_delivered_j",
    "retries_per_generated",
]

DIRECTION = {
    "FND": 1,
    "HND": 1,
    "LND": 1,
    "PDR_percent": 1,
    "average_delivered_hops": 0,
    "average_delay_ms": -1,
    "energy_per_delivered_j": -1,
    "retries_per_generated": -1,
}


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


# ---------------------------------------------------------
# Means / SD / 95% CI
# ---------------------------------------------------------

summary_rows = []

for profile in PROFILES:
    for mode in MODES:
        sub = df[
            (df["profile"] == profile)
            & (df["mode"] == mode)
        ]

        for metric in (
            METRICS
            + [
                "attempted_mean_payload_bits",
                "event_payload_preservation",
                "event_payload_delivery_ratio",
                "within_round_targeting_gap_bits",
            ]
        ):
            values = (
                pd.to_numeric(
                    sub[metric],
                    errors="coerce",
                )
                .dropna()
                .to_numpy(dtype=float)
            )

            n = len(values)
            mean = float(np.mean(values))
            sd = float(np.std(values, ddof=1))
            sem = sd / math.sqrt(n)

            tcrit = stats.t.ppf(
                0.975,
                n - 1,
            )

            summary_rows.append({
                "profile": profile,
                "mode": mode,
                "metric": metric,
                "n": n,
                "mean": mean,
                "sd": sd,
                "ci95_low": mean - tcrit * sem,
                "ci95_high": mean + tcrit * sem,
            })

summary = pd.DataFrame(summary_rows)

summary.to_csv(
    OUTDIR / "topology_sensitivity_summary.csv",
    index=False,
)


# ---------------------------------------------------------
# Paired contrasts
# ---------------------------------------------------------

CONTRASTS = [
    ("C1", "C3", "C1_to_C3"),
    ("C5", "C3", "C5_to_C3"),
]

test_rows = []

for profile in PROFILES:
    for baseline, treatment, contrast in CONTRASTS:

        a = (
            df[
                (df["profile"] == profile)
                & (df["mode"] == baseline)
            ]
            .sort_values("seed")
        )

        b = (
            df[
                (df["profile"] == profile)
                & (df["mode"] == treatment)
            ]
            .sort_values("seed")
        )

        assert np.array_equal(
            a["seed"].to_numpy(),
            b["seed"].to_numpy(),
        )

        for metric in METRICS:
            x = a[metric].astype(float).to_numpy()
            y = b[metric].astype(float).to_numpy()

            d = y - x
            n = len(d)

            mean_diff = float(np.mean(d))
            sd_diff = float(np.std(d, ddof=1))
            sem = sd_diff / math.sqrt(n)

            tcrit = stats.t.ppf(
                0.975,
                n - 1,
            )

            ttest = stats.ttest_rel(
                y,
                x,
            )

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

            direction = DIRECTION[metric]

            if direction == 0:
                interpretation = "descriptive"
            elif mean_diff * direction > 0:
                interpretation = "favors_treatment"
            elif mean_diff * direction < 0:
                interpretation = "favors_baseline"
            else:
                interpretation = "no_difference"

            test_rows.append({
                "profile": profile,
                "family": f"{profile}_{contrast}",
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
                "wilcoxon_p": wilcoxon_p,
                "cohen_dz": dz,
                "interpretation": interpretation,
            })

tests = pd.DataFrame(test_rows)

tests["holm_p"] = np.nan

for family in tests["family"].unique():
    idx = tests[
        tests["family"] == family
    ].index

    tests.loc[
        idx,
        "holm_p"
    ] = holm_adjust(
        tests.loc[
            idx,
            "paired_t_p"
        ].to_numpy()
    )

tests["holm_significant_0.05"] = (
    tests["holm_p"] < 0.05
)

tests.to_csv(
    OUTDIR / "topology_sensitivity_paired_tests.csv",
    index=False,
)


# ---------------------------------------------------------
# Budget diagnostic
# ---------------------------------------------------------

budget = (
    df.groupby(
        ["profile", "mode"]
    )[
        [
            "attempted_mean_payload_bits",
            "average_delivered_hops",
            "within_round_targeting_gap_bits",
        ]
    ]
    .mean()
    .round(3)
)

budget.to_csv(
    OUTDIR / "topology_sensitivity_budget_check.csv"
)


# ---------------------------------------------------------
# Console output
# ---------------------------------------------------------

print()
print("=" * 120)
print("TOPOLOGY SENSITIVITY — MEAN RESULTS OVER 10 SEEDS")
print("=" * 120)

main_means = (
    df.groupby(
        ["profile", "mode"]
    )[
        [
            "FND",
            "HND",
            "LND",
            "PDR_percent",
            "average_delivered_hops",
            "average_delay_ms",
            "energy_per_delivered_j",
            "attempted_mean_payload_bits",
            "within_round_targeting_gap_bits",
        ]
    ]
    .mean()
    .round(4)
)

print(main_means.to_string())

print()
print("=" * 120)
print("C3 vs C5 PAYLOAD-BUDGET CHECK")
print("=" * 120)

for profile in PROFILES:
    c3 = df[
        (df["profile"] == profile)
        & (df["mode"] == "C3")
    ]["attempted_mean_payload_bits"].mean()

    c5 = df[
        (df["profile"] == profile)
        & (df["mode"] == "C5")
    ]["attempted_mean_payload_bits"].mean()

    print(
        f"{profile:8s}: "
        f"C3={c3:.2f} bits, "
        f"C5={c5:.2f} bits, "
        f"difference={c3-c5:+.2f} bits "
        f"({100*(c3-c5)/c3:+.2f}% of C3)"
    )

print()
print("=" * 120)
print("PAIRED C1→C3 AND C5→C3 TESTS")
print("=" * 120)

view = tests[
    [
        "profile",
        "contrast",
        "metric",
        "baseline_mean",
        "treatment_mean",
        "mean_difference",
        "ci95_low",
        "ci95_high",
        "holm_p",
        "holm_significant_0.05",
        "interpretation",
    ]
]

pd.set_option("display.width", 240)
pd.set_option("display.max_rows", 100)

print(view.to_string(index=False))

print()
print("SAVED:")
print(
    "results/master_validation/statistics/"
    "topology_sensitivity_summary.csv"
)
print(
    "results/master_validation/statistics/"
    "topology_sensitivity_paired_tests.csv"
)
print(
    "results/master_validation/statistics/"
    "topology_sensitivity_budget_check.csv"
)
