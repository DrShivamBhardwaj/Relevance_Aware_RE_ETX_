"""Analytical neighbor-observation overhead: a bounded accounting illustration.

Not a network rerun. Uses the repository's first-order TX/RX radio model.
Assumes one exchange per attempted report, all receivers successfully obtain
the context, no retries, no extra MAC framing, and a stated distance.
"""
from pathlib import Path
import csv
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from config import SimulationConfig
from simulator.energy import RadioEnergyModel
import pandas as pd

radio = RadioEnergyModel(SimulationConfig())
archive = pd.read_csv(ROOT / "results/master_validation/statistics/control_multiseed_raw.csv")
c1 = archive.loc[archive["mode"] == "C1", "energy_per_delivered_j"].mean()
c3 = archive.loc[archive["mode"] == "C3", "energy_per_delivered_j"].mean()
# Per-delivered-report accounting comparison only: not lifetime or total
# network-energy counterfactual.
margin_j = float(c1-c3)
rows = []
for bits in (0, 100, 200, 500, 1000, 2000, 4000, 8000):
  for receivers in (1, 2, 4):
    distance_m = 20.0
    extra_j = float(radio.tx_energy(bits,distance_m) + receivers*radio.rx_energy(bits))
    rows.append({
      "observation_bits_per_exchange": bits,
      "recipients": receivers,
      "distance_m": distance_m,
      "context_energy_mJ_per_attempted_report_no_retries": round(1000*extra_j, 6),
      "C1_minus_C3_archived_mJ_per_delivered_report": round(1000*margin_j, 6),
      "illustrative_fraction_of_margin": round(extra_j/margin_j, 6),
      "scope": "illustrative, not lifetime, requires delivery denominator and framing"
    })
target=ROOT/"reviewer_audit/PAPER024501/context_overhead_sensitivity.csv"
with target.open("w",newline="") as f:
  writer=csv.DictWriter(f, fieldnames=list(rows[0]))
  writer.writeheader();writer.writerows(rows)
print("ARCHIVED C1-C3 energy per delivered report margin (mJ):", round(1000*margin_j,6))
print("100 bits, 20m, one receiver: (mJ)",next(r["context_energy_mJ_per_attempted_report_no_retries"] for r in rows if r["observation_bits_per_exchange"]==100 and r["recipients"]==1))
print("Rows:",len(rows),"saved:",target)
