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


def test_publication_table_manifest_hashes_match():
    manifest = json.loads((ROOT / "tables/TABLE_FREEZE_MANIFEST.json").read_text())
    assert manifest["status"] == "FROZEN"
    for group in ("source_sha256", "generated_sha256"):
        for rel, expected in manifest[group].items():
            path = ROOT / rel
            assert path.exists(), rel
            assert sha256(path) == expected, rel


def test_har_relay_tradeoff_is_retained():
    manifest = json.loads((ROOT / "tables/TABLE_FREEZE_MANIFEST.json").read_text())
    change = manifest["frozen_claims"]["har_c0.9_vs_resource"]["max_relay_energy_percent"]
    assert change > 200.0
    text = (ROOT / "MANUSCRIPT_RECONSTRUCTION.md").read_text()
    assert "209.28% increase relative to resource-only" in text


def test_resource_contrast_significance_is_not_overstated():
    rows = read_csv(ROOT / "tables/table4_resource_contrasts.csv")
    intel_rmse = next(r for r in rows if r["dataset"] == "intel_lab" and r["metric"] == "rmse_c")
    intel_bits = next(r for r in rows if r["dataset"] == "intel_lab" and r["metric"] == "effective_bits")
    assert float(intel_rmse["holm_p"]) > 0.05
    assert float(intel_bits["holm_p"]) < 0.05
