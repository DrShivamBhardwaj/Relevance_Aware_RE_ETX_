"""Reviewer M1: 100-node C3 extra context-energy charge, paired archived seeds.

Experiment model: each live node broadcasts one CONTEXT_BITS update to all
currently live nodes within 20 m once per simulation round. Charges source
TX at furthest neighbour and per-neighbour RX into actual node battery.
No MAC framing/retries, and spatial sensing remains centrally available:
this is a sensitivity/break-even model, NOT deployed distributed sensing.

C1 and C5 baselines are original archive, not charged for unused context.
"""
from pathlib import Path
import csv, json, os, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/"context_only_battery"
OUT.mkdir(exist_ok=True)
SEEDS=[11,23,42,67,101,137,173,211,257,307]
BITS=[100,200,500,1000,2000,4000]
KEYS={"FND":"FND","HND":"HND","LND":"LND",
      "PDR (%)":"pdr_percent","Average delay":"delay_ms",
      "Energy/delivered message":"energy_per_delivered_j",
      "Review control energy J":"control_energy_j",
      "Review sensing energy J":"sensing_energy_j",
      "Review CPU energy J":"cpu_energy_j",
      "Review idle energy J":"idle_energy_j",
      "Review ACK energy J":"ack_energy_j"}
def parse(output):
 data={}
 for label,key in KEYS.items():
  m=re.search(r"^"+re.escape(label)+r"\s*:\s*([-+\d.eE]+)",output,re.M)
  if not m:raise ValueError("Missing metric: "+label)
  data[key]=float(m.group(1))
 return data
def progress():
 found=[]
 for f in OUT.glob("context_*_seed*.json"):
  try:
   a=json.loads(f.read_text())
   if a["passed"]:found.append(a)
  except Exception:pass
 found.sort(key=lambda x:(x["context_bits"],x["seed"]))
 if found:
  fields=["context_bits","seed","FND","HND","LND","pdr_percent","delay_ms",
          "energy_per_delivered_j","control_energy_j","sensing_energy_j",
          "cpu_energy_j","idle_energy_j","ack_energy_j"]
  with (OUT/"completed.csv").open("w",newline="") as h:
   w=csv.DictWriter(h,fieldnames=fields,extrasaction="ignore")
   w.writeheader();w.writerows(found)
 (OUT/"progress.json").write_text(json.dumps({"completed":len(found),"planned":len(SEEDS)*len(BITS),
     "scope":"C3-only ideal-one-hop per-neighbour context cost charged to 100-node simulator batteries",
     "distributed_context_delivery_verified":False,
     "independent_physical_calibration":False},indent=2)+"\n")
for bits in BITS:
 for seed in SEEDS:
  target=OUT/f"context_{bits}_seed{seed}.json"
  if target.is_file():
   try:
    if json.loads(target.read_text())["passed"]:continue
   except Exception:pass
  wd=OUT/"workdirs"/f"context_{bits}_seed{seed}"
  (wd/"results").mkdir(parents=True,exist_ok=True)
  env=dict(os.environ,PYTHONPATH=str(ROOT),EXPERIMENT_MODE="C3",
           SEMANTIC_SEED=str(seed),REVIEW_CONTEXT_BITS=str(bits),
           REVIEW_ROUTING_BITS="0",REVIEW_SENSING_UJ="0",REVIEW_CPU_UJ="0",
           REVIEW_IDLE_UJ="0",REVIEW_ACK_BITS="0",REVIEW_GOSSIP_RADIUS_M="20")
  proc=subprocess.run([sys.executable,str(ROOT/"run_semantic_re_etx.py")],
      cwd=wd,capture_output=True,text=True,env=env,timeout=1200)
  (wd/"run.log").write_text(proc.stdout+"\n"+proc.stderr)
  if proc.returncode:
   print("FAIL",bits,seed,proc.returncode,proc.stderr[-240:],flush=True)
   (OUT/f"context_{bits}_seed{seed}.error").write_text(proc.stderr[-1000:])
  else:
   result={"context_bits":bits,"seed":seed,"passed":True,
      "hardware_equivalent":False,**parse(proc.stdout)}
   target.write_text(json.dumps(result,indent=2)+"\n")
   print("PASS",bits,seed,result["LND"],flush=True)
  progress()
progress()
