# Final-study clean-room reconstruction

This directory documents a **specification-based independent replication** of the final J0--J7 journal study. It does not contain, and must not be represented as, the lost original final-study raw matrices or original runner.

## Execution status

The reconstruction was executed for all eight J0--J7 modes over the twenty frozen inferential seeds (160 trajectories total). The integrated J4--J7 modes reproduce the frozen manuscript headline metrics with an average absolute relative deviation of about 4.54% across eight headline outcomes.

The main causal interpretation is preserved: the reconstructed J4->J5 transition shows a large broad benefit from reduced source traffic, while the stricter J7->J5 mapping-control comparison is nonsignificant across all seven broad network outcomes after Holm correction. Event-targeting behavior is also retained.

## Provenance boundary

J0/J2/J3 use a documented reconstruction choice for the conventional energy-weighted cluster-head selector: fixed-cardinality residual-energy-proportional sampling without replacement. The exact lost conventional selector was not uniquely recoverable. Therefore the reconstructed archive is an independent replication/robustness check, not a byte-identical reproduction.

## Independent IEEE 802.15.4 validation

A separate event-driven unslotted CSMA/CA validation was executed for J4/J5/J6 over the same twenty seeds at 2.5, 5 and 10 s/report. It mirrors the standard/ns-3 LR-WPAN default backoff parameters (macMinBE=3, macMaxBE=5, macMaxCSMABackoffs=4, 20-symbol unit backoff) but is **not ns-3**.

At the central 5 s/report stress point, mean RDR is 46.02% for J4, 78.73% for J5 and 78.54% for J6; mean MAC service delay is 77.62, 41.51 and 41.61 ms, respectively. J4->J5 differences remain Holm-significant, while J6->J5 broad MAC differences do not.

## What is intentionally not claimed

- The regenerated files are not the lost original J0--J7 raw data.
- The independent MAC validator is not an ns-3 result.
- No physical FIT IoT-LAB or local-hardware experiment has been executed yet.

The complete checksummed execution archive, including all 160 trajectory checkpoints and executable source, is maintained separately in the final submission/reproducibility package.