"""Reproducible reviewer-only 100-node received-neighbour-context scenarios.

These tests *change* the original central-context assumption. Each source
broadcasts its own observation and each receiver's local neighbour cache
is updated only after a successful reception. The model charges actual
sender and receiver batteries, with an explicitly idealised broadcast PHY.
No reviewer or paper-equivalent deployment claim follows automatically.
"""
from pathlib import Path
import subprocess,os,re,json,csv,sys
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/"distributed_context_100node"
OUT.mkdir(exist_ok=True)
SEEDS=(11,23,42,67,101)
CASES=(("q100_13B",13,1.0),("q080_13B",13,0.8),
       ("q080_25B",25,0.8),("q080_50B",50,0.8))
PATTERNS={
 "FND":r"^FND\s*:\s*([-+.0-9eE]+)",
 "HND":r"^HND\s*:\s*([-+.0-9eE]+)",
 "LND":r"^LND\s*:\s*([-+.0-9eE]+)",
 "PDR_percent":r"^PDR \(%\)\s*:\s*([-+.0-9eE]+)",
 "delay_ms":r"^Average delay\s*:\s*([-+.0-9eE]+)",
 "energy_per_delivered_j":r"^Energy/delivered message\s*:\s*([-+.0-9eE]+)",
 "context_packets_sent":r"^Distributed context_packets_sent\s*:\s*([-+.0-9eE]+)",
 "context_receive_attempts":r"^Distributed context_receive_attempts\s*:\s*([-+.0-9eE]+)",
 "context_updates_received":r"^Distributed context_updates_received\s*:\s*([-+.0-9eE]+)",
 "context_rx_fraction":r"^Distributed context_rx_fraction\s*:\s*([-+.0-9eE]+)",
 "cached_context_age_rounds":r"^Distributed mean_cached_context_age_rounds\s*:\s*([-+.0-9eE]+)",
 "context_battery_energy_j":r"^Distributed total_context_battery_energy_J\s*:\s*([-+.0-9eE]+)"
}
def publish():
 found=[]
 for p in OUT.glob("*_seed*.json"):
  try:
   z=json.loads(p.read_text())
   if z["passed"]:found.append(z)
  except (ValueError,KeyError):pass
 found.sort(key=lambda z:(z["variant"],z["seed"]))
 if found:
  with (OUT/"completed.csv").open("w",newline="") as f:
   w=csv.DictWriter(f,fieldnames=list(found[0]),extrasaction="ignore")
   w.writeheader();w.writerows(found)
 (OUT/"progress.json").write_text(json.dumps({
  "completed":len(found),"planned":len(CASES)*len(SEEDS),
  "model":"100-node local receiver caches from independently received context packets",
  "scope":"independent per-neighbour packet erasures, no MAC contention, no physical code-equivalence",
  "all_configs":[x[0] for x in CASES]},indent=2)+"\n")
for label,bytes_n,q in CASES:
 for seed in SEEDS:
  saved=OUT/f"{label}_seed{seed}.json"
  if saved.exists():
   try:
    if json.loads(saved.read_text())["passed"]:continue
   except (KeyError,ValueError):pass
  wd=OUT/"workdirs"/f"{label}_seed{seed}"
  (wd/"results").mkdir(parents=True,exist_ok=True)
  env=os.environ.copy()
  env.update({"PYTHONPATH":str(ROOT),"EXPERIMENT_MODE":"C3",
      "SEMANTIC_SEED":str(seed),"REVIEW_DISTRIBUTED_CONTEXT":"1",
      "REVIEW_CONTEXT_BYTES":str(bytes_n),"REVIEW_CONTEXT_SUCCESS":str(q),
      "REVIEW_CONTEXT_BITS":"0","REVIEW_ROUTING_BITS":"0",
      "REVIEW_SENSING_UJ":"0","REVIEW_CPU_UJ":"0","REVIEW_IDLE_UJ":"0",
      "REVIEW_ACK_BITS":"0"})
  try:
   p=subprocess.run([sys.executable,str(ROOT/"run_semantic_re_etx.py")],
      cwd=wd,capture_output=True,text=True,env=env,timeout=1500)
   (wd/"stdout.log").write_text(p.stdout+"\n"+p.stderr)
   if p.returncode:raise RuntimeError(f"run failed: {p.returncode}: {p.stderr[-300:]}")
   data={}
   for key,pattern in PATTERNS.items():
    m=re.search(pattern,p.stdout,re.M)
    if not m:raise ValueError(f"missing {key}")
    data[key]=float(m.group(1))
   saved.write_text(json.dumps({"variant":label,"seed":seed,"context_bytes":bytes_n,
      "context_delivery_probability":q,"passed":True,**data},indent=2)+"\n")
   print("PASS",label,seed,"LND",data["LND"],"RX",data["context_rx_fraction"],flush=True)
  except Exception as e:
   (OUT/f"{label}_seed{seed}.error").write_text(repr(e))
   print("FAIL",label,seed,str(e),flush=True)
  publish()
publish()
