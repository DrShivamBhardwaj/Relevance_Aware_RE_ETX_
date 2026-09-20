from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parent


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def main():
    config = (ROOT / "src/wsn_hfl/config.py").read_text()
    manuscript = (ROOT / "MANUSCRIPT_RECONSTRUCTION.md").read_text()
    selection = json.loads((ROOT / "results/OPERATING_POINT_SELECTION.json").read_text())

    assert "relay_pressure_weight: float = 5.0" in config
    assert selection["selected"]["relay_pressure_weight"] == 5.0
    assert selection["selected"]["compression_distortion_weight"] == 0.1
    assert "utility-target JS" in manuscript
    assert "maximum relay energy 628.9%" in manuscript
    assert "Resource-adaptive uses 8.3% less traffic" in manuscript

    rows = read_csv(ROOT / "tables/table4_heldout_contrasts.csv")
    assert any(
        r["dataset"] == "uci_har"
        and r["baseline"] == "resource_adaptive"
        and r["metric"] == "accuracy"
        for r in rows
    )
    print("consistency audit passed")


if __name__ == "__main__":
    main()
