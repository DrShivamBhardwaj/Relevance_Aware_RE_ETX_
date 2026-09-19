# Prior-work boundary

## Earlier WSN codebase

The earlier repository `DrShivamBhardwaj/Relevance_Aware_RE_ETX_` already contains:

- residual-energy-aware ETX routing;
- semantic-age terms in the route cost;
- relevance-aware application-payload adaptation;
- multi-hop WSN simulation and relay-load measurements.

The earlier routing implementation uses a dynamic cost of the form:

~~~text
ETX_ij * (1 + energy-scarcity penalty + semantic-age penalty)
~~~

and the earlier payload controller maps sensing/event relevance to application payload size.

These mechanisms are treated as **prior infrastructure** in the present project.

## What is intentionally different here

The new implementation does not present a new ETX-family metric and does not reuse sensing relevance as federated-learning utility.

Instead, it introduces a separate learning-layer state:

- local loss / learning difficulty;
- historical update novelty;
- observed local improvement;
- participation deficit;
- model-update staleness.

The scheduler combines that learning state with route burden and relay-energy pressure to decide **participation and model-update fidelity**.

Thus the conceptual transition is:

~~~text
Earlier work: how should sensed traffic be routed and sized?
Current work: whose model update is worth transporting, at what fidelity, and with what aggregation influence?
~~~

## Code-level separation

- `src/wsn_hfl/topology.py` contains an independent minimal RE-ETX-like network substrate; it is not claimed as the new algorithm.
- `src/wsn_hfl/scheduler.py` contains the new client-selection / update-fidelity decision layer.
- `src/wsn_hfl/simulator.py` contains relay-energy externality, hierarchical aggregation, participation-deficit queues and utility-aware staleness.
- No source file from the earlier repository is copied byte-for-byte into this project.

Any manuscript derived from this repository should cite and explicitly distinguish the earlier WSN work rather than presenting ETX/RE-ETX or semantic payload control as new.