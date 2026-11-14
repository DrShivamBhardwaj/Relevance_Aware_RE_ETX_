"""Reviewer M5: matched event traffic timing in original simulator.

Counterfactual pairs must share seed, source, round AND both delivery success.
Unmatched per-report observations cannot be treated as independent trials.
All lag times exclude external sensing periods; this is not true AoI or
physical event-onset staleness. Statistical unit = seed (n=10 per profile).
"""
from pathlib import Path
from collections import defaultdict,Counter
from scipy.stats import ttest_1samp,t
import pandas as pd,numpy as np,csv,json
BASE=Path(__file__).resolve().parent
SEEDS=(11,23,42,67,101,137,173,211,257,307)
MODES=("C3","C5")
PROFILES=("shallow","medium","deep")
PER_SEED=[]
DISTRIBUTIONS=[]
match_per_seed=[]
for profile in PROFILES:
 for mode in MODES:
  for seed in SEEDS:
   file=BASE/"traces"/f"{profile}_{mode}_seed{seed}.csv"
   if not file.is_file():raise SystemExit(f"MISSING_TRACE {file}")
   d=pd.read_csv(file)
   d["seed"]=seed;d["profile"]=profile;d["mode"]=mode
   good=d[d.success==1]
   for metric in ["route_hops","within_round_service_lag_s","event_to_delivery_channel_time_only_s"]:
    PER_SEED.append({"profile":profile,"mode":mode,"seed":seed,"metric":metric,
                     "n_event_attempted":len(d),"n_event_delivered":len(good),
                     "mean":float((good if metric!="route_hops" else d)[metric].mean())})
   for hops,n in d.route_hops.value_counts().items():
    DISTRIBUTIONS.append({"profile":profile,"mode":mode,"seed":seed,"hops":int(hops),
                         "event_reports_with_hops":int(n)})
 for seed in SEEDS:
  df={}
  for mode in MODES:
   df[mode]=pd.read_csv(BASE/"traces"/f"{profile}_{mode}_seed{seed}.csv")
  a=df["C3"];b=df["C5"]
  a=a[a.success==1].set_index(["round","source"])
  b=b[b.success==1].set_index(["round","source"])
  joined=a.join(b,lsuffix="_c3",rsuffix="_c5",how="inner")
  if joined.empty:raise SystemExit(f"NO_MATCHED_EVENTS {profile} {seed}")
  age_equal=joined.event_onset_round_c3.eq(joined.event_onset_round_c5)
  if not age_equal.all():raise SystemExit(f"EVENT_ONSET_MISMATCH {profile} {seed}")
  for metric in ("route_hops","within_round_service_lag_s","event_to_delivery_channel_time_only_s"):
   diff=joined[f"{metric}_c3"]-joined[f"{metric}_c5"]
   match_per_seed.append({"profile":profile,"seed":seed,"metric":metric,
     "matched_both_delivered_events":len(joined),
     "seed_mean_C3_minus_C5":float(diff.mean()),
     "seed_median_C3_minus_C5":float(diff.median())})
pd.DataFrame(PER_SEED).to_csv(BASE/"event_timing_by_seed.csv",index=False)
pd.DataFrame(DISTRIBUTIONS).to_csv(BASE/"event_hop_distributions.csv",index=False)
df=pd.DataFrame(match_per_seed)
df.to_csv(BASE/"matched_report_differences_by_seed.csv",index=False)
rows=[]
for (profile,metric),group in df.groupby(["profile","metric"]):
 differences=group["seed_mean_C3_minus_C5"].to_numpy(dtype=float)
 n=len(differences)
 if n!=10:raise SystemExit(f"EXPECTED_10_PAIRED_SEEDS: {profile} {metric}, GOT {n}")
 avg=float(np.mean(differences))
 se=float(np.std(differences,ddof=1)/np.sqrt(n))
 z=ttest_1samp(differences,0.0)
 half=float(t.ppf(.975,n-1)*se)
 rows.append({"profile":profile,"metric":metric,"n_paired_seeds":n,
  "mean_C3_minus_C5":avg,
  "CI95_lower":avg-half,"CI95_upper":avg+half,
  "p_raw":float(z.pvalue),"matched_both_delivered_events":int(group.matched_both_delivered_events.sum())})
rows.sort(key=lambda d:d["p_raw"])
prev=0
for i,d in enumerate(rows):
 prev=max(prev,min(1.0,d["p_raw"]*(len(rows)-i)))
 d["p_holm"]=prev
with (BASE/"event_timing_paired_tests.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
plot=pd.DataFrame(PER_SEED)
aggregates=[]
for (profile,mode,metric),g in plot.groupby(["profile","mode","metric"]):
 x=g["mean"].to_numpy(float)
 avg=float(x.mean())
 se=float(x.std(ddof=1)/np.sqrt(len(x)))
 half=float(t.ppf(.975,len(x)-1)*se)
 aggregates.append({"profile":profile,"mode":mode,"metric":metric,
    "n_seeds":len(x),"mean_of_seed_means":avg,
    "CI95_lower":avg-half,"CI95_upper":avg+half})
pd.DataFrame(aggregates).to_csv(BASE/"event_timing_summary.csv",index=False)
record={"completed_original_simulator_runs":60,
 "source":"original simulator; event labels only in offline logging",
 "all_10_matched_seeds_per_topology":True,
 "match_condition":"same profile, same seed, same source, same round, both C3/C5 reports delivered",
 "time_units":"within-round seconds and cumulative channel-occupied seconds ONLY",
 "physical_event_staleness_measured":False,
 "application_reconstruction_proven":False,
 "interpretation_limit":"External inter-round sensing periods are absent; cumulative channel occupancy must not be renamed wall-clock event-to-sink latency or full AoI.",
 "experimental_profiles":{"shallow":1.483,"medium":2.910,"deep":4.929},
 "paired_seed_contrasts":rows,
 "non_independent_report_statistics":"packet rows are descriptive only, seed is inference unit"}
(BASE/"event_timing_audit.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps({"completed":60,"paired_seed_contrasts":len(rows),
 "sig_Holm":sum(float(r["p_holm"])<.05 for r in rows),
 "staleness_wallclock":False},indent=2))
try:
 import matplotlib
 matplotlib.use("Agg")
 import matplotlib.pyplot as plt
 for metric,label,filename in [
    ("route_hops","Mean selected hops for event-active reports","event_route_hops_by_depth.png"),
    ("within_round_service_lag_s","Event-report service lag (s, modelled channel schedule)","event_service_lag_by_depth.png"),
    ("event_to_delivery_channel_time_only_s","Event onset to delivery: channel-occupancy proxy (s)","event_channel_occupancy_proxy.png")
 ]:
  fig,ax=plt.subplots(figsize=(8,4.6))
  for mode in MODES:
   a=[next(x for x in aggregates if x["profile"]==profile and x["mode"]==mode and x["metric"]==metric) for profile in PROFILES]
   y=[r["mean_of_seed_means"] for r in a]
   errlo=[v["mean_of_seed_means"]-v["CI95_lower"] for v in a]
   errhi=[v["CI95_upper"]-v["mean_of_seed_means"] for v in a]
   ax.errorbar(PROFILES,y,yerr=[errlo,errhi],marker="o",capsize=4,label=mode)
  ax.set_xlabel("Calibrated initial route-depth profile")
  ax.set_ylabel(label)
  ax.legend()
  ax.grid(alpha=.25)
  fig.tight_layout()
  fig.savefig(BASE/filename,dpi=300)
  plt.close(fig)
except ImportError as e:
 print("PLOTS_UNAVAILABLE",repr(e))
