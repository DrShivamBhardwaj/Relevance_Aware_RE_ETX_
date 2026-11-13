"""Bounded application-report energy overhead sensitivity, not an emulator.

Comparisons are normalized to generated and delivered reports in each archived
seed. This avoids mislabeling the equal 50J energy at full LND as energy saving.
"""
from pathlib import Path
import csv,json
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
raw=pd.read_csv(ROOT/"results/master_validation/statistics/control_multiseed_raw.csv")
rows=[]
for extra_mj in (0,0.005,0.01,0.05,0.1,0.25,0.5,1.0,2.0):
 for seed in sorted(raw.seed.unique()):
  a={m:raw[(raw.seed==seed)&(raw["mode"]==m)].iloc[0] for m in ("C1","C3","C5","C6")}
  report={}
  for mode,r in a.items():
   n_generated=float(r["generated_messages"]);n_delivered=float(r["delivered_messages"])
   radio_j=float(r["energy_per_delivered_j"])*n_delivered
   counterfactual_j=radio_j + extra_mj/1000*n_generated
   report[mode]=counterfactual_j/n_delivered
  rows.append({"seed":int(seed),"additional_sensing_computation_control_idle_mJ_per_generated_report":extra_mj,**{mode+"_normalized_mJ_per_delivered_report":report[mode]*1000 for mode in report},
               "C3_vs_C1_reduction_percent":100*(1-report["C3"]/report["C1"]),
               "C3_vs_C5_reduction_percent":100*(1-report["C3"]/report["C5"])})
path=OUT/"extended_energy_accounting.csv"
with path.open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
summary={
 "rows":len(rows),"scope":"counterfactual report-normalized accounting; NOT re-simulated node survival",
 "cost_included":"constant additional mJ per generated report",
 "cost_excluded":"node-specific sensing/idle state, energy-induced route/lifetime changes, extra control packets, interference",
 "source":"results/master_validation/statistics/control_multiseed_raw.csv",
 "warning":"Do not update FND/HND/LND or claim actual distributed energy savings from this table"
}
(OUT/"extended_energy_accounting_meta.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary))
