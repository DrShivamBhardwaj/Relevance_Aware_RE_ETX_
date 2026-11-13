#!/bin/bash
set -u
cd "$(dirname "$0")/../.." || exit 2
ROOT="$PWD"
BASE="reviewer_audit/PAPER024501"
PY="$HOME/ns3-validation/.venv/bin/python"
"$PY" "$BASE/run_parameter_network_sweep.py" >"$BASE/network_parameter_sweep_worker.log" 2>&1
exitcode=$?
"$PY" "$BASE/analyze_parameter_network_sweep.py" >>"$BASE/network_parameter_sweep_worker.log" 2>&1 || true
git add "$BASE/network_parameter_sweep" "$BASE/run_parameter_network_sweep.py" "$BASE/analyze_parameter_network_sweep.py"
if ! git diff --cached --quiet; then
 git commit -m "Record executed PAPER024501 C3 parameter network sensitivity runs" >>"$BASE/network_parameter_sweep_worker.log" 2>&1
 git push origin review/PAPER024501-audit >>"$BASE/network_parameter_sweep_worker.log" 2>&1 || echo "PUSH_FAILED" >>"$BASE/network_parameter_sweep_worker.log"
fi
echo "SWEEP_EXIT_CODE=$exitcode" >>"$BASE/network_parameter_sweep_worker.log"
exit "$exitcode"
