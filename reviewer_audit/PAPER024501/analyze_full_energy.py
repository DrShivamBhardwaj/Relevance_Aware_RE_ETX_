"""Paired full-node-battery sensitivity, with explicit assumption labels."""
from pathlib import Path
import json,csv
import numpy as np
from scipy.stats import ttest_rel,t
BASE=Path(__file__).resolve().parent/"full_network_energy"
data={}
for path in BASE.glob("*_seed*.json"):
 try:
  d=json.loads(path.read_text())
  if d.get("passed"):data[(d["scenario"],d["mode"],d["seed"])]=d
 except Exception:pass
rows=[]
metrics=["FND","HND","LND","PDR_percent","energy_per_delivered_j"]
scenarios=("zero_extra","moderate_extra","high_extra")
for scenario in scenarios:
 for a,b in (("C3","C1"),):
  ids=sorted({s for sc,m,s in data if (sc,m)==(scenario,a) and (scenario,b,s) in data})
  if len(ids)<3:continue
  for key in metrics:
   x=np.array([data[(scenario,a,i)][key] for i in ids])
   y=np.array([data[(scenario,b,i)][key] for i in ids])
   d=x-y
   ci=float(t.ppf(.975,len(ids)-1)*np.std(d,ddof=1)/np.sqrt(len(ids)))
   rows.append({"contrast":f"{scenario}: C3-C1","metric":key,"n":len(ids),"a_mean":float(x.mean()),"b_mean":float(y.mean()),"mean_diff":float(d.mean()),"CI_low":float(d.mean()-ci),"CI_high":float(d.mean()+ci),"p_raw":float(ttest_rel(x,y).pvalue)})
for scenario in scenarios[1:]:
 for mode in ("C1","C3"):
  ids=sorted({s for sc,m,s in data if (sc,m)==(scenario,mode) and ("zero_extra",mode,s) in data})
  if len(ids)<3:continue
  for key in metrics:
   x=np.array([data[(scenario,mode,i)][key] for i in ids])
   y=np.array([data[("zero_extra",mode,i)][key] for i in ids])
   d=x-y
   ci=float(t.ppf(.975,len(ids)-1)*np.std(d,ddof=1)/np.sqrt(len(ids)))
   rows.append({"contrast":f"{mode}: {scenario}-zero_extra","metric":key,"n":len(ids),"a_mean":float(x.mean()),"b_mean":float(y.mean()),"mean_diff":float(d.mean()),"CI_low":float(d.mean()-ci),"CI_high":float(d.mean()+ci),"p_raw":float(ttest_rel(x,y).pvalue)})
rows.sort(key=lambda r:r["p_raw"])
p=0.
for i,r in enumerate(rows):
 p=max(p,min(1.0,r["p_raw"]*(len(rows)-i)));r["p_holm"]=p
if rows:
 with (BASE/"paired_results.csv").open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({"completed":len(data),"planned":60,"contrasts":len(rows),"not_calibrated":True,"scope":"node-state full network reruns using scenario assumed energy costs, not calibrated hardware"}))
