"""Paired-seed analysis of *executed* review-branch parameter simulations."""
import json,csv,math,pathlib
import numpy as np
from scipy.stats import ttest_rel,t
BASE=pathlib.Path(__file__).resolve().parent/"network_parameter_sweep"
data=[]
for p in BASE.glob("*_seed*.json"):
 try:
  r=json.loads(p.read_text())
  if r.get("completed"):data.append(r)
 except ValueError:pass
metrics=["FND","HND","LND","pdr_percent","delay_ms","energy_per_delivered_j"]
variant_names=sorted({r["variant"] for r in data})
by={(r["variant"],r["seed"]):r for r in data}
rows=[]
for variant in variant_names:
 if variant=="baseline":continue
 seeds=sorted(s for name,s in by if name==variant and ("baseline",s) in by)
 for metric in metrics:
  if len(seeds)<3:continue
  a=np.array([by[(variant,s)][metric] for s in seeds],dtype=float)
  b=np.array([by[("baseline",s)][metric] for s in seeds],dtype=float)
  diff=a-b
  z=ttest_rel(a,b)
  half=float(t.ppf(.975,len(seeds)-1)*np.std(diff,ddof=1)/math.sqrt(len(seeds)))
  rows.append({"variant":variant,"metric":metric,"n_paired_seeds":len(seeds),"mean_variant":float(np.mean(a)),"mean_baseline":float(np.mean(b)),"mean_diff":float(np.mean(diff)),"ci95_lower":float(np.mean(diff)-half),"ci95_upper":float(np.mean(diff)+half),"p_raw":float(z.pvalue)})
# Holm adjustment per prespecified family across every tested alternative and metric
rows.sort(key=lambda x:x["p_raw"])
m=len(rows);prev=0.
for i,r in enumerate(rows):
 prev=max(prev,min(1.,r["p_raw"]*(m-i)))
 r["p_holm"]=prev
out=BASE/"paired_sensitivity_analysis.csv"
if rows:
 with out.open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({"completed":len(data),"variants":variant_names,"contrasts":len(rows),"output":str(out),"warning":"Parameters evaluated on identical seeds as archival work; do not claim independent confirmatory test. Incomplete variants are provisional."},indent=2))
