# Editorial-revision reproducibility report

Date: 2026-09-20

This report records the rerun performed after correcting hierarchical cloud-influence accounting and separating parameter tuning from final evaluation.

## Final test state

The Python validation suite passes 13/13 tests. This includes the dedicated two-level cloud-influence regression test, queue and finite-set decision checks, error-feedback conservation, frozen-table hash verification, and tests that adverse matched-control trade-offs remain represented in the manuscript.

## HFL simulation campaign

- 240 tuning-grid runs: 12 settings x 10 tuning seeds x 2 real datasets.
- 540 held-out real-data comparison runs: 9 methods x 3 correlation levels x 10 held-out seeds x 2 datasets.
- 100 held-out ablation runs: 5 variants x 10 held-out seeds x 2 datasets.
- 120 held-out synthetic runs: 4 policies x 3 correlation levels x 10 held-out seeds.
- Total: 1,000 HFL simulations.

## ns-3.47 campaign

The hop-equivalent and ETX-equivalent LR-WPAN sweeps were rerun using held-out synthetic traffic profiles:

4 policies x 5 conditions x 10 held-out seeds x 2 traffic mappings = 400 ns-3 runs.

## Frozen operating point

The tuning-only selection rule chooses relay-pressure coefficient 5.0, compression-distortion coefficient 0.10, and V = 0.5.

## Current held-out headline values

Intel proposed: RMSE 1.7348 C, effective traffic 0.992 Mbit, modeled energy 3.482 J, max relay energy 0.0969 J, utility-target JS 0.0118.

HAR proposed: accuracy 0.8867, Macro-F1 0.8827, effective traffic 11.253 Mbit, modeled energy 19.20 J, max relay energy 1.242 J, utility-target JS 0.0275.

## Interpretation boundary

The implementation uses full-batch local gradient descent. It does not implement FedProx, FedAdam/FedOpt, or server momentum. The FedCG-adapted comparator is a favorable gradient-diversity/capability adaptation and is not represented as an exact reproduction of the original FedCG topology.

Host wall-clock timing is an execution diagnostic and is not used as sensor-node or radio latency evidence.