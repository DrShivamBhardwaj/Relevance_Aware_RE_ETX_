# Experimental evidence summary

This file summarizes the evidence base generated for the reconstructed WSN-IoT HFL manuscript. It distinguishes implemented evidence from remaining validation gaps.

## Evidence layers completed

- Synthetic correlated system/data heterogeneity experiment.
- Intel Berkeley Lab real WSN sensing + measured connectivity experiment.
- UCI HAR real inertial-sensing experiment.
- ns-3.47 IEEE 802.15.4/LR-WPAN communication replay.
- Host-hardware execution timing/memory report.
- 10-seed paired statistical robustness report.
- Component ablations and parameter-sensitivity grid.

## Frozen operating point

- `relay_pressure_weight = 3.0`
- `compression_distortion_weight = 0.10`
- `drift_v = 0.5`
- Top-k candidate ratios: `{0.15, 0.30, 0.50, 0.75, 1.0}`

## Intel Berkeley Lab WSN result at correlation 0.9

| Method | RMSE (C) | MAE (C) | Effective bits | Energy (J) | Max relay energy (J) | Rep. JS |
|---|---:|---:|---:|---:|---:|---:|
| random | 1.7381 | 0.8021 | 2515488 | 6.986 | 0.2736 | 0.0749 |
| resource | 1.7451 | 0.8297 | 2216534 | 6.298 | 0.1393 | 0.1231 |
| utility | 1.7293 | 0.7786 | 2692320 | 7.392 | 0.3136 | 0.0561 |
| proposed | 1.7417 | 0.7968 | 982636 | 3.460 | 0.0976 | 0.0231 |

Against resource-only scheduling, the proposed method changes:

- RMSE: -0.19% (comparable; sign-flip p-value is not significant).
- MAE: -3.96%.
- Effective communication: -55.67%.
- Modeled energy: -45.06%.
- Maximum relay energy: -29.94%.
- Representation divergence: -81.21%.

## UCI HAR result at correlation 0.9

| Method | Accuracy | Macro-F1 | Worst-client acc. | Effective bits | Energy (J) | Rep. JS |
|---|---:|---:|---:|---:|---:|---:|
| random | 0.8216 | 0.7949 | 0.6479 | 41416156 | 70.83 | 0.0590 |
| resource | 0.8754 | 0.8724 | 0.6814 | 29651089 | 45.92 | 0.1634 |
| utility | 0.7188 | 0.6626 | 0.5682 | 42333751 | 72.35 | 0.0763 |
| proposed | 0.9061 | 0.9060 | 0.7169 | 11638512 | 20.03 | 0.0327 |

Against resource-only scheduling, the proposed method changes:

- Accuracy: +0.0308 absolute (+3.51% relative).
- Macro-F1: +0.0336 absolute.
- Worst-client accuracy: +0.0355 absolute.
- Effective communication: -60.75%.
- Modeled energy: -56.38%.
- Representation divergence: -79.97%.

## ns-3.47 evidence

The ns-3.47 validation replays FL-derived traffic over IEEE 802.15.4/LR-WPAN with CSMA/CA, ACKs, retransmissions and channel contention. The report is stored in `validation/ns3_47_hfl/results/NS3_VALIDATION_REPORT.md`.

The ns-3 evidence validates the communication consequence of the traffic profile. It does not execute the full Python HFL optimizer inside ns-3.

## Statistical robustness

Exact paired sign-flip permutation tests, Holm corrections and bootstrap confidence intervals are stored in `validation/statistics/STATISTICAL_ROBUSTNESS_REPORT.md` and `validation/statistics/statistical_tests.csv`.

## Remaining gap

Physical WSN-node/MCU radio experimentation has not yet been performed. No physical IEEE 802.15.4/ESP/Arduino-class sensor nodes were connected during execution, so the repository does not claim MCU current draw, RSSI/LQI, on-device training time or physical-radio packet measurements.
