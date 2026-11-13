# PAPER024501 — Three Scientific Validation Gaps

**Status: NOT fully closed.** All reported experiment numbers refer to actual completed/running files in this repository. Do not claim source-codec fidelity, independently calibrated components, or paper-equivalent M3 RE-ETX superiority.

## Receiver-side fidelity

The submitted simulator selects application payload lengths but specifies no binary source representation, corresponding receiver decoder or reconstruction estimator. This is not recoverable by reinterpreting the original payload-length trace as an encoded sample. A new fixed-point Q8.8 scalar bitstream is explicitly introduced as a diagnostic only.

| Policy | 100-round RMSE | 100-round F1 | 200-round RMSE | 200-round F1 |
|---|---:|---:|---:|---:|
| C1 | 0.001129 | 0.956292 | 0.003342 | 0.964072 |
| C3 | 0.001129 | 0.956292 | 0.001128 | 0.964452 |
| C5 | 0.001129 | 0.956292 | 0.001128 | 0.964452 |
| C6 | 0.001129 | 0.956292 | 0.001128 | 0.964452 |

The C3/C5/C6 outcomes are identical under Q8.8 source encoding. At 200 rounds, C1 has different available-node/report counts because of mortality, so its RMSE comparison uses non-identical observed samples and must not be interpreted as a matched reconstruction-quality effect.

The earlier newly introduced progressive DCT waveform codec also did not demonstrate a C3 fidelity advantage over equal-budget C5. There is no verified original-codec RMSE/F1. Resolution requires either a documented source/receiver codec with full payload/traces or removal of unsupported semantic-fidelity claims.

## Hardware component-level power

Experiment 458482 captured M3 raw DC voltage/current/power profiles for three devices; the independently measured total board powers are not sensing/CPU/MAC power decomposition. Experiment 458510 contained 15 usable phase windows, but brief work at timer boundaries caused non-positive differences against idle; it cannot be used to calibrate component coefficients.

An improved four-phase experiment 458514 uses the actual ISL29020 light sensor, controlled CPU workload and radio broadcast. Its parsed phase windows are 63; individual whole-board power differences still require caution about contention and time drift.

## Cooja and FIT IoT-LAB RE-ETX proxy

A portable C implementation now reproduces the Python payload mapping on 1,001 sampled relevance values, following correction of an observed 20-point float32 and fused-arithmetic mismatch. The corrected firmware images were compiled but were NOT the ones deployed in physical experiment 458513.

The 2×2 Cooja comparison deliberately places the source beyond direct radio range, with a reachable relay. Each mode has three deterministic seeds and 89 attempted source-3 reports per seed:

| Mode | Source-3 complete / attempted | Relay parent fraction | Mean requested bits |
|---|---:|---:|---:|
| adaptive_reetx | 89.0/89.0 | 1.00 | 1366.4 |
| fixed_reetx | 89.0/89.0 | 1.00 | 4000.0 |
| adaptive_direct | 0.0/89.0 | 0.00 | 1369.1 |
| fixed_direct | 0.0/89.0 | 0.00 | 4000.0 |

This demonstrates relay reachability, not a relevance-based delivery improvement: both payload policies deliver through relay, and both direct-only policies fail by imposed geometry. No across-network generalization or original MRHOF/RE-ETX superiority follows.

Physical Grenoble M3 experiment 458513 used a three-board A/B diagnostic. The current audit identified 78 source transmissions in a partial serial window, and no observed relay-parent selection. Direct links were successful in that deployment, so it did not verify a hardware routing advantage.

## Scientific release gates

1. Source-authentic application codec (or a claim-revised IJWMT manuscript disclosing the absence of receiver reconstruction).
2. Repeated, phase-labelled per-sample/per-CPU/per-packet current measurement and calibration of the actual deployed policy—not merely whole-board phase comparisons.
3. Source-equivalent relevance scoring, distributed context, message-level ETX, energy-residual acquisition, full sink-rooted routing and paired hardware repetitions on conditions where competing routes exist.
4. Integrate valid negative results, accepted reviewer scope and page-specific replies; do not silently relabel a diagnostic firmware as the submitted protocol.
