# Energy-Information Co-Design for Resource-Bounded Edge Intelligence

Research implementation of a systems-learning federated framework for resource-constrained edge-cloud sensing. The project studies how client utility, participation history, route burden, update fidelity, staleness, and relay-pressure feedback interact when learning traffic traverses multi-hop low-power networks.

## Scope and novelty boundary

ETX/residual-energy routing, hierarchical aggregation, Top-k sparsification, and staleness weighting are treated as established ingredients. The research object is their **systems-learning co-design**: exposing network state to learning orchestration and measuring the resulting Pareto trade-offs.

The repository reports modeled communication/energy, real sensing datasets, measured Intel connectivity, held-out statistical analysis, and ns-3.47 LR-WPAN replay. It does not claim physical mote/MCU energy measurements, battery lifetime, or environmental sustainability.

## Revised evaluation protocol

Parameter tuning and final inference are separated.

- Tuning seeds: 7, 11, 19, 23, 29, 31, 37, 41, 43, 47.
- Held-out evaluation seeds: 53, 59, 61, 67, 71, 73, 79, 83, 89, 97.
- Tuning grid: relay-pressure coefficient {1,2,3,5}; compression-distortion coefficient {0.1,0.2,0.4}.
- Frozen operating point: relay-pressure coefficient 5.0, compression-distortion coefficient 0.10, drift V = 0.5.
- Final real-data comparisons, paired inference, and control-plane audit use only held-out evaluation seeds.

The deterministic selection rule is recorded in results/OPERATING_POINT_SELECTION.json. Utility-target JS and independent coverage metrics are excluded from parameter selection.

## Baselines and controls

Real-data experiments include random, resource-only, utility-only, compression-matched adaptive versions of those policies, proposed-fixed-50%-compression, a FedCG-adapted gradient-diversity/capability comparator, and the proposed controller. FedCG-adapted is explicitly an adaptation rather than an exact reproduction of the original FedCG system model.

## Corrected influence accounting

Each client's realized cloud influence is recorded after both within-edge normalization and cloud-level edge normalization. Utility-target JS measures alignment with the controller-defined target and is not interpreted as population representativeness. Independent diagnostics are temperature-coverage JS for Intel and class-coverage JS for HAR.

## UCI HAR evaluation

Because UCI HAR windows overlap by 50%, each subject is partitioned into ordered 10-window blocks; one of every five blocks is held out and the immediately adjacent training window is purged at each test boundary. This is an approximately 80/20 overlap-safe within-client holdout, not the canonical unseen-subject benchmark.

## Current held-out results at correlation 0.9

Intel proposed: RMSE 1.7348 C, model-update traffic 0.992 Mbit, modeled energy 3.482 J, maximum relay energy 0.0969 J, utility-target JS 0.0118. Resource-adaptive obtains lower RMSE and lower traffic/energy; proposed provides substantially stronger utility-target alignment.

HAR proposed: accuracy 0.8867, Macro-F1 0.8827, model-update traffic 11.253 Mbit, modeled energy 19.20 J, maximum relay energy 1.242 J, utility-target JS 0.0275. Proposed improves held-out accuracy over resource-adaptive and FedCG-adapted but uses more traffic, energy, and relay energy.

Adaptive update fidelity reduces model-update traffic by 58.2% on Intel and 64.0% on HAR relative to proposed-fixed-50%.

## Control-plane signaling audit

Pre-selection metadata are explicitly priced rather than assumed free. Each candidate report is 168 bits (21 bytes): 96-bit header, 32-bit local loss, 32-bit residual-energy estimate, and 8-bit availability flag.

Held-out mean results:

- Intel: 29.53 KiB raw metadata, 1.219 Mbit ETX-weighted metadata, conservative metadata radio-energy upper bound 2.803 J.
- UCI HAR: 15.38 KiB raw metadata, 0.306 Mbit ETX-weighted metadata, conservative metadata radio-energy upper bound 0.705 J.
- Control-inclusive adaptive-vs-fixed traffic reduction remains 38.4% on Intel and 63.3% on HAR.

Thus metadata is not universally negligible. It is material for the small Intel model but does not erase the adaptive-fidelity advantage. Global-model downlink dissemination remains outside the reported control-inclusive uplink accounting.

## Open-loop ns-3 validation

The current Python-to-ns-3 workflow is open loop: Python first produces the learning traffic profile, then ns-3 resolves CSMA/CA, acknowledgments, retries, delivery ratio, and delay. Packet outcomes do not feed back into future learning decisions. The replay therefore validates network consequences of offered load, not full closed-loop cyber-physical behavior.

## Reproducibility campaign

Primary evaluation:

- 240 tuning-grid HFL runs,
- 540 held-out real-data comparison runs,
- 100 held-out ablation runs,
- 120 held-out synthetic runs,
- 400 ns-3.47 replay runs.

The systems-learning revision additionally executes 40 control-plane accounting runs.

## Reproduction

See reproducibility/REPRODUCTION_COMMANDS.md for the canonical command sequence.

Seed configuration:
- src/wsn_hfl/config.py
- reproducibility/seed_config.json

Hardware/evidence boundary:
- reproducibility/HARDWARE_SPECIFICATIONS.md
- validation/hardware/HARDWARE_EXECUTION_REPORT.md

Control-plane analysis:
- analyze_control_plane_overhead.py
- validation/control_plane/

## Publication artifacts

- MANUSCRIPT_RECONSTRUCTION.md — authoritative manuscript source.
- submission/nexus/NEXUS_FINAL_MANUSCRIPT.docx — generated submission manuscript.
- NEXUS_SUBMISSION_READY_FINAL.docx — root submission copy after final synchronization.
- results/OPERATING_POINT_SELECTION.json — deterministic tuning rule and selected point.
- validation/statistics/statistical_tests.csv — held-out paired inference.
- tables/TABLE_FREEZE_MANIFEST.json — hashes for frozen publication tables.
- figures/final/ — exactly seven user-verified manuscript figures.
- figures/APPROVED_FINAL_SHA256.json — SHA-256 lock file for the approved figure set.

Do not regenerate or substitute figures/final/ for publication without explicit author approval.
