"""Paired seed analysis for reviewer M1 context-exchange diagnostics.

Every comparison is seed-paired to the archived original simulator (C1/C3/C5).
No new measurements/claims are written into the publication tables here.
Incomplete campaigns are summarised explicitly as provisional, never done.
"""
from pathlib import Path
import csv,json,statistics,math
import pandas as pd
from scipy.stats import t
BASE=Path(__file__).resolve().parent
ARCHIVE=pd.read_csv(BASE.parents[1]/"results/master_validation/statistics/control_multiseed_raw.csv")
MODES=["C1","C3","C5"]
METRICS=["FND","HND","LND","PDR_percent","energy_per_delivered_j"]
tables={}
for label,relpath in [("distributed_cache","distributed_context_100node"),
                      ("charged_broadcast_only","context_only_battery")]:
 folder=BASE/relpath
 path=folder/"completed.csv"
 if not path.exists():
  continue
 records=pd.read_csv(path)
 variable="variant" if label=="distributed_cache" else "context_bits"
 out=[]
 for name,group in records.groupby(variable):
  matched=group.set_index("seed")
  for ref_mode in MODES:
   comparison=ARCHIVE[ARCHIVE["mode"]==ref_mode].set_index("seed")
   for metric in METRICS:
    local_key=("pdr_percent" if metric=="PDR_percent" and label=="charged_broadcast_only" else metric)
    common=sorted(set(matched.index)&set(comparison.index))
    if len(common)<2:continue
    a=matched.loc[common,local_key].to_numpy(dtype=float)
    b=comparison.loc[common,metric].to_numpy(dtype=float)
    diff=a-b
    mean=float(diff.mean())
    half=float(t.ppf(0.975,len(common)-1)*diff.std(ddof=1)/math.sqrt(len(common)))
    out.append({"scenario":name,"reference":ref_mode,"metric":metric,
      "n_paired_seeds":len(common),"mean_scenario":float(a.mean()),"mean_reference":float(b.mean()),
      "mean_scenario_minus_reference":mean,"CI95_low":mean-half,"CI95_high":mean+half,
      "direction_unverified":len(common)<10})
 result=folder/"paired_vs_original.csv"
 if out:
  with result.open("w",newline="") as f:
   w=csv.DictWriter(f,fieldnames=list(out[0]))
   w.writeheader();w.writerows(out)
 p=json.loads((folder/"progress.json").read_text())
 tables[label]={"completed":p["completed"],"planned":p["planned"],
   "paired_contrasts_so_far":len(out),
   "completion_verified":p["completed"]==p["planned"],
   "note":"Independent simulator reruns; no source-decoder or physical wireless calibration."}
report={
 "kind":"PAPER024501 author-side reviewer M1 experimental audit",
 "datasets":tables,
 "original_code_path_modified_when_option_disabled":False,
 "original_source_decoder_validated":False,
 "fully_distributed_mac_phy_measured":False,
 "original_paper_equivalent_100node_hardware_validated":False,
 "physical_context_trial_458578":"PARTIAL serial logs, three-board whole-power",
 "physical_context_replication_458597":"FAILED instrumentation; raw current traces no phase-tagged context packets",
 "warning":"Do not infer physical lifetime or semantic reconstruction from synthetic/idealised neighbour context"
}
(BASE/"context_experiment_evidence_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(tables,indent=2))
