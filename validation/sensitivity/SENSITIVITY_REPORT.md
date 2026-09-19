# Parameter-sensitivity report

This report uses the executed 10-seed joint grid stored in `results/intel_lab/joint_grid.csv` and `results/uci_har/joint_grid.csv`. It varies relay-pressure weight and compression-distortion weight for the proposed scheduler at strong correlation 0.9.

The selected operating point is `relay_pressure_weight = 3.0` and `compression_distortion_weight = 0.10`. This point is not a single-metric optimum; it is a conservative cross-dataset operating point emphasizing low communication/energy while preserving learning and representation.

## intel_lab

| Rank | Relay weight | Compression beta | RMSE | Effective bits | Energy | Max relay E | Rep. JS | Jain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 1.0 | 0.1 | 1.7427 | 992796 | 3.483 | 0.1004 | 0.0201 | 0.6612 |
| 2 | 2.0 | 0.1 | 1.7410 | 988334 | 3.473 | 0.0999 | 0.0218 | 0.6558 |
| 3 | 5.0 | 0.1 | 1.7423 | 988117 | 3.473 | 0.0981 | 0.0220 | 0.6667 |
| 4 | 3.0 | 0.1 | 1.7417 | 982636 | 3.460 | 0.0976 | 0.0231 | 0.6605 |
| 5 | 1.0 | 0.2 | 1.7374 | 1209966 | 3.983 | 0.1119 | 0.0233 | 0.6638 |
| 6 | 2.0 | 0.2 | 1.7403 | 1200693 | 3.962 | 0.1079 | 0.0235 | 0.6641 |

## uci_har

| Rank | Relay weight | Compression beta | Accuracy | Effective bits | Energy | Max relay E | Rep. JS | Jain |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3.0 | 0.1 | 0.9061 | 11638512 | 20.030 | 1.4152 | 0.0327 | 0.8318 |
| 2 | 2.0 | 0.2 | 0.9051 | 12264574 | 21.009 | 1.4506 | 0.0278 | 0.8360 |
| 3 | 2.0 | 0.1 | 0.9037 | 11747599 | 20.241 | 1.4657 | 0.0280 | 0.8327 |
| 4 | 1.0 | 0.2 | 0.9055 | 12380423 | 21.237 | 1.5295 | 0.0279 | 0.8273 |
| 5 | 5.0 | 0.1 | 0.9032 | 11510271 | 19.758 | 1.3113 | 0.0379 | 0.8169 |
| 6 | 1.0 | 0.1 | 0.9041 | 11842365 | 20.467 | 1.5836 | 0.0279 | 0.8354 |

## Interpretation

Lower compression-distortion weights substantially reduce traffic and modeled energy. Relay pressure materially reduces hotspot burden, especially in the ablation comparisons. A moderate relay-pressure value avoids over-concentrating traffic while preserving learning quality.

The grid supports retaining both adaptive compression and relay pressure. The frozen setting `(3.0, 0.10)` is used in the final real-data reports; it is reported as an engineering operating point, not a universal optimum.
