# Hardware specifications and evidence boundary

## Host used for the executed campaigns

- Device: MacBook Air (MacBookAir10,1)
- Processor: Apple M1
- CPU cores: 8
- Memory: 8 GB
- Architecture: arm64
- Role: host execution of Python learning/orchestration experiments and analysis

The host specification is an engineering reproducibility record. It is **not** evidence of sensor-node compute time, IEEE 802.15.4 radio current, battery lifetime, or on-device TinyML performance.

## Physical sensor-node status

No compatible instrumented IEEE 802.15.4/MCU testbed was used for the reported experiments. The evidence boundary is therefore:

1. executed learning/orchestration code on the physical host above;
2. Intel Berkeley Lab sensing data and measured connectivity;
3. UCI HAR real inertial-sensing data;
4. executed ns-3.47 IEEE 802.15.4/LR-WPAN replay;
5. no physical sensor-mote energy or latency measurement.

## Frozen controller point

- relay-pressure coefficient: 5.0
- compression-distortion coefficient: 0.10
- drift parameter V: 0.5

The relay value 0.004 J/round is treated in the manuscript as a virtual relay-pressure reference, not a hard finite-horizon energy cap.
