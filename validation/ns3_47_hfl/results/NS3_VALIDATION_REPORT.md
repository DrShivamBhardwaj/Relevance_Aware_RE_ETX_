# ns-3.47 LR-WPAN validation report

This report is generated from **executed ns-3.47 IEEE 802.15.4/LR-WPAN simulations** on the connected Mac.
It is a communication-layer validation of the FL-derived traffic burden, not a full reproduction of the Python HFL optimizer inside ns-3.

Two mappings are reported deliberately:

- **Hop-equivalent**: compressed update bits × mean selected hop count. This avoids embedding ETX retransmission expectation before ns-3 applies its own MAC retries.
- **ETX-equivalent**: HFL effective bits/update (compressed bits × route ETX sum). This is a conservative offered-load stress mapping and may double-count part of retransmission burden.

All results use 10 paired seeds. Official ns-3 LR-WPAN unit suites were also executed separately.

## HOP-equivalent mapping

### dense_fast

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 3934 | 60.09 ± 15.15 | 46.89 ± 4.35 | 0.088 | 2.343 | 265.4 |
| resource | 3431 | 64.89 ± 14.41 | 44.66 ± 4.14 | 0.088 | 2.239 | 226.0 |
| utility | 3710 | 62.06 ± 15.24 | 46.08 ± 3.82 | 0.091 | 2.301 | 246.2 |
| proposed | 1204 | 98.33 ± 2.25 | 13.25 ± 1.22 | 0.025 | 1.321 | 7.6 |

### dense_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 3934 | 85.44 ± 9.97 | 38.29 ± 2.74 | 0.032 | 1.492 | 41.2 |
| resource | 3431 | 85.79 ± 8.99 | 35.99 ± 2.67 | 0.033 | 1.456 | 38.5 |
| utility | 3710 | 86.49 ± 9.36 | 37.59 ± 2.28 | 0.035 | 1.473 | 37.3 |
| proposed | 1204 | 99.47 ± 1.22 | 12.26 ± 0.99 | 0.016 | 1.173 | 1.2 |

### dense_relaxed

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 3934 | 93.95 ± 5.32 | 36.57 ± 1.96 | 0.020 | 1.259 | 8.1 |
| resource | 3431 | 93.67 ± 4.69 | 34.47 ± 2.35 | 0.023 | 1.250 | 7.8 |
| utility | 3710 | 92.72 ± 5.68 | 35.36 ± 1.82 | 0.022 | 1.259 | 9.3 |
| proposed | 1204 | 99.82 ± 0.56 | 11.69 ± 0.96 | 0.009 | 1.095 | 0.2 |

### light_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 3934 | 92.81 ± 7.79 | 36.02 ± 2.87 | 0.017 | 1.240 | 9.2 |
| resource | 3431 | 93.07 ± 7.81 | 33.94 ± 2.81 | 0.018 | 1.234 | 8.3 |
| utility | 3710 | 92.81 ± 7.77 | 35.06 ± 2.75 | 0.020 | 1.239 | 8.8 |
| proposed | 1204 | 100.00 ± 0.00 | 11.56 ± 0.76 | 0.006 | 1.076 | 0.0 |

### scale_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 3934 | 54.80 ± 9.94 | 46.23 ± 3.06 | 0.102 | 2.572 | 341.3 |
| resource | 3431 | 57.72 ± 10.37 | 44.25 ± 3.05 | 0.105 | 2.480 | 305.2 |
| utility | 3710 | 56.78 ± 9.97 | 45.53 ± 3.18 | 0.097 | 2.513 | 318.0 |
| proposed | 1204 | 96.56 ± 3.28 | 13.83 ± 0.94 | 0.034 | 1.448 | 16.1 |

## ETX-equivalent mapping

### dense_fast

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 7518 | 2.96 ± 1.10 | 115.80 ± 15.67 | 0.208 | 4.237 | 1696.5 |
| resource | 6118 | 14.91 ± 4.71 | 86.53 ± 8.74 | 0.166 | 3.530 | 970.1 |
| utility | 6941 | 6.69 ± 1.67 | 99.30 ± 12.28 | 0.188 | 3.928 | 1335.4 |
| proposed | 2215 | 90.37 ± 8.04 | 23.95 ± 2.28 | 0.042 | 1.615 | 49.6 |

### dense_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 7518 | 44.12 ± 14.10 | 83.36 ± 4.96 | 0.094 | 2.305 | 274.9 |
| resource | 6118 | 61.67 ± 15.12 | 65.11 ± 5.25 | 0.064 | 1.959 | 150.9 |
| utility | 6941 | 52.28 ± 14.66 | 75.11 ± 4.84 | 0.079 | 2.145 | 207.0 |
| proposed | 2215 | 97.15 ± 2.93 | 21.69 ± 1.61 | 0.018 | 1.286 | 6.6 |

### dense_relaxed

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 7518 | 74.98 ± 12.51 | 72.69 ± 3.19 | 0.041 | 1.508 | 46.1 |
| resource | 6118 | 82.15 ± 10.66 | 58.84 ± 4.03 | 0.029 | 1.414 | 28.3 |
| utility | 6941 | 79.18 ± 11.33 | 65.88 ± 3.66 | 0.031 | 1.446 | 36.1 |
| proposed | 2215 | 98.24 ± 2.36 | 20.32 ± 1.37 | 0.013 | 1.164 | 2.0 |

### light_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 7518 | 75.09 ± 20.42 | 75.05 ± 7.23 | 0.031 | 1.477 | 41.5 |
| resource | 6118 | 82.63 ± 16.50 | 59.09 ± 5.91 | 0.025 | 1.372 | 25.3 |
| utility | 6941 | 79.21 ± 18.70 | 67.80 ± 7.02 | 0.033 | 1.440 | 31.9 |
| proposed | 2215 | 98.77 ± 1.56 | 20.37 ± 1.80 | 0.008 | 1.146 | 1.4 |

### scale_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 7518 | 7.21 ± 4.56 | 107.12 ± 18.31 | 0.206 | 4.238 | 1758.0 |
| resource | 6118 | 17.79 ± 4.47 | 77.67 ± 9.63 | 0.169 | 3.629 | 1071.8 |
| utility | 6941 | 10.94 ± 5.50 | 91.87 ± 15.21 | 0.185 | 3.940 | 1410.8 |
| proposed | 2215 | 86.91 ± 6.80 | 25.16 ± 1.61 | 0.057 | 1.802 | 70.0 |

## Interpretation boundary

The hop-equivalent mapping is the more conservative primary network validation because it lets ns-3 generate MAC retransmissions itself.
The ETX-equivalent mapping is retained as a sensitivity analysis because ETX is already an expected-transmission measure.
Therefore, claims about absolute network superiority should be based on the hop-equivalent results; the ETX-equivalent results show sensitivity to the traffic mapping.

The proposed learning policy is not expected to minimize every pure MAC metric: it deliberately trades some network cost for utility-target participation and relay-load control.
The correct claim is therefore Pareto-oriented rather than an unconditional network-performance win.