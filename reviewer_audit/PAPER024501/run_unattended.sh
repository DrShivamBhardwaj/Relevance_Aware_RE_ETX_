#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
BRANCH="$(git branch --show-current)"
if [[ "$BRANCH" != "review/PAPER024501-audit" ]]; then
  echo "Refusing to run on branch $BRANCH"; exit 2
fi
LOGROOT="$ROOT/reviewer_audit/PAPER024501"
PY="$HOME/ns3-validation/.venv/bin/python"
"$PY" "$LOGROOT/run_revision_pipeline.py" --pilot >"$LOGROOT/worker_output.log" 2>&1 || true
# Never add any original source/results, only isolated evidence and status.
git add reviewer_audit/PAPER024501
if ! git diff --cached --quiet; then
  git commit -m "Record PAPER024501 unattended pipeline outcomes"
  git push origin review/PAPER024501-audit || echo "PUSH_FAILED: local commit retained" >>"$LOGROOT/worker_output.log"
fi
