# Intel Berkeley Lab real-WSN validation report

## Dataset and task

The experiment uses the Intel Berkeley Research Lab deployment: 54 Mica2Dot motes with measured temperature, humidity, light, voltage, physical locations, and aggregate directed connectivity probabilities. The original source is `https://db.csail.mit.edu/labdata/labdata.html`.

The learning task is **per-mote next-temperature regression**. Each sample uses a 16-step history of temperature, humidity, log-light and voltage (64 input features) to predict the next temperature. Clients are physical motes; four spatially distributed high-connectivity motes (10, 26, 48, 38) are treated as edge gateways. Gateway nodes are not learning clients.

Measured bidirectional packet-delivery probabilities are converted to ETX-style link costs using `1/(p_uv*p_vu)` when the product is at least 0.01. This is a benchmarking substrate, not a new routing contribution.

## Experimental design

- 48 learning clients after gateway exclusion/data sufficiency filtering.
- 30 federated rounds, 10 clients selected per round.
- Four policies: random, resource-only, statistical-utility-only, and proposed cross-layer orchestration.
- Resource-data correlation levels: 0.0, 0.5, 0.9.
- 10 paired random seeds per condition.
- Local model: regularized linear next-temperature predictor; Top-k update sparsification uses error feedback.

## Main result at correlation = 0.9

| Method | RMSE (C) | Effective bits | Energy (J) | Max relay energy (J) | Representation JS | Participation Jain |
|---|---:|---:|---:|---:|---:|---:|
| random | 1.7381 +/- 0.0028 | 2515488 | 6.986 | 0.2736 | 0.0749 | 0.8910 |
| resource | 1.7451 +/- 0.0030 | 2216534 | 6.298 | 0.1393 | 0.1231 | 0.6993 |
| utility | 1.7293 +/- 0.0015 | 2692320 | 7.392 | 0.3136 | 0.0561 | 0.5591 |
| proposed | 1.7417 +/- 0.0052 | 982636 | 3.460 | 0.0976 | 0.0231 | 0.6605 |

Against the resource-only baseline at correlation 0.9, the proposed method changes:

- RMSE: -0.19% (negative is better).
- Effective communication burden: -55.67% (negative means fewer effective bits).
- Total modeled energy: -45.06%.
- Maximum relay energy: -29.94%.
- Representation divergence: -81.21%.

## Ablation at correlation = 0.9

| Variant | RMSE (C) | Effective bits | Energy (J) | Rep. JS | Max relay energy (J) |
|---|---:|---:|---:|---:|---:|
| proposed | 1.7417 | 982636 | 3.460 | 0.0231 | 0.0976 |
| proposed_no_rep | 1.7413 | 1006294 | 3.514 | 0.0401 | 0.1023 |
| proposed_fixed_comp | 1.7333 | 2418802 | 6.763 | 0.0408 | 0.1642 |
| proposed_age_only | 1.7423 | 983818 | 3.463 | 0.0239 | 0.0967 |
| proposed_no_relay | 1.7419 | 1039319 | 3.590 | 0.0213 | 0.1089 |

The ablation supports three distinct roles: removing the representation-deficit term roughly doubles representation divergence; fixing compression materially increases communication/energy; removing relay pressure substantially increases relay-energy concentration. Utility-aware staleness has a smaller effect in this dataset because most model updates arrive within low staleness.

## Statistical contrasts

Exact paired sign-flip permutation p-values (10 paired seeds, correlation 0.9) are stored in `results/intel_lab/paired_contrasts.csv`. These tests are reported as evidence about repeatability, not as proof of external validity.

## Evidence boundary

This is a real WSN **dataset/topology/connectivity** validation executed on the implementation. It is not a replay on the original 2004 Mica2Dot hardware. Physical-node radio/MCU measurements remain a separate future validation layer.