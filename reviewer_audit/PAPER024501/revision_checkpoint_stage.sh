#!/bin/bash
# Run a cheap, deterministic evidence refresh before the 20-minute Git sync.
set -u
ROOT="/Users/shivambhardwaj/ns3-validation/repo-git"
cd "$ROOT" || exit 2
BASE="reviewer_audit/PAPER024501"
if [[ "$(git branch --show-current)" != "review/PAPER024501-audit" ]]; then exit 3; fi
/bin/bash "$BASE/run_extended_revision_pipeline.sh" >"$BASE/revision_checkpoint_stage.log" 2>&1
# Recompute statistics only from completed per-seed evidence.
for script in analyze_receiver_campaign.py analyze_receiver_100round_matched.py analyze_full_energy.py; do
 "$HOME/ns3-validation/.venv/bin/python" "$BASE/$script" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo "STAT_STAGE_FAILED $script" >>"$BASE/revision_checkpoint_stage.log"
done
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/build_response_docx.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'DOCX_DRAFT_FAILED' >>"$BASE/revision_checkpoint_stage.log"
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/stage_ijwmt_manuscript.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'MANUSCRIPT_STAGE_FAILED' >>"$BASE/revision_checkpoint_stage.log"
