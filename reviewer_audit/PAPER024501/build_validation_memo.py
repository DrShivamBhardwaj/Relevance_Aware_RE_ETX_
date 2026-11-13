"""Build an evidence-only research note from completed PAPER024501 diagnostics.

This deliberately keeps the newly added reference codec and IoT-LAB NullNet
transport separate from the original IJWMT protocol, whose full deployment is
not established. Reject incomplete experiment sets rather than extrapolate.
"""
from pathlib import Path
import json, math, subprocess
import pandas as pd
BASE=Path(__file__).resolve().parent
R200=pd.read_csv(BASE/"receiver_campaign/completed.csv")
R100=pd.read_csv(BASE/"receiver_campaign_100r/completed.csv")
RSTAT200=pd.read_csv(BASE/"receiver_campaign/paired_results.csv")
RSTAT100=pd.read_csv(BASE/"receiver_campaign_100r/paired_results.csv")
ENERGY=pd.read_csv(BASE/"full_network_energy/completed.csv")
ENERGYSTAT=pd.read_csv(BASE/"full_network_energy/paired_results.csv")
COOJA=json.loads((BASE/"cooja_transport/campaign_results.json").read_text())
PHY0=json.loads((BASE/"iotlab_m3/experiment_458478/serial_capture2_audit.json").read_text())
PHY1=json.loads((BASE/"iotlab_m3/experiment_458478/staggered_serial_audit.json").read_text())
assert len(R200)==40 and len(R100)==40 and len(ENERGY)==60 and len(COOJA)==15
assert R200.groupby("mode").size().to_dict()=={x:10 for x in ("C1","C3","C5","C6")}
assert R100.groupby("mode").size().to_dict()=={x:10 for x in ("C1","C3","C5","C6")}
assert ENERGY.groupby(["scenario","mode"]).size().eq(10).all()
assert all(x["simulator_exit"]==0 for x in COOJA)
def receiver_table(df):
 lines=["| Mode | Receiver RMSE ↓ | Event F1 ↑ | Reports per run (mean) |","|---|---:|---:|---:|"]
 for mode in ("C1","C3","C5","C6"):
  d=df.loc[df["mode"]==mode]
  lines.append(f"| {mode} | {d.rmse.mean():.5f} | {d.event_f1.mean():.5f} | {d.reports.mean():.1f} |")
 return "\n".join(lines)
def paired(df,model="C5",reference="C3",metric="rmse"):
 x=df[(df["mode"]==model)&(df["reference"]==reference)&(df["metric"]==metric)].iloc[0]
 return f"{x['mean_diff']:+.6f} (95% CI {x['CI95_lower']:+.6f} to {x['CI95_upper']:+.6f}; Holm p={x['p_holm']:.6g}; n={int(x['n_paired'])})"
def energy_table():
 lines=["| Assumed overhead | Policy | FND (rounds) | HND (rounds) | LND (rounds) | PDR (%) | mJ per delivered report |","|---|---|---:|---:|---:|---:|---:|"]
 for scenario in ("zero_extra","moderate_extra","high_extra"):
  for mode in ("C1","C3"):
   d=ENERGY[(ENERGY.scenario==scenario)&(ENERGY["mode"]==mode)]
   lines.append(f"| {scenario} | {mode} | {d.FND.mean():.1f} | {d.HND.mean():.1f} | {d.LND.mean():.1f} | {d.PDR_percent.mean():.3f} | {d.energy_per_delivered_j.mean()*1000:.4f} |")
 return "\n".join(lines)
def quality_table():
 lines=["| Cooja per-link quality parameter | Complete reports / 42 requested | Source seeds |","|---:|---:|---|"]
 for quality in sorted(set(x["radio_success_parameter_rx"] for x in COOJA),reverse=True):
  group=[x for x in COOJA if x["radio_success_parameter_rx"]==quality]
  n=sum(x["reports_transmitted"] for x in group)
  good=sum(x["reports_reassembled"] for x in group)
  lines.append(f"| {quality:.2f} | {good}/{n} | 11, 42, 101 |")
 return "\n".join(lines)
physical_lines=["| Physical capture window | Source TX logged | Sink complete logged | Matched eligible | Trace-window match ratio | Median matched latency |","|---|---:|---:|---:|---:|---:|"]
for name,p in (("Simultaneous-source diagnostic",PHY0),("Staggered-source diagnostic",PHY1)):
 physical_lines.append(f"| {name} | {p['source_reports_observed']} | {p['sink_complete_reports_observed']} | {p['matched_completed']}/{p['eligible']} | {100*p['trace_window_matched_ratio']:.1f}% | {p['median_matched_latency_ms']:.1f} ms |")
text=f"""# PAPER024501 — Reviewer-focused validation memorandum

**Status:** Diagnostic experiments executed; complete paper-equivalent hardware, receiver implementation and calibrated energy evaluation remain **not established**. This note is not a replacement for the 32-item revision response.

## Evidence registry

- Repository branch: `review/PAPER024501-audit`
- Original C1–C7 archive remains unchanged. Original paper does **not** implement the synthetic DCT reference codec below.
- Newly executed receiver experiments: 40 runs × 200 rounds and 40 runs × 100 rounds, across C1/C3/C5/C6, 10 matched seeds each.
- Newly executed node-state battery scenarios: 60 full network reruns (3 overhead profiles × C1/C3 × 10 matched seeds).
- Cooja: 15 three-node direct NullNet/CSMA fragmentation experiments, three seeds and five configured TX/RX success parameters.
- FIT IoT-LAB experiment 458478: Grenoble M3 boards 96, 101, 102; direct fragmented-report diagnostic on real 802.15.4 hardware. Not a port of RE-ETX.

## 1. Receiver-side fidelity

**100-round matched evaluation**, before policy-dependent network mortality:

{receiver_table(R100)}

**200-round extended evaluation**, whose available-source counts are affected by mortality:

{receiver_table(R200)}

Paired C5–C3 RMSE, 100-round cohort: {paired(RSTAT100)}.

Paired C5–C3 RMSE, 200-round cohort: {paired(RSTAT200)}.

**Scientific interpretation:** The fixed equal-budget C5 control reconstructed the diagnostic DCT signal more accurately than relevance-adaptive C3. C3 did not establish a consistent fidelity advantage over shuffled C6. Event F1 reflects a threshold decision on the reconstructed *synthetic* waveform derived from actual scalar network observations; it is not a validated application classifier. The reference codec assumes 256 signal samples per report, 16-bit progressively transmitted orthonormal DCT coefficients, quantization step 1/512, and a sink last-sample hold on report loss. No source/receiver bitstream is specified in the original IJWMT manuscript. Accordingly, these results **do not prove semantic or event utility improvements for the original algorithm**.

## 2. Node-state network energy reruns

{energy_table()}

Every simulated source has its battery debited for sensing, computation, idle energy, neighbour context/routing-control radio exchange and an approximate ACK radio ledger. The original radio transmission and relay-reception costs remain active. Conditions: `zero_extra` keeps all new costs zero and reproduces the archived C1/C3 lifetime metrics. `moderate_extra` assumes 10 µJ sensing, 5 µJ computation and 5 µJ idle per alive node/round, 100 context bits and 64 routing bits per node/round, and 88 ACK bits per frame attempt. `high_extra` uses 100/40/50 µJ sensing/computation/idle, 200 context bits, 128 routing bits and the same 88 ACK bits. Control broadcast ranges are modeled as 20 m. These are **assumptions, not measurements**.

The C3 lifetime advantage persists under both tested assumed profiles but contracts substantially as costs grow. The high-cost profile reduces C3 LND from 2636.4 to 1047.7 rounds; the no-extra baseline and high profile are different energy-system models. ACK attempts are allocated approximately across hops and this ledger does not model actual ACK scheduling, sensing device current, control-frame contention, acquisition reliability, or chip-level duty-state traces. Thus this is a **network-state scenario sensitivity**, not a hardware-calibrated energy validation or a demonstration of universal energy superiority.

## 3. Cooja radio-transport diagnostic

{quality_table()}

Each configuration has 14 reported attempts in a 60-second 3-node network, where complete reports require all fragments at the sink. The application payload safeguard at relevance 0.50 yields 3000 bits; at 0.85 it yields 4000 bits, but the corresponding equation in the manuscript requires correction. The configured channel quality is a simulator input, not measured SNR–PER. Cooja runs use NullNet/CSMA, direct one-hop messages, no RE-ETX parent selection and no battery-aware routing.

## 4. FIT IoT-LAB M3 physical diagnostic

Experiment **458478**, Grenoble; sink M3-96, sources M3-101/M3-102. Five compiled binary images (original sink/two sources plus two staggered sources) have SHA-256 manifests. Successful flash and reset responses are stored with raw serial traces.

{"\n".join(physical_lines)}

These ratios describe matching **within captured serial-log windows only**; they are **not calibrated PDR or physical-layer PER**. Some source lines may be absent from the aggregator and two sources can contend for the same channel. The second period is brief and follows new flashing; no causal staggered-scheduling gain is established. Hardware receive-completion logs do confirm that some actual M3 radio reports survived fragmented transport. No paper-equivalent distributed relevance scoring, RE-ETX route choice, measured current/energy, or multipath fault recovery was validated.

## 5. Implications for reviewer responses

1. Mark receiver reconstruction as **diagnostic-only** and explicitly report the C3 fidelity-negative result. Do not claim original paper semantic accuracy improvement.
2. Mark the network energy concern as **partially addressed by model-based sensitivity**. Calibrated sensing, CPU, idle, ACK and control costs must be identified before adopting these scenario results as physical energy evidence.
3. Mark Cooja and FIT IoT-LAB **transport probes completed, protocol-level validation pending**. A full RE-ETX/semantic-policy firmware port and repeated paired hardware trials remain necessary for stronger claims.
4. Keep Eq. (6), algorithm pseudocode, exact paper-source revision, redlines, DOI verification, journal author profiles and all declarations under separate manuscript gates.
5. Commit source, checksum manifest, seed files, raw traces, and statistical tables. Maintain the original archived source results separately.

**No original experiment, hardware measurement, or cited paper is invented by this memorandum.**
"""
(BASE/"PAPER024501_validation_memorandum.md").write_text(text)
out={"receiver_200_runs":len(R200),"receiver_100_runs":len(R100),
     "battery_network_runs":len(ENERGY),"cooja_runs":len(COOJA),
     "iotlab_experiment":458478,"hardware_full_RE_ETX":False,
     "receiver_reference_only":True,"energy_device_calibrated":False,
     "cooja_fragmentation_tested":True,
     "source_input_archive_unchanged":True}
(BASE/"new_validation_summary.json").write_text(json.dumps(out,indent=2)+"\n")
print("MEMO_WRITE_SUCCESS",len(text),"bytes")
