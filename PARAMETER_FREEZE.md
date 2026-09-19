# Parameter freeze after sensitivity analysis

The final shared operating point is:

- relay-pressure coefficient `relay_pressure_weight = 3.0`
- compression-distortion coefficient `compression_distortion_weight = 0.10`
- drift parameter `V = 0.5`
- compression candidates `{0.15, 0.30, 0.50, 0.75, 1.0}`
- staleness decay `lambda = 0.35`
- utility-staleness coefficient `mu = 0.80`

The two-dimensional 10-seed grid is stored in:

- `results/intel_lab/joint_grid.csv`
- `results/uci_har/joint_grid.csv`

One-factor sensitivity tables are stored in each dataset result directory as `sensitivity_summary.csv`.

The selected point is not the single-metric optimum on every dataset. It is a cross-dataset Pareto operating point: aggressive compression substantially reduces communication/energy, relay pressure materially reduces hotspot energy, and learning/representation quality remains competitive. This parameter choice should be frozen before final manuscript comparisons to avoid tuning separately against each baseline or dataset.
