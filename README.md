# Controlled Attribution and Robustness in IoT Wireless Sensor Networks

This repository contains the wireless sensor network simulation code, archived validation artifacts, and the canonical current manuscript source associated with:

**Controlled Attribution of Cross-Layer Gains and Robustness Limits in IoT Wireless Sensor Networks: AD-CWOA Clustering, Relevance-Aware Reporting, and RE-ETX Routing**

## Canonical manuscript

The current manuscript is maintained only at:

- `manuscript/main.tex`
- `manuscript/references.bib`

These unversioned paths are the canonical manuscript source on the `main` branch. Superseded manuscript filenames such as `V1`, `V2`, `V3`, etc. should not be committed; future manuscript corrections should replace `manuscript/main.tex` in place.

## Repository status

The repository also contains a substantial earlier semantic RE-ETX validation archive, including the C1--C7/10-seed experiment generation and associated source-control, event-quality, routing, and topology-sensitivity results.

The current manuscript reports a later J0--J7/20-seed integrated study combining AD-CWOA clustering, relevance-aware reporting, RE-ETX routing, controlled attribution, optimizer/reclustering experiments, routing-geometry and deployment-size stress, an EEL-2024 external comparator, and an IEEE 802.15.4-style contention sensitivity.

**Important reproducibility boundary:** the earlier public C1--C7 archive should not be represented as an exact end-to-end reproduction of every numerical claim in the current J0--J7 manuscript. Exact public reproduction requires synchronization of the final frozen J0--J7 runners and the final archived `journal_v1_*` raw/statistical matrices described in `REPRODUCIBILITY.md`.

## Main repository structure

```text
.
├── manuscript/
│   ├── main.tex
│   └── references.bib
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

See `REPRODUCIBILITY.md` for the exact distinction between the archived public validation generation and the frozen final-study design.