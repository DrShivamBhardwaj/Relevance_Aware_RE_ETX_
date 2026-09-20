# Frozen-parameter sensitivity report

The final controller parameters were frozen **before the final baseline comparisons** using a joint 10-seed grid on both real-data experiments at strong resource-data correlation (`c=0.9`).

The evaluated grid was:

- relay-pressure coefficient `eta_R in {1,2,3,5}`;
- compression-distortion coefficient `beta in {0.1,0.2,0.4}`;
- 10 paired seeds for every grid point on Intel Berkeley Lab WSN and UCI HAR.

The complete tables are:

- `results/intel_lab/joint_grid.csv`
- `results/uci_har/joint_grid.csv`

## Selected shared operating point

The frozen cross-dataset setting is:

- `relay_pressure_weight = 3.0`
- `compression_distortion_weight = 0.10`
- `V = 0.5`
- compression candidates `{0.15, 0.30, 0.50, 0.75, 1.0}`
- staleness decay `lambda = 0.35`
- utility-staleness coefficient `mu = 0.80`

This is **not** claimed to be a universal optimum. It is an engineering operating point that keeps learning quality competitive while aggressively reducing communication/energy and adding meaningful relay-pressure control on both datasets.

## Representative joint-grid results

| eta_R | beta | HAR accuracy | HAR effective bits | HAR energy | HAR max relay E | Intel RMSE | Intel effective bits | Intel energy | Intel max relay E |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.1 | 0.9041 | 11.84 M | 20.47 J | 1.584 J | 1.7427 C | 0.993 M | 3.483 J | 0.1004 J |
| 2 | 0.1 | 0.9037 | 11.75 M | 20.24 J | 1.466 J | 1.7410 C | 0.988 M | 3.473 J | 0.0999 J |
| **3** | **0.1** | **0.9061** | **11.64 M** | **20.03 J** | **1.415 J** | **1.7417 C** | **0.983 M** | **3.460 J** | **0.0976 J** |
| 5 | 0.1 | 0.9032 | 11.51 M | 19.76 J | 1.311 J | 1.7423 C | 0.988 M | 3.473 J | 0.0981 J |
| 3 | 0.2 | 0.9016 | 12.11 M | 20.75 J | 1.421 J | 1.7375 C | 1.200 M | 3.960 J | 0.1080 J |
| 3 | 0.4 | 0.9060 | 14.66 M | 24.55 J | 1.395 J | 1.7352 C | 1.834 M | 5.418 J | 0.1215 J |

`beta=0.1` materially lowers communication and energy compared with 0.2/0.4. Increasing `eta_R` from 1 to 3 lowers relay hotspot burden while preserving HAR accuracy. `eta_R=5` yields still lower HAR relay energy but worsens representation divergence and does not improve the Intel regression/representation trade-off enough to justify using the more aggressive relay penalty as the shared default.

## Final-baseline consequence

At the frozen setting (`eta_R=3`, `beta=0.1`):

- Intel vs resource-only: communication `-55.67%`, energy `-45.06%`, max relay energy `-29.94%`, representation JS `-81.21%`; RMSE difference is small and not significant (`p=0.2246`), while MAE improves significantly (`p=0.00195`).
- UCI HAR vs resource-only: accuracy `+3.08` percentage points, Macro-F1 `+3.36` points, communication `-60.75%`, energy `-56.38%`, representation JS `-79.97%`. The resource-only baseline retains lower max relay energy on HAR; the proposed method instead occupies a broader learning/communication/representation Pareto point.

This trade-off must be preserved in the manuscript; the method is not claimed to dominate every pure networking metric.

## Independent full rerun verification

On 2026-09-20 the complete implemented controller campaign was rerun from base commit 21325708792fe079db24eed92c9fc16c83520621 after 11/11 automated tests passed. The Intel and HAR 12-point grids were each executed over all 10 frozen seeds (120 runs per dataset), and the synthetic 4-policy × 3-correlation × 10-seed reference campaign was rerun separately. The rerun reproduced the same shared point (eta_R,beta)=(3,0.1) and left the tracked result CSVs unchanged. Full evidence is in validation/OPTIMIZER_RERUN_REPORT.md.
