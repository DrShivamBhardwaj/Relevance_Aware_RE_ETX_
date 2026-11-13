"""Non-destructive consistency checks for IJWMT PAPER024501.

This checks archived results and code behavior. It does not rerun the
original radio simulation or claim distributed-control validation.
"""
from pathlib import Path
import json
import sys
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from config import SimulationConfig
from simulator.semantic_payload import SemanticPayloadController

BASE = ROOT / "results/master_validation/statistics"
controls = pd.read_csv(BASE / "control_multiseed_raw.csv")
topologies = pd.read_csv(BASE / "topology_sensitivity_raw.csv")
events = pd.read_csv(BASE / "event_quality_multiseed_raw.csv")
expected_seeds = {11,23,42,67,101,137,173,211,257,307}
expected_modes = {"C1","C2","C3","C4","C5","C6","C7"}
checks = {
  "control_count_70": len(controls) == 70,
  "control_modes": set(controls["mode"]) == expected_modes,
  "control_ten_seeds_per_mode": all(set(g["seed"]) == expected_seeds and len(g) == 10 for _,g in controls.groupby("mode")),
  "topology_count_90": len(topologies) == 90,
  "topology_profiles": set(topologies["profile"]) == {"shallow","medium","deep"},
  "topology_ten_seeds_per_profile_mode": all(set(g["seed"]) == expected_seeds and len(g) == 10 for _,g in topologies.groupby(["profile","mode"])),
  "event_quality_count_70": len(events) == 70,
}
p = SemanticPayloadController(SimulationConfig())
mapping = {str(x): int(p.payload_bits([x])[0]) for x in (0.0,0.49,0.50,0.51,0.85,1.0)}
checks["threshold_050_3000_bits"] = mapping["0.5"] == 3000
checks["threshold_085_4000_bits"] = mapping["0.85"] == 4000
def means(mode):
    d = controls.loc[controls["mode"] == mode]
    return {k:round(float(d[k].mean()),6) for k in ("FND","HND","LND","PDR_percent","average_delay_ms","energy_per_delivered_j","attempted_mean_payload_bits") if k in d}
out = {
  "source": "Archived C1-C7 source-control and 3-profile topology data",
  "not_a_simulation_rerun": True,
  "checks": checks,
  "payload_mapping_bits": mapping,
  "means": {m:means(m) for m in ("C1","C3","C5","C6")},
  "limitations": ["Original results not regenerated", "Receiver reconstruction not tested", "Distributed neighbor exchange not measured"]
}
target = ROOT / "reviewer_audit/PAPER024501/archive_check.json"
target.write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out, indent=2))
if not all(checks.values()):
    raise SystemExit("One or more archive consistency checks failed")
