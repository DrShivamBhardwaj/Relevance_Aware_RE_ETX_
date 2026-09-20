# Joint sensitivity and operating-point report

The revised parameter search uses a two-dimensional grid on both real datasets with tuning seeds only.

- relay-pressure coefficient: {1, 2, 3, 5}
- compression-distortion coefficient: {0.1, 0.2, 0.4}
- 10 tuning seeds per grid point
- strong resource-data correlation c = 0.9

The complete grid files are results/intel_lab/joint_grid.csv and results/uci_har/joint_grid.csv.

## Selection rule

A grid point is learning-feasible when Intel RMSE is within 0.010 C of the best tuning-grid RMSE and HAR accuracy is within 0.5 percentage points of the best tuning-grid accuracy. Among feasible points, the selected setting minimizes an equal-weight min-max-normalized systems score over effective bits, total modeled energy, and maximum relay energy on both datasets.

This deterministic rule selects relay-pressure coefficient 5.0 and compression-distortion coefficient 0.10. The drift parameter remains V = 0.5.

Utility-target JS and independent temperature/class coverage metrics are excluded from parameter selection and reserved for held-out evaluation. The full ranking and component scores are stored in results/OPERATING_POINT_SELECTION.json.

## Evaluation separation

Tuning seeds: 7, 11, 19, 23, 29, 31, 37, 41, 43, 47.

Held-out evaluation seeds: 53, 59, 61, 67, 71, 73, 79, 83, 89, 97.

No final real-data comparison or statistical test reuses the tuning seeds.

## Interpretation

The selected point is not claimed to optimize every learning or networking metric. Held-out results show that resource-adaptive can outperform the proposed controller on Intel error, traffic, energy, and relay hotspot, while the proposed controller has substantially lower utility-target JS. On HAR, proposed improves held-out accuracy over matched controls at additional traffic and relay-energy cost.