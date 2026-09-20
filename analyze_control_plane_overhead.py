import csv
import statistics
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from wsn_hfl.config import EVALUATION_SEEDS, SimConfig
from wsn_hfl.har import simulate_har
from wsn_hfl.intel_lab import simulate_intel


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    out = ROOT / "validation" / "control_plane"
    out.mkdir(parents=True, exist_ok=True)

    intel_cfg = replace(
        SimConfig(),
        num_clients=54,
        num_gateways=4,
        rounds=30,
        clients_per_round=10,
        local_steps=1,
        learning_rate=0.010,
        l2=0.010,
        round_slot_s=0.20,
        relay_budget_j_per_round=0.004,
        relay_pressure_weight=5.0,
        compression_distortion_weight=0.10,
    )
    har_cfg = replace(
        SimConfig(),
        num_clients=30,
        num_gateways=4,
        num_classes=6,
        feature_dim=561,
        rounds=25,
        clients_per_round=8,
        local_steps=1,
        learning_rate=0.02,
        l2=0.001,
        bandwidth_bps=250000.0,
        round_slot_s=0.25,
        relay_budget_j_per_round=0.004,
        relay_pressure_weight=5.0,
        compression_distortion_weight=0.10,
    )

    rows = []
    cases = (
        ("intel_lab", intel_cfg, simulate_intel, ROOT / "data" / "intel_lab"),
        ("uci_har", har_cfg, simulate_har, ROOT / "data" / "uci_har"),
    )

    for dataset, cfg, fn, data_path in cases:
        for method in ("proposed_fixed_comp", "proposed"):
            for seed in EVALUATION_SEEDS:
                summary, _ = fn(method, replace(cfg, seed=seed), data_path, 0.9)
                rows.append(
                    {
                        "dataset": dataset,
                        "method": method,
                        "seed": seed,
                        "metadata_packet_bits": summary["metadata_packet_bits"],
                        "metadata_raw_bits": summary["metadata_raw_bits"],
                        "metadata_effective_bits": summary["metadata_effective_bits"],
                        "metadata_radio_energy_upper_j": summary["metadata_radio_energy_upper_j"],
                        "model_update_effective_bits": summary["effective_bits"],
                        "model_energy_j": summary["energy_j"],
                        "control_inclusive_uplink_bits": summary["control_inclusive_uplink_bits"],
                    }
                )

    write_csv(out / "metadata_compression_contrast.csv", rows)

    lines = [
        "# Control-plane-aware compression contrast",
        "",
        "Each candidate reports 168 bits (21 bytes) per round: 96-bit header, "
        "32-bit local loss, 32-bit residual-energy estimate, and 8-bit availability.",
        "",
    ]
    summary_rows = []

    for dataset in ("intel_lab", "uci_har"):
        grouped = {
            method: [r for r in rows if r["dataset"] == dataset and r["method"] == method]
            for method in ("proposed_fixed_comp", "proposed")
        }
        means = {}
        for method, group in grouped.items():
            means[method] = {
                key: statistics.fmean(float(r[key]) for r in group)
                for key in (
                    "metadata_raw_bits",
                    "metadata_effective_bits",
                    "metadata_radio_energy_upper_j",
                    "model_update_effective_bits",
                    "model_energy_j",
                    "control_inclusive_uplink_bits",
                )
            }

        fixed = means["proposed_fixed_comp"]
        prop = means["proposed"]
        model_reduction = 100.0 * (1.0 - prop["model_update_effective_bits"] / fixed["model_update_effective_bits"])
        inclusive_reduction = 100.0 * (1.0 - prop["control_inclusive_uplink_bits"] / fixed["control_inclusive_uplink_bits"])
        meta_pct = 100.0 * prop["metadata_effective_bits"] / prop["model_update_effective_bits"]

        summary_rows.append(
            {
                "dataset": dataset,
                "raw_metadata_kib": prop["metadata_raw_bits"] / 8.0 / 1024.0,
                "metadata_effective_mbit": prop["metadata_effective_bits"] / 1e6,
                "metadata_radio_energy_upper_j": prop["metadata_radio_energy_upper_j"],
                "metadata_pct_of_proposed_model_traffic": meta_pct,
                "proposed_control_inclusive_mbit": prop["control_inclusive_uplink_bits"] / 1e6,
                "proposed_fixed_control_inclusive_mbit": fixed["control_inclusive_uplink_bits"] / 1e6,
                "model_only_reduction_pct": model_reduction,
                "control_inclusive_reduction_pct": inclusive_reduction,
            }
        )

        lines.extend(
            [
                f"## {dataset}",
                f"- Raw metadata: {prop['metadata_raw_bits']/8/1024:.2f} KiB.",
                f"- ETX-weighted metadata: {prop['metadata_effective_bits']/1e6:.3f} Mbit.",
                f"- Conservative metadata radio-energy upper bound: {prop['metadata_radio_energy_upper_j']:.3f} J.",
                f"- Metadata / proposed model traffic: {meta_pct:.2f}%.",
                f"- Proposed control-inclusive uplink: {prop['control_inclusive_uplink_bits']/1e6:.3f} Mbit.",
                f"- Proposed-fixed control-inclusive uplink: {fixed['control_inclusive_uplink_bits']/1e6:.3f} Mbit.",
                f"- Adaptive reduction: model-only {model_reduction:.1f}%; control-inclusive {inclusive_reduction:.1f}%.",
                "",
            ]
        )

    write_csv(out / "metadata_summary.csv", summary_rows)
    (out / "METADATA_OVERHEAD_REPORT.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
