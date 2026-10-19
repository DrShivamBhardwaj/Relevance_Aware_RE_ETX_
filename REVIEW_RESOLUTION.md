# Reviewer issue resolution status

Status: component implementation and local checks completed; Cooja experiments and manuscript integration remain pending.

| Review concern | Implemented response | Remaining evidence |
| --- | --- | --- |
| Payload bits had no specified content | 250-sample progressive codec and explicit decoder; full-depth lossless and bounded-error tests | Actual network reconstruction errors |
| Novelty was weak | Receiver utility per offered transmission budget is the new evaluation question | Scientific advantage is not established before execution |
| Mean bits did not match frame distribution | Per-round exact offered payload-size multiset replay; common full-depth warm-up | Verify packet path, MAC behaviour and measured results |
| Central and dead-neighbour context | TTL-limited one-hop context beacons; no central context reads | Outage/stale-context Cooja outcomes |
| Lifetime and survivorship denominators | Fixed horizon; unavailable/late reports enter reconstruction error | Execute complete offered-report population |
| Statistical fragility | Twenty new seeds; one primary contrast; paired effects and exact sensitivity; historical global correction retained | New Cooja seed-level observations |
| Easy event regime | Weak, persistent, drifting and biased workloads specified | Exploratory outcomes must be retained even if negative |
| Geometry was not scalability | 25/100 sources at fixed spacing; delivered-hop instrumentation | Executed density-preserving scaling |
| Channel/energy inconsistency | Actual Contiki CSMA/RPL; radio activity with declared CC2420 nominal-current model | Cooja native is not hardware or complete-device energy |
| Weak age-routing formulation | Excluded from the new controller; no freshness-superiority claim | Historical negative result remains narrowly scoped |
| Missing-route crash | Initialised zero-work result; failure-path tests pass | Additional packet-path testing in Cooja |
| Reproducibility | Pinned sources, analysis requirements, output manifests, workflow, isolated archives | Public branch/release pending explicit approval |
| Figure resolution and final paper presentation | No speculative Cooja figures inserted | Regenerate figures and revise paper after actual results |
| Author metadata/declarations | No author roles invented | Author contribution/email confirmation still required |

No new Cooja results, hardware results, statistical superiority, or submission readiness is claimed. The old manuscript remains a historical-results draft until the new evidence is available.
