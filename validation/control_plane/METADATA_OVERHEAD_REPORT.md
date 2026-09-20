# Control-plane-aware compression contrast

Each candidate reports 168 bits (21 bytes) per round: 96-bit header, 32-bit local loss, 32-bit residual-energy estimate, and 8-bit availability.

## intel_lab
- Raw metadata: 29.53 KiB.
- ETX-weighted metadata: 1.219 Mbit.
- Conservative metadata radio-energy upper bound: 2.803 J.
- Metadata / proposed model traffic: 122.81%.
- Proposed control-inclusive uplink: 2.211 Mbit.
- Proposed-fixed control-inclusive uplink: 3.592 Mbit.
- Adaptive reduction: model-only 58.2%; control-inclusive 38.4%.

## uci_har
- Raw metadata: 15.38 KiB.
- ETX-weighted metadata: 0.306 Mbit.
- Conservative metadata radio-energy upper bound: 0.705 J.
- Metadata / proposed model traffic: 2.72%.
- Proposed control-inclusive uplink: 11.559 Mbit.
- Proposed-fixed control-inclusive uplink: 31.539 Mbit.
- Adaptive reduction: model-only 64.0%; control-inclusive 63.3%.
