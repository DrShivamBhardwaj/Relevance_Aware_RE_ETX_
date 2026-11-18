# IJWMT revision audit and supplementary experiment records

The audit table accounts for all 32 reviewer points. The response notes summarize the manuscript changes and evidence. The accompanying analysis and data document the Appendix D receiver and event-delivery studies. The CSVs retain the output from the reported campaign.

- Frozen model source: tag `submission-ready-v1`, commit `b5d5ac75c981b1eff0171a8cb885ef5764183d85`.
- `execution_environment.json` identifies the Appendix D execution environment. The older control-study software snapshot is under `results/master_validation` at the frozen tag.
- `source-blobs.json` records hashes for source files used in the campaign. The runner requires an adjacent `source/` copy of the frozen source tree, and the analysis expects the generated `runs/` traces adjacent to its script.
- `receiver_paired.csv` summarizes the codec comparisons. `topology_paired_5s.csv` summarizes the primary timing contrasts. `event_timestamps_simulated.csv` records event-onset and delivery times under the simulated clock.
- `CHECKSUMS.sha256` identifies the corresponding manuscript and submission files.
