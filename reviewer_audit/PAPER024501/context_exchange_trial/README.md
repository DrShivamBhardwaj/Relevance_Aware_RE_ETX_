# PAPER024501 distributed-neighbour-context pilot, 14 November 2026

**Purpose.** Directly transmit source-2 neighbour observations to source 3
in Contiki-NG NullNet, while sources 2 and 3 transmit a fixed 32-byte report
to sink 1. Application-level neighbour-context payloads are 0, 13 (104 bits),
25 (200 bits) and 50 (400 bits), rotated every 30 seconds. Context is
synthetic, not the paper's actual correlated sensing field; the experiment
does not implement the 100-node sink-rooted RE-ETX protocol.

**Cooja.** Five independently seeded (deterministic) three-mote simulations,
code in `paper024501-context-pilot.c`; run `run_cooja_context.py`. Logs and
`cooja_results.csv` report sends and matching receives. All packets happened
to arrive in this favourable radio geometry, so it cannot establish
performance under contention or a 100-node network.

**FIT IoT-LAB Grenoble.** Experiment **458578**, reservation profile
`array_active_power_20261110`, motes 97/100/102. Per-role binaries are
archived in `m3_firmware/` and original submission/flash/reset receipts
in `active/`. The serial-capture window began after experiment start and
ended before termination, so packet-log matching is not a full-run radio
sniffer PDR. The original first serial_aggregator capture stopped almost
immediately. `active/serial_capture_retry.log` is the usable source.

**Power caution.** The first two 120-second cycles show non-stationary
whole-board consumption. `analyze_power_steady.py` excludes these cycles,
uses measured phase epoch alignment and the firmware's 30-second timer to
label the remaining full physical-trace windows. It provides within-board
whole-board *differences* under context workloads, not per-message joules,
independently measured TX/ACK states or calibrated RE-ETX battery costs.
The aggregate changes are very small and may reflect clock drift or MAC
activity unrelated to the 13/25/50-byte payload itself.

**Scope.** Evidence of context exchange implementation, not proof that
54% archival traffic-only savings survive decentralised deployment.
