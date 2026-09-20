# Parameter freeze after held-out revision

The current shared operating point is:

- relay-pressure coefficient: 5.0
- compression-distortion coefficient: 0.10
- drift parameter V: 0.5
- energy-scarcity coefficient: 0.5
- compression candidates: {0.15, 0.30, 0.50, 0.75, 1.0}
- fixed-compression control: 0.50
- staleness decay lambda: 0.35
- utility-staleness coefficient mu: 0.80

Parameter selection uses only tuning seeds 7, 11, 19, 23, 29, 31, 37, 41, 43, 47. Final comparisons and inferential statistics use disjoint held-out seeds 53, 59, 61, 67, 71, 73, 79, 83, 89, 97.

The 12-point tuning grids are stored in results/intel_lab/joint_grid.csv and results/uci_har/joint_grid.csv. The deterministic selection rule and ranked grid are stored in results/OPERATING_POINT_SELECTION.json.

A point is learning-feasible when Intel RMSE is within 0.010 C of the best tuning-grid RMSE and HAR accuracy is within 0.5 percentage points of the best tuning-grid accuracy. Among feasible points, the selected setting minimizes an equal-weight min-max-normalized systems score over effective bits, total modeled energy, and maximum relay energy on both datasets.

Utility-target JS and independent coverage metrics are excluded from tuning and evaluated only on held-out seeds. The selected point is an engineering operating point, not a universal optimum.