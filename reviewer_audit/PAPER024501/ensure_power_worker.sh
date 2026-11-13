#!/bin/bash
# Resume the single already-registered experiment only; no duplicate bookings.
set -u
ROOT="/Users/shivambhardwaj/ns3-validation/repo-git"
BASE="$ROOT/reviewer_audit/PAPER024501/hardware_power_calibration"
cd "$ROOT" || exit 2
if [ "$(git branch --show-current)" != "review/PAPER024501-audit" ]; then exit 3; fi
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/audit_measurement_archive.py" >/dev/null 2>&1 || true
STATE="$BASE/m3_power_run_state.json"
# Never submit a new experiment after the first one; register state first.
[ -f "$STATE" ] || exit 0
"$HOME/Research/wsn-array-validation-env/bin/python" - <<'PY'
import json,pathlib,sys
p=pathlib.Path("reviewer_audit/PAPER024501/hardware_power_calibration/m3_power_run_state.json")
x=json.loads(p.read_text())
sys.exit(0 if x.get("completed") or not x.get("experiment_id") else 1)
PY
if [ "$?" -eq 0 ]; then exit 0; fi
if pgrep -f 'run_m3_power_once.py' >/dev/null 2>&1; then exit 0; fi
nohup caffeinate -i -t 14400 "$HOME/Research/wsn-array-validation-env/bin/python"   "$BASE/run_m3_power_once.py" >>"$BASE/worker.log" 2>&1 < /dev/null &
echo "RESUMED_EXISTING_POWER_EXPERIMENT_PID=$!" >>"$BASE/resume.log"
