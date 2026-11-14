# PAPER024501 — Evidence closure audit for nine previously partial reviewer requirements

**Date:** 14 November 2026. **Branch:** `review/PAPER024501-audit`.
**Scientific release:** BLOCKED. The entries below are internal, evidence-based
revision assessments, not editorial acceptance or permission to claim a full
physical deployment. The isolated context-energy sweep is now 60/60 complete,
the optional receiver-cache experiment is 20/20 complete, and the Cooja
reception sweep is 15/15 complete.

## M1 — distributed neighbour observations and their energy

**Implemented and tested:**
- Existing 100-node original simulator with six isolated context-energy charging
  configurations (100, 200, 500, 1000, 2000, 4000 observation bits per
  node/round, 10 archived seeds each; **60/60 complete**); `run_context_only_battery_campaign.py`.
  TX/RX costs are charged to node batteries, with ideal context reception.
- New *alternative* 100-node receiver-local cache model:
  `distributed_neighbour_context.py`; when a sensor receives a neighbour
  observation its cache updates, otherwise it keeps the previous value.
  Each broadcast TX and each neighbour RX costs battery energy; application
  uses only receiver-cached neighbour values. The scenario varies update size
  (13/25/50 bytes) and independent receiving probability (1.0 or 0.8), over
  five matched seeds per configuration (**20/20 complete**), without changing the original archived configuration.
- Cooja 3-node NullNet context transport in three configured UDGM reception
  conditions, 0.60, 0.80 and 1.00, five seeds per setting (15 successful
  simulations, four context-length modes per case); see
  `context_exchange_trial/cooja_rx_sweep/results.csv`.
- FIT IoT-LAB Grenoble M3 experiment **458578** archived actual serial packet
  evidence and whole-board consumption traces from three nodes. The physical
  follow-up allocation **458597** terminated with successful firmware flashing
  and retrieved raw board-power OML data, but the serial aggregator was empty
  on both captures. This follow-up is **not a successful replication**.

**Quantitative limits:** With ideal context reception and separately charged
per-round context costs, mean C3 LND falls from 2636.4 at zero additional
context cost to 2271.5 (100 bits), 2041.5 (200 bits), 1627.2 (500 bits),
1297.6 (1000 bits), 1039.9 (2000 bits) and 886.1 (4000 bits). Energy per
delivered report rises from 0.526 mJ to 1.533 mJ at 2000 context bits;
this exceeds the unchanged C1 baseline of 1.147 mJ, while LND falls below
C1's 1268.6 rounds. The evidence therefore contains a **model-based
advantage reversal**, not a measured physical threshold.

The receiver-local-cache C3 diagnostic, over five matched seeds, yields
mean LND 1957.4 rounds with 13-byte and 100% reception, 1961.8 with
13-byte and 80% reception, 1797.6 with 25-byte and 80%, and 1566.0 with
50-byte and 80%. Original central-context C3 on those five seeds had
mean LND 2633.2. A single archived C3 seed-11 rerun with this optional
mode OFF matched the original six numerical metrics with zero differences.

**Boundaries:** The new local-cache model still idealises independent erasures,
synchronous one-hop broadcast, collision handling and retry costs. The M3
firmware tests synthetic neighbour observations, not the original full RE-ETX
network. Neither original-codec utility nor fully calibrated physical network
energy is established. Never combine asynchronous results as though all
were a single matched, physical experiment.

## M2 — weight and threshold choice

**Evidence:** 90 executed C3 network runs (10 matched seeds per nine parameter
configurations), with Holm-adjusted paired tests:
`network_parameter_sweep/paired_sensitivity_analysis.csv`.
Values include 0.4/0.8 temporal weights, 0.4/0.6 lower thresholds, 0.75/0.95
upper thresholds and energy weights 0.10/0.50. The baseline uses 0.6 temporal,
0.4 spatial, 0.50 and 0.85 thresholds and 0.25 energy weighting.
**Boundary:** local one-factor sensitivity and reused seeds. No global optimum,
nonlinear-map superiority or independently tuned external cohort.

## M4 — sensing, computation, control, idle and ACK energy

**Evidence:** 60 complete 100-node C1/C3 battery-ledger reruns across zero,
moderate and high *assumed* additional costs, 10 seeds each:
`full_network_energy/completed.csv`. Physical M3 light sensor, CPU-workload,
radio-broadcast (458514) and context-packet (458578) board-power measurements
exist, separately.
**Boundary:** workload phase watts are not independent joules per sensing
sample, ACK, CPU task or routing event. Scenario parameters are not hardware
calibration of the full RE-ETX protocol.

## M5 — deep-topology routing mechanism and event delivery

**Evidence:** 60 original 100-node simulation traces from three calibrated
initial-route depths × C3/C5 × 10 seeds:
`event_timing_depth/event_timing_audit.json`. Event-active hop counts,
within-round service lag and cumulative channel-occupancy timing are logged
with matched source/round/seed; nine seed-level contrasts use Holm correction.
In the deep profile, the C3−C5 matched within-round lag was −0.1826 s
(95% CI [−0.5190, 0.1537], Holm p=1.0): no demonstrated C3 advantage.
**Boundary:** inter-round physical sampling time is undefined. Channel
occupancy is not wall-clock event staleness or full AoI.

## Mandatory R2 — table format

Three-line summary and bordered source-data table styling is partly prepared.
A final check against the journal template, with all supplementary tables and
precise captions, remains necessary.

## Mandatory R5 — reference proof

All 26 DOI-carrying entries among 27 revised-manuscript references have
independently Crossref-verified **titles**:
`provenance/reference_doi_title_audit.json`. Reference [24] is an archival
Holm record without a supplied DOI. This does **not** validate every author
name, volume, issue, page, publication status and main-text citation mapping.

## Mandatory R9 — camera-ready template

The Word manuscript has been repeatedly rendered; final camera-ready
compliance still requires all author metadata, declaration values and journal
template checks. Do not label complete until the actual final DOCX is audited.

## Mandatory R10 — nine declarations

Nine statement headings exist but author-confirmed contents, contribution
statements and correct N/A choices require author confirmation. Do not infer
personal or institutional declarations from experimental scripts.

## Minor m14 — computational provenance

Verified *connected review execution* host: Apple M1 MacBook Air, 8 GB,
Python 3.14.7, NumPy 2.5.3, SciPy 1.18.1, pandas 3.0.5, and recorded
Contiki-NG commit. The exact original archival execution computer is not
established by this later audit. Keep the two environments distinct.

## Gates retained

- No original application source encoder/decoder and no supported general
  equal-budget receiver-utility superiority.
- No physically calibrated, paper-equivalent 100-node RE-ETX deployment or
  independently verified alternate-parent benefit.
- All physical experiments and simulations must keep their distinct scopes.
- The completed 60/60 and 20/20 100-node context campaigns and 15/15
  Cooja cases are verified against their individual progress files and
  seed-level outputs; this does not certify 100-node physical deployment.
