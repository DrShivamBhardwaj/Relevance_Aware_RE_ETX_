"""Paired 2×2 Cooja transport/parent-policy diagnostic.

Routing option: fixed direct vs limited 3-node beacon-based RE-ETX proxy.
Payload option: 4000 bits vs relevance-adaptive safeguarded 1000..4000 bits.
These controlled simulations do not implement the full 100-node manuscript,
measured battery remaining, original sensing, or independent physical trial.
"""
import csv,json,re,subprocess
from pathlib import Path
BASE=Path(__file__).resolve().parent
COOJA=Path.home()/"Research/contiki-ng/tools/cooja"
OUT=BASE/"factorial"
OUT.mkdir(exist_ok=True)
SEEDS=(123456,942,271828)
CONFIGS={
 "adaptive_reetx":"route_probe_multihop.csc",
 "fixed_reetx":"route_fixed_reetx.csc",
 "adaptive_direct":"route_adaptive_direct.csc",
 "fixed_direct":"route_probe_fixed_direct.csc",
}
rows=[]
for mode,filename in CONFIGS.items():
 for seed in SEEDS:
  case=OUT/mode/str(seed)
  case.mkdir(parents=True,exist_ok=True)
  p=case/"result.json"
  if p.is_file():
   try:
    x=json.loads(p.read_text())
    if x.get("passed"):rows.append(x);continue
   except Exception:pass
  content=(BASE/filename).read_text().replace("<randomseed>123456</randomseed>",f"<randomseed>{seed}</randomseed>")
  conf=case/"test.csc";conf.write_text(content)
  cmd=["./gradlew","run","--args=--no-gui --autostart --logdir "+str(case/"logs")+" "+str(conf)]
  try:
   run=subprocess.run(cmd,cwd=COOJA,capture_output=True,text=True,timeout=100)
   (case/"runner.log").write_text(run.stdout+"\n"+run.stderr)
   if run.returncode or "TEST OK" not in run.stdout+run.stderr:
    raise RuntimeError("Cooja did not report TEST OK, exit "+str(run.returncode))
   trace=(case/"logs/COOJA.testlog").read_text()
   def n(pattern):return len(re.findall(pattern,trace))
   attempted=n(r"PAPER_PARENT source=3 ")
   delivered=n(r"PAPER_RX_COMPLETE src=3 ")
   s2attempted=n(r"PAPER_PARENT source=2 ")
   s2delivered=n(r"PAPER_RX_COMPLETE src=2 ")
   parents=n(r"PAPER_PARENT source=3 .*parent=2 ")
   payloads=[int(z) for z in re.findall(r"PAPER_PARENT source=3 .*payload_bits=(\d+)",trace)]
   if not attempted or not s2attempted:raise RuntimeError("No source traffic")
   result={"mode":mode,"seed":seed,"passed":True,
      "source3_attempted":attempted,"source3_delivered":delivered,
      "source2_attempted":s2attempted,"source2_delivered":s2delivered,
      "source3_relay_parent_choices":parents,
      "source3_parent2_fraction":parents/attempted,
      "source3_PDR_application":delivered/attempted,
      "source2_PDR_application":s2delivered/s2attempted,
      "source3_mean_application_bits":sum(payloads)/len(payloads),
      "forwarded_fragments":n(r"PAPER_RELAY src=3 ")}
   p.write_text(json.dumps(result,indent=2)+"\n")
   rows.append(result)
   print("PASS",mode,seed,delivered,attempted,flush=True)
  except Exception as e:
   (case/"error.txt").write_text(repr(e))
   print("FAIL",mode,seed,str(e),flush=True)
  with (OUT/"results.csv").open("w",newline="") as f:
   if rows:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  (OUT/"progress.json").write_text(json.dumps({"completed":len(rows),"planned":len(SEEDS)*len(CONFIGS),
      "scope":"three-node Cooja synthetic sensing and beacon-ETX proxy only"},indent=2)+"\n")
