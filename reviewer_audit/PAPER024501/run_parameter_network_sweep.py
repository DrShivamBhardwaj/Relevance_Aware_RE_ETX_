"""Seed-level, one-factor-at-a-time C3 network sensitivity; original untouched.

Resumes individual runs by checking complete JSON summaries.
The non-default parameters are used ONLY on this review branch.
Pilot/archived datasets are not changed.
"""
import csv, json, os, pathlib, re, subprocess, sys, time
ROOT=pathlib.Path(__file__).resolve().parents[2]
BASE=pathlib.Path(__file__).resolve().parent
OUT=BASE/"network_parameter_sweep"
OUT.mkdir(exist_ok=True)
PY=sys.executable
SEEDS=[11,23,42,67,101,137,173,211,257,307]
CONFIGS=[
 ("baseline",{}),
 ("temporal_040",{"REVIEW_TEMPORAL_WEIGHT":"0.4"}),
 ("temporal_080",{"REVIEW_TEMPORAL_WEIGHT":"0.8"}),
 ("low_threshold_040",{"REVIEW_LOW_THRESHOLD":"0.4"}),
 ("low_threshold_060",{"REVIEW_LOW_THRESHOLD":"0.6"}),
 ("energy_weight_010",{"REVIEW_ENERGY_WEIGHT":"0.1"}),
 ("energy_weight_050",{"REVIEW_ENERGY_WEIGHT":"0.5"}),
 ("high_threshold_075",{"REVIEW_HIGH_THRESHOLD":"0.75"}),
 ("high_threshold_095",{"REVIEW_HIGH_THRESHOLD":"0.95"}),
]
LABELS={"FND":"FND","HND":"HND","LND":"LND","PDR (%)":"pdr_percent","Average delay":"delay_ms","Energy/delivered message":"energy_per_delivered_j"}
def parse(t):
 d={}
 for label,key in LABELS.items():
  m=re.search(r"^"+re.escape(label)+r"\s*:\s*([-+0-9.eE]+)",t,re.M)
  if m:d[key]=float(m.group(1))
 if len(d)!=len(LABELS):raise ValueError("Missing summary labels: "+str(d))
 return d
def run(name,extra,seed):
 target=OUT/(name+"_seed"+str(seed)+".json")
 if target.exists():
  try:
   if json.loads(target.read_text()).get("completed"):return
  except ValueError:pass
 wd=OUT/"workdirs"/(name+"_seed"+str(seed))
 (wd/"results").mkdir(parents=True,exist_ok=True)
 env=os.environ.copy()
 env.update({"PYTHONPATH":str(ROOT),"EXPERIMENT_MODE":"C3","SEMANTIC_SEED":str(seed),**extra})
 cmd=[PY,str(ROOT/"run_semantic_re_etx.py")]
 try:
  p=subprocess.run(cmd,cwd=wd,env=env,capture_output=True,text=True,timeout=1500)
  (wd/"stdout.log").write_text(p.stdout+"\n"+p.stderr)
  if p.returncode:raise RuntimeError("exit="+str(p.returncode))
  record={"variant":name,"seed":seed,"parameters":extra,"completed":True,**parse(p.stdout)}
  target.write_text(json.dumps(record,indent=2)+"\n")
  print("PASS",name,seed,flush=True)
 except Exception as e:
  (OUT/(name+"_seed"+str(seed)+".error")).write_text(repr(e))
  print("FAILED",name,seed,str(e),flush=True)
def main():
 for name,extra in CONFIGS:
  for seed in SEEDS:
   run(name,extra,seed)
   # keep a complete checkpoint after every run
   records=[]
   for p in OUT.glob("*_seed*.json"):
    try:
     d=json.loads(p.read_text())
     if d.get("completed"):records.append(d)
    except ValueError:pass
   records.sort(key=lambda d:(d["variant"],d["seed"]))
   with (OUT/"completed_run_summary.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["variant","seed","FND","HND","LND","pdr_percent","delay_ms","energy_per_delivered_j"],extrasaction="ignore")
    w.writeheader();w.writerows(records)
   (OUT/"progress.json").write_text(json.dumps({"completed":len(records),"total":len(CONFIGS)*len(SEEDS),"failed_files":len(list(OUT.glob("*.error"))),"interpretation":"Network-level reviewer sensitivity. Do not compare without statistical analysis and control for multiple tests."},indent=2)+"\n")
if __name__=="__main__":main()
