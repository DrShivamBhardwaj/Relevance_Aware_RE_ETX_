# Intel Berkeley Lab WSN held-out evaluation report

Final comparisons use 10 evaluation seeds that are disjoint from the 10 tuning seeds. Utility-target JS uses corrected cloud-level client coefficients after both edge and cloud normalization. Temperature-coverage JS is independent of the controller target and measures how the cloud-influence-weighted client temperature distribution matches the pooled training distribution.

| Method | RMSE (C) | MAE (C) | Effective Mbit | Energy (J) | Max relay E (J) | Utility-target JS | Temp.-coverage JS | Jain |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| random | 1.7427 ± 0.0029 | 0.8126 ± 0.0084 | 2.552 | 7.071 | 0.2661 | 0.0642 | 0.00020 | 0.8858 |
| resource | 1.7473 ± 0.0018 | 0.8369 ± 0.0048 | 2.230 | 6.328 | 0.1378 | 0.1057 | 0.00082 | 0.7006 |
| utility | 1.7293 ± 0.0015 | 0.7772 ± 0.0051 | 2.687 | 7.380 | 0.3234 | 0.0409 | 0.00416 | 0.5609 |
| random_adaptive | 1.7543 ± 0.0079 | 0.8272 ± 0.0174 | 0.977 | 3.446 | 0.0963 | 0.0540 | 0.00020 | 0.8858 |
| resource_adaptive | 1.7285 ± 0.0034 | 0.7638 ± 0.0114 | 0.916 | 3.307 | 0.0902 | 0.0843 | 0.00034 | 0.8187 |
| utility_adaptive | 1.7422 ± 0.0042 | 0.8003 ± 0.0102 | 1.060 | 3.637 | 0.1127 | 0.0325 | 0.00472 | 0.5832 |
| proposed_fixed_comp | 1.7369 ± 0.0029 | 0.8048 ± 0.0080 | 2.373 | 6.658 | 0.1430 | 0.0283 | 0.00258 | 0.6752 |
| fedcg_adapted | 1.7362 ± 0.0023 | 0.7903 ± 0.0065 | 0.980 | 3.454 | 0.0964 | 0.0911 | 0.00027 | 0.8191 |
| proposed | 1.7348 ± 0.0030 | 0.7790 ± 0.0060 | 0.992 | 3.482 | 0.0969 | 0.0118 | 0.00375 | 0.6627 |

## Matched-compression interpretation

The adaptive controls use the same client-specific Top-k ratio rule as the proposed method while preserving their original random/resource/utility selection logic. proposed_fixed_comp fixes the proposed selector at 50% Top-k. fedcg_adapted is a favorable gradient-diversity/capability comparator inspired by FedCG; it is not represented as an exact reproduction because FedCG does not assume this multi-hop HFL topology.

## Ablation

| Variant | RMSE | Effective Mbit | Energy (J) | Max relay E (J) | Utility-target JS | Temp.-coverage JS |
|---|---:|---:|---:|---:|---:|---:|
| proposed | 1.7348 | 0.992 | 3.482 | 0.0969 | 0.0118 | 0.00375 |
| proposed_no_rep | 1.7353 | 1.023 | 3.553 | 0.0990 | 0.0318 | 0.00465 |
| proposed_fixed_comp | 1.7369 | 2.373 | 6.658 | 0.1430 | 0.0283 | 0.00258 |
| proposed_age_only | 1.7356 | 0.991 | 3.479 | 0.0973 | 0.0115 | 0.00365 |
| proposed_no_relay | 1.7359 | 1.044 | 3.601 | 0.1062 | 0.0112 | 0.00359 |

Paired held-out-seed exact sign-flip tests and Holm-adjusted p-values are stored in validation/statistics/statistical_tests.csv.