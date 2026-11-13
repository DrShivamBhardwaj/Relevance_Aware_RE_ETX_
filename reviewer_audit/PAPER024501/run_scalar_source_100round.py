"""New-codec receiver accuracy under actual modeled delivery (not hardware).

Modes C1,C3,C5,C6, ten matched seeds, 100 rounds; channel and topology taken
from project simulator. Explicit DCT/hold decoder assumptions are new.
"""
from pathlib import Path
import os,sys,json,csv,subprocess,re
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/"receiver_scalar_100r"
OUT.mkdir(exist_ok=True)
SEEDS=[11,23,42,67,101,137,173,211,257,307]
MODES=["C1","C3","C5","C6"]
KEYS={"Scalar receiver rmse":"rmse","Scalar receiver zero_rmse":"zero_rmse","Scalar receiver event_f1":"event_f1","Scalar receiver precision":"precision","Scalar receiver recall":"recall","Scalar receiver tp":"tp","Scalar receiver fp":"fp","Scalar receiver fn":"fn","Scalar receiver reports":"reports","Scalar receiver received":"received","PDR (%)":"pdr_percent"}
def parse(out):
 values={}
 for label,key in KEYS.items():
  match=re.search("^"+re.escape(label)+r"\s*:\s*([-+0-9.eE]+)",out,re.M)
  if not match:raise ValueError("Missing "+label)
  values[key]=float(match.group(1))
 return values
def save():
 data=[]
 for p in OUT.glob("*_seed*.json"):
  try:
   d=json.loads(p.read_text())
   if d.get("passed"):data.append(d)
  except Exception:pass
 data.sort(key=lambda r:(r["mode"],r["seed"]))
 with (OUT/"completed.csv").open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=["mode","seed",*KEYS.values()],extrasaction="ignore");w.writeheader();w.writerows(data)
 (OUT/"progress.json").write_text(json.dumps({"completed":len(data),"planned":len(MODES)*len(SEEDS),"not_original_codec":True,"scope":"original scalar sensing source; explicitly added Q8.8 receiver, not manuscript codec","assumed_codec":"Q8.8 fixed-point source scalar in first 16 bits, zero padding, last-value hold","rounds_per_run":100},indent=2)+"\n")
for mode in MODES:
 for seed in SEEDS:
  result=OUT/f"{mode}_seed{seed}.json"
  if result.exists():
   try:
    if json.loads(result.read_text()).get("passed"):continue
   except Exception:pass
  wd=OUT/"workdirs"/f"{mode}_seed{seed}"
  (wd/"results").mkdir(parents=True,exist_ok=True)
  env=os.environ.copy()
  env.update({"EXPERIMENT_MODE":mode,"SEMANTIC_SEED":str(seed),"REVIEW_SCALAR_SOURCE":"1","REVIEW_MAX_ROUNDS":"100","PYTHONPATH":str(ROOT)})
  try:
   p=subprocess.run([sys.executable,str(ROOT/"run_semantic_re_etx.py")],cwd=wd,env=env,capture_output=True,text=True,timeout=1200)
   (wd/"run.log").write_text(p.stdout+"\n"+p.stderr)
   if p.returncode:raise RuntimeError(f"exit={p.returncode}, stderr={p.stderr[-300:]}")
   result.write_text(json.dumps({"mode":mode,"seed":seed,"passed":True,**parse(p.stdout)},indent=2)+"\n")
   print("PASS",mode,seed,flush=True)
  except Exception as e:
   (OUT/f"{mode}_seed{seed}.error").write_text(repr(e))
   print("FAIL",mode,seed,repr(e),flush=True)
  save()
save()
