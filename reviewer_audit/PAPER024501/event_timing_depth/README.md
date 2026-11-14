# PAPER024501 event timing and route-depth inspection

Reruns **60 original 100-node simulator cases**, crossing C3/C5,
shallow/medium/deep pre-calibrated topology profiles and the archived 10
seeds. The only source modification adds optional, offline trace output
when `REVIEW_EVENT_TRACE_PATH` is provided; event truth remains
unavailable to the relevance controller, the routing model and packet
decisions. The original archived seed-11 shallow C3 and C5 FND/HND/LND,
PDR and mean delay were rechecked with zero numerical differences.

Per-report columns distinguish:
- route hops selected for the event-active report;
- within-round modelled service lag from source processing to sink;
- event-onset-to-delivery *cumulative channel-airtime proxy*, which
  excludes inter-round sensing intervals.

The source simulator has no external sampling interval. Therefore the
proxy is not wall-clock event staleness, full AoI, or physical sensor-event
latency. Matched C3 and C5 samples require the **same seed, source, round,
event-onset round and successful delivery in both cases**. Every inference
uses the ten seed-level means as paired statistical observations, not
individual packets. Holm adjustment covers nine depth/metric tests.

No universal C3 event-staleness advantage is established by these data.
