"""Repeat physical-frame Cooja diagnostic under controlled UDGM reception.

NOT full PAPER024501 RE-ETX validation; direct NullNet/CSMA only.
A report counts delivered only with all fragments received at sink.
"""
import json,re,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=Path(__file__).resolve().parent/"cooja_transport"
COOJA=Path(os.environ.get("CONTIKI_NG",str(Path.home()/"Research/contiki-ng")))/"tools/cooja"
TEMPLATE=(BASE/"paper024501-transport.csc").read_text()
experiments=[(seed,quality) for seed in (11,42,101) for quality in (1.0,0.95,0.80,0.50,0.20)]
results=[]
for seed,quality in experiments:
 case=BASE/"campaign"/f"seed{seed}_quality{str(quality).replace('.','p')}"
 case.mkdir(parents=True,exist_ok=True)
 summary=case/"summary.json"
 if summary.exists():
  try:
   rec=json.loads(summary.read_text())
   if rec.get("simulator_exit")==0:results.append(rec);continue
  except Exception:pass
 sim=TEMPLATE.replace("<randomseed>123456</randomseed>",f"<randomseed>{seed}</randomseed>")
 sim=sim.replace("<success_ratio_tx>1.0</success_ratio_tx>",f"<success_ratio_tx>{quality}</success_ratio_tx>")
 sim=sim.replace("<success_ratio_rx>1.0</success_ratio_rx>",f"<success_ratio_rx>{quality}</success_ratio_rx>")
 csc=case/"test.csc";csc.write_text(sim)
 command=["./gradlew","run","--args=--no-gui --autostart --logdir "+str(case/"logs")+" "+str(csc)]
 try:
  r=subprocess.run(command,cwd=COOJA,capture_output=True,text=True,timeout=180)
  (case/"console.log").write_text(r.stdout+"\n"+r.stderr)
  if r.returncode:raise RuntimeError("cooja build/run rc "+str(r.returncode))
  t=(case/"logs/COOJA.testlog").read_text()
  tx={(int(a),int(b)) for a,b in re.findall(r"PAPER024501_TX source=(\d+) seq=(\d+)",t)}
  rx={(int(a),int(b)) for a,b in re.findall(r"PAPER024501_RX_COMPLETE source=(\d+) seq=(\d+)",t)}
  rec={"seed":seed,"radio_success_parameter_tx":quality,"radio_success_parameter_rx":quality,
       "simulator_exit":r.returncode,"reports_transmitted":len(tx),"reports_reassembled":len(rx),
       "complete_report_ratio":len(rx)/len(tx) if tx else None,
       "scope":"nullnet direct 3 nodes; guarded source bit rule; application fragmentation/reassembly"}
  summary.write_text(json.dumps(rec,indent=2)+"\n")
  results.append(rec)
  print("PASS",seed,quality,len(tx),len(rx),flush=True)
 except Exception as e:
  (case/"error.txt").write_text(repr(e))
  print("FAIL",seed,quality,repr(e),flush=True)
 (BASE/"campaign_progress.json").write_text(json.dumps({"completed":len(results),"planned":len(experiments)},indent=2)+"\n")
(BASE/"campaign_results.json").write_text(json.dumps(results,indent=2)+"\n")
