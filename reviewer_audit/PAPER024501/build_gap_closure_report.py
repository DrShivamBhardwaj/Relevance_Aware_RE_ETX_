"""Produce a claim-safe status report for the three unresolved reviewer issues."""
from pathlib import Path
import json,csv,statistics
BASE=Path(__file__).resolve().parent
def j(path):
 p=BASE/path
 return json.loads(p.read_text()) if p.exists() else {}
def rows(path):
 p=BASE/path
 return list(csv.DictReader(p.open())) if p.exists() else []
def mean(records,key):
 return statistics.mean(float(r[key]) for r in records) if records else None
s100=rows("receiver_scalar_100r/completed.csv")
s200=rows("receiver_scalar_200r/completed.csv")
fac=rows("reetx_port/factorial_paced/results.csv")
p1=j("energy_phase_probe/phase_power_audit.json")
p2=j("energy_phase_probe_v2/phase_v2_audit.json")
hardware=j("reetx_port/hardware/hardware_ab_audit.json")
pyparity=j("reetx_port/c_python_policy_parity.json")
complete=(len(s100)==40 and len(s200)==40 and len(fac)==12)
by_mode={}
for mode in ("C1","C3","C5","C6"):
 a=[x for x in s100 if x["mode"]==mode]
 b=[x for x in s200 if x["mode"]==mode]
 by_mode[mode]={"100round_rmse":mean(a,"rmse"),"100round_event_f1":mean(a,"event_f1"),
                "200round_rmse":mean(b,"rmse"),"200round_event_f1":mean(b,"event_f1"),
                "200round_received":mean(b,"received"),"200round_attempted":mean(b,"reports")}
by_factor={}
for mode in sorted({x["mode"] for x in fac}):
 r=[x for x in fac if x["mode"]==mode]
 by_factor[mode]={"runs":len(r),"source3_mean_delivered":mean(r,"source3_delivered"),
                  "source3_mean_attempted":mean(r,"source3_attempted"),
                  "source3_parent2_fraction":mean(r,"source3_parent2_fraction"),
                  "mean_app_bits":mean(r,"source3_mean_application_bits")}
status={
 "paper":"PAPER024501",
 "reviewer_fidelity":{"state":"NOT_ESTABLISHED_FOR_ORIGINAL_MANUSCRIPT",
    "new_scalar_reference_runs":len(s100)+len(s200),
    "source_model":"actual original simulator scalar observations; new Q8.8 source and sink contract",
    "by_policy":by_mode,"reason":"The original manuscript defines bit length but no source bitstream encoder/decoder. Equal scalar-reference performance does not establish a semantic utility advantage."},
 "component_energy":{"state":"PARTIAL_HARDWARE_MEASUREMENT_NOT_FULL_COMPONENT_CALIBRATION",
    "board_power_experiment":458482,"initial_phase_experiment":458510,
    "initial_phase_windows":p1.get("phase_windows_with_usable_current_samples"),
    "new_light_CPU_radio_phase_experiment":p2.get("experiment_id"),
    "new_phase_windows":p2.get("phase_windows",0),
    "new_phase_evidence_verified":bool(p2.get("phase_windows",0)),
    "reason":"Not all sensing CPU radio packet-control and idle activity currents are calibrated to the original algorithm; no real RE-ETX battery ledger."},
 "full_REETX_hardware":{"state":"PARTIAL_DIAGNOSTIC_PORT_NOT_PAPER_EQUIVALENT",
    "Cooja_matched_scenarios":len(fac),"factorial":by_factor,
    "physical_experiment_id":458513,
    "physical_probe_captured":bool(hardware.get("paired_rows",0)),
    "physical_relay_choices_observed":sum(int(r.get("relay_parent_count",0)) for r in hardware.get("mode_summary",[])),
    "python_c_payload_grid_match":pyparity.get("same_rule_on_full_grid",False),
    "corrected_firmware_deployed_on_hardware":False,
    "reason":"Physical experiment uses beacon PRR, modeled energy fraction, synthetic sensing and only three nodes; no 100-node Dijkstra or calibrated message ETX."},
 "all_three_closed":False
}
(BASE/"gap_closure_status.json").write_text(json.dumps(status,indent=2)+"\n")
lines=["# PAPER024501 — Three Scientific Validation Gaps","",
 "**Status: NOT fully closed.** All reported experiment numbers refer to actual completed/running files in this repository. Do not claim source-codec fidelity, independently calibrated components, or paper-equivalent M3 RE-ETX superiority.","",
 "## Receiver-side fidelity","",
 "The submitted simulator selects application payload lengths but specifies no binary source representation, corresponding receiver decoder or reconstruction estimator. This is not recoverable by reinterpreting the original payload-length trace as an encoded sample. A new fixed-point Q8.8 scalar bitstream is explicitly introduced as a diagnostic only.","",
 "| Policy | 100-round RMSE | 100-round F1 | 200-round RMSE | 200-round F1 |",
 "|---|---:|---:|---:|---:|"]
for m in ("C1","C3","C5","C6"):
 x=by_mode[m];lines.append(f"| {m} | {x['100round_rmse']:.6f} | {x['100round_event_f1']:.6f} | {x['200round_rmse']:.6f} | {x['200round_event_f1']:.6f} |")
lines+=["",
 "The C3/C5/C6 outcomes are identical under Q8.8 source encoding. At 200 rounds, C1 has different available-node/report counts because of mortality, so its RMSE comparison uses non-identical observed samples and must not be interpreted as a matched reconstruction-quality effect.","",
 "The earlier newly introduced progressive DCT waveform codec also did not demonstrate a C3 fidelity advantage over equal-budget C5. There is no verified original-codec RMSE/F1. Resolution requires either a documented source/receiver codec with full payload/traces or removal of unsupported semantic-fidelity claims.","",
 "## Hardware component-level power","",
 "Experiment 458482 captured M3 raw DC voltage/current/power profiles for three devices; the independently measured total board powers are not sensing/CPU/MAC power decomposition. Experiment 458510 contained 15 usable phase windows, but brief work at timer boundaries caused non-positive differences against idle; it cannot be used to calibrate component coefficients.",""]
if p2:
 lines += [f"An improved four-phase experiment {p2.get('experiment_id')} uses the actual ISL29020 light sensor, controlled CPU workload and radio broadcast. Its parsed phase windows are {p2.get('phase_windows',0)}; individual whole-board power differences still require caution about contention and time drift.",""]
else:
 lines += ["A second experiment with real ISL29020 sensing and sustained CPU/radio workloads was initiated; its raw phase analysis must pass independent checks before use.",""]
lines += ["## Cooja and FIT IoT-LAB RE-ETX proxy","",
 "A portable C implementation now reproduces the Python payload mapping on 1,001 sampled relevance values, following correction of an observed 20-point float32 and fused-arithmetic mismatch. The corrected firmware images were compiled but were NOT the ones deployed in physical experiment 458513.","",
 "The 2×2 Cooja comparison deliberately places the source beyond direct radio range, with a reachable relay. Each mode has three deterministic seeds and 89 attempted source-3 reports per seed:","",
 "| Mode | Source-3 complete / attempted | Relay parent fraction | Mean requested bits |","|---|---:|---:|---:|"]
for m in ("adaptive_reetx","fixed_reetx","adaptive_direct","fixed_direct"):
 x=by_factor.get(m,{})
 if x:
  lines.append(f"| {m} | {x['source3_mean_delivered']:.1f}/{x['source3_mean_attempted']:.1f} | {x['source3_parent2_fraction']:.2f} | {x['mean_app_bits']:.1f} |")
lines+=["",
 "This demonstrates relay reachability, not a relevance-based delivery improvement: both payload policies deliver through relay, and both direct-only policies fail by imposed geometry. No across-network generalization or original MRHOF/RE-ETX superiority follows.","",
 f"Physical Grenoble M3 experiment 458513 used a three-board A/B diagnostic. The current audit identified {hardware.get('paired_rows',0)} source transmissions in a partial serial window, and no observed relay-parent selection. Direct links were successful in that deployment, so it did not verify a hardware routing advantage.","",
 "## Scientific release gates","",
 "1. Source-authentic application codec (or a claim-revised IJWMT manuscript disclosing the absence of receiver reconstruction).",
 "2. Repeated, phase-labelled per-sample/per-CPU/per-packet current measurement and calibration of the actual deployed policy—not merely whole-board phase comparisons.",
 "3. Source-equivalent relevance scoring, distributed context, message-level ETX, energy-residual acquisition, full sink-rooted routing and paired hardware repetitions on conditions where competing routes exist.",
 "4. Integrate valid negative results, accepted reviewer scope and page-specific replies; do not silently relabel a diagnostic firmware as the submitted protocol.",
 ""]
(BASE/"PAPER024501_GAP_CLOSURE_REPORT.md").write_text("\n".join(lines))
print(json.dumps({"source_scalar_runs":len(s100)+len(s200),"cooja_factorial_runs":len(fac),"phase_v2_windows":p2.get('phase_windows'),"closed":False}))
if not complete:raise SystemExit("Incomplete diagnostic datasets")
