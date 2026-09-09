# Reproducibility Status

## Canonical manuscript

Current source:

- `manuscript/main.tex`
- `manuscript/references.bib`

Only the unversioned canonical manuscript source should be maintained on `main`.

## Frozen final-study design

The journal study uses twenty inferential seeds:

`11, 23, 42, 67, 101, 137, 173, 211, 257, 307, 349, 401, 457, 503, 557, 601, 653, 701, 757, 809`

Calibration seeds are `3, 5, 7, 19, 31`.

The frozen design includes J0--J7 attribution, equal 150-objective-evaluation optimizer comparisons, reclustering sensitivity, CH-count sensitivity, sink-distance stress, density-preserving deployment expansion, EXT-EEL2024-H comparison, and IEEE 802.15.4-style contention sensitivity.

## Historical public archive

The earlier public simulator/results generation is centered on C1--C7 and ten primary seeds. It remains an auditable historical archive, but it is not identical to the final J0--J7 journal experiment generation and must not be presented as byte-identical support for every frozen manuscript number.

## Clean-room J0--J7 reconstruction - completed 2026-09-09

A specification-based independent reconstruction was executed across all eight modes and all twenty frozen inferential seeds: **160 trajectories**.

This is regenerated independent-replication evidence, not the lost original runner/raw archive. The integrated J4--J7 modes show about **4.54% average absolute relative deviation** across eight headline outcomes. The broad J4->J5 traffic-volume effect is retained, while J7->J5 remains nonsignificant across the seven broad network outcomes after Holm correction.

The exact historical conventional "energy-weighted" CH selector could not be uniquely recovered; J0/J2/J3 therefore use a documented residual-energy-proportional fixed-cardinality reconstruction choice.

Repository records: `reproducibility/final_study_reconstruction/`.

## Independent IEEE 802.15.4 MAC validator - completed

A separate event-driven unslotted CSMA/CA validator was executed for J4/J5/J6 over the same twenty seeds. It uses macMinBE=3, macMaxBE=5, macMaxCSMABackoffs=4, 20-symbol unit backoff, the manuscript framing/retry logic, three offered-load levels, and PHY frame-error sensitivity.

This validator is **not ns-3** and is **not hardware evidence**. At 5 s/report and the central FER condition it produced mean RDR of 46.02%, 78.73%, and 78.54% for J4, J5, and J6, respectively, retaining the traffic-volume interpretation.

## Executed ns-3.47 LR-WPAN validation - completed 2026-09-09

A real ns-3.47 optimized LR-WPAN build was installed and executed on Apple Silicon. Before the paper-specific scenario, the following **11/11 official LR-WPAN test suites passed with zero failed/crashed suites**:

- lr-wpan-ack
- lr-wpan-cca-test
- lr-wpan-collision
- lr-wpan-energy-detection
- lr-wpan-error-model
- lr-wpan-ifs-test
- lr-wpan-mac-test
- lr-wpan-packet
- lr-wpan-phy-test
- lr-wpan-slotted-csmaca
- lr-wpan-spectrum-value-helper

The custom validation then completed **180/180 runs**:

- 20 paired seeds
- J4, J5, J6
- report periods 2.5, 5, and 10 s
- 100 sensor nodes plus one sink in a controlled single-contention-domain geometry
- unslotted CSMA/CA: macMinBE=3, macMaxBE=5, macMaxCSMABackoffs=4
- ACK requested, macMaxFrameRetries=3
- J4 4000-bit reports, J6 1712-bit reports, J5 reconstructed seed-specific mean relevance-aware payloads

### Primary 5 s/report ns-3 means

| Mode | RDR (%) | Delay (ms) | Retries/frame | CSMA cycles/frame | Access failures/report |
|---|---:|---:|---:|---:|---:|
| J4 | 62.152 | 45.009 | 0.0888 | 2.3056 | 0.5774 |
| J5 | 91.862 | 21.731 | 0.0459 | 1.5752 | 0.0889 |
| J6 | 91.939 | 21.717 | 0.0455 | 1.5737 | 0.0873 |

For J5-J4 at 5 s/report, the paired RDR difference is **+29.709 percentage points** (95% CI 27.589--31.830, Holm p=8.32e-17) and delivered-report delay changes by **-23.278 ms** (95% CI -23.864 to -22.693, Holm p=4.09e-25). Retries/frame, CSMA cycles/frame, and access failures/report also remain Holm-significant. All five J5-J6 Holm-adjusted p values are 1.0.

The same qualitative separation persists at 2.5 and 10 s/report.

### ns-3 archive

`validation/ns3_47_lrwpan/` contains:

- `j4j5j6-lrwpan-validation.cc` - executed custom C++ scenario
- `run_ns3_validation.py` - exact execution runner
- `analyze_ns3_validation.py` - statistical/figure analysis
- `results/ns3_j4j5j6_20seed_load_sweep.csv` - all 180 raw runs
- `results/ns3_group_summary.csv`
- `results/ns3_paired_contrasts.csv`
- `figures/` - vector PDF and 600-dpi PNG load-sensitivity figures
- `official_lr_wpan_tests.log`
- `run.log`
- `analysis_stdout.txt`
- `NS3_EXECUTION_MANIFEST.json`
- `ENVIRONMENT_AND_CHECKSUMS.txt`
- `NS3_VALIDATION_REPORT.md`

## ns-3 claim boundary

The executed ns-3 family validates the traffic-volume causal direction under an independent IEEE 802.15.4 LR-WPAN MAC/PHY stack. It does **not** reproduce the complete multihop AD-CWOA/RE-ETX network dynamics and is not used for the manuscript's radio-energy ledger. Absolute ns-3 delivery/delay values therefore need not equal the earlier contention abstraction.

## Physical-hardware status

No authenticated FIT IoT-LAB or local physical IEEE 802.15.4 experiment has been executed. Hardware validation must not be claimed unless a real reservation/device run is subsequently completed.

## Assets still missing for byte-identical recovery of the original final J0--J7 study

Exact recovery would still require the frozen original versions of the final J0--J7 Stage-A runner, the exact conventional energy-weighted selector, the original `journal_v1_*` raw/statistical matrices, the original final inferential scripts/environment, and checksums tying those files to the frozen manuscript.

Accordingly, the repository preserves the distinction among historical C1--C7 evidence, frozen manuscript values, the clean-room J0--J7 reconstruction, the independent contention validator, and the executed ns-3.47 LR-WPAN validation.
