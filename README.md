# Cross-Layer Statistical-Utility-Aware HFL for Multi-Hop WSN-IoT

Research implementation of a hierarchical federated-learning simulator for resource-constrained, multi-hop wireless sensor / IoT networks.

The prototype studies a specific coupling: **which client update is worth transporting, at what fidelity, and with what staleness tolerance when the route itself consumes relay energy and statistically important clients may have expensive links**.

## Scope

The simulated architecture is:

~~~text
Learning-capable sensor / IoT node
        -> multi-hop WSN relays
        -> cluster-head / edge gateway
        -> cloud aggregator
~~~

Not every sensor is assumed to train a large model. The implementation represents learning-capable WSN/IoT nodes and separate relay burden explicitly.

## Main mechanisms

- Multi-hop ETX / residual-energy-aware routing substrate.
- Non-IID client data with controllable correlation between statistical heterogeneity and route difficulty.
- Hierarchical client -> edge -> cloud aggregation.
- Drift-plus-penalty-style client orchestration using statistical utility, participation deficit, route cost and relay pressure.
- Client-specific Top-k model-update sparsification with error feedback.
- Statistical-utility-aware staleness weighting.
- Explicit source, relay-transmit and relay-receive energy accounting.
- Participation Jain index, representation divergence, class-coverage divergence, effective transmitted bits and relay-energy metrics.
## Important prior-work boundary

This repository does **not** claim ETX, residual-energy-aware ETX routing, or relevance-aware sensing-payload adaptation as new contributions.

Those concepts belong to the earlier WSN study:

- https://github.com/DrShivamBhardwaj/Relevance_Aware_RE_ETX_

In the present implementation, the RE-ETX-like network metric is treated as an **existing routing substrate / network-state input**. The new research object is the cross-layer coupling between:

~~~text
statistical learning utility
    <-> client participation
    <-> multi-hop route burden
    <-> model-update fidelity
    <-> staleness / aggregation influence
    <-> relay-energy depletion
~~~

See [PRIOR_WORK_BOUNDARY.md](PRIOR_WORK_BOUNDARY.md) for the explicit separation.

## Installation

Tested on macOS arm64 with Python 3.14.

~~~bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
~~~

## Tests

~~~bash
.venv/bin/pytest -q
~~~

Current verified state: **11 tests passed**, including queue-bound, finite-set compression, top-k selection, error-feedback conservation, and frozen publication-table integrity checks.
## Run the simulator

Short validation run:

~~~bash
.venv/bin/python run_experiment.py --quick
~~~

Full reference run:

~~~bash
.venv/bin/python run_experiment.py
.venv/bin/python summarize_results.py
~~~

The final reference results evaluate four policies (`random`, `resource`, `utility`, `proposed`) over three resource-data correlation levels (0.0, 0.5, 0.9) and 10 seeds (7, 11, 19, 23, 29, 31, 37, 41, 43, 47).

Outputs are written to `results/`:

- `aggregate_summary.csv` — mean and standard deviation across seeds.
- `raw_summary.csv` — per-seed final metrics.
- `round_history.csv` — per-round trajectories.
- `run_manifest.json` — exact experiment configuration.

A human-readable snapshot is in [RESULTS.md](RESULTS.md).

## Reproducibility status

The repository now contains executed synthetic results, Intel Berkeley Lab real-WSN replay, UCI HAR real sensing experiments, ns-3.47 LR-WPAN validation, and host-hardware execution evidence. Physical sensor-node radio/MCU measurements are still not claimed.

The full default experiment plus tests executed successfully on the connected Mac in about 18 seconds for the current configuration.
## Repository layout

~~~text
src/wsn_hfl/
  config.py       experiment parameters
  topology.py     multi-hop WSN and route computation
  data.py         correlated non-IID synthetic sensing data
  model.py        softmax model, local SGD, Top-k + error feedback
  scheduler.py    baselines and proposed cross-layer scheduler
  simulator.py    hierarchical FL, queues, energy and metrics
tests/
run_experiment.py
summarize_results.py
results/
~~~

## Research interpretation

The current code is a research prototype, not a claim that the final algorithm is publication-complete. The repository now includes real WSN/IoT datasets, ablation and sensitivity studies, 10-seed statistical validation, and ns-3.47 LR-WPAN replay. The remaining major extensions are:

1. stronger external FL baselines implemented under the same budget,
2. larger/TinyML model families,
3. physical sensor-node radio/MCU measurements,
4. convergence / bounded-drift analysis for the coupled selection, compression and staleness dynamics.

The implementation intentionally keeps the novelty claim narrower than “ETX-aware FL”: the primary candidate contribution is **route-level learning-value orchestration with representation and relay-energy constraints**.
## Executed ns-3.47 validation

An independent IEEE 802.15.4/LR-WPAN validation has now been executed with ns-3.47.

- 4 scheduling policies
- 5 contention/scaling conditions
- 10 paired seeds
- 2 traffic mappings (hop-equivalent and ETX-equivalent)
- **400 executed ns-3 runs**
- **11/11 official LR-WPAN unit suites passed**

The primary hop-equivalent mapping intentionally lets ns-3 generate retransmissions itself. The ETX-equivalent mapping is retained as a sensitivity analysis.

See `validation/ns3_47_hfl/` and the generated `validation/ns3_47_hfl/results/NS3_VALIDATION_REPORT.md`.

The ns-3 evidence does **not** show that the proposed policy wins every pure MAC metric. Under the conservative hop-equivalent mapping, resource-only scheduling often has lower delay because it deliberately chooses cheaper network paths. The proposed method is evaluated as a learning-network Pareto trade-off, not as an unconditional networking optimum.

## Executed host-hardware evidence

The final implementation was executed on an Apple M1 MacBook Air (8 cores, 8 GB RAM). The frozen campaign includes the 10-seed synthetic reference run, Intel WSN and UCI HAR experiments, ablations, the joint sensitivity grid, and ns-3.47 replay. Representative measured wall-clock times are documented in the hardware report rather than reused as sensor-node latency claims.

See `validation/hardware/HARDWARE_EXECUTION_REPORT.md` for the final host execution timings and evidence boundary.

A physical sensor-node probe found no connected USB/serial MCU or IEEE 802.15.4 development board. Therefore this repository does **not** claim on-device sensor hardware, radio-energy, RSSI/LQI, or physical packet-delivery measurements. Device-level hardware evidence remains a separate future experiment.

## Real-data validation added

The repository now includes two real sensing datasets and a frozen cross-layer operating point:

- **Intel Berkeley Lab WSN**: real sensor readings, physical mote locations and measured connectivity; 48 learning clients after gateway/data filtering.
- **UCI HAR**: 30 subject-clients, six activity classes, 561 inertial features.
- **Frozen default**: relay-pressure weight `3.0`, compression-distortion weight `0.1`, selected after a 12-point × 10-seed joint cross-dataset sensitivity study.

Detailed reports:

- `validation/real_data/INTEL_LAB_REPORT.md`
- `validation/real_data/UCI_HAR_REPORT.md`
- `validation/SENSITIVITY_REPORT.md`
- `FINAL_FORMULATION.md`
- `THEORY.md` — exact queue/drift/decision guarantees and explicit non-claims
- `PARAMETER_FREEZE.md`
- `PUBLICATION_TABLES.md` — frozen main/supplementary result selection and manuscript-safe claims
- `tables/TABLE_FREEZE_MANIFEST.json` — source/generated table hashes and frozen headline effects
- `MANUSCRIPT_RECONSTRUCTION.md`
