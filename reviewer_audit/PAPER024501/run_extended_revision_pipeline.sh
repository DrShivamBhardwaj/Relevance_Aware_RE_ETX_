#!/bin/bash
set -u
ROOT="/Users/shivambhardwaj/ns3-validation/repo-git"
cd "$ROOT" || exit 2
[[ "$(git branch --show-current)" == "review/PAPER024501-audit" ]] || exit 3
PY="$HOME/ns3-validation/.venv/bin/python"
BASE="reviewer_audit/PAPER024501"
for script in receiver_validation_gate.py extended_energy_accounting.py topology_mechanism_audit.py build_reviewer_response_draft.py scientific_revision_gate.py; do
 "$PY" "$BASE/$script" || echo "STAGE_FAILED $script" >&2
done
