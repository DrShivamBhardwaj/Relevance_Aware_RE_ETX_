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
| random | 3970 | 63.07 ± 12.48 | 48.16 ± 3.33 | 0.094 | 2.309 | 234.6 |
| resource | 3476 | 66.25 ± 12.07 | 44.65 ± 3.58 | 0.087 | 2.178 | 207.4 |
| utility | 3796 | 63.84 ± 12.73 | 46.09 ± 3.33 | 0.087 | 2.235 | 226.2 |
| proposed | 1219 | 98.09 ± 3.51 | 13.46 ± 2.07 | 0.025 | 1.345 | 8.8 |

### dense_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 3970 | 84.12 ± 13.69 | 39.69 ± 3.42 | 0.040 | 1.544 | 44.1 |
| resource | 3476 | 86.49 ± 12.05 | 37.45 ± 3.61 | 0.036 | 1.497 | 36.5 |
| utility | 3796 | 85.09 ± 12.42 | 39.05 ± 3.67 | 0.040 | 1.524 | 41.4 |
| proposed | 1219 | 99.47 ± 1.52 | 12.02 ± 1.34 | 0.009 | 1.138 | 1.2 |

### dense_relaxed

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 3970 | 93.56 ± 8.79 | 36.28 ± 2.87 | 0.018 | 1.251 | 8.7 |
| resource | 3476 | 94.44 ± 8.00 | 34.56 ± 3.56 | 0.022 | 1.235 | 7.7 |
| utility | 3796 | 93.75 ± 8.04 | 35.62 ± 2.97 | 0.018 | 1.238 | 8.0 |
| proposed | 1219 | 100.00 ± 0.00 | 11.31 ± 0.61 | 0.005 | 1.034 | 0.0 |

### light_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 3970 | 92.72 ± 9.32 | 36.90 ± 3.83 | 0.016 | 1.254 | 8.7 |
| resource | 3476 | 93.60 ± 7.71 | 34.89 ± 4.15 | 0.019 | 1.245 | 7.7 |
| utility | 3796 | 93.42 ± 8.13 | 36.22 ± 3.87 | 0.019 | 1.249 | 7.9 |
| proposed | 1219 | 100.00 ± 0.00 | 11.62 ± 1.28 | 0.004 | 1.073 | 0.0 |

### scale_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 3970 | 56.05 ± 9.07 | 46.15 ± 2.77 | 0.102 | 2.492 | 311.3 |
| resource | 3476 | 60.70 ± 7.62 | 44.23 ± 2.82 | 0.097 | 2.379 | 271.7 |
| utility | 3796 | 57.41 ± 8.51 | 45.14 ± 2.59 | 0.099 | 2.444 | 297.2 |
| proposed | 1219 | 97.48 ± 2.06 | 13.75 ± 0.86 | 0.029 | 1.398 | 11.6 |

## ETX-equivalent mapping

### dense_fast

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 7825 | 3.40 ± 3.11 | 121.02 ± 20.92 | 0.199 | 4.191 | 1692.5 |
| resource | 6433 | 10.75 ± 4.11 | 96.39 ± 14.05 | 0.183 | 3.733 | 1201.2 |
| utility | 7237 | 4.34 ± 3.21 | 115.66 ± 13.68 | 0.208 | 4.142 | 1609.7 |
| proposed | 2268 | 90.44 ± 8.01 | 24.74 ± 2.81 | 0.048 | 1.636 | 47.0 |

### dense_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 7825 | 44.87 ± 13.95 | 86.53 ± 5.39 | 0.093 | 2.273 | 255.1 |
| resource | 6433 | 55.75 ± 14.54 | 73.97 ± 5.59 | 0.082 | 2.043 | 175.9 |
| utility | 7237 | 47.94 ± 15.07 | 83.32 ± 6.31 | 0.092 | 2.215 | 235.1 |
| proposed | 2268 | 96.14 ± 5.74 | 21.77 ± 2.42 | 0.020 | 1.297 | 9.6 |

### dense_relaxed

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 7825 | 73.47 ± 17.87 | 75.95 ± 4.56 | 0.037 | 1.536 | 47.7 |
| resource | 6433 | 79.09 ± 16.07 | 65.62 ± 5.38 | 0.035 | 1.458 | 35.8 |
| utility | 7237 | 73.58 ± 16.53 | 73.00 ± 4.33 | 0.039 | 1.523 | 47.7 |
| proposed | 2268 | 99.47 ± 1.13 | 20.26 ± 1.98 | 0.009 | 1.106 | 0.6 |

### light_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 7825 | 77.72 ± 16.89 | 75.04 ± 7.10 | 0.030 | 1.429 | 35.5 |
| resource | 6433 | 81.32 ± 17.26 | 64.03 ± 5.52 | 0.027 | 1.359 | 26.6 |
| utility | 7237 | 79.12 ± 16.62 | 72.73 ± 7.23 | 0.030 | 1.403 | 32.8 |
| proposed | 2268 | 99.21 ± 1.68 | 20.65 ± 2.17 | 0.013 | 1.132 | 0.9 |

### scale_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 7825 | 5.18 ± 1.72 | 103.38 ± 15.79 | 0.204 | 4.273 | 1785.1 |
| resource | 6433 | 11.01 ± 2.01 | 89.90 ± 8.35 | 0.185 | 3.843 | 1307.2 |
| utility | 7237 | 5.92 ± 1.87 | 102.32 ± 16.13 | 0.208 | 4.205 | 1708.2 |
| proposed | 2268 | 85.99 ± 6.50 | 25.26 ± 1.67 | 0.051 | 1.802 | 72.5 |

## Interpretation boundary

The hop-equivalent mapping is the more conservative primary network validation because it lets ns-3 generate MAC retransmissions itself.
The ETX-equivalent mapping is retained as a sensitivity analysis because ETX is already an expected-transmission measure.
Therefore, claims about absolute network superiority should be based on the hop-equivalent results; the ETX-equivalent results show sensitivity to the traffic mapping.

The proposed learning policy is not expected to minimize every pure MAC metric: it deliberately trades some network cost for statistical representation and relay-energy protection.
The correct claim is therefore Pareto-oriented rather than an unconditional network-performance win.