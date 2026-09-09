# Reproducibility Status

## Current manuscript

Canonical manuscript source:

- `manuscript/main.tex`
- `manuscript/references.bib`

Manuscript title:

**Controlled Attribution of Cross-Layer Gains and Robustness Limits in IoT Wireless Sensor Networks: AD-CWOA Clustering, Relevance-Aware Reporting, and RE-ETX Routing**

Only the unversioned canonical manuscript source should be maintained on `main`.

## Frozen final-study design

The final journal study uses twenty inferential seed/topology trajectories:

`11, 23, 42, 67, 101, 137, 173, 211, 257, 307, 349, 401, 457, 503, 557, 601, 653, 701, 757, 809`

The disjoint calibration seeds are:

`3, 5, 7, 19, 31`

The final design includes:

- J0--J7 controlled attribution modes;
- AD-CWOA, original CWOA, PSO, and random-search optimizer comparisons;
- a hard budget of 150 clustering-objective evaluations per optimization decision;
- state-triggered versus periodic reclustering;
- cluster-count sensitivity;
- sink-distance/routing-geometry stress;
- density-preserving deployment-size stress;
- traffic-matched EXT-EEL2024-H external validation; and
- IEEE 802.15.4-style contention sensitivity.

## Public archive currently present in this repository

The repository retains an earlier semantic RE-ETX validation generation centered on C1--C7 experiments over ten primary seeds. These files remain useful as an auditable historical validation archive for relevance-aware payload adaptation and residual-energy ETX routing.

They are **not identical to the frozen final J0--J7 journal experiment generation** and must not be presented as though they reproduce every number in the current manuscript.

## Assets required for exact public reproduction of the final study

An exact end-to-end public reproduction package should contain the frozen final versions of:

1. the J0--J7 Stage-A experiment runner;
2. AD-CWOA, CWOA, PSO, and random-search clustering implementations;
3. state-triggered and periodic reclustering implementations;
4. the alive-neighbor relevance estimator used by the final study;
5. J6 byte-matched and J7 shuffled-mapping controls;
6. all twenty inferential trajectories and the five calibration-seed outputs;
7. the original final-study matrices, including:
   - `journal_v1_main_20seed.csv`
   - `journal_v1_optimizer_objective_checkpoints.csv`
   - `journal_v1_optimizer_summary_mean.csv`
   - `journal_v1_route_stress_summary_mean.csv`
   - `journal_v1_scale_summary_mean.csv`
   - `journal_v1_ext_eel2024_inference.csv`
   - `journal_v1_mac_contention_summary.csv`
   - `journal_v1_mac_contention_contrasts.csv`
8. the final inferential/statistical scripts;
9. environment and dependency snapshots; and
10. checksums tying code, raw matrices, statistical outputs, figures, and manuscript claims together.

Until those exact frozen final-study assets are synchronized, the repository should be cited as the project/code archive rather than as a complete public reproduction of every final manuscript result.

## Scientific reporting boundary

The current manuscript therefore uses conservative Data Availability and Code Availability language. Existing repository artifacts should not be relabeled or retroactively modified to make them appear to be final-study raw data. If the original final-study runners and matrices are recovered, they should be added as a clearly frozen reproduction package with checksums and a tagged release.