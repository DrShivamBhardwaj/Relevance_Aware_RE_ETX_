"""Paired comparisons: effect size, paired CI and family-wide Holm test."""
from pathlib import Path
import json,csv
import numpy as np
from scipy.stats import t,ttest_rel
BASE=Path(__file__).resolve().parent/"receiver_campaign_100r"
data={}
for f in BASE.glob("*_seed*.json"):
 try:
  r=json.loads(f.read_text())
  if r.get("passed"):data[(r["mode"],r["seed"])]=r
 except Exception:pass
rows=[]
for contrast in ("C3","C5","C6"):
 for benchmark in ("C1","C3"):
  if contrast==benchmark:continue
  seeds=sorted(k for m,k in data if m==contrast and (benchmark,k) in data)
  if len(seeds)<3:continue
  for metric in ("rmse","event_f1"):
   a=np.array([data[(contrast,k)][metric] for k in seeds])
   b=np.array([data[(benchmark,k)][metric] for k in seeds])
   delta=a-b
   ci=t.ppf(.975,len(seeds)-1)*delta.std(ddof=1)/np.sqrt(len(seeds))
   rows.append({"mode":contrast,"reference":benchmark,"metric":metric,"n_paired":len(seeds),"mean_mode":a.mean(),"mean_reference":b.mean(),"mean_diff":delta.mean(),"CI95_lower":delta.mean()-ci,"CI95_upper":delta.mean()+ci,"p_raw":ttest_rel(a,b).pvalue})
rows.sort(key=lambda r:r["p_raw"])
p=0
for i,r in enumerate(rows):
 p=max(p,min(1.0,r["p_raw"]*(len(rows)-i)));r["p_holm"]=p
if rows:
 with (BASE/"paired_results.csv").open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print(json.dumps({"valid_runs":len(data),"comparisons":len(rows),"warning":"New reference codec. Any benefit is codec-specific and simulator-only, not claimed for original paper"}))
