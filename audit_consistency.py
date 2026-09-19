import csv
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from wsn_hfl.config import SimConfig

EXPECTED = {
    "relay_pressure_weight": 3.0,
    "compression_distortion_weight": 0.10,
    "drift_v": 0.5,
    "staleness_lambda": 0.35,
    "utility_staleness_mu": 0.80,
}
SEEDS = [7, 11, 19, 23, 29, 31, 37, 41, 43, 47]


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def row_at(path, method, corr=0.9):
    rows = read_csv(path)
    return next(r for r in rows if r["method"] == method and abs(float(r["correlation"]) - corr) < 1e-12)
def close(a, b, tol=5e-4):
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol)


def pct_change(new, old):
    return 100.0 * (float(new) - float(old)) / float(old)


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def check_manifest(path, issues):
    j = json.loads(path.read_text())
    cfg = j["config"]
    for key, value in EXPECTED.items():
        if not close(cfg[key], value, 1e-12):
            issues.append(f"{path}: {key}={cfg[key]} != {value}")
    if list(j["seeds"]) != SEEDS:
        issues.append(f"{path}: seeds are not the frozen 10-seed set")
    return j
def main():
    issues = []
    cfg = SimConfig()
    for key, value in EXPECTED.items():
        if not close(getattr(cfg, key), value, 1e-12):
            issues.append(f"SimConfig.{key}={getattr(cfg,key)} != {value}")

    synth_manifest = check_manifest(ROOT / "results/final_synthetic_10seed/run_manifest.json", issues)
    intel_manifest = check_manifest(ROOT / "results/intel_lab/run_manifest.json", issues)
    har_manifest = check_manifest(ROOT / "results/uci_har/run_manifest.json", issues)

    if (ROOT / "results/aggregate_summary.csv").read_bytes() != (ROOT / "results/final_synthetic_10seed/aggregate_summary.csv").read_bytes():
        issues.append("root synthetic aggregate is not identical to final 10-seed aggregate")
    if (ROOT / "results/raw_summary.csv").read_bytes() != (ROOT / "results/final_synthetic_10seed/raw_summary.csv").read_bytes():
        issues.append("root synthetic raw summary is not identical to final 10-seed raw summary")

    intel_p = row_at(ROOT / "results/intel_lab/aggregate_summary.csv", "proposed")
    intel_r = row_at(ROOT / "results/intel_lab/aggregate_summary.csv", "resource")
    har_p = row_at(ROOT / "results/uci_har/aggregate_summary.csv", "proposed")
    har_r = row_at(ROOT / "results/uci_har/aggregate_summary.csv", "resource")
    syn_p = row_at(ROOT / "results/final_synthetic_10seed/aggregate_summary.csv", "proposed")
    syn_r = row_at(ROOT / "results/final_synthetic_10seed/aggregate_summary.csv", "resource")
    manuscript = (ROOT / "MANUSCRIPT_RECONSTRUCTION.md").read_text()
    evidence = (ROOT / "EXPERIMENTAL_EVIDENCE_SUMMARY.md").read_text()
    freeze = (ROOT / "PARAMETER_FREEZE.md").read_text()
    readme = (ROOT / "README.md").read_text()
    required_text = [
        ("MANUSCRIPT_RECONSTRUCTION.md", manuscript, "\\(\\eta_R=3\\) and \\(\\beta=0.1\\)"),
        ("PARAMETER_FREEZE.md", freeze, "relay_pressure_weight = 3.0"),
        ("PARAMETER_FREEZE.md", freeze, "compression_distortion_weight = 0.10"),
        ("EXPERIMENTAL_EVIDENCE_SUMMARY.md", evidence, "compression_distortion_weight = 0.10"),
        ("README.md", readme, "Frozen default"),
        ("README.md", readme, "compression-distortion weight `0.1`"),
        ("MANUSCRIPT_RECONSTRUCTION.md", manuscript, "55.67%"),
        ("MANUSCRIPT_RECONSTRUCTION.md", manuscript, "60.75%"),
        ("MANUSCRIPT_RECONSTRUCTION.md", manuscript, "86.49%"),
        ("MANUSCRIPT_RECONSTRUCTION.md", manuscript, "99.47%"),
    ]
    for name, text, needle in required_text:
        if needle not in text:
            issues.append(f"{name}: missing frozen text/value {needle!r}")
    for stale in ("full 36-run reference experiment", "synthetic setting should be followed by"):
        if stale in readme:
            issues.append(f"README.md: stale pre-final wording remains: {stale!r}")

    computed = {
        "intel_comm_pct": pct_change(intel_p["effective_bits_mean"], intel_r["effective_bits_mean"]),
        "intel_energy_pct": pct_change(intel_p["energy_j_mean"], intel_r["energy_j_mean"]),
        "intel_relay_pct": pct_change(intel_p["max_relay_energy_j_mean"], intel_r["max_relay_energy_j_mean"]),
        "intel_rep_pct": pct_change(intel_p["representation_js_mean"], intel_r["representation_js_mean"]),
        "har_acc_pp": 100.0 * (float(har_p["accuracy_mean"]) - float(har_r["accuracy_mean"])),
        "har_comm_pct": pct_change(har_p["effective_bits_mean"], har_r["effective_bits_mean"]),
        "har_energy_pct": pct_change(har_p["energy_j_mean"], har_r["energy_j_mean"]),
        "har_rep_pct": pct_change(har_p["representation_js_mean"], har_r["representation_js_mean"]),
    }
    expected_claims = {
        "intel_comm_pct": -55.67,
        "intel_energy_pct": -45.06,
        "intel_relay_pct": -29.94,
        "intel_rep_pct": -81.21,
        "har_acc_pp": 3.08,
        "har_comm_pct": -60.75,
        "har_energy_pct": -56.38,
        "har_rep_pct": -79.97,
    }
    for key, expected in expected_claims.items():
        if not close(computed[key], expected, 0.015):
            issues.append(f"claim mismatch {key}: computed {computed[key]:.4f}, expected {expected:.2f}")

    data_manifest_checks = [
        ("data/intel_lab/data.txt.gz", intel_manifest["checksums"]["data.txt.gz"]),
        ("data/intel_lab/mote_locs.txt", intel_manifest["checksums"]["mote_locs.txt"]),
        ("data/intel_lab/connectivity.txt", intel_manifest["checksums"]["connectivity.txt"]),
        ("data/uci_har/har.zip", har_manifest["har_zip_sha256"]),
    ]
    for rel, expected in data_manifest_checks:
        p = ROOT / rel
        if not p.exists():
            issues.append(f"missing dataset file {rel}")
        elif sha256(p) != expected:
            issues.append(f"checksum mismatch for {rel}")

    obsolete_active = [
        ROOT / "results/pre_tuning",
        ROOT / "results/final_synthetic",
        ROOT / "validation/sensitivity",
        ROOT / "MANUSCRIPT_DRAFT.md",
    ]
    for p in obsolete_active:
        if p.exists():
            issues.append(f"obsolete active artifact should be archived/removed: {p.relative_to(ROOT)}")
    print("CONSISTENCY AUDIT")
    print("=================")
    print(f"Frozen config: eta_R={cfg.relay_pressure_weight}, beta={cfg.compression_distortion_weight}, V={cfg.drift_v}")
    print(f"Synthetic c=0.9: resource acc={float(syn_r['accuracy_mean']):.4f}, proposed acc={float(syn_p['accuracy_mean']):.4f}")
    print(f"Intel c=0.9: comm {computed['intel_comm_pct']:.2f}%, energy {computed['intel_energy_pct']:.2f}%, relay {computed['intel_relay_pct']:.2f}%, rep {computed['intel_rep_pct']:.2f}%")
    print(f"HAR c=0.9: accuracy +{computed['har_acc_pp']:.2f} pp, comm {computed['har_comm_pct']:.2f}%, energy {computed['har_energy_pct']:.2f}%, rep {computed['har_rep_pct']:.2f}%")
    if issues:
        print("\nFAIL")
        for item in issues:
            print("-", item)
        raise SystemExit(1)
    print("\nPASS: frozen configuration, manifests, key manuscript claims, result mirrors, and dataset checksums are consistent.")


if __name__ == "__main__":
    main()
