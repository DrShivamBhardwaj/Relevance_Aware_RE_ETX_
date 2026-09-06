# Dual-Journal Validation Package

This directory contains the reproducibility artifacts used to strengthen the
experimental validation of the relevance-aware payload adaptation and
residual-energy ETX routing study.

## Reproducibility

Primary random seeds:

`11, 23, 42, 67, 101, 137, 173, 211, 257, 307`

Python/environment snapshots:

- `python_version.txt`
- `requirements_snapshot.txt`
- `base_commit.txt`

## Experiment Modes

- **C1** — residual-energy ETX routing, fixed 4000-bit payload.
- **C2** — residual-energy ETX + semantic-age routing term, fixed 4000-bit payload.
- **C3** — residual-energy ETX routing with relevance-adaptive payload.
- **C4** — residual-energy ETX + semantic-age routing with relevance-adaptive payload.
- **C5** — equal-budget fixed-payload control.
- **C6** — shuffled-relevance payload control.
- **C7** — temporal-only relevance ablation.

The default C5 equal-budget payload is **1744 bits**, corresponding to the
nearest lower byte-aligned value to the pooled C3 attempted-payload mean in
the baseline topology.

## Main Control Study

The 70-run control experiment evaluates C1-C7 over all 10 seeds.

Primary files:

- `statistics/control_multiseed_raw.csv`
- `statistics/control_multiseed_means.csv`
- `statistics/planned_paired_tests_holm.csv`
- `statistics/source_control_paired_tests.csv`

The principal source-control comparison is C5 versus C3. C5 controls for the
traffic-volume reduction while C3 retains relevance-dependent allocation.

## Event-Quality Evaluation

Event truth is used only for offline evaluation and is not supplied to the
routing or payload-selection algorithms.

Primary files:

- `statistics/event_quality_multiseed_raw.csv`
- `statistics/event_quality_summary.csv`
- `statistics/event_quality_paired_tests.csv`

Reported event-quality quantities include event-report delivery, event payload
preservation, event payload delivery, and event/non-event payload targeting.

## Within-Round Targeting Evaluation

The within-round targeting gap removes a confound that can arise when event
reports occur disproportionately in rounds having different overall payload
distributions.

Primary files:

- `statistics/within_round_targeting_multiseed.csv`
- `statistics/within_round_targeting_summary.csv`
- `statistics/within_round_targeting_paired_tests.csv`

This metric is particularly important for the shuffled-relevance control C6.

## RE-ETX Weight Sweep

Primary files:

- `raw/re_etx_multiseed_raw.csv`
- `statistics/re_etx_multiseed_summary.csv`
- `statistics/re_etx_multiseed_paired_tests.csv`

These runs evaluate residual-energy weighting independently of semantic
payload adaptation.

## Topology-Depth Sensitivity

Three calibrated multi-hop regimes were evaluated:

- **Shallow:** field height 150 m, BS y=200 m, sensor radius 25 m.
- **Medium:** field height 400 m, BS y=450 m, sensor radius 45 m.
- **Deep:** field height 600 m, BS y=650 m, sensor radius 60 m.

The corresponding calibrated initial mean route depths are approximately:

- shallow: 1.483 hops
- medium: 2.910 hops
- deep: 4.929 hops

C1, C3, and C5 were evaluated across all 10 seeds in each regime.

For the topology-sensitivity C5 control, the fixed payload was calibrated
separately to the C3 attempted-payload budget of each topology:

- shallow: 1744 bits
- medium: 1648 bits
- deep: 1568 bits

This keeps the C5-versus-C3 traffic budget closely matched within each
topology.

Primary files:

- `statistics/topology_sensitivity_raw.csv`
- `statistics/topology_sensitivity_summary.csv`
- `statistics/topology_sensitivity_paired_tests.csv`
- `statistics/topology_sensitivity_budget_check.csv`

## Raw Round Archives

Per-round CSVs are compressed to reduce repository size:

- `raw/control_rounds.tar.gz`
- `raw/topology_rounds.tar.gz`

Representative regression/sanity runs are also retained directly under
`raw/`.

## Analysis Scripts

- `../../analyze_control_results.py`
- `../../analyze_event_quality.py`
- `../../analyze_targeting_results.py`
- `../../analyze_topology_sensitivity.py`

## Batch Runners

- `../../run_control_multiseed.py`
- `../../run_event_quality_multiseed.py`
- `../../run_targeting_multiseed.py`
- `../../run_topology_sensitivity.py`

## Calibration / Correction Utilities

- `../../calibrate_topology_depth.py`
- `../../correct_topology_c5_budget.py`
