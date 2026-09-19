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

Current verified state: **3 tests passed**.
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

The default full run evaluates four policies (`random`, `resource`, `utility`, `proposed`) over three resource-data correlation levels (0.0, 0.5, 0.9) and three seeds (7, 11, 19).

Outputs are written to `results/`:

- `aggregate_summary.csv` — mean and standard deviation across seeds.
- `raw_summary.csv` — per-seed final metrics.
- `round_history.csv` — per-round trajectories.
- `run_manifest.json` — exact experiment configuration.

A human-readable snapshot is in [RESULTS.md](RESULTS.md).

## Reproducibility status

The included results are **executed synthetic-simulator results**, not hardware results and not ns-3 validation. They are intended to validate the algorithmic coupling and experimental pipeline before the next stage of network-emulation / hardware validation.

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

The current code is a research prototype, not a claim that the final algorithm is publication-complete. In particular, the synthetic setting should be followed by:

1. WSN/IoT datasets,
2. stronger FL baselines,
3. larger model families,
4. sensitivity and ablation studies,
5. ns-3 / Contiki-NG or equivalent networking validation,
6. convergence / bounded-drift analysis for selection, compression and staleness together.

The implementation intentionally keeps the novelty claim narrower than “ETX-aware FL”: the primary candidate contribution is **route-level learning-value orchestration with representation and relay-energy constraints**.