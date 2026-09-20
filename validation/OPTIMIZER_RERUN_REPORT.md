# Full HFL controller optimizer rerun report

## Scope

This report records the full reproducibility rerun executed on 2026-09-20 for the Cross-Layer Statistical-Utility-Aware HFL study. The rerun started from base commit `21325708792fe079db24eed92c9fc16c83520621`. It verifies the implemented cross-layer controller and the frozen `(relay_pressure_weight, compression_distortion_weight)` grid. It is **not** a FedAvg/FedProx/FedOpt optimizer-family benchmark because those alternative server optimizers are not implemented in the current codebase.

## Pre-run verification

- Automated tests: **11 passed / 11**.
- Frozen seeds: `7, 11, 19, 23, 29, 31, 37, 41, 43, 47`.
- Real-data grid: `eta_R in {1,2,3,5}`, `beta in {0.1,0.2,0.4}`.
- Frozen shared point: `eta_R=3.0`, `beta=0.10`, `V=0.5`.

## Executed campaign

| Component | Design | Runs | Host wall-clock |
|---|---:|---:|---:|
| Synthetic reference | 4 policies × 3 correlations × 10 seeds | 120 | 60.71 s |
| Intel Berkeley Lab grid | 12 parameter points × 10 seeds | 120 | 65.22 s |
| UCI HAR grid | 12 parameter points × 10 seeds | 120 | 96.26 s |
| **Total** |  | **360** | **222.19 s** |

Host wall-clock values are execution diagnostics for the Apple M1 host and are not sensor-node or radio-latency claims.

## Reproduced frozen operating point

### Intel Berkeley Lab WSN

- RMSE: `1.7417307659976191 °C`
- Effective transmitted bits: `982635.8705102557`
- Modeled energy: `3.4600625021735874 J`
- Maximum relay energy: `0.09756673513200116 J`
- Representation JS: `0.023140083726042926`
- Participation Jain index: `0.6604515854033168`

### UCI HAR

- Accuracy: `0.9061234329797493`
- Macro-F1: `0.9059549010194374`
- Effective transmitted bits: `11638511.96515354`
- Modeled energy: `20.030055811286125 J`
- Maximum relay energy: `1.415180482055437 J`
- Representation JS: `0.032732129204276`
- Participation Jain index: `0.831783001855085`

### Synthetic reference at c=0.9

For the proposed controller, the explicit 10-seed reference rerun reproduced mean accuracy `0.9364`, Macro-F1 `0.9365`, and representation JS `0.0202`.

## Output integrity

After the explicit 10-seed synthetic rerun and both real-data optimizer grids, `git diff` reported no tracked numerical changes. Selected SHA-256 values were:

- `results/intel_lab/joint_grid.csv`: `6be33d25410ab4723c144bad2274120bf6d57d02fd0a26d58100b3dd028f2dc2`
- `results/uci_har/joint_grid.csv`: `d0c8cfe3396697d3c83b7e1d835c4ffea0582fdd9e831fae034055b6c984d528`
- `results/aggregate_summary.csv`: `c6cb598bccaefeeebe1f493c0e418cc70ec26b08013a1b4140b0f2d1c2dc6598`
- `results/raw_summary.csv`: `7391f17fbf60f7670b3d8a864aa95118943e23fcfae239c9888336a68d4ff857`
- `results/round_history.csv`: `9c1ff00648a9c940c6e864d271fcba36d9ccdd2841155651499ff307132e53f4`
- `results/run_manifest.json`: `5ff4551a228eb3cfb2a5478bd7d51d53049e9dd1a7dd189c8d94c55ea8930b36`

## Commands

```bash
.venv/bin/pytest -q
.venv/bin/python run_experiment.py --seeds 7 11 19 23 29 31 37 41 43 47
.venv/bin/python summarize_results.py
.venv/bin/python run_joint_grid.py --dataset intel
.venv/bin/python run_joint_grid.py --dataset har
```

`run_experiment.py` has now been corrected so its default seed list is the same frozen 10-seed set documented by the manuscript and README.
