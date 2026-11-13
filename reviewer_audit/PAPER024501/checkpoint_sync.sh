#!/bin/bash
# Local-only periodic recovery checkpoint; does not call ChatGPT.
set -u
ROOT="/Users/shivambhardwaj/ns3-validation/repo-git"
BRANCH="review/PAPER024501-audit"
BASE="$ROOT/reviewer_audit/PAPER024501"
LOG="$BASE/checkpoint_sync.log"
LOCK="$BASE/.checkpoint_sync.lock"
mkdir -p "$BASE"
if ! mkdir "$LOCK" 2>/dev/null; then
  # Release a stale lock only if the recorded process is no longer alive.
  prior="$(cat "$LOCK/pid" 2>/dev/null || true)"
  if [[ "$prior" =~ ^[0-9]+$ ]] && kill -0 "$prior" 2>/dev/null; then exit 0; fi
  rm -rf "$LOCK"
  mkdir "$LOCK" 2>/dev/null || exit 0
fi
echo "$$" >"$LOCK/pid"
trap 'rm -rf "$LOCK"' EXIT
{
 date -u '+%Y-%m-%dT%H:%M:%SZ checkpoint begin'
 cd "$ROOT" || exit 1
 actual="$(git branch --show-current)"
 if [ "$actual" != "$BRANCH" ]; then echo "SKIP wrong branch: $actual"; exit 2; fi
 # Lightweight self-contained reviewer-analysis and response draft refresh:
 /bin/bash "$BASE/revision_checkpoint_stage.sh" >>"$LOG" 2>&1 || echo 'REVISION_REFRESH_FAILED' >>"$LOG"
 git diff --quiet -- config.py run_semantic_re_etx.py || { echo 'SKIP source files changed during simulation'; exit 3; }
 # Keep full per-round trajectories LOCAL; version only compact completed
 # seed summaries and progress needed to resume the experiment.
 shopt -s nullglob
 files=("$BASE"/network_parameter_sweep/*_seed*.json
        "$BASE"/network_parameter_sweep/*.csv
        "$BASE"/network_parameter_sweep/progress.json
        "$BASE"/receiver_campaign/*_seed*.json
        "$BASE"/receiver_campaign/*.csv
        "$BASE"/receiver_campaign/progress.json
        "$BASE"/receiver_campaign_100r/*_seed*.json
        "$BASE"/receiver_campaign_100r/*.csv
        "$BASE"/receiver_campaign_100r/progress.json
        "$BASE"/receiver_scalar_100r/*_seed*.json
        "$BASE"/receiver_scalar_100r/*.csv
        "$BASE"/receiver_scalar_100r/progress.json
        "$BASE"/receiver_scalar_200r/*_seed*.json
        "$BASE"/receiver_scalar_200r/*.csv
        "$BASE"/receiver_scalar_200r/progress.json
        "$BASE"/reetx_port/c_python_policy_parity.json
        "$BASE"/reetx_port/factorial_paced/results.csv
        "$BASE"/reetx_port/factorial_paced/progress.json
        "$BASE"/reetx_port/hardware/m3_reetx_ab_state.json
        "$BASE"/reetx_port/hardware/hardware_ab_audit.json
        "$BASE"/reetx_port/hardware/physical_mode_summary.csv
        "$BASE"/reetx_port/hardware/matched_trace.csv
        "$BASE"/energy_phase_probe/phase_run_state.json
        "$BASE"/energy_phase_probe/phase_power_audit.json
        "$BASE"/energy_phase_probe/*.csv
        "$BASE"/energy_phase_probe_v2/phase_v2_run_state.json
        "$BASE"/energy_phase_probe_v2/phase_v2_audit.json
        "$BASE"/energy_phase_probe_v2/*.csv
        "$BASE"/gap_closure_status.json
        "$BASE"/PAPER024501_GAP_CLOSURE_REPORT.md
        "$BASE"/cooja_transport/campaign_results.json
        "$BASE"/cooja_transport/campaign_progress.json
        "$BASE"/cooja_transport/campaign_summary.json
        "$BASE"/iotlab_m3/hardware_status.json
        "$BASE"/iotlab_m3/experiment_458478/*_audit.json
        "$BASE"/iotlab_m3/experiment_458478/*_matched.csv
        "$BASE"/PAPER024501_validation_memorandum.md
        "$BASE"/new_validation_summary.json
        "$BASE"/full_network_energy/*_seed*.json
        "$BASE"/full_network_energy/*.csv
        "$BASE"/full_network_energy/progress.json
        "$BASE"/pipeline_status.json
        "$BASE"/revision_gate_status.json
        "$BASE"/receiver_validation_gate.json
        "$BASE"/revision_response_matrix.csv
        "$BASE"/REVISION_RESPONSE_DRAFT.md
        "$BASE"/PAPER024501_Revision_Response_DRAFT.docx
        "$BASE"/manuscript_stage_status.json
        "$BASE"/unattended_release_status.json
        "$BASE"/payload_mapping_review.csv
        "$BASE"/manuscript_working/*.docx
        "$BASE"/manuscript_working/*.json
        "$BASE"/manuscript_working/rendered/*.pdf
        "$BASE"/manuscript_working/*.sha256
        "$BASE"/hardware_power_calibration/m3_power_run_state.json
        "$BASE"/hardware_power_calibration/power_archive_audit.json
        "$BASE"/hardware_power_calibration/m3_power_measurement_audit.json
        "$BASE"/hardware_power_calibration/m3_power_node_summary.csv
        "$BASE"/hardware_power_calibration/active/consumption/*.oml
        "$BASE"/PAPER024501_IJWMT_WORKING_DRAFT.docx
        "$BASE"/extended_energy_accounting.csv
        "$BASE"/extended_energy_accounting_meta.json
        "$BASE"/topology_paired_mechanism_audit.csv
        "$BASE"/topology_mechanism_audit_meta.json
        "$BASE"/archive_check.json
        "$BASE"/context_overhead_sensitivity.csv)
 existing=()
 for file in "${files[@]}"; do [ -f "$file" ] && existing+=("$file"); done
 if [ ${#existing[@]} -gt 0 ]; then git add -- "${existing[@]}"; fi
 if ! git diff --cached --quiet; then
   git commit -m "checkpoint(PAPER024501): $(date -u '+%Y-%m-%dT%H:%MZ')" || exit 4
 fi
 # Retry pending prior commits, even when no files changed this cycle.
 if git push origin "$BRANCH"; then
   echo "PUSH_OK $(git rev-parse --short HEAD)"
 else
   echo 'PUSH_FAILED local commits remain queued for next cycle'
   exit 5
 fi
 date -u '+%Y-%m-%dT%H:%M:%SZ checkpoint end'
} >>"$LOG" 2>&1
