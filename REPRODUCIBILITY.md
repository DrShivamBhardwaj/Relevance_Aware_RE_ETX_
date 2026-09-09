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

## Historical public archive

The repository retains an earlier semantic RE-ETX validation generation centered on C1--C7 experiments over ten primary seeds. These files remain useful as an auditable historical validation archive for relevance-aware payload adaptation and residual-energy ETX routing.

They are **not identical to the frozen final J0--J7 journal experiment generation** and must not be presented as though they reproduce every number in the current manuscript.

## Clean-room J0--J7 reconstruction completed on 2026-09-09

A specification-based independent reconstruction of the final J0--J7 study has now been executed across all eight modes and all twenty frozen inferential seeds: **160 trajectories total**.

This reconstruction is explicitly classified as regenerated independent-replication evidence. It is not the lost original runner and it does not replace the frozen manuscript data.

Key audit result:

- average absolute relative deviation across eight headline outcomes for integrated J4--J7: **4.54%**;
- J4: 4.15%; J5: 4.40%; J6: 4.20%; J7: 5.41%.

The reconstructed J4->J5 transition preserves the broad traffic-volume effect. J7->J5 remains nonsignificant across all seven broad network outcomes after Holm correction. Event-targeting behavior is also retained.

### Conventional-selector boundary

The exact final implementation of the older conventional "energy-weighted" CH selector was not recoverable uniquely. Therefore J0/J2/J3 use a documented reconstruction choice: fixed-cardinality residual-energy-proportional sampling without replacement. This is why the reconstruction should not be described as byte-identical end-to-end reproduction.

Repository summaries and provenance metadata are stored at:

`reproducibility/final_study_reconstruction/`

The complete checksummed execution archive additionally contains all 160 trajectory checkpoints, executable reconstruction source, combined/per-mode CSVs, inferential contrasts, environment metadata, and internal SHA-256 checksums.

## Independent IEEE 802.15.4 MAC validation completed

A second, separately implemented event-driven validation was executed for J4, J5, and J6 over the same twenty seeds. It uses unslotted IEEE 802.15.4-style CSMA/CA defaults consistent with the ns-3 LR-WPAN implementation: macMinBE=3, macMaxBE=5, macMaxCSMABackoffs=4, and a 20-symbol unit backoff. It retains the manuscript's 250 kbit/s rate, 800+216-bit fragmentation, and three frame retries.

This is a conservative single-contention-domain stress test and is **not ns-3**. It was run at report periods of 2.5, 5, and 10 s and with PHY frame-error sensitivity at 0%, 1%, and 5%.

At 5 s/report and 1% independent PHY FER:

- J4 RDR = 46.02%, mean MAC delay = 77.62 ms;
- J5 RDR = 78.73%, mean MAC delay = 41.51 ms;
- J6 RDR = 78.54%, mean MAC delay = 41.61 ms.

The J4->J5 RDR/delay/access-load differences remain Holm-significant, while J6->J5 broad MAC differences do not. The traffic-volume interpretation therefore survives this independent contention model.

## ns-3 and physical-hardware status

Neither of the following should currently be claimed:

- **ns-3 validation**: ns-3.47 was verified as the appropriate current LR-WPAN platform, but no ns-3 executable was preinstalled and the official source archive could not be transferred into the execution container because binary network download was blocked.
- **physical FIT IoT-LAB/local-hardware validation**: no authenticated FIT IoT-LAB session or locally attached IEEE 802.15.4 nodes were available to this execution environment.

A FIT IoT-LAB experiment template has been prepared separately for M3/AT86RF231 nodes, including consumption-monitoring and workload-analysis tooling. A real testbed result must only be reported after an authenticated reservation and actual firmware execution.

## Assets still required for exact recovery of the original final study

An exact byte-identical original reproduction would still require recovery of the frozen original versions of:

1. the original J0--J7 Stage-A experiment runner;
2. the exact original conventional energy-weighted CH selector;
3. original final-study matrices including `journal_v1_main_20seed.csv` and the remaining `journal_v1_*` statistical/robustness matrices;
4. original final inferential scripts and their environment snapshot; and
5. checksums tying those original files to the frozen manuscript figures and tables.

Until those originals are recovered, the repository should distinguish clearly among:

1. the historical C1--C7 archive;
2. the frozen manuscript results;
3. the 2026-09-09 clean-room J0--J7 reconstruction; and
4. the independently executed IEEE 802.15.4 contention validator.

Existing historical artifacts must not be relabeled or retroactively modified to make them appear to be lost final-study raw data.