"""Restartable paired, scenario-based FULL NETWORK reruns.

Charges sensor, CPU, idle, context, routing and ACK costs into network node
batteries. All extra costs are explicit, uncalibrated scenarios, not measured
hardware currents. Per-seed source and initial topology stay matched.
"""
from pathlib import Path
import subprocess,sys,os,json,re,csv
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/"full_network_energy"
OUT.mkdir(exist_ok=True)
PY=sys.executable
SEEDS=[11,23,42,67,101,137,173,211,257,307]
MODELS={
 "zero_extra":{},
 "moderate_extra":{"REVIEW_SENSING_UJ":"10","REVIEW_CPU_UJ":"5","REVIEW_IDLE_UJ":"5","REVIEW_CONTEXT_BITS":"100","REVIEW_ROUTING_BITS":"64","REVIEW_ACK_BITS":"88"},
 "high_extra":{"REVIEW_SENSING_UJ":"100","REVIEW_CPU_UJ":"40","REVIEW_IDLE_UJ":"50","REVIEW_CONTEXT_BITS":"200","REVIEW_ROUTING_BITS":"128","REVIEW_ACK_BITS":"88"}
}
keys={"FND":"FND","HND":"HND","LND":"LND","PDR (%)":"PDR_percent","Energy/delivered message":"energy_per_delivered_j","Review sensing energy J":"sensing_j","Review CPU energy J":"cpu_j","Review idle energy J":"idle_j","Review control energy J":"control_j","Review ACK energy J":"ack_j"}
def extract(t):
 out={}
 for label,k in keys.items():
  m=re.search(r"^"+re.escape(label)+r"\s*:\s*([-+0-9.eE]+)",t,re.M)
  if not m:raise ValueError("Missing "+label)
  out[k]=float(m.group(1))
 return out
def save_progress():
 arr=[]
 for path in OUT.glob("*_seed*.json"):
  try:
   r=json.loads(path.read_text())
   if r.get("passed"):arr.append(r)
  except Exception:pass
 arr.sort(key=lambda x:(x["scenario"],x["mode"],x["seed"]))
 fields=["scenario","mode","seed",*keys.values()]
 with (OUT/"completed.csv").open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(arr)
 (OUT/"progress.json").write_text(json.dumps({"completed":len(arr),"planned":len(SEEDS)*len(MODELS)*2,"calibration":"UNVALIDATED SCENARIO ASSUMPTIONS","full_node_battery_state_rerun":True},indent=2)+"\n")
for scenario,costs in MODELS.items():
 for mode in ("C1","C3"):
  for seed in SEEDS:
   target=OUT/f"{scenario}_{mode}_seed{seed}.json"
   if target.exists():
    try:
     if json.loads(target.read_text()).get("passed"):continue
    except Exception:pass
   wd=OUT/"workdirs"/f"{scenario}_{mode}_seed{seed}"
   (wd/"results").mkdir(parents=True,exist_ok=True)
   env=os.environ.copy();env.update({"EXPERIMENT_MODE":mode,"SEMANTIC_SEED":str(seed),"PYTHONPATH":str(ROOT),**costs})
   try:
    proc=subprocess.run([PY,str(ROOT/"run_semantic_re_etx.py")],cwd=wd,env=env,timeout=1500,text=True,capture_output=True)
    (wd/"run.log").write_text(proc.stdout+"\n"+proc.stderr)
    if proc.returncode:raise RuntimeError(f"exit={proc.returncode}: {proc.stderr[-500:]}")
    target.write_text(json.dumps({"scenario":scenario,"mode":mode,"seed":seed,"passed":True,"assumptions":costs,**extract(proc.stdout)},indent=2)+"\n")
    print("PASS",scenario,mode,seed,flush=True)
   except Exception as e:
    (OUT/f"{scenario}_{mode}_seed{seed}.error").write_text(repr(e))
    print("FAIL",scenario,mode,seed,repr(e),flush=True)
   save_progress()
save_progress()
