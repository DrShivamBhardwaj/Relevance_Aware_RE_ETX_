# Reproduction commands

Run from the repository root with the project virtual environment.

## Integrity and tests

    .venv/bin/pytest -q
    .venv/bin/python audit_consistency.py

## Parameter tuning

    .venv/bin/python run_joint_grid.py --dataset intel
    .venv/bin/python run_joint_grid.py --dataset har
    .venv/bin/python select_operating_point.py

## Tables 2 and 3 real-data campaigns

    .venv/bin/python run_intel_lab_experiment.py
    .venv/bin/python run_har_experiment.py
    .venv/bin/python analyze_statistics.py
    .venv/bin/python analyze_intel_results.py
    .venv/bin/python analyze_har_results.py

## Ablations and synthetic experiment

    .venv/bin/python run_intel_ablation.py
    .venv/bin/python run_har_ablation.py
    .venv/bin/python run_experiment.py --out results/final_synthetic_10seed

## Control-plane signaling audit

    .venv/bin/python analyze_control_plane_overhead.py

## Frozen publication tables

    .venv/bin/python freeze_publication_tables.py

## ns-3 validation

See validation/ns3_47_hfl/ for the ns-3.47 runner and analysis scripts.

## Seed configuration

The canonical tuning/evaluation split is defined in src/wsn_hfl/config.py and mirrored in reproducibility/seed_config.json.
