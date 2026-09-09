# Controlled Attribution and Robustness in IoT Wireless Sensor Networks

This repository contains the WSN simulation code, archived validation evidence, and the canonical manuscript source for:

**Controlled Attribution of Cross-Layer Gains and Robustness Limits in IoT Wireless Sensor Networks: AD-CWOA Clustering, Relevance-Aware Reporting, and RE-ETX Routing**

## Canonical manuscript

The current manuscript source on `main` is maintained only at:

- `manuscript/main.tex`
- `manuscript/references.bib`

The manuscript now includes the independently executed ns-3.47 LR-WPAN validation. Superseded versioned manuscript files should not be committed.

## Evidence layers

The repository intentionally keeps distinct evidence generations separate rather than relabeling historical artifacts:

1. **Historical public C1--C7 archive** - earlier semantic RE-ETX experiments.
2. **Frozen J0--J7 journal results** - the numerical results reported in the manuscript; the original byte-identical final raw archive is not fully preserved.
3. **Clean-room J0--J7 reconstruction** - 160 regenerated trajectories over the twenty frozen inferential seeds, stored under `reproducibility/final_study_reconstruction/`. Integrated J4--J7 reproduce the frozen headline metrics with about 4.54% average absolute relative deviation.
4. **Independent IEEE 802.15.4 contention validation** - a separately implemented event-driven validator, not ns-3 and not hardware evidence.
5. **Executed ns-3.47 LR-WPAN validation** - 180/180 custom runs (20 paired seeds x J4/J5/J6 x 2.5/5/10 s report periods), with 11/11 official LR-WPAN test suites passed before the custom experiment.

The executed ns-3 package is stored at:

- `validation/ns3_47_lrwpan/`

At the primary 5 s/report ns-3 condition, mean report delivery is 62.152% for J4, 91.862% for J5, and 91.939% for J6. J5 improves RDR over J4 by 29.709 percentage points and reduces delivered-report delay by 23.278 ms; all five prespecified J5--J4 MAC outcomes survive Holm correction. All corresponding J5--J6 outcomes are nonsignificant after correction, independently supporting the manuscript's traffic-volume attribution.

## Important claim boundary

The ns-3 experiment is an executed IEEE 802.15.4/LR-WPAN MAC/PHY contention validation. It is **not** a full reproduction of the paper's multihop AD-CWOA/RE-ETX dynamics, is **not** used as radio-energy validation, and is **not** physical-hardware evidence. No FIT IoT-LAB or local-device hardware result is claimed.

The clean-room reconstruction and the validation archives must not be relabeled as the lost original J0--J7 raw data. See `REPRODUCIBILITY.md` for the full provenance boundary.

## Repository structure

```text
.
├── manuscript/
│   ├── main.tex
│   └── references.bib
├── reproducibility/
│   └── final_study_reconstruction/
├── validation/
│   └── ns3_47_lrwpan/
├── simulator/
├── results/
├── plots/
├── config.py
├── main.py
├── run_semantic_re_etx.py
├── run_control_multiseed.py
├── run_event_quality_multiseed.py
├── run_targeting_multiseed.py
├── run_topology_sensitivity.py
├── requirements.txt
└── REPRODUCIBILITY.md
```

## Software environment

The historical Python simulator uses the dependencies declared in `requirements.txt`.

The ns-3 validation was executed with ns-3.47, LR-WPAN enabled, optimized Apple Silicon build, with exact source, raw outputs, statistical analysis, official test log, environment information, and checksums preserved under `validation/ns3_47_lrwpan/`.
