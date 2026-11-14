"""Three-node context broadcast comparison: 0/13/25/50 B per exchange.
Pure transport experiment; not original network or source reconstruction.
"""
from pathlib import Path
import re,json,csv,subprocess
BASE=Path(__file__).resolve().parent
COOJA=Path.home()/"Research/contiki-ng/tools/cooja"
SEEDS=(123456,942,271828,35185,70017)
records=[]
for seed in SEEDS:
 dest=BASE/"cooja"/str(seed);dest.mkdir(parents=True,exist_ok=True)
 path=dest/"result.json"
 if path.exists():
  try:
   row=json.loads(path.read_text())
   if row["passed"]:records.extend(row["mode_rows"]);continue
  except Exception:pass
 conf=dest/"trial.csc"
 conf.write_text((BASE/"context_trial.csc").read_text().replace("<randomseed>123456</randomseed>",f"<randomseed>{seed}</randomseed>"))
 p=subprocess.run(["./gradlew","run",f"--args=--no-gui --autostart --logdir {dest/'logs'} {conf}"],
                  cwd=COOJA,text=True,capture_output=True,timeout=105)
 (dest/"run.log").write_text(p.stdout+"\n"+p.stderr)
 if p.returncode or "TEST OK" not in p.stdout+p.stderr:
  print("FAIL",seed,p.returncode,p.stderr[-250:],flush=True);continue
 text=(dest/"logs/COOJA.testlog").read_text()
 mode_rows=[]
 for mode,expected in enumerate((0,13,25,50)):
  def count(pattern):return len(re.findall(pattern,text))
  tx=count(rf"CONTEXT_TX mode={mode} second=")
  rx=count(rf"CONTEXT_RX role=3 mode={mode} second=")
  reports=count(rf"REPORT_TX source=(?:2|3) mode={mode} second=")
  arrived=count(rf"REPORT_RX source=(?:2|3) mode={mode} second=")
  mode_rows.append({"seed":seed,"mode":mode,"application_context_bytes":expected,
         "context_tx":tx,"context_rx":rx,"report_tx":reports,"report_rx":arrived,
         "context_delivery_ratio":rx/tx if tx else None,
         "report_delivery_ratio":arrived/reports if reports else None})
 passed=all((row["context_tx"]>0 and row["context_rx"]>0) if row["mode"]>0 else row["context_tx"]==0 for row in mode_rows)
 (path).write_text(json.dumps({"seed":seed,"passed":passed,"mode_rows":mode_rows},indent=2)+"\n")
 print("CASE",seed,"PASSED",passed,[(x['mode'],x['context_tx'],x['context_rx']) for x in mode_rows],flush=True)
 if passed:records.extend(mode_rows)
 with (BASE/"cooja_results.csv").open("w",newline="") as f:
  if records:
   w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 (BASE/"cooja_progress.json").write_text(json.dumps({"runs_passed":len(records)//4,"runs_planned":len(SEEDS),"scope":"3-node synthetic context transport; not 100-node original; no battery calibration"},indent=2)+"\n")
