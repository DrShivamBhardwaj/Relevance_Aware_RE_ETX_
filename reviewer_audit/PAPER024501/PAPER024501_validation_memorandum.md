# PAPER024501 — Reviewer-focused validation memorandum

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

| Mode | Receiver RMSE ↓ | Event F1 ↑ | Reports per run (mean) |
|---|---:|---:|---:|
| C1 | 0.01225 | 0.95615 | 10000.0 |
| C3 | 0.06534 | 0.95628 | 10000.0 |
| C5 | 0.06060 | 0.95615 | 10000.0 |
| C6 | 0.06534 | 0.95628 | 10000.0 |

**200-round extended evaluation**, whose available-source counts are affected by mortality:

| Mode | Receiver RMSE ↓ | Event F1 ↑ | Reports per run (mean) |
|---|---:|---:|---:|
| C1 | 0.01344 | 0.96394 | 19236.1 |
| C3 | 0.06315 | 0.96432 | 20000.0 |
| C5 | 0.06062 | 0.96428 | 20000.0 |
| C6 | 0.06315 | 0.96432 | 20000.0 |

Paired C5–C3 RMSE, 100-round cohort: -0.004742 (95% CI -0.005711 to -0.003772; Holm p=1.07158e-05; n=10).

Paired C5–C3 RMSE, 200-round cohort: -0.002526 (95% CI -0.003352 to -0.001701; Holm p=0.000481173; n=10).

**Scientific interpretation:** The fixed equal-budget C5 control reconstructed the diagnostic DCT signal more accurately than relevance-adaptive C3. C3 did not establish a consistent fidelity advantage over shuffled C6. Event F1 reflects a threshold decision on the reconstructed *synthetic* waveform derived from actual scalar network observations; it is not a validated application classifier. The reference codec assumes 256 signal samples per report, 16-bit progressively transmitted orthonormal DCT coefficients, quantization step 1/512, and a sink last-sample hold on report loss. No source/receiver bitstream is specified in the original IJWMT manuscript. Accordingly, these results **do not prove semantic or event utility improvements for the original algorithm**.

## 2. Node-state network energy reruns

| Assumed overhead | Policy | FND (rounds) | HND (rounds) | LND (rounds) | PDR (%) | mJ per delivered report |
|---|---|---:|---:|---:|---:|---:|
| zero_extra | C1 | 125.5 | 409.1 | 1268.6 | 95.350 | 1.1473 |
| zero_extra | C3 | 275.2 | 870.1 | 2636.4 | 97.812 | 0.5255 |
| moderate_extra | C1 | 121.9 | 365.6 | 1042.9 | 95.222 | 1.3243 |
| moderate_extra | C3 | 260.2 | 715.2 | 1862.7 | 97.664 | 0.6729 |
| high_extra | C1 | 115.1 | 311.7 | 725.9 | 95.296 | 1.6377 |
| high_extra | C3 | 233.9 | 537.5 | 1047.7 | 97.698 | 0.9587 |

Every simulated source has its battery debited for sensing, computation, idle energy, neighbour context/routing-control radio exchange and an approximate ACK radio ledger. The original radio transmission and relay-reception costs remain active. Conditions: `zero_extra` keeps all new costs zero and reproduces the archived C1/C3 lifetime metrics. `moderate_extra` assumes 10 µJ sensing, 5 µJ computation and 5 µJ idle per alive node/round, 100 context bits and 64 routing bits per node/round, and 88 ACK bits per frame attempt. `high_extra` uses 100/40/50 µJ sensing/computation/idle, 200 context bits, 128 routing bits and the same 88 ACK bits. Control broadcast ranges are modeled as 20 m. These are **assumptions, not measurements**.

The C3 lifetime advantage persists under both tested assumed profiles but contracts substantially as costs grow. The high-cost profile reduces C3 LND from 2636.4 to 1047.7 rounds; the no-extra baseline and high profile are different energy-system models. ACK attempts are allocated approximately across hops and this ledger does not model actual ACK scheduling, sensing device current, control-frame contention, acquisition reliability, or chip-level duty-state traces. Thus this is a **network-state scenario sensitivity**, not a hardware-calibrated energy validation or a demonstration of universal energy superiority.

## 3. Cooja radio-transport diagnostic

| Cooja per-link quality parameter | Complete reports / 42 requested | Source seeds |
|---:|---:|---|
| 1.00 | 42/42 | 11, 42, 101 |
| 0.95 | 42/42 | 11, 42, 101 |
| 0.80 | 42/42 | 11, 42, 101 |
| 0.50 | 40/42 | 11, 42, 101 |
| 0.20 | 9/42 | 11, 42, 101 |

Each configuration has 14 reported attempts in a 60-second 3-node network, where complete reports require all fragments at the sink. The application payload safeguard at relevance 0.50 yields 3000 bits; at 0.85 it yields 4000 bits, but the corresponding equation in the manuscript requires correction. The configured channel quality is a simulator input, not measured SNR–PER. Cooja runs use NullNet/CSMA, direct one-hop messages, no RE-ETX parent selection and no battery-aware routing.

## 4. FIT IoT-LAB M3 physical diagnostic

Experiment **458478**, Grenoble; sink M3-96, sources M3-101/M3-102. Five compiled binary images (original sink/two sources plus two staggered sources) have SHA-256 manifests. Successful flash and reset responses are stored with raw serial traces.

| Physical capture window | Source TX logged | Sink complete logged | Matched eligible | Trace-window match ratio | Median matched latency |
|---|---:|---:|---:|---:|---:|
| Simultaneous-source diagnostic | 32 | 17 | 17/31 | 54.8% | 220.6 ms |
| Staggered-source diagnostic | 13 | 6 | 6/12 | 50.0% | 129.8 ms |

These ratios describe matching **within captured serial-log windows only**; they are **not calibrated PDR or physical-layer PER**. Some source lines may be absent from the aggregator and two sources can contend for the same channel. The second period is brief and follows new flashing; no causal staggered-scheduling gain is established. Hardware receive-completion logs do confirm that some actual M3 radio reports survived fragmented transport. No paper-equivalent distributed relevance scoring, RE-ETX route choice, measured current/energy, or multipath fault recovery was validated.

## 5. Implications for reviewer responses

1. Mark receiver reconstruction as **diagnostic-only** and explicitly report the C3 fidelity-negative result. Do not claim original paper semantic accuracy improvement.
2. Mark the network energy concern as **partially addressed by model-based sensitivity**. Calibrated sensing, CPU, idle, ACK and control costs must be identified before adopting these scenario results as physical energy evidence.
3. Mark Cooja and FIT IoT-LAB **transport probes completed, protocol-level validation pending**. A full RE-ETX/semantic-policy firmware port and repeated paired hardware trials remain necessary for stronger claims.
4. Keep Eq. (6), algorithm pseudocode, exact paper-source revision, redlines, DOI verification, journal author profiles and all declarations under separate manuscript gates.
5. Commit source, checksum manifest, seed files, raw traces, and statistical tables. Maintain the original archived source results separately.

**No original experiment, hardware measurement, or cited paper is invented by this memorandum.**
