"""Topology C3-vs-C5 sensitivity with paired inference; no staleness claims."""
from pathlib import Path
import csv,json
import numpy as np,pandas as pd
from scipy.stats import ttest_rel,t
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
data=pd.read_csv(ROOT/"results/master_validation/statistics/topology_sensitivity_raw.csv")
metrics=["HND","LND","PDR_percent","average_delay_ms","energy_per_delivered_j"]
rows=[]
for profile in sorted(data.profile.unique()):
 a=data[(data.profile==profile)&(data["mode"]=="C3")].set_index("seed")
 b=data[(data.profile==profile)&(data["mode"]=="C5")].set_index("seed")
 seeds=sorted(set(a.index)&set(b.index))
 if len(seeds)!=10:raise ValueError("Unmatched profile: "+profile)
 for key in metrics:
  x=a.loc[seeds,key].astype(float).to_numpy()
  y=b.loc[seeds,key].astype(float).to_numpy()
  dif=x-y
  p=float(ttest_rel(x,y).pvalue)
  half=float(t.ppf(.975,len(seeds)-1)*np.std(dif,ddof=1)/(len(seeds)**.5))
  rows.append({"profile":profile,"metric":key,"n_paired":len(seeds),"C3_mean":float(x.mean()),"C5_mean":float(y.mean()),"C3_minus_C5":float(dif.mean()),"ci95_lower":float(dif.mean()-half),"ci95_upper":float(dif.mean()+half),"p_raw":p,
               "initial_mean_hops":float(a["calibrated_initial_mean_hops"].mean())})
rows.sort(key=lambda x:x["p_raw"])
m=len(rows);q=0
for i,r in enumerate(rows):
 q=max(q,min(1.0,r["p_raw"]*(m-i)));r["p_holm"]=q
with (OUT/"topology_paired_mechanism_audit.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/"topology_mechanism_audit_meta.json").write_text(json.dumps({"contrasts":len(rows),"scope":"Topology-depth outcome association; NOT per-packet staleness","missing":"Source/event timestamps and receiver arrival times needed to establish staleness mechanism"},indent=2)+"\n")
print(json.dumps({"contrasts":len(rows),"significant_after_holm":sum(r["p_holm"]<.05 for r in rows),"staleness_measured":False}))
