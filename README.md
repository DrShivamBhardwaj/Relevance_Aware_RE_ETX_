# Controlled Attribution and Robustness in IoT Wireless Sensor Networks

This repository contains the wireless sensor network simulation code, archived validation artifacts, and the canonical current manuscript source associated with:

**Controlled Attribution of Cross-Layer Gains and Robustness Limits in IoT Wireless Sensor Networks: AD-CWOA Clustering, Relevance-Aware Reporting, and RE-ETX Routing**

## Canonical manuscript

The current manuscript is maintained only at:

- `manuscript/main.tex`
- `manuscript/references.bib`

These unversioned paths are the canonical manuscript source on the `main` branch. Superseded manuscript filenames such as `V1`, `V2`, `V3`, etc. should not be committed; future manuscript corrections should replace `manuscript/main.tex` in place.

## Repository status

The repository contains an earlier semantic RE-ETX validation archive centered on C1--C7/10-seed experiments, together with the later manuscript source for the J0--J7/20-seed integrated study.

A clean-room final-study reconstruction has now also been executed for all J0--J7 modes over the twenty frozen inferential seeds (160 trajectories total). The reconstruction is maintained as **independent replication evidence**, not as the lost original final-study raw archive. Its provenance record and summaries are under:

- `reproducibility/final_study_reconstruction/`

The integrated J4--J7 modes reproduce the frozen headline metrics with about 4.54% average absolute relative deviation across eight headline outcomes. The main traffic-attribution conclusion is retained: J4->J5 shows a broad benefit from lower offered traffic, whereas the strict J7->J5 source-mapping control remains nonsignificant across the seven broad network outcomes after Holm correction.

A separate independent IEEE 802.15.4-style unslotted CSMA/CA validation was also executed for J4/J5/J6 over all twenty seeds and three offered-load levels. This validator is **not ns-3** and is not hardware evidence. At 5 s/report, mean RDR is 46.02% for J4, 78.73% for J5, and 78.54% for J6; mean MAC service delay is 77.62, 41.51, and 41.61 ms, respectively. J6 remains statistically close to J5, reinforcing the traffic-volume attribution.

**Important reproducibility boundary:** neither the clean-room reconstruction nor the independent MAC validator should be relabeled as the lost original J0--J7 data. Exact recovery of the original final-study raw matrices remains unresolved. See `REPRODUCIBILITY.md`.

## Main repository structure

```text
.
├── manuscript/
│   ├── main.tex
│   └── references.bib
├── reproducibility/
│   └── final_study_reconstruction/
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

The simulation code is Python-based. Install the currently declared dependencies with:

```bash
pip install -r requirements.txt
```

See `REPRODUCIBILITY.md` for the distinction between the historical public archive, the frozen original manuscript results, the clean-room J0--J7 reconstruction, and the independent IEEE 802.15.4 contention validation.