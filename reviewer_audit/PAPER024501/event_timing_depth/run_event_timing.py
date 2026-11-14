"""Actual archived simulator C3/C5 × 3 route-depth profiles × 10 seeds.
Outputs per-attempt event-labeled routing delays without changing results.
'event_to_delivery_channel_time_only_s' excludes external sensing period.
"""
from pathlib import Path
import os,json,subprocess,csv,sys,re
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[2]
PROFILES={"shallow":(150,200,25,1744),"medium":(400,450,45,1648),"deep":(600,650,60,1568)}
SEEDS=(11,23,42,67,101,137,173,211,257,307)
ROWS=[]
for prof,(h,bs,r,b) in PROFILES.items():
 for mode in ("C3","C5"):
  for seed in SEEDS:
   name=f"{prof}_{mode}_seed{seed}"
   p=BASE/f"{name}.json"
   if p.exists():
    try:
     d=json.loads(p.read_text())
     if d.get("passed"):ROWS.append(d);continue
    except ValueError:pass
   work=BASE/"workdirs"/name
   work.mkdir(parents=True,exist_ok=True)
   (work/"results").mkdir(exist_ok=True)
   trace=BASE/"traces"/f"{name}.csv"
   env=os.environ.copy()
   env.update({"SEMANTIC_SEED":str(seed),"EXPERIMENT_MODE":mode,
    "NUM_NODES":"100","AREA_WIDTH_M":"100","AREA_HEIGHT_M":str(h),
    "BS_X_M":"50","BS_Y_M":str(bs),"MAX_SENSOR_LINK_DISTANCE_M":str(r),
    "EQUAL_BUDGET_PAYLOAD_BITS":str(b),"REVIEW_EVENT_TRACE_PATH":str(trace.absolute()),
    "PYTHONPATH":str(ROOT)})
   run=subprocess.run([sys.executable,str(ROOT/"run_semantic_re_etx.py")],
       cwd=work,env=env,capture_output=True,text=True,timeout=1500)
   (work/"run.log").write_text(run.stdout+"\n"+run.stderr)
   if run.returncode or not trace.is_file() or "All dynamic minimum-ETX checks PASSED." not in run.stdout:
    (BASE/f"{name}.error").write_text(f"returncode={run.returncode};\n"+run.stderr[-500:]+run.stdout[-500:])
    print("FAIL",name,flush=True);continue
   with trace.open(newline="") as f:
    q=list(csv.DictReader(f))
   succ=[v for v in q if v["success"]=="1"]
   ages=[float(v["event_to_delivery_channel_time_only_s"]) for v in succ]
   within=[float(v["within_round_service_lag_s"]) for v in succ]
   hops=[int(v["route_hops"]) for v in q]
   row={"profile":prof,"mode":mode,"seed":seed,"passed":True,
     "event_attempts":len(q),"event_delivered":len(succ),
     "event_report_PDR":len(succ)/len(q) if q else None,
     "mean_route_hops_on_event_reports":sum(hops)/len(hops) if hops else None,
     "mean_event_report_service_s":sum(within)/len(within) if within else None,
     "mean_event_onset_channel_time_only_s":sum(ages)/len(ages) if ages else None,
     "origin":"synthetic spatial event threshold 0.5",
     "limitation":"Not real elapsed event staleness; excludes inter-round sensing intervals"}
   p.write_text(json.dumps(row,indent=2)+"\n")
   ROWS.append(row)
   print("PASS",name,"events",len(q),"delivered",len(succ),flush=True)
   with (BASE/"completed.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(ROWS[0]));w.writeheader();w.writerows(ROWS)
   (BASE/"progress.json").write_text(json.dumps({"completed":len(ROWS),"planned":60,
          "validated_protocol":"original 100-node simulator event trace only",
          "staleness_physical_seconds_established":False},indent=2)+"\n")
