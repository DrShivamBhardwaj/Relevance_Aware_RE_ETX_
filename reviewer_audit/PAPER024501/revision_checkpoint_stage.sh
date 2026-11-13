#!/bin/bash
# Run a cheap, deterministic evidence refresh before the 20-minute Git sync.
set -u
ROOT="/Users/shivambhardwaj/ns3-validation/repo-git"
cd "$ROOT" || exit 2
BASE="reviewer_audit/PAPER024501"
if [[ "$(git branch --show-current)" != "review/PAPER024501-audit" ]]; then exit 3; fi
/bin/bash "$BASE/run_extended_revision_pipeline.sh" >"$BASE/revision_checkpoint_stage.log" 2>&1
# Verify physical M3 measured OML data when available. No extrapolated components.
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/hardware_power_calibration/analyze_m3_oml.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'M3_POWER_TRACE_PENDING' >>"$BASE/revision_checkpoint_stage.log"
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/hardware_power_calibration/audit_measurement_archive.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || true
# Recompute statistics only from completed per-seed evidence.
for script in analyze_receiver_campaign.py analyze_receiver_100round_matched.py analyze_full_energy.py; do
 "$HOME/ns3-validation/.venv/bin/python" "$BASE/$script" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo "STAT_STAGE_FAILED $script" >>"$BASE/revision_checkpoint_stage.log"
done
# Extend with original-source scalar reconstruction diagnostics and genuine
# phase-aligned testbed data. The original source still has no decoder.
for script in analyze_scalar_100round.py analyze_scalar_200round.py; do
 "$HOME/ns3-validation/.venv/bin/python" "$BASE/$script" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo "SCALAR_ANALYSIS_PENDING $script" >>"$BASE/revision_checkpoint_stage.log"
done
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/reetx_port/hardware/audit_hardware_ab.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo "HARDWARE_AB_PENDING" >>"$BASE/revision_checkpoint_stage.log"
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/energy_phase_probe_v2/analyze_v2.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo "POWER_V2_PENDING" >>"$BASE/revision_checkpoint_stage.log"
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/build_gap_closure_report.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo "GAP_REPORT_PENDING" >>"$BASE/revision_checkpoint_stage.log"
# Evidence-only research memo; refuses incomplete input arrays.
"$HOME/ns3-validation/.venv/bin/python" "$BASE/build_validation_memo.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'VALIDATION_MEMO_INCOMPLETE' >>"$BASE/revision_checkpoint_stage.log"
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/build_response_docx.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'DOCX_DRAFT_FAILED' >>"$BASE/revision_checkpoint_stage.log"
# The real submitted source and IJWMT template are in Mac Downloads, not in repo.
# Keep Git checkpoints progressing even if a FileProvider-backed DOCX stalls.
"$HOME/Research/wsn-array-validation-env/bin/python" - <<'RUN_UNATTENDED_MANUSCRIPT' >>"$BASE/revision_checkpoint_stage.log" 2>&1
import subprocess,sys
try:
    r=subprocess.run([sys.executable, "reviewer_audit/PAPER024501/unattended_release_workflow.py"],timeout=75,check=False)
    if r.returncode:print("SOURCE_MANUSCRIPT_PIPELINE_FAILED",r.returncode)
except subprocess.TimeoutExpired:
    print("SOURCE_MANUSCRIPT_PIPELINE_TIMEOUT_75S")
RUN_UNATTENDED_MANUSCRIPT
# Render/inspect a working draft without claiming human editorial QA.
"$HOME/Research/wsn-array-validation-env/bin/python" "$BASE/render_manuscript_preflight.py" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'DOCX_RENDER_AUDIT_FAILED' >>"$BASE/revision_checkpoint_stage.log"
# Resume only the already reserved IoT-LAB experiment (if needed).
/bin/bash "$BASE/ensure_power_worker.sh" >>"$BASE/revision_checkpoint_stage.log" 2>&1 || echo 'POWER_RESUME_CHECK_FAILED' >>"$BASE/revision_checkpoint_stage.log"
