# Cross-Layer Utility-Aware HFL for Multi-Hop WSN-IoT

Research implementation of hierarchical federated learning for resource-constrained multi-hop sensing networks. The project studies how client utility, participation history, route burden, update fidelity, staleness, and relay-energy pressure interact.

## Scope and novelty boundary

ETX/residual-energy routing is treated as prior network infrastructure. The research object is the learning-layer orchestration above that substrate. The repository reports modeled communication/energy, real sensing data, measured Intel WSN connectivity, and ns-3.47 LR-WPAN replay. It does not claim physical mote/MCU energy measurements, battery lifetime, or environmental sustainability.

## Revised evaluation protocol

Parameter tuning and final inference are separated.

- Tuning seeds: 7, 11, 19, 23, 29, 31, 37, 41, 43, 47.
- Held-out evaluation seeds: 53, 59, 61, 67, 71, 73, 79, 83, 89, 97.
- Tuning grid: relay-pressure coefficient {1,2,3,5}; compression-distortion coefficient {0.1,0.2,0.4}.
- Frozen operating point: relay-pressure coefficient 5.0, compression-distortion coefficient 0.10, drift V = 0.5.
- Final real-data comparisons and statistical tests use only held-out evaluation seeds.

The deterministic selection rule is recorded in results/OPERATING_POINT_SELECTION.json. Utility-target JS and independent coverage metrics are excluded from parameter selection.

## Baselines and controls

Real-data experiments include random, resource-only, utility-only, compression-matched adaptive versions of those policies, proposed-fixed-50%-compression, a FedCG-adapted gradient-diversity/capability comparator, and the proposed controller. FedCG-adapted is explicitly an adaptation rather than an exact reproduction of the original FedCG system model.

## Corrected influence accounting

Each client's realized cloud influence is recorded after both within-edge normalization and cloud-level edge normalization. Utility-target JS measures alignment with the controller-defined utility target. It is not interpreted as population representativeness. Independent diagnostics are temperature-coverage JS for Intel and class-coverage JS for HAR.

## UCI HAR evaluation

Because UCI HAR windows overlap by 50%, the earlier random within-subject split was replaced. Each subject is now partitioned into ordered 10-window blocks; one of every five blocks is held out and the immediately adjacent training window is purged at each test boundary. This is an approximately 80/20 overlap-safe within-client holdout, not the canonical unseen-subject benchmark.

## Current held-out results at correlation 0.9

Intel proposed: RMSE 1.7348 C, effective traffic 0.992 Mbit, modeled energy 3.482 J, maximum relay energy 0.0969 J, utility-target JS 0.0118. Resource-adaptive obtains lower RMSE and lower traffic/energy. FedCG-adapted is statistically comparable to proposed on Intel RMSE and systems cost.

HAR proposed: accuracy 0.8867, Macro-F1 0.8827, effective traffic 11.253 Mbit, modeled energy 19.20 J, maximum relay energy 1.242 J, utility-target JS 0.0275. Proposed improves held-out accuracy over resource-adaptive and FedCG-adapted but uses more traffic, energy, and relay energy.

Adaptive update fidelity is the dominant communication-saving mechanism: proposed adaptive traffic is 58.2% lower than proposed-fixed-50% on Intel and 64.0% lower on HAR.

## Reproducibility campaign

The revised campaign contains 1,000 HFL simulations:

- 240 tuning-grid runs,
- 540 held-out real-data comparison runs,
- 100 held-out ablation runs,
- 120 held-out synthetic runs.

A separate 400-run ns-3.47 campaign replays held-out synthetic traffic. The Python test suite passes 13/13 tests, including a dedicated two-level aggregation-influence test and frozen-table integrity checks.

## Run commands

~~~bash
.venv/bin/pytest -q
.venv/bin/python run_joint_grid.py --dataset intel
.venv/bin/python run_joint_grid.py --dataset har
.venv/bin/python select_operating_point.py
.venv/bin/python run_intel_lab_experiment.py
.venv/bin/python run_har_experiment.py
.venv/bin/python run_intel_ablation.py
.venv/bin/python run_har_ablation.py
.venv/bin/python run_experiment.py --out results/final_synthetic_10seed
.venv/bin/python analyze_statistics.py
.venv/bin/python freeze_publication_tables.py
~~~

The ns-3 runner is under validation/ns3_47_hfl/.

## Key files

- MANUSCRIPT_RECONSTRUCTION.md — authoritative manuscript source.
- submission/nexus/NEXUS_FINAL_MANUSCRIPT.docx — final Word manuscript.
- results/OPERATING_POINT_SELECTION.json — deterministic tuning rule and selected point.
- validation/statistics/statistical_tests.csv — held-out paired inference.
- validation/real_data/INTEL_LAB_REPORT.md and UCI_HAR_REPORT.md — current real-data reports.
- tables/TABLE_FREEZE_MANIFEST.json — hashes for frozen source/result tables.
- figures/final/ — final manuscript figures.