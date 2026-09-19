# Host-hardware execution report — final frozen configuration

## Physical host

The final implementation was executed on a **MacBook Air (MacBookAir10,1) with Apple M1, 8 CPU cores and 8 GB RAM, arm64**. This is genuine host-hardware execution evidence for the Python learning/orchestration implementation; it is not sensor-node hardware evidence.

## Final executed workloads

The frozen operating point is `relay_pressure_weight=3.0` and `compression_distortion_weight=0.10`.

The final execution campaign completed successfully on the physical host:

- 10-seed synthetic reference experiment (4 policies × 3 correlation levels × 40 rounds): approximately **17.25 s** wall-clock in the final rerun.
- Intel Berkeley Lab WSN experiment (4 policies × 3 correlation levels × 10 seeds × 30 rounds): approximately **57.57 s** wall-clock.
- UCI HAR experiment (4 policies × 3 correlation levels × 10 seeds × 25 rounds): approximately **95.85 s** wall-clock.
- Intel 10-seed ablation campaign: approximately **25.33 s** wall-clock.
- 12-point × 10-seed joint parameter grid was executed on each of Intel WSN and UCI HAR; the resulting tables are committed as `results/intel_lab/joint_grid.csv` and `results/uci_har/joint_grid.csv`.
- Updated ns-3.47 traffic replay: **400 LR-WPAN runs** plus **11/11 official LR-WPAN unit suites passed**.

These timings are execution records from the connected Mac and are included for reproducibility/engineering characterization; they are not used as MCU latency claims.

## Physical WSN-node status

A device probe found no connected compatible USB/serial MCU, ESP32/Arduino-class board, or IEEE 802.15.4 sensor mote during the experiment. Therefore the project does **not** claim:

- on-device TinyML training time,
- physical radio current/energy,
- measured RSSI/LQI,
- physical-node PDR,
- real sensor-mote update latency.

The evidence boundary is therefore:

1. executed learning/orchestration implementation on real host hardware;
2. real WSN/IoT datasets and measured Intel Lab connectivity;
3. executed ns-3.47 IEEE 802.15.4/LR-WPAN validation;
4. **no physical sensor-node testbed yet**.

Physical MCU/radio measurements should be added only after suitable sensor-class nodes are connected and instrumented.
