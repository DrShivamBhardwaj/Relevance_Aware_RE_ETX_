# Executable Cooja validation

This package extends the archived payload-allocation study with an actual source representation, receiver error, distributed neighbour context, and transmission-level controls. The executed revision-2 study completed 200 primary and 280 exploratory research runs, all passing independent source/log/control audits. Results and raw archives are under `results/cooja_v2/`. The exact-size primary comparison favours shuffling over the relevance rule; no superiority claim is supported.

## Pinned components

- Contiki-NG release/v4.9: `c20b12cd2db707d6c07918f8b26cfeb52cf298ca`.
- Cooja: `33d41ae9f8acd6075fb903b0bcd5b4122bad8d8f`.
- Java 17, GCC and Make.
- `requirements-analysis.txt` pins the Python statistical dependencies.

## Run

On a connected Linux host or the supplied GitHub Actions workflow:

```bash
# If an existing compatible checkout is available:
export CONTIKI_DIR=/absolute/path/to/contiki-ng
bash validation/cooja/RUN_COOJA.sh smoke
bash validation/cooja/RUN_COOJA.sh primary
python3 -m pip install -r validation/cooja/requirements-analysis.txt
python3 validation/cooja/analyse.py cooja-output --output cooja-analysis.json
```

The `smoke` profile is an infrastructure and packet-path check, not an inferential experiment. `primary` runs 20 new seeds, 25 sources, 60 rounds, and ten policies. `all` adds exploratory weak-event, persistent-event, drift, sensor-bias, radio-outage, 100-node and shorter-report-period cases on four seeds. Parallel jobs use `--shard K --shards M`; combine the resulting run folders before analysis.

The workflow runs four primary shards on a push, each preceded by component, upstream IPv6 and ten-policy smoke gates. Manual dispatch also accepts `primary` or `all`. Archival-only commits may use `[skip ci]` to avoid duplicating the research runs. An output folder contains a manifest, generated input, console log, Cooja test log, offered report trace and summary. A failed or incomplete run cannot pass the analysis gate.

## Implemented method

Each source measures a synthetic block of 250 signed 16-bit observations. Explicit bit packing retains 4, 8, 12 or 16 high-order bits per sample, yielding 125, 250, 375 or 500 data bytes. A 16-byte application header is additional. SixLoWPAN, CSMA and RPL run in Contiki-NG; the Cooja radio medium supplies contention and loss. This quantised controller is a new validation implementation, not a bit-exact port of the historical linear payload map.

Current/previous block means and recently received one-hop beacons determine temporal and spatial novelty. Neighbour observations expire after one report interval. There are no reads from dead or silent neighbours and no central observation oracle. Synthetic event parameters belong to the workload generator and do not enter the scoring function. A receiver-side observer regenerates truth only after receipt to evaluate decoding error, without feedback to the controller.

An explicit MRHOF hook retains the estimated link ETX and adds a non-negative residual-radio-reserve penalty. Reserve is a declared virtual model derived from radio TX/listen activity; it is advertised in the same context beacon. The hook's modified source hash is recorded. This is an experimental RPL integration, not a claim of standards certification, hardware measurement, or a formal routing guarantee.

## Controls and endpoints

All policies use 16-bit reports for the first ten rounds; warm-up is excluded from receiver utility. Adaptive and shuffled controls have exactly the same offered payload-size multiset within each round. Temporal matching assigns that same multiset according to recorded temporal scores. Both are offline replay controls, not deployable online algorithms. Balanced allocation preserves total offered application bytes while changing their distribution; full reporting is an upper-size reference. Full reporting without context beacons is an additional operational baseline.

The primary contrast is adaptive versus shuffled receiver RMSE over a fixed external horizon. Every source/round is in the denominator. An unavailable or late report receives the declared zero-block reconstruction; it is never silently excluded. Delay has a one-period deadline. There is no FND/HND/LND or wall-clock battery-life claim in this validation.

Radio activity includes data, beacons, routing control and retransmissions. The optional radio-energy calculation assumes 3 V and CC2420 nominal TX/RX currents 17.4/18.8 mA from https://www.ti.com/lit/ds/symlink/cc2420.pdf. It excludes CPU, sensing and unmodelled circuit states and is not calibrated total-device energy. Native Cooja CPU timing cannot establish embedded runtime. Raw activity times remain the primary accounting record. Activity ends at each source’s final snapshot, before the simulation drain; radio work after that snapshot and sink activity are excluded, even where a legacy raw summary descriptor says full-run.

The declared zero estimator, thresholds, virtual reserve and workload are frozen in `design.json` before Cooja outputs. This is a prospective project analysis plan, not an externally registered study. Weak signals, missing context, biases, outages and scaling may overturn the proposed method's advantage; negative results must be retained.

## Executed checks

The portable codec and control/analysis invariants have automated tests. The firmware has been compiled with the pinned Contiki-NG native target, CSMA and the modified MRHOF hook. The 21 component tests passed, and all four successful GitHub jobs passed the upstream IPv6 and ten-policy smoke gates before the 200 primary runs. Independent audits additionally passed all 280 local exploratory outcomes. Component checks alone are not statistical evidence.

## Pre-execution revision 2

A conventional causal local rate-distortion baseline directly measures the implemented codec error on its own current block. It chooses depth by minimising signal MSE plus a nonnegative byte price. The projected price update targets 250 data bytes per report, with initial price .001 and step .01; it is not a hard per-round budget or a claimed novel optimal-control result. Its own shuffled control preserves its exact offered size multiset. The original primary contrast is unchanged.

A fixed-schedule 2-by-2 routing experiment replays the adaptive and shuffled schedules under standard MRHOF and the radio-reserve hook. The ETX conditions are offline schedule replays. A secondary seed-paired difference-in-differences estimates allocation-by-routing interaction conditional on this offered schedule. This does not identify a universal online deployment effect. Source decisions can change contention and packet paths even when application-size multisets match; identical physical airtime is not claimed.

Complete network failures are retained as zero-delivery outcomes. Existing run folders cannot be overwritten, and manifests record study-source and raw-log hashes. These safeguards prevent selective survivor analysis and stale-log reuse.
