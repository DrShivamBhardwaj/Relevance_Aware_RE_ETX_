import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def contrast(rows, dataset, baseline, metric):
    return next(
        r for r in rows
        if r["dataset"] == dataset
        and r["baseline"] == baseline
        and r["metric"] == metric
    )


def test_publication_table_manifest_hashes_match():
    manifest = json.loads((ROOT / "tables/TABLE_FREEZE_MANIFEST.json").read_text())
    assert manifest["status"] == "FROZEN"
    for group in ("source_sha256", "generated_sha256"):
        for rel, expected in manifest[group].items():
            path = ROOT / rel
            assert path.exists(), rel
            assert sha256(path) == expected, rel


def test_har_matched_compression_tradeoff_is_retained():
    rows = read_csv(ROOT / "tables/table4_heldout_contrasts.csv")
    relay = contrast(rows, "uci_har", "resource_adaptive", "max_relay_energy_j")
    accuracy = contrast(rows, "uci_har", "resource_adaptive", "accuracy")

    # The revised paper must retain the adverse network cost rather than
    # presenting the proposed controller as an unconditional winner.
    assert float(relay["percent_change_vs_baseline"]) > 500.0
    assert float(relay["holm_p"]) < 0.05
    assert float(accuracy["mean_diff"]) > 0.0
    assert float(accuracy["holm_p"]) < 0.05

    text = (ROOT / "MANUSCRIPT_RECONSTRUCTION.md").read_text()
    assert "maximum relay energy 628.9%" in text
    assert "1.16 percentage points over resource-adaptive" in text


def test_intel_matched_control_prevents_overclaim():
    rows = read_csv(ROOT / "tables/table4_heldout_contrasts.csv")
    rmse = contrast(rows, "intel_lab", "resource_adaptive", "rmse_c")
    bits = contrast(rows, "intel_lab", "resource_adaptive", "effective_bits")
    utility_js = contrast(rows, "intel_lab", "resource_adaptive", "utility_target_js")

    # Resource-adaptive is better on pure error/traffic, while proposed is
    # better on its endogenous utility-target alignment metric.
    assert float(rmse["mean_diff"]) > 0.0
    assert float(bits["mean_diff"]) > 0.0
    assert float(utility_js["mean_diff"]) < 0.0
    assert float(utility_js["holm_p"]) < 0.05

    text = (ROOT / "MANUSCRIPT_RECONSTRUCTION.md").read_text()
    assert "Resource-adaptive uses 8.3% less traffic" in text
    assert "utility-target JS by 86.0%" in text


def test_fedcg_adapted_comparator_is_not_overstated():
    rows = read_csv(ROOT / "tables/table4_heldout_contrasts.csv")

    intel_rmse = contrast(rows, "intel_lab", "fedcg_adapted", "rmse_c")
    intel_bits = contrast(rows, "intel_lab", "fedcg_adapted", "effective_bits")
    har_accuracy = contrast(rows, "uci_har", "fedcg_adapted", "accuracy")

    # Intel performance/systems differences are statistically comparable,
    # whereas the HAR accuracy difference remains significant.
    assert float(intel_rmse["holm_p"]) > 0.05
    assert float(intel_bits["holm_p"]) > 0.05
    assert float(har_accuracy["mean_diff"]) > 0.0
    assert float(har_accuracy["holm_p"]) < 0.05
