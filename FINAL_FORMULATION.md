# Frozen mathematical formulation

## 1. System model

Consider a multi-hop WSN-IoT graph \(G=(\mathcal V,\mathcal E)\) with learning-capable clients \(\mathcal C\subseteq\mathcal V\), relay nodes, edge gateways \(\mathcal G\), and a cloud server. Client \(i\) owns non-IID data \(D_i\) and at round \(t\) may participate through \(x_i(t)\in\{0,1\}\). Its current path to an assigned edge gateway is \(\mathcal P_i(t)\). The routing layer is an inherited ETX / residual-energy-aware substrate; the present work does not claim a new ETX metric.

For link \((u,v)\), let \(q_{uv}(t)\) denote packet-delivery probability and \(\operatorname{ETX}_{uv}(t)\) its expected transmission count. The route burden is

\[
C_i^{\mathrm{route}}(t)=\sum_{(u,v)\in\mathcal P_i(t)}\operatorname{ETX}_{uv}(t).
\]

If \(b_i(t)\) compressed update bits are transmitted, expected communication burden is

\[
B_i^{\mathrm{eff}}(t)=x_i(t)b_i(t)C_i^{\mathrm{route}}(t).
\]

The route also creates an energy externality on relays. Let \(E_{ir}^{\mathrm{relay}}(t)\) be the energy charged to relay \(r\) when transporting client \(i\)'s update.

## 2. Learning utility

The learning layer distinguishes network quality from statistical value. A client utility estimator is

\[
U_i(t)=\alpha_g G_i(t)+\alpha_l L_i(t)+\alpha_h H_i(t),
\]

where \(G_i\) denotes update novelty (e.g. cosine distance from an edge/global reference), \(L_i\) denotes local loss reduction or learning difficulty, and \(H_i\) may denote a distribution/rarity term when available. The implementation uses privacy-compatible proxies based on local loss, update novelty, local improvement, and history; raw client data are not exposed to the scheduler.

Normalize the statistical target share as

\[
\pi_i(t)=\frac{U_i(t)+\epsilon}{\sum_j(U_j(t)+\epsilon)}.
\]

## 3. Representation-deficit queue

To prevent persistent exclusion of statistically informative but resource-poor clients, maintain

\[
Q_i(t+1)=\big[Q_i(t)+\pi_i(t)-a_i(t)\big]^+,
\]

where \(a_i(t)\) is the realized round participation share. Mean-rate stability of \(Q_i\) implies long-term participation tracks the desired statistical share in aggregate rather than enforcing equal participation.

A post-hoc representation metric is

\[
\Phi_{\mathrm{rep}}(T)=D_{JS}(\mathbf p(T)\Vert\boldsymbol\pi(T)),
\]

where \(\mathbf p(T)\) is cumulative aggregation influence and \(\boldsymbol\pi(T)\) cumulative statistical target influence.

## 4. Relay-energy virtual queue

For each relay \(r\), define

\[
Z_r(t+1)=\left[Z_r(t)+E_r^{\mathrm{relay}}(t)-\bar E_r\right]^+,
\]

where \(\bar E_r\) is the admissible long-term per-round relay-energy budget. The route pressure seen by client \(i\) is

\[
R_i(t)=\sum_{r\in\mathcal P_i(t)}Z_r(t).
\]

This explicitly prices the WSN funneling/hotspot effect created by model traffic traversing shared relays.

## 5. Adaptive update fidelity

Let \(\rho_i(t)\in\mathcal R\subset(0,1]\) denote the retained Top-k fraction. For each eligible client, the controller chooses \(\rho_i\) by minimizing the per-client proxy

\[
J_i^{\mathrm{comp}}(\rho)=
\rho\left(\widetilde C_i^{\mathrm{route}}+eta_E\widetilde S_i+\eta_R\widetilde R_i\right)
+\beta U_i(t)(1-\rho)^2,
\]

where tildes denote normalized route, energy-scarcity, and relay-pressure terms. The first component prices network burden; the second penalizes compression distortion more strongly for statistically valuable updates. Top-k sparsification uses error feedback so discarded coordinates are accumulated for later transmission.

The sensitivity study freezes \(\eta_R=3\) and \(\beta=0.1\) as the common cross-dataset operating point. This point was selected after a 10-seed sweep rather than chosen post hoc from a single run.

## 6. Drift-plus-penalty client orchestration

For eligible client \(i\), define normalized system cost

\[
C_i(t,\rho_i)=\rho_i(t)\left(
\widetilde C_i^{\mathrm{route}}(t)
+\eta_E\widetilde S_i(t)
+\eta_R\widetilde R_i(t)
\right).
\]

The round scheduler ranks candidates by

\[
\Gamma_i(t)=V\widetilde U_i(t)+Q_i(t)-V C_i(t,\rho_i),
\]

and admits at most \(K_t\) clients with highest \(\Gamma_i(t)\), subject to availability and residual-energy feasibility. This replaces the original manually weighted RACE-FL resource score.

The corresponding long-term systems objective is

\[
\min \limsup_{T\to\infty}\frac1T\sum_{t=0}^{T-1}
\mathbb E\left[
\lambda_B B_{\mathrm{eff}}(t)+
\lambda_E E_{\mathrm{net}}(t)+
\lambda_R\Phi_{\mathrm{relay}}(t)
-\lambda_U U_{\mathrm{sel}}(t)
\right]
\]

subject to participation/representation and relay-energy constraints induced by stable virtual queues. Model loss is evaluated end-to-end rather than inserted as an instantaneous schedulable cost that is unavailable before training.

## 7. Hierarchical aggregation and staleness

Client updates first aggregate at the edge and then at the cloud. For an update generated at round \(t_i\) and aggregated at round \(t\), staleness is \(s_i=t-t_i\). Its edge-level raw weight is

\[
\omega_i(t)=n_i e^{-\lambda_s s_i}\left(1+\mu U_i(t_i)\right),
\]

followed by normalization within the edge aggregate. Thus age reduces influence, but statistically valuable delayed updates are not automatically discarded solely because they are slow.

## 8. Decision variables and constraints

The final implementation optimizes/controls

\[
\{x_i(t),\rho_i(t),\omega_i(t)\}
\]

over a routing substrate that supplies \(\mathcal P_i(t)\) and route state. Constraints include

\[
\sum_i x_i(t)\le K_t,
\qquad E_i^{\mathrm{train}}(t)+E_i^{\mathrm{tx}}(t)\le E_i^{\mathrm{res}}(t),
\]

\[
0\le s_i(t)\le s_{\max},
\qquad \rho_i(t)\in\mathcal R,
\]

plus long-term participation and relay-energy constraints represented through \(Q_i\) and \(Z_r\).

## 9. What is and is not claimed theoretically

The scheduler has the standard structure of Lyapunov drift-plus-penalty control. Under bounded per-round utilities/costs and existence of a feasible stationary policy, standard Lyapunov arguments motivate an \(O(1/V)\) utility-cost gap with \(O(V)\) virtual-queue growth for the scheduling subproblem. The present implementation does **not yet claim a complete non-convex FL convergence theorem simultaneously covering biased selection, Top-k error feedback, hierarchy, and staleness**. A manuscript must state that distinction explicitly unless a formal proof is added.

## 10. Computational complexity

For \(N\) eligible clients, \(|\mathcal R|\) candidate compression ratios, and model dimension \(d\):

- client scoring/compression-ratio search: \(O(N|\mathcal R|)\),
- ranking for top-\(K\): \(O(N\log N)\) in the current implementation,
- Top-k sparsification: \(O(d)\) expected using partial selection,
- aggregation: \(O(Kd)\),
- routing is external/prior infrastructure and is not charged as a novel algorithmic component.

This formulation is the frozen basis for the reconstructed manuscript and future theorem development.
