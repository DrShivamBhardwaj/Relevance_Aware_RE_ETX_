import csv
import os

import numpy as np
import pandas as pd

from scipy import stats

from run_re_etx_sweep import (
    run_single_weight
)


SEEDS = [
    11,
    23,
    42,
    67,
    101,
    137,
    173,
    211,
    257,
    307
]


ENERGY_WEIGHTS = [
    0.0,
    0.25,
    0.5,
    1.0
]


SUMMARY_METRICS = [
    "FND",
    "HND",
    "LND",
    "PDR_percent",
    "delivered_messages",
    "retransmissions",
    "average_hops",
    "average_delay_ms",
    "goodput_kbps",
    "energy_per_delivered_j",
    "relay_HHI",
    "max_relay_share",
    "mean_alive_fraction"
]


def mean_ci95(values):
    values = np.asarray(
        values,
        dtype=np.float64
    )

    values = values[
        np.isfinite(values)
    ]

    n = len(values)

    if n == 0:
        return (
            np.nan,
            np.nan,
            np.nan,
            np.nan,
            0
        )

    mean = float(
        np.mean(values)
    )

    if n == 1:
        return (
            mean,
            0.0,
            mean,
            mean,
            1
        )

    std = float(
        np.std(
            values,
            ddof=1
        )
    )

    sem = (
        std
        / np.sqrt(n)
    )

    tcrit = float(
        stats.t.ppf(
            0.975,
            df=n - 1
        )
    )

    margin = (
        tcrit
        * sem
    )

    return (
        mean,
        std,
        mean - margin,
        mean + margin,
        n
    )


def main():
    os.makedirs(
        "results/re_etx_multiseed",
        exist_ok=True
    )

    raw_results = []

    total_runs = (
        len(SEEDS)
        * len(ENERGY_WEIGHTS)
    )

    run_number = 0

    print("=" * 100)
    print(
        "MULTI-SEED RESIDUAL-ENERGY-AWARE ETX VALIDATION"
    )
    print("=" * 100)

    print(
        f"Seeds              : {SEEDS}"
    )

    print(
        f"Lambda values      : {ENERGY_WEIGHTS}"
    )

    print(
        f"Total simulations  : {total_runs}"
    )

    print()

    for seed in SEEDS:
        for weight in ENERGY_WEIGHTS:
            run_number += 1

            print(
                f"[{run_number:02d}/{total_runs}] "
                f"seed={seed:3d}, "
                f"lambda={weight:.2f}"
            )

            result = run_single_weight(
                energy_weight=weight,
                seed=seed
            )

            raw_results.append(
                result
            )

            print(
                "    "
                f"FND/HND/LND="
                f"{result['FND']}/"
                f"{result['HND']}/"
                f"{result['LND']} | "
                f"PDR="
                f"{result['PDR_percent']:.3f}% | "
                f"Delivered="
                f"{result['delivered_messages']} | "
                f"HHI="
                f"{result['relay_HHI']:.5f}"
            )

    # ==================================================
    # Save raw run-level results
    # ==================================================

    raw_path = (
        "results/"
        "re_etx_multiseed_raw.csv"
    )

    raw_df = pd.DataFrame(
        raw_results
    )

    raw_df.to_csv(
        raw_path,
        index=False
    )

    # ==================================================
    # Aggregate mean, SD and 95% CI
    # ==================================================

    summary_rows = []

    for weight in ENERGY_WEIGHTS:
        subset = raw_df[
            raw_df[
                "lambda_energy"
            ] == weight
        ]

        row = {
            "lambda_energy":
                weight,

            "num_seeds":
                len(subset)
        }

        for metric in SUMMARY_METRICS:
            values = pd.to_numeric(
                subset[metric],
                errors="coerce"
            ).to_numpy()

            (
                mean,
                std,
                ci_low,
                ci_high,
                n
            ) = mean_ci95(
                values
            )

            row[
                f"{metric}_mean"
            ] = mean

            row[
                f"{metric}_std"
            ] = std

            row[
                f"{metric}_ci95_low"
            ] = ci_low

            row[
                f"{metric}_ci95_high"
            ] = ci_high

        summary_rows.append(
            row
        )

    summary_df = pd.DataFrame(
        summary_rows
    )

    summary_path = (
        "results/"
        "re_etx_multiseed_summary.csv"
    )

    summary_df.to_csv(
        summary_path,
        index=False
    )

    # ==================================================
    # Paired comparisons against lambda=0
    #
    # Same seed is used for every lambda, so paired
    # statistics are more appropriate than independent
    # tests.
    # ==================================================

    paired_rows = []

    base = raw_df[
        raw_df[
            "lambda_energy"
        ] == 0.0
    ].sort_values(
        "seed"
    )

    comparison_metrics = [
        "FND",
        "HND",
        "LND",
        "PDR_percent",
        "delivered_messages",
        "average_delay_ms",
        "goodput_kbps",
        "relay_HHI",
        "mean_alive_fraction"
    ]

    for weight in [
        w
        for w in ENERGY_WEIGHTS
        if w != 0.0
    ]:
        treatment = raw_df[
            raw_df[
                "lambda_energy"
            ] == weight
        ].sort_values(
            "seed"
        )

        assert np.array_equal(
            base["seed"].to_numpy(),
            treatment["seed"].to_numpy()
        )

        for metric in comparison_metrics:
            x = pd.to_numeric(
                base[metric],
                errors="coerce"
            ).to_numpy(
                dtype=np.float64
            )

            y = pd.to_numeric(
                treatment[metric],
                errors="coerce"
            ).to_numpy(
                dtype=np.float64
            )

            mask = (
                np.isfinite(x)
                & np.isfinite(y)
            )

            x = x[mask]
            y = y[mask]

            difference = (
                y - x
            )

            if len(x) >= 2:
                t_result = (
                    stats.ttest_rel(
                        y,
                        x
                    )
                )

                t_stat = float(
                    t_result.statistic
                )

                p_value = float(
                    t_result.pvalue
                )

                # Wilcoxon gives a useful non-parametric
                # paired robustness check.
                try:
                    w_result = (
                        stats.wilcoxon(
                            y,
                            x,
                            zero_method="wilcox"
                        )
                    )

                    wilcoxon_p = float(
                        w_result.pvalue
                    )

                except ValueError:
                    wilcoxon_p = np.nan

            else:
                t_stat = np.nan
                p_value = np.nan
                wilcoxon_p = np.nan

            paired_rows.append({
                "lambda_energy":
                    weight,

                "metric":
                    metric,

                "n":
                    len(x),

                "baseline_mean":
                    float(
                        np.mean(x)
                    ),

                "treatment_mean":
                    float(
                        np.mean(y)
                    ),

                "mean_difference":
                    float(
                        np.mean(
                            difference
                        )
                    ),

                "paired_t_stat":
                    t_stat,

                "paired_t_p":
                    p_value,

                "wilcoxon_p":
                    wilcoxon_p
            })

    paired_df = pd.DataFrame(
        paired_rows
    )

    paired_path = (
        "results/"
        "re_etx_multiseed_paired_tests.csv"
    )

    paired_df.to_csv(
        paired_path,
        index=False
    )

    # ==================================================
    # Console summary
    # ==================================================

    print()
    print("=" * 100)
    print("MULTI-SEED SUMMARY: MEAN ± SD")
    print("=" * 100)

    header = (
        f"{'lambda':>7} "
        f"{'FND':>15} "
        f"{'HND':>15} "
        f"{'LND':>15} "
        f"{'PDR%':>17} "
        f"{'Delivered':>20} "
        f"{'Delay ms':>19} "
        f"{'Goodput':>18} "
        f"{'HHI':>17} "
        f"{'AliveFrac':>18}"
    )

    print(header)
    print("-" * len(header))

    for _, row in summary_df.iterrows():

        def pm(metric, digits=2):
            mean = row[
                f"{metric}_mean"
            ]

            std = row[
                f"{metric}_std"
            ]

            return (
                f"{mean:.{digits}f}"
                f"±"
                f"{std:.{digits}f}"
            )

        print(
            f"{row['lambda_energy']:7.2f} "
            f"{pm('FND', 1):>15} "
            f"{pm('HND', 1):>15} "
            f"{pm('LND', 1):>15} "
            f"{pm('PDR_percent', 3):>17} "
            f"{pm('delivered_messages', 1):>20} "
            f"{pm('average_delay_ms', 2):>19} "
            f"{pm('goodput_kbps', 2):>18} "
            f"{pm('relay_HHI', 5):>17} "
            f"{pm('mean_alive_fraction', 4):>18}"
        )

    print()
    print(
        "Raw results CSV        :",
        raw_path
    )

    print(
        "Aggregate summary CSV  :",
        summary_path
    )

    print(
        "Paired statistics CSV  :",
        paired_path
    )

    print()
    print(
        "Multi-seed validation COMPLETED."
    )


if __name__ == "__main__":
    main()
