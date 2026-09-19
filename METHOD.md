# Method model

## State variables

For client `i` at round `t`:

- `x_i(t)` — binary participation decision.
- `rho_i(t)` — transmitted model-update fraction.
- `P_i(t)` — current multi-hop route to an edge gateway.
- `U_i(t)` — estimated statistical learning utility.
- `Q_i(t)` — participation-deficit virtual queue.
- `Z_r(t)` — relay-energy virtual queue for relay `r`.

## Network cost

The routing substrate computes a prior-work RE-ETX-like route cost. The learning layer does not redefine ETX.

For a compressed update of `b_i(t)` bits, expected route traffic is

~~~text
B_eff,i(t) = b_i(t) * sum_{(u,v) in P_i(t)} ETX_uv(t)
~~~

and relay energy is charged to every sensor that transmits or receives the update along that path.

## Statistical utility

The implementation maintains a private-learning proxy from current local loss plus an exponentially smoothed history of update novelty / local loss improvement. Raw local data are not shared.

## Drift-plus-penalty scheduler

The proposed scheduler uses a Lyapunov-inspired score:

~~~text
score_i = V * utility_i + Q_i
          - V * communication_and_energy_cost_i
          - relay_pressure_i
~~~

with `Q_i` updated from the gap between desired statistical influence and realized participation.

## Adaptive update fidelity

For each candidate compression ratio `rho`, a per-client proxy balances route burden and compression distortion:

~~~text
cost(rho) = rho * network_pressure
            + beta * utility_i * (1-rho)^2
~~~

The selected `rho` minimizes this proxy. Top-k sparsification uses error feedback, so discarded coordinates are accumulated rather than permanently lost.

## Staleness

Arriving updates are weighted by exponential age decay. For the proposed method this is modulated by statistical utility:

~~~text
weight_i(t) = exp(-lambda * staleness_i) * (1 + mu * utility_i)
~~~

before edge aggregation and cloud aggregation.

## Evaluation quantities

The implementation reports accuracy, macro-F1, expected transmitted bits, energy, minimum residual energy, Jain participation index, representation JS divergence, class-coverage JS divergence, relay queue pressure and maximum cumulative relay energy.