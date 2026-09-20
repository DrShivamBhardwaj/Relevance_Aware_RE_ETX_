from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = (ROOT / "src/wsn_hfl/config.py").read_text()
    manuscript = (ROOT / "MANUSCRIPT_RECONSTRUCTION.md").read_text()
    selection = json.loads((ROOT / "results/OPERATING_POINT_SELECTION.json").read_text())

    assert "relay_pressure_weight: float = 5.0" in config
    assert selection["selected"]["relay_pressure_weight"] == 5.0
    assert selection["selected"]["compression_distortion_weight"] == 0.1
    assert "utility-target JS" in manuscript
    assert "maximum relay energy by 628.9%" in manuscript or "maximum relay energy 628.9%" in manuscript
    assert "Resource-adaptive uses 8.3% less traffic" in manuscript
    assert "Control-plane overhead audit" in manuscript
    assert "38.4% control-inclusive uplink reduction" in manuscript
    assert "63.3% on HAR" in manuscript
    assert "open loop" in manuscript.lower()
    assert "Model-complexity scaling" in manuscript

    rows = read_csv(ROOT / "tables/table4_heldout_contrasts.csv")
    assert any(
        r["dataset"] == "uci_har"
        and r["baseline"] == "resource_adaptive"
        and r["metric"] == "accuracy"
        for r in rows
    )

    control = {r["dataset"]: r for r in read_csv(ROOT / "validation/control_plane/metadata_summary.csv")}
    assert abs(float(control["intel_lab"]["metadata_effective_mbit"]) - 1.218662728490601) < 1e-12
    assert abs(float(control["intel_lab"]["control_inclusive_reduction_pct"]) - 38.44106075655178) < 1e-10
    assert abs(float(control["uci_har"]["control_inclusive_reduction_pct"]) - 63.34834260031486) < 1e-10

    lock = json.loads((ROOT / "figures/APPROVED_FINAL_SHA256.json").read_text())
    assert lock["status"] == "USER_VERIFIED_LOCKED"
    assert len(lock["images"]) == 7
    for name, meta in lock["images"].items():
        path = ROOT / "figures/final" / name
        assert path.exists(), name
        assert sha256(path) == meta["sha256"], name

    print("consistency audit passed; approved figure hashes verified")


if __name__ == "__main__":
    main()
