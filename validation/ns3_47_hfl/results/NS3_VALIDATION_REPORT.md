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
| random | 4333 | 48.99 ± 11.51 | 57.23 ± 4.76 | 0.113 | 2.569 | 373.4 |
| resource | 3679 | 64.67 ± 11.97 | 45.62 ± 3.53 | 0.083 | 2.206 | 218.3 |
| utility | 3930 | 61.67 ± 12.66 | 47.01 ± 3.38 | 0.084 | 2.272 | 241.5 |
| proposed | 4138 | 48.82 ± 12.59 | 56.32 ± 4.54 | 0.109 | 2.526 | 362.5 |

### dense_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 4333 | 79.25 ± 14.54 | 47.30 ± 3.94 | 0.049 | 1.637 | 60.2 |
| resource | 3679 | 85.26 ± 12.18 | 38.51 ± 3.92 | 0.040 | 1.514 | 40.9 |
| utility | 3930 | 85.31 ± 12.22 | 39.64 ± 3.69 | 0.039 | 1.539 | 41.9 |
| proposed | 4138 | 79.96 ± 14.64 | 46.24 ± 4.17 | 0.050 | 1.617 | 60.2 |

### dense_relaxed

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 4333 | 90.50 ± 10.59 | 42.67 ± 4.02 | 0.027 | 1.308 | 12.7 |
| resource | 3679 | 93.92 ± 7.66 | 35.24 ± 3.12 | 0.019 | 1.230 | 7.8 |
| utility | 3930 | 93.12 ± 9.42 | 35.88 ± 2.71 | 0.015 | 1.239 | 8.8 |
| proposed | 4138 | 91.10 ± 11.39 | 41.79 ± 3.55 | 0.024 | 1.288 | 12.3 |

### light_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 4333 | 90.53 ± 9.89 | 43.02 ± 5.11 | 0.018 | 1.280 | 12.0 |
| resource | 3679 | 93.33 ± 8.07 | 35.65 ± 3.83 | 0.020 | 1.247 | 8.1 |
| utility | 3930 | 93.25 ± 8.85 | 36.77 ± 3.80 | 0.019 | 1.255 | 8.1 |
| proposed | 4138 | 89.56 ± 10.01 | 41.97 ± 4.61 | 0.020 | 1.280 | 12.9 |

### scale_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 4333 | 44.74 ± 9.02 | 54.89 ± 3.38 | 0.121 | 2.761 | 457.1 |
| resource | 3679 | 58.66 ± 8.29 | 44.95 ± 2.96 | 0.099 | 2.425 | 289.8 |
| utility | 3930 | 57.26 ± 8.69 | 46.00 ± 3.01 | 0.100 | 2.474 | 310.4 |
| proposed | 4138 | 45.66 ± 7.48 | 54.00 ± 3.40 | 0.118 | 2.716 | 441.4 |

## ETX-equivalent mapping

### dense_fast

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 8572 | 0.99 ± 0.62 | 120.29 ± 45.17 | 0.223 | 4.544 | 2138.7 |
| resource | 6752 | 8.99 ± 4.64 | 102.34 ± 12.68 | 0.187 | 3.806 | 1250.1 |
| utility | 7557 | 3.75 ± 3.66 | 116.66 ± 17.35 | 0.202 | 4.170 | 1655.1 |
| proposed | 6364 | 16.54 ± 4.11 | 86.53 ± 10.82 | 0.162 | 3.484 | 947.4 |

### dense_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 8572 | 35.88 ± 11.67 | 96.85 ± 6.09 | 0.103 | 2.451 | 333.1 |
| resource | 6752 | 53.86 ± 15.83 | 73.94 ± 4.65 | 0.076 | 2.057 | 182.7 |
| utility | 7557 | 45.53 ± 15.08 | 84.46 ± 6.10 | 0.090 | 2.223 | 246.3 |
| proposed | 6364 | 60.92 ± 14.95 | 67.68 ± 5.10 | 0.068 | 1.955 | 142.6 |

### dense_relaxed

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 8572 | 68.82 ± 18.25 | 83.98 ± 4.89 | 0.041 | 1.595 | 59.3 |
| resource | 6752 | 78.73 ± 16.40 | 66.77 ± 4.68 | 0.034 | 1.463 | 37.2 |
| utility | 7557 | 73.91 ± 17.91 | 75.14 ± 5.11 | 0.040 | 1.530 | 47.6 |
| proposed | 6364 | 81.39 ± 15.42 | 59.76 ± 4.48 | 0.029 | 1.420 | 30.6 |

### light_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 8572 | 72.11 ± 20.07 | 82.81 ± 7.69 | 0.037 | 1.499 | 48.7 |
| resource | 6752 | 82.28 ± 15.85 | 66.28 ± 7.05 | 0.024 | 1.360 | 27.1 |
| utility | 7557 | 77.81 ± 17.97 | 73.24 ± 6.16 | 0.029 | 1.412 | 36.3 |
| proposed | 6364 | 83.51 ± 15.05 | 60.03 ± 6.15 | 0.028 | 1.351 | 22.9 |

### scale_nominal

| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |
|---|---:|---:|---:|---:|---:|---:|
| random | 8572 | 2.89 ± 2.04 | 111.15 ± 14.21 | 0.216 | 4.550 | 2201.3 |
| resource | 6752 | 10.11 ± 2.11 | 88.97 ± 6.02 | 0.185 | 3.907 | 1349.9 |
| utility | 7557 | 5.57 ± 1.74 | 101.11 ± 15.91 | 0.209 | 4.261 | 1752.8 |
| proposed | 6364 | 16.29 ± 3.28 | 81.23 ± 6.69 | 0.169 | 3.635 | 1057.5 |

## Interpretation boundary

The hop-equivalent mapping is the more conservative primary network validation because it lets ns-3 generate MAC retransmissions itself.
The ETX-equivalent mapping is retained as a sensitivity analysis because ETX is already an expected-transmission measure.
Therefore, claims about absolute network superiority should be based on the hop-equivalent results; the ETX-equivalent results show sensitivity to the traffic mapping.

The proposed learning policy is not expected to minimize every pure MAC metric: it deliberately trades some network cost for statistical representation and relay-energy protection.
The correct claim is therefore Pareto-oriented rather than an unconditional network-performance win.