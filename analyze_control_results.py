import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

INPUT = Path(
    "results/master_validation/statistics/control_multiseed_raw.csv"
)

OUTDIR = Path(
    "results/master_validation/statistics"
)

OUTDIR.mkdir(
    parents=True,
    exist_ok=True
)

df = pd.read_csv(INPUT)

METRICS = [
    "FND",
    "HND",
    "LND",
    "PDR_percent",
    "average_delay_ms",
    "energy_per_delivered_j",
    "retries_per_generated",
]

# Positive direction means "better" for interpretation.
DIRECTION = {
    "FND": 1,
    "HND": 1,
    "LND": 1,
    "PDR_percent": 1,
    "average_delay_ms": -1,
    "energy_per_delivered_j": -1,
    "retries_per_generated": -1,
}

# Separate statistical families.
CONTRASTS = [
    # Existing manuscript family: 21 tests
    (
        "legacy_21",
        "C1",
        "C2",
        "C1_to_C2"
    ),
    (
        "legacy_21",
        "C1",
        "C3",
        "C1_to_C3"
    ),
    (
        "legacy_21",
        "C3",
        "C4",
        "C3_to_C4"
    ),

    # New equal-budget / traffic-source family: 21 tests
    (
        "source_controls_21",
        "C1",
        "C5",
        "C1_to_C5"
    ),
    (
        "source_controls_21",
        "C5",
        "C3",
        "C5_to_C3"
    ),
    (
        "source_controls_21",
        "C6",
        "C3",
        "C6_to_C3"
    ),

    # Separate temporal-only sensitivity family: 7 tests
    (
        "temporal_only_7",
        "C3",
        "C7",
        "C3_to_C7"
    ),
]


def holm_adjust(pvalues):
    pvalues = np.asarray(
        pvalues,
        dtype=float
    )

    n = len(pvalues)

    order = np.argsort(pvalues)

    adjusted = np.empty(
        n,
        dtype=float
    )

    running = 0.0

    for rank, idx in enumerate(order):
        candidate = (
            (n - rank)
            * pvalues[idx]
        )

        running = max(
            running,
            candidate
        )

        adjusted[idx] = min(
            running,
            1.0
        )

    return adjusted


def exact_sign_flip_p(d):
    d = np.asarray(
        d,
        dtype=float
    )

    d = d[
        np.isfinite(d)
    ]

    n = len(d)

    if n == 0:
        return np.nan

    observed = abs(
        np.mean(d)
    )

    count = 0
    total = 2 ** n

    for signs in itertools.product(
        [-1.0, 1.0],
        repeat=n
    ):
        flipped = (
            d
            * np.asarray(signs)
        )

        if (
            abs(np.mean(flipped))
            >= observed - 1e-15
        ):
            count += 1

    return (
        count / total
    )


rows = []

for (
    family,
    baseline_mode,
    treatment_mode,
    contrast
) in CONTRASTS:

    base = (
        df[
            df["mode"] == baseline_mode
        ]
        .sort_values("seed")
    )

    treatment = (
        df[
            df["mode"] == treatment_mode
        ]
        .sort_values("seed")
    )

    assert np.array_equal(
        base["seed"].to_numpy(),
        treatment["seed"].to_numpy()
    )

    for metric in METRICS:
        x = pd.to_numeric(
            base[metric],
            errors="coerce"
        ).to_numpy(
            dtype=float
        )

        y = pd.to_numeric(
            treatment[metric],
            errors="coerce"
        ).to_numpy(
            dtype=float
        )

        mask = (
            np.isfinite(x)
            & np.isfinite(y)
        )

        x = x[mask]
        y = y[mask]

        d = y - x

        n = len(d)

        mean_diff = float(
            np.mean(d)
        )

        sd_diff = float(
            np.std(
                d,
                ddof=1
            )
        )

        sem = (
            sd_diff
            / math.sqrt(n)
        )

        tcrit = float(
            stats.t.ppf(
                0.975,
                n - 1
            )
        )

        ci_low = (
            mean_diff
            - tcrit * sem
        )

        ci_high = (
            mean_diff
            + tcrit * sem
        )

        t_result = stats.ttest_rel(
            y,
            x
        )

        if sd_diff > 0:
            cohen_dz = (
                mean_diff
                / sd_diff
            )
        else:
            cohen_dz = np.nan

        try:
            wilcoxon = stats.wilcoxon(
                y,
                x,
                zero_method="wilcox",
                alternative="two-sided"
            )

            wilcoxon_p = float(
                wilcoxon.pvalue
            )

        except ValueError:
            wilcoxon_p = np.nan

        signflip_p = exact_sign_flip_p(
            d
        )

        direction = DIRECTION[metric]

        favorable_mean_change = (
            mean_diff
            * direction
        )

        if favorable_mean_change > 0:
            interpretation = "favors_treatment"
        elif favorable_mean_change < 0:
            interpretation = "favors_baseline"
        else:
            interpretation = "no_mean_difference"

        rows.append({
            "family":
                family,

            "contrast":
                contrast,

            "baseline":
                baseline_mode,

            "treatment":
                treatment_mode,

            "metric":
                metric,

            "n":
                n,

            "baseline_mean":
                float(
                    np.mean(x)
                ),

            "treatment_mean":
                float(
                    np.mean(y)
                ),

            "mean_difference":
                mean_diff,

            "ci95_low":
                ci_low,

            "ci95_high":
                ci_high,

            "paired_t":
                float(
                    t_result.statistic
                ),

            "paired_t_p":
                float(
                    t_result.pvalue
                ),

            "wilcoxon_p":
                wilcoxon_p,

            "exact_signflip_p":
                signflip_p,

            "cohen_dz":
                cohen_dz,

            "directional_interpretation":
                interpretation,
        })


results = pd.DataFrame(
    rows
)

results[
    "holm_p"
] = np.nan

for family in results[
    "family"
].unique():

    idx = results[
        results["family"] == family
    ].index

    results.loc[
        idx,
        "holm_p"
    ] = holm_adjust(
        results.loc[
            idx,
            "paired_t_p"
        ].to_numpy()
    )


results[
    "holm_significant_0.05"
] = (
    results["holm_p"]
    < 0.05
)


output = (
    OUTDIR
    / "planned_paired_tests_holm.csv"
)

results.to_csv(
    output,
    index=False
)


# Compact equal-budget table.
important = results[
    results["contrast"].isin(
        [
            "C1_to_C5",
            "C5_to_C3",
            "C6_to_C3",
            "C3_to_C7",
        ]
    )
].copy()

important_output = (
    OUTDIR
    / "source_control_paired_tests.csv"
)

important.to_csv(
    important_output,
    index=False
)


print()
print("=" * 110)
print("PLANNED PAIRED TESTS WITH HOLM CORRECTION")
print("=" * 110)

display_cols = [
    "family",
    "contrast",
    "metric",
    "baseline_mean",
    "treatment_mean",
    "mean_difference",
    "ci95_low",
    "ci95_high",
    "holm_p",
    "cohen_dz",
    "directional_interpretation",
]

pd.set_option(
    "display.max_rows",
    100
)

pd.set_option(
    "display.width",
    220
)

pd.set_option(
    "display.max_columns",
    20
)

print(
    results[
        display_cols
    ].to_string(
        index=False
    )
)

print()
print("=" * 110)
print("SOURCE-CONTROL SIGNIFICANCE SUMMARY")
print("=" * 110)

print(
    important[
        [
            "contrast",
            "metric",
            "mean_difference",
            "ci95_low",
            "ci95_high",
            "holm_p",
            "holm_significant_0.05",
            "directional_interpretation",
        ]
    ].to_string(
        index=False
    )
)

print()
print("SAVED:")
print(output)
print(important_output)
