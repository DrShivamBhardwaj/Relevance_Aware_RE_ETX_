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
# Evidence-only research memo; refuses incomplete input arrays.
"$HOME/ns3-validation/.venv/bin/python" "$BASE/build_validation_memo.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'VALIDATION_MEMO_INCOMPLETE' >>"$BASE/revision_checkpoint_stage.log"
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/build_response_docx.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'DOCX_DRAFT_FAILED' >>"$BASE/revision_checkpoint_stage.log"
# The real submitted source and IJWMT template are in Mac Downloads, not in repo.
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/unattended_release_workflow.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'SOURCE_MANUSCRIPT_PIPELINE_FAILED' >>"$BASE/revision_checkpoint_stage.log"
# Resume only the already reserved IoT-LAB experiment (if needed).
/bin/bash "$BASE/ensure_power_worker.sh" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'POWER_RESUME_CHECK_FAILED' >>"$BASE/revision_checkpoint_stage.log"
