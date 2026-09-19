# ns-3.47 LR-WPAN validation

This directory contains an executed IEEE 802.15.4/LR-WPAN communication-layer validation for the WSN-HFL prototype.

## What was validated

The Python HFL simulator produces method-specific communication burdens. Those burdens were mapped into ns-3.47 LR-WPAN traffic and subjected to real ns-3 MAC/PHY contention, CSMA/CA, acknowledgments and retransmissions.

Two mappings were executed to avoid hiding a modeling choice:

- **Hop-equivalent mapping**: mean compressed update bits × mean selected hop count.
- **ETX-equivalent mapping**: mean HFL effective bits/update, which already includes route ETX expectation.

The hop-equivalent mapping is the primary conservative validation because ns-3 generates retransmissions itself. The ETX-equivalent mapping is a sensitivity/stress case and may partially double-count retransmission burden.

## Executed campaign

- 4 policies: random, resource, utility, proposed
- 5 load/scaling conditions
- 10 paired seeds
- 200 runs per mapping
- 400 ns-3 runs total
- ns-3 version 3.47
- IEEE 802.15.4/LR-WPAN MAC/PHY model
- 11 official LR-WPAN unit suites executed: **11 passed, 0 failed**

The raw sweeps, manifests, group summaries, paired contrasts, official test log, and SHA-256 checksums are stored under `results/`.

## Important interpretation

The hop-equivalent ns-3 results show that the resource-only policy can have better pure MAC delivery/latency under heavy contention because it selects lower-cost routes. The proposed policy is therefore **not claimed to dominate every network metric**.

Its purpose is to improve the joint learning-network trade-off: representation disparity, learning performance, communication burden and relay energy. The ns-3 results should be interpreted together with the HFL results in the repository root.

The ETX-equivalent sensitivity mapping shows the proposed method receiving the smallest expected offered load at correlation 0.9, but this is not used as the sole proof of superiority because ETX already represents expected transmissions.

## Scope boundary

This validation is not a full execution of the learning algorithm inside ns-3 and is not physical hardware evidence. It validates the communication consequences of the FL-derived traffic burden under an independently executed LR-WPAN MAC/PHY simulator.
