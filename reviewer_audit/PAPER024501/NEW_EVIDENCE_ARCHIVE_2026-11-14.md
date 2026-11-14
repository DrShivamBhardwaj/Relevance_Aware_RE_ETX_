# PAPER024501 new evidence archive — 14 November 2026

This archive records the additional distributed-neighbour-context work present in this repository. It preserves raw run outputs, Cooja configurations/logs, analysis scripts, per-seed results, summary CSVs, firmware images and available FIT IoT-LAB capture artefacts.

## Archived campaigns

- `context_only_battery/`: 60 model runs (six context-payload sizes × ten seeds), per-run JSON, per-run work directories and output CSVs. These are model-based battery-cost sensitivity results, not hardware-calibrated energy measurements.
- `distributed_context_100node/`: 20 model runs (four reception/payload configurations × five seeds), per-run JSON and work-directory outputs. These are exploratory 100-node model results; five seeds do not establish broad deployment generality.
- `context_exchange_trial/cooja_rx_sweep/`: 15 Cooja runs (three configured reception probabilities × five seeds), with trial `.csc` files, `COOJA.testlog`, per-run results and aggregate CSV. Reception ratios are application-log counts, not independent PHY PDR measurements.
- `context_exchange_trial/`: C source, Makefile, Cooja runner and analysis scripts, M3 firmware images, experiment 458578 receipts/serial captures and whole-board power analysis files.
- `context_exchange_replication/active/`: retained board flash/reset text records for the replication attempt.

## FIT IoT-LAB evidence boundary

The archived physical pilot is experiment **458578**, on three Grenoble M3 nodes (97, 100 and 102). The capture is partial and does not cover the full experiment. The audit records 415 serial lines, 21 usable power windows and 12 paired board-mode comparisons. It explicitly records that physical/channel PDR, full-network energy savings and original RE-ETX firmware validation were not established. Whole-board phase differences must not be presented as independently calibrated per-message or per-component energy coefficients.

No completed physical result for experiment 458597 is included in this archive. Do not cite that identifier as a completed experiment without a separate verified archive and audit.

## Reproducibility and claim limits

The Cooja and model campaigns are retained with their per-run inputs/outputs. The model-based distributed-context results quantify sensitivity to context traffic under the implemented assumptions; they are not a 100-node physical deployment. The Cooja pilot uses a small three-mote geometry and does not validate the full 100-node sink-rooted RE-ETX system. The M3 pilot demonstrates limited prototype execution and partial serial/power observations only.

The archive does not close the original receiver encoder/decoder fidelity gap, component-level hardware energy calibration, or full deployment-equivalent multihop RE-ETX comparison. These remain open scientific requirements.
