# Frozen publication tables and manuscript-safe result policy

Status: **FROZEN for manuscript reconstruction**

Source of truth: the CSV files in `tables/` and `tables/TABLE_FREEZE_MANIFEST.json`. The manifest stores SHA-256 hashes of every source result file used to generate these tables.

## Selection policy

The main text uses the predeclared strongest correlated system/statistical heterogeneity condition, \(c=0.9\), for Intel and UCI HAR. Results at \(c=0\) and \(c=0.5\) remain in supplementary tables so the main text does not cherry-pick across heterogeneity levels.

The primary inferential contrast is **proposed versus resource-only scheduling**, because that comparison directly tests the central claim that network-only efficiency can suppress statistically valuable clients. Random and utility-only baselines remain visible in the descriptive result tables.

All real-data values are reported as **mean ± 95% CI over 10 paired seeds**. Exact paired sign-flip tests are the primary small-sample significance test; Holm-adjusted p-values are used when discussing multiple metrics.

Negative trade-offs are retained. In particular, UCI HAR maximum relay energy is **higher** under the proposed controller than under resource-only scheduling. That result must not be hidden or rewritten as a relay-energy improvement.

## Table 1. Experimental design

| Evidence layer | Clients | Task | Rounds | Clients/round | Correlation | Seeds | Network evidence |
|---|---:|---|---:|---:|---|---:|---|
| Synthetic | 24 | 5-class classification | 40 | 6 | 0, 0.5, 0.9 | 10 | multi-hop simulated WSN |
| Intel Berkeley Lab | 48 learning + 4 gateways | next-temperature regression | 30 | 10 | 0, 0.5, 0.9 | 10 | real mote locations + measured connectivity |
| UCI HAR | 30 subjects | 6-class activity recognition | 25 | 8 | 0, 0.5, 0.9 | 10 | real sensing data + simulated multi-hop substrate |
| ns-3.47 | traffic replay | LR-WPAN delivery/latency | — | — | frozen profiles | 10 | IEEE 802.15.4 MAC/PHY |

## Table 2. Intel Berkeley Lab at \(c=0.9\)

| Method | RMSE °C ↓ | MAE °C ↓ | Effective Mbit ↓ | Energy J ↓ | Max relay J ↓ | Rep. JS ↓ | Jain ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Random | 1.7381 ± 0.0028 | 0.8021 ± 0.0074 | 2.515 ± 0.050 | 6.986 ± 0.116 | 0.2736 ± 0.0247 | 0.0749 ± 0.0060 | 0.8910 ± 0.0124 |
| Resource-only | 1.7451 ± 0.0030 | 0.8297 ± 0.0087 | 2.217 ± 0.014 | 6.298 ± 0.031 | 0.1393 ± 0.0060 | 0.1231 ± 0.0068 | 0.6993 ± 0.0118 |
| Utility-only | **1.7293 ± 0.0015** | **0.7786 ± 0.0055** | 2.692 ± 0.019 | 7.392 ± 0.045 | 0.3136 ± 0.0178 | 0.0561 ± 0.0025 | 0.5591 ± 0.0088 |
| Proposed | 1.7417 ± 0.0052 | 0.7968 ± 0.0113 | **0.983 ± 0.019** | **3.460 ± 0.043** | **0.0976 ± 0.0024** | **0.0231 ± 0.0023** | 0.6605 ± 0.0126 |

Manuscript-safe interpretation: utility-only obtains the lowest regression error, whereas the proposed method provides a substantially lower communication/energy/relay burden and representation mismatch. Proposed versus resource-only RMSE is statistically comparable rather than a significant learning win.

## Table 3. UCI HAR at \(c=0.9\)

| Method | Accuracy ↑ | Macro-F1 ↑ | Worst-client acc. ↑ | Effective Mbit ↓ | Energy J ↓ | Max relay J ↓ | Rep. JS ↓ | Jain ↑ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Random | 0.8216 ± 0.0345 | 0.7949 ± 0.0489 | 0.6479 ± 0.0409 | 41.416 ± 3.318 | 70.83 ± 7.38 | 3.812 ± 1.189 | 0.0590 ± 0.0103 | 0.8875 ± 0.0170 |
| Resource-only | 0.8754 ± 0.0196 | 0.8724 ± 0.0226 | 0.6814 ± 0.0173 | 29.651 ± 1.154 | 45.92 ± 1.80 | **0.458 ± 0.091** | 0.1634 ± 0.0302 | 0.6518 ± 0.0585 |
| Utility-only | 0.7188 ± 0.0303 | 0.6626 ± 0.0406 | 0.5682 ± 0.0270 | 42.334 ± 2.904 | 72.35 ± 6.54 | 5.036 ± 1.102 | 0.0763 ± 0.0101 | 0.5963 ± 0.0475 |
| Proposed | **0.9061 ± 0.0022** | **0.9060 ± 0.0024** | **0.7169 ± 0.0150** | **11.639 ± 0.713** | **20.03 ± 1.57** | 1.415 ± 0.344 | **0.0327 ± 0.0078** | 0.8318 ± 0.0173 |

Manuscript-safe interpretation: proposed improves learning, communication, total modeled energy and representation relative to resource-only, but **maximum relay energy is 209.28% higher than resource-only**. Resource-only achieves the lowest relay-hotspot burden by favoring cheap network paths. Proposed still reduces maximum relay energy relative to random and utility-only scheduling.

## Table 4. Proposed versus resource-only: paired statistical contrasts

| Dataset | Metric | Effect | Exact sign-flip p | Holm p | Paired Cohen d |
|---|---|---:|---:|---:|---:|
| Intel | RMSE | −0.19% | 0.2246 | 0.2246 | −0.410 |
| Intel | MAE | −3.96% | 0.0020 | 0.0117 | −1.631 |
| Intel | Effective bits | −55.67% | 0.0020 | 0.0117 | −37.019 |
| Intel | Total energy | −45.06% | 0.0020 | 0.0117 | −37.019 |
| Intel | Max relay energy | −29.94% | 0.0020 | 0.0117 | −4.326 |
| Intel | Representation JS | −81.21% | 0.0020 | 0.0117 | −8.033 |
| UCI HAR | Accuracy | +3.08 pp | 0.0020 | 0.0156 | +0.998 |
| UCI HAR | Macro-F1 | +3.36 pp | 0.0020 | 0.0156 | +0.944 |
| UCI HAR | Worst-client accuracy | +3.55 pp | 0.0156 | 0.0156 | +0.973 |
| UCI HAR | Effective bits | −60.75% | 0.0020 | 0.0156 | −10.784 |
| UCI HAR | Total energy | −56.38% | 0.0020 | 0.0156 | −9.547 |
| UCI HAR | Max relay energy | **+209.28%** | 0.0020 | 0.0156 | +1.950 |
| UCI HAR | Representation JS | −79.97% | 0.0020 | 0.0156 | −2.909 |

The bootstrap confidence intervals for these paired differences are retained in `tables/table4_resource_contrasts.csv`.

## Table 5. Component ablation at \(c=0.9\)

The main paper should report the full proposed controller and four controlled removals: no representation-deficit term, fixed 50% compression, age-only staleness weighting, and no relay-pressure term. The exact table is frozen at `tables/table5_ablation.csv`.

The most diagnostic effects are:

- Intel: removing the representation queue raises JS divergence from 0.0231 to 0.0401.
- Intel: fixed 50% compression raises effective traffic from 0.983 Mbit to 2.419 Mbit and energy from 3.460 J to 6.763 J.
- Intel: removing relay pressure raises maximum relay energy from 0.0976 J to 0.1089 J.
- HAR: removing the representation queue raises JS divergence from 0.0327 to 0.0665.
- HAR: fixed compression lowers accuracy from 0.9061 to 0.7912 and raises traffic from 11.639 Mbit to 33.622 Mbit.
- HAR: removing relay pressure raises maximum relay energy from 1.415 J to 1.654 J.

## Table 6. ns-3.47 primary hop-equivalent replay

| Condition | Method | Mapped payload bits | Report RDR % ↑ | Delay ms ↓ | Access failures ↓ |
|---|---|---:|---:|---:|---:|
| dense nominal | Random | 3970 | 84.12 ± 8.48 | 39.69 ± 2.12 | 44.1 ± 29.3 |
| dense nominal | Resource-only | 3476 | 86.49 ± 7.47 | 37.45 ± 2.23 | 36.5 ± 24.1 |
| dense nominal | Utility-only | 3796 | 85.09 ± 7.70 | 39.05 ± 2.28 | 41.4 ± 25.8 |
| dense nominal | Proposed | **1219** | **99.47 ± 0.94** | **12.02 ± 0.83** | **1.2 ± 2.1** |
| 24-sensor nominal | Random | 3970 | 56.05 ± 5.62 | 46.15 ± 1.72 | 311.3 ± 58.8 |
| 24-sensor nominal | Resource-only | 3476 | 60.70 ± 4.72 | 44.23 ± 1.75 | 271.7 ± 54.9 |
| 24-sensor nominal | Utility-only | 3796 | 57.41 ± 5.27 | 45.14 ± 1.60 | 297.2 ± 60.4 |
| 24-sensor nominal | Proposed | **1219** | **97.48 ± 1.28** | **13.75 ± 0.53** | **11.6 ± 5.9** |

These values validate the consequences of the frozen traffic profile under LR-WPAN contention. They do not imply that the Python scheduler runs inside ns-3.

## Supplementary tables

- `table_s1_synthetic_all.csv`: all synthetic correlations and methods.
- `table_s2_intel_all_correlations.csv`: all Intel correlations and methods.
- `table_s3_har_all_correlations.csv`: all HAR correlations and methods.
- `table_s4_sensitivity_neighborhood.csv`: neighborhood around the frozen cross-dataset operating point.

## Claims that should not appear

- “The proposed method is best on every metric.”
- “Relay energy is lower than resource-only on UCI HAR.”
- “Intel RMSE is significantly better than resource-only.”
- “The ns-3 experiment executes the complete FL optimizer.”
- “Energy values are hardware-measured sensor-node energy.”
- “The results prove global optimality or end-to-end FL convergence.”

