# Hardware execution report

## What was physically executed

The Python WSN-HFL implementation was executed on a **MacBook Air (MacBookAir10,1) with Apple M1, 8 CPU cores and 8 GB RAM**. This is real host-hardware execution evidence for the learning/simulation code path.

The full reference experiment comprises:

- 4 scheduling policies,
- 3 system-data correlation levels,
- 3 independent seeds,
- 40 federated rounds per run.

The full experiment completed successfully in **19.32 s wall-clock time** with a maximum resident set size of approximately **40.0 MB** as reported by macOS `/usr/bin/time -l`.

A short validation configuration also completed in **0.54 s** with maximum resident set size approximately **39.5 MB**.

The detailed stdout and timing records are stored in this directory.

## Device-level WSN hardware status

A physical-device probe was also performed. No USB/serial MCU or IEEE 802.15.4 sensor board was connected to the Mac at execution time. No ESP32/Arduino-class serial device was detected, and neither `arduino-cli` nor PlatformIO was installed.

Therefore, this repository **does not claim physical sensor-radio, MCU energy, RSSI/LQI, packet-delivery, or on-device training measurements**.

The valid evidence boundary is:

1. executed host-hardware implementation evidence on Apple M1;
2. executed ns-3.47 IEEE 802.15.4/LR-WPAN network simulation evidence;
3. no physical WSN-node experiment yet.

## Why this distinction matters

Host execution verifies that the implementation is runnable and resource-light on the available computer, but it does not establish feasibility on constrained sensor MCUs. The ns-3 study provides protocol-level MAC/PHY contention evidence, but it is still simulation. A later hardware campaign should use actual sensor-class devices and measure wall-clock local-training time, radio traffic, energy/current draw, packet delivery, route changes, and update latency.

No hardware result should be reported in a manuscript beyond the host-execution evidence above until suitable sensor nodes are physically connected and measured.
