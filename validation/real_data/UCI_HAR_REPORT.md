# UCI HAR held-out evaluation report

The official UCI train/test partitions are recombined because each subject is modeled as a persistent FL client. Within each subject, ordered windows are assigned to contiguous 10-window blocks; one of every five blocks is held out, and one adjacent window is purged from training at each test boundary to prevent 50%-overlap leakage. This is a within-client blocked holdout, not the canonical unseen-subject UCI benchmark. Final comparisons use 10 evaluation seeds that are disjoint from the 10 tuning seeds.

| Method | Accuracy | Macro-F1 | Worst-client acc. | Effective Mbit | Energy (J) | Max relay E (J) | Utility-target JS | Class-coverage JS | Jain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| random | 0.8276 ± 0.0189 | 0.8129 ± 0.0247 | 0.5133 ± 0.0348 | 39.653 | 67.30 | 3.342 | 0.0731 | 0.000033 | 0.8933 |
| resource | 0.8641 ± 0.0114 | 0.8565 ± 0.0140 | 0.5467 ± 0.0227 | 28.785 | 44.73 | 0.459 | 0.1716 | 0.000081 | 0.6658 |
| utility | 0.7956 ± 0.0354 | 0.7564 ± 0.0508 | 0.4910 ± 0.0464 | 40.942 | 69.91 | 4.045 | 0.0562 | 0.000062 | 0.6629 |
| random_adaptive | 0.8792 ± 0.0029 | 0.8749 ± 0.0033 | 0.5583 ± 0.0219 | 12.397 | 21.32 | 1.630 | 0.0535 | 0.000022 | 0.8933 |
| resource_adaptive | 0.8751 ± 0.0047 | 0.8698 ± 0.0057 | 0.5567 ± 0.0254 | 8.872 | 14.34 | 0.170 | 0.1553 | 0.000075 | 0.6703 |
| utility_adaptive | 0.8779 ± 0.0082 | 0.8736 ± 0.0086 | 0.5931 ± 0.0392 | 12.645 | 21.81 | 1.936 | 0.0421 | 0.000034 | 0.7110 |
| proposed_fixed_comp | 0.7947 ± 0.0253 | 0.7570 ± 0.0392 | 0.5032 ± 0.0512 | 31.232 | 49.26 | 0.807 | 0.1010 | 0.000078 | 0.7032 |
| fedcg_adapted | 0.8760 ± 0.0033 | 0.8705 ± 0.0041 | 0.5367 ± 0.0270 | 9.311 | 15.34 | 0.643 | 0.1341 | 0.000070 | 0.6979 |
| proposed | 0.8867 ± 0.0012 | 0.8827 ± 0.0011 | 0.5683 ± 0.0294 | 11.253 | 19.20 | 1.242 | 0.0275 | 0.000064 | 0.8172 |

## Matched-compression interpretation

The adaptive controls receive the same client-specific Top-k ratio rule as the proposed controller. proposed_fixed_comp isolates the selector/queue mechanisms at a fixed 50% Top-k ratio. fedcg_adapted is a favorable gradient-diversity/capability comparator inspired by FedCG and is explicitly not claimed as an exact reproduction of its original single-level communication model.

## Ablation

| Variant | Accuracy | Effective Mbit | Energy (J) | Max relay E (J) | Utility-target JS | Class-coverage JS |
|---|---:|---:|---:|---:|---:|---:|
| proposed | 0.8867 | 11.253 | 19.20 | 1.242 | 0.0275 | 0.000064 |
| proposed_no_rep | 0.8839 | 10.070 | 16.66 | 0.571 | 0.0854 | 0.000098 |
| proposed_fixed_comp | 0.7947 | 31.232 | 49.26 | 0.807 | 0.1010 | 0.000078 |
| proposed_age_only | 0.8861 | 11.278 | 19.26 | 1.265 | 0.0268 | 0.000057 |
| proposed_no_relay | 0.8824 | 11.681 | 20.09 | 1.599 | 0.0187 | 0.000051 |

Paired held-out-seed exact sign-flip tests and Holm-adjusted p-values are stored in validation/statistics/statistical_tests.csv.