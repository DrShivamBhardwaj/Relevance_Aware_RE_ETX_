# Host-hardware execution report — current frozen configuration

## Physical host

The primary Python learning/orchestration campaigns were executed on a **MacBook Air (MacBookAir10,1) with Apple M1, 8 CPU cores and 8 GB RAM, arm64**. This is host-execution evidence only; it is not sensor-node hardware evidence.

## Current frozen operating point

- relay-pressure coefficient: **5.0**
- compression-distortion coefficient: **0.10**
- drift parameter: **V = 0.5**
- relay-pressure reference: **0.004 J/round**

The 0.004-J value is used as a virtual-queue reference and is not presented as a hard finite-horizon relay-energy cap.

## Executed evidence base

The current revision retains the 1,000-run primary HFL campaign:

- 240 tuning-grid runs;
- 540 held-out real-data comparison runs;
- 100 held-out ablation runs;
- 120 held-out synthetic runs.

It also includes 400 ns-3.47 IEEE 802.15.4/LR-WPAN replay runs. The systems-learning revision adds 40 control-plane accounting runs: proposed and proposed-fixed compression, 10 held-out seeds, on Intel and UCI HAR.

These host timings and campaign counts are engineering/reproducibility records. They are not MCU latency or sensor-radio measurements.

## Physical WSN-node status

No compatible instrumented USB/serial MCU, ESP32/Arduino-class board, or IEEE 802.15.4 sensor mote was used for the reported experiments. Therefore the project does **not** claim:

- on-device TinyML training time;
- physical radio current or energy;
- measured RSSI/LQI;
- physical-node PDR;
- measured sensor-mote update latency;
- battery lifetime or environmental sustainability.

## Evidence boundary

1. executed learning/orchestration implementation on physical host hardware;
2. real Intel Berkeley Lab sensing data and measured connectivity;
3. UCI HAR real inertial-sensing data;
4. executed ns-3.47 IEEE 802.15.4/LR-WPAN replay;
5. no physical sensor-node testbed.

The concise canonical hardware description is also stored in reproducibility/HARDWARE_SPECIFICATIONS.md.
