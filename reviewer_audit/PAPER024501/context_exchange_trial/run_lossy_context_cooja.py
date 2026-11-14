"""Controlled Cooja PHY reception sensitivity of real context transport.

A 3-node NullNet application exchanges 0/13/25/50-byte messages, at
different independent UDGM receive-success settings. This is NOT the
original 100-node RE-ETX/routing algorithm or hardware PHY calibration.
Individual packet counters are read from actual Cooja mote serial logs.
"""
from pathlib import Path
import subprocess,re,csv,json
BASE=Path(__file__).resolve().parent
OUT=BASE/"cooja_rx_sweep"
COOJA=Path.home()/"Research/contiki-ng/tools/cooja"
OUT.mkdir(exist_ok=True)
SEEDS=[123456,942,271828,35185,70017]
PRR=[0.60,0.80,1.00]
result=[]
for prr in PRR:
 for seed in SEEDS:
  case=OUT/f"rx_{int(prr*100)}_seed{seed}"
  case.mkdir(exist_ok=True)
  saved=case/"result.json"
  if saved.exists():
   try:
    d=json.loads(saved.read_text())
    if d.get("passed"):result.extend(d["mode_rows"]);continue
   except Exception:pass
  csc=(BASE/"context_trial.csc").read_text()
  assert "<success_ratio_rx>1.0</success_ratio_rx>" in csc
  csc=csc.replace("<success_ratio_rx>1.0</success_ratio_rx>",
                  f"<success_ratio_rx>{prr:.2f}</success_ratio_rx>")
  csc=csc.replace("<randomseed>123456</randomseed>",
                  f"<randomseed>{seed}</randomseed>")
  conf=case/"trial.csc";conf.write_text(csc)
  cmd=["./gradlew","run",f"--args=--no-gui --autostart --logdir {case/'logs'} {conf}"]
  try:
   proc=subprocess.run(cmd,cwd=COOJA,capture_output=True,text=True,timeout=130)
   (case/"cooja_runner.log").write_text(proc.stdout+"\n"+proc.stderr)
   if proc.returncode or "TEST OK" not in proc.stdout+proc.stderr:
    raise RuntimeError(f"runner returned {proc.returncode} or no TEST OK")
   trace=(case/"logs/COOJA.testlog").read_text(errors="replace")
   rows=[]
   for mode,bytes_n in enumerate((0,13,25,50)):
    ct=lambda pattern: len(re.findall(pattern,trace))
    cx=ct(rf"CONTEXT_TX mode={mode} second=")
    cr=ct(rf"CONTEXT_RX role=3 mode={mode} second=")
    tx=ct(rf"REPORT_TX source=(?:2|3) mode={mode} second=")
    rx=ct(rf"REPORT_RX source=(?:2|3) mode={mode} second=")
    rows.append({"seed":seed,"udgm_rx_success":prr,"mode":mode,"context_app_bytes":bytes_n,
      "context_tx":cx,"context_rx":cr,"data_tx":tx,"data_rx":rx,
      "context_rx_over_tx":cr/cx if cx else "",
      "data_rx_over_tx":rx/tx if tx else ""})
   if not all(x["data_tx"]>0 for x in rows):
    raise RuntimeError("No report data in one or more modes")
   result.extend(rows)
   saved.write_text(json.dumps({"passed":True,"mode_rows":rows},indent=2)+"\n")
   print("PASS",seed,prr,[(x["mode"],x["context_rx"],x["context_tx"]) for x in rows],flush=True)
  except Exception as e:
   (case/"error.txt").write_text(str(e))
   print("FAIL",seed,prr,str(e),flush=True)
  with (OUT/"results.csv").open("w",newline="") as f:
   w=csv.DictWriter(f,fieldnames=list(result[0]) if result else ["seed"])
   w.writeheader();w.writerows(result)
  (OUT/"progress.json").write_text(json.dumps({"passed":len(result)//4,"planned":len(SEEDS)*len(PRR),
       "scope":"three-node Cooja serial logs; sensitivity to configured UDGM receive success; NOT full RE-ETX or independently calibrated PHY",
       "phy_rx_configurations":PRR},indent=2)+"\n")
