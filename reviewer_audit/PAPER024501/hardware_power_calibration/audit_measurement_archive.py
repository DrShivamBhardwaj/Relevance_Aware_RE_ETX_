"""Conservative IoT-LAB archive audit.

Only identify power traces and units; never pretend a measurement archive
alone proves calibrated sensing/CPU/MAC energy. A separate hardware state
label and known sampling interval are necessary for that decomposition.
"""
from pathlib import Path
import json,tarfile
BASE=Path(__file__).resolve().parent
STATE=BASE/"m3_power_run_state.json"
out=BASE/"power_archive_audit.json"
try:
 s=json.loads(STATE.read_text())
except (FileNotFoundError,ValueError):
 s={}
report={"experiment_id":s.get("experiment_id"),"profile":s.get("profile"),
        "archive_verified":False,"raw_power_trace_verified":False,
        "calibrated_energy_model":False,
        "source_firmware":"NullNet application-fragmentation probe, not RE-ETX",
        "next_requirement":"Timestamped calibrated current and voltage samples + idle/control/app phases"}
archive_path=s.get("archive_path")
if archive_path and Path(archive_path).is_file():
 try:
  with tarfile.open(archive_path,"r:gz") as f:
   names=[m.name for m in f.getmembers() if m.isfile()]
  report["archive_verified"]=True
  report["archive_members"]=names[:150]
  report["potential_power_files"]=[name for name in names if any(x in name.lower() for x in (".oml","consumption","power","current","voltage"))]
  report["raw_power_trace_verified"]=bool(report["potential_power_files"])
  if not report["raw_power_trace_verified"]:
   report["reason"]="Experiment archive returned no obvious sampled power/current/voltage trace; inspect site data export"
 except Exception as e:
  report["reason"]=repr(e)
out.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k not in ("archive_members","potential_power_files")}))
