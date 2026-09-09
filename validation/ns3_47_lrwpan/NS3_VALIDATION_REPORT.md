# Executed ns-3.47 LR-WPAN validation report

## Status

- ns-3 version: 3.47, optimized Apple Silicon build.
- Official LR-WPAN unit suites: 11/11 passed before the custom experiment.
- Custom validation: 180/180 runs completed (20 paired seeds x J4/J5/J6 x 3 report periods).
- This is an independent IEEE 802.15.4 MAC/PHY contention validation, not a reproduction of the original full multihop WSN simulator.

## Design

- 100 sensor nodes plus one sink in a controlled single-contention-domain geometry.
- Unslotted CSMA/CA with macMinBE=3, macMaxBE=5, macMaxCSMABackoffs=4.
- ACK requested; macMaxFrameRetries=3.
- Paper framing retained as 800 payload bits per fragment. A 16-byte synthetic non-MAC header plus ns-3 MAC/FCS overhead approximates the paper's 216-bit per-frame overhead while respecting the IEEE 802.15.4 PHY frame-size ceiling.
- Paired seeds use identical node geometry/report phases across J4, J5, and J6. J5 uses the reconstructed seed-specific mean payload; J4 uses 4000 bits and J6 uses 1712 bits.
- Report periods 2.5, 5, and 10 s provide high, central, and low offered-load conditions.

## Central 5 s/report results

| Mode | Report RDR (%) | Delay (ms) | Retries/frame | CSMA cycles/frame | Access failures/report |
|---|---:|---:|---:|---:|---:|
| J4 | 62.152 | 45.009 | 0.0888 | 2.3056 | 0.5774 |
| J5 | 91.862 | 21.731 | 0.0459 | 1.5752 | 0.0889 |
| J6 | 91.939 | 21.717 | 0.0455 | 1.5737 | 0.0873 |

## Paired central contrasts

| Contrast | Metric | Mean difference | 95% CI | Holm p | dz |
|---|---|---:|---:|---:|---:|
| J5-J4 | Report RDR (pp) | 29.7094 | [27.5886, 31.8302] | 8.32e-17 | 6.556 |
| J5-J4 | Delivered-report delay (ms) | -23.2782 | [-23.8638, -22.6926] | 4.09e-25 | -18.603 |
| J5-J4 | MAC retries/frame | -0.0429 | [-0.0488, -0.0370] | 3.9e-12 | -3.420 |
| J5-J4 | CSMA cycles/frame | -0.7304 | [-0.7811, -0.6798] | 6.45e-17 | -6.750 |
| J5-J4 | Channel-access failures/report | -0.4885 | [-0.5350, -0.4420] | 1.13e-14 | -4.917 |
| J5-J6 | Report RDR (pp) | -0.0770 | [-0.3624, 0.2084] | 1 | -0.126 |
| J5-J6 | Delivered-report delay (ms) | 0.0139 | [-0.1185, 0.1463] | 1 | 0.049 |
| J5-J6 | MAC retries/frame | 0.0004 | [-0.0028, 0.0036] | 1 | 0.055 |
| J5-J6 | CSMA cycles/frame | 0.0015 | [-0.0053, 0.0083] | 1 | 0.104 |
| J5-J6 | Channel-access failures/report | 0.0015 | [-0.0018, 0.0049] | 1 | 0.215 |

## Interpretation

At the central load, J5 retains a large delivery advantage over J4 and materially reduces delivered-report service delay, retry burden, CSMA/CA access cycles, and channel-access failures. J6 remains close to J5 because both generate three IEEE 802.15.4 data frames per report under this framing. This independently supports the paper's attribution that broad contention gains arise mainly from source-traffic reduction rather than relevance-directed source mapping.

Absolute ns-3 values are not expected to equal the paper's earlier contention abstraction because this experiment uses the ns-3 LR-WPAN MAC/PHY implementation, built-in ACK/retry timing, a controlled one-hop contention domain, and an IEEE 802.15.4 frame-size ceiling. The validation target is robustness of the causal direction under an independent protocol stack, not numerical reproduction of the abstraction.

## Claim boundary

This experiment supports an executed ns-3.47 IEEE 802.15.4/LR-WPAN contention-validation claim. It does not constitute physical-hardware validation, a complete emulation of the paper's multihop clustering/routing dynamics, or a radio-energy validation. The ns-3 LR-WPAN module does not provide the paper's full radio-energy ledger; therefore energy outcomes remain sourced from the original simulator and analytical sensitivities.
