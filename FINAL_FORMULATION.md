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

where \(G_i\) denotes update novelty (e.g. cosine distance from an edge/global reference), \(L_i\) denotes local loss reduction or learning difficulty, and \(H_i\) may denote a distribution/rarity term when available. In the executed scheduler, the pre-selection utility uses normalized current local loss together with an exponentially smoothed utility history. Update novelty and local improvement are observed only after a selected client trains, then update that history and the later staleness weight. Raw client examples are not exposed to the scheduler.

Normalize the statistical participation target share as

\[
\pi_i(t)=\frac{U_i(t)+\epsilon}{\sum_j(U_j(t)+\epsilon)}.
\]

## 3. Representation-deficit queue

To prevent persistent exclusion of statistically informative but resource-poor clients, maintain

\[
Q_i(t+1)=\big[Q_i(t)+\pi_i(t)-a_i(t)\big]^+,
\]

where \(a_i(t)=x_i(t)/k_t\) for a selected set of size \(k_t>0\), and \(a_i(t)=0\) when no client is selected. Hence \(\sum_i a_i(t)=1\) whenever a round selects at least one client. The exact finite-horizon queue identity gives

\[
\frac1T\sum_{t=0}^{T-1} a_i(t)
\ge
\frac1T\sum_{t=0}^{T-1}\pi_i(t)
-\frac{Q_i(T)-Q_i(0)}{T}.
\]

Therefore, if \(Q_i(T)/T\to0\) (rate stability), the long-term participation share meets the statistical target in the time-average sense. This is a **participation-share guarantee only**; it does not by itself guarantee equality between final aggregation influence and \(\pi_i\), because compression, staleness, packet loss, and hierarchical aggregation also affect influence.

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

The revised tuning-only sensitivity study freezes \(\eta_R=5\) and \(\beta=0.1\) as the common cross-dataset operating point. The setting is selected on 10 tuning seeds using a deterministic learning-feasibility plus systems-score rule; final comparisons use a disjoint 10-seed evaluation set.

## 6. Drift-plus-penalty client orchestration

For eligible client \(i\), define normalized system cost

\[
C_i(t,\rho_i)=\rho_i(t)\left(
\widetilde C_i^{\mathrm{route}}(t)
+\eta_E\widetilde S_i(t)
+\eta_R\widetilde R_i(t)
\right).
\]

The executed round scheduler ranks candidates by

\[
\Gamma_i(t)=V\widetilde U_i(t)+Q_i(t)-V C_i(t,\rho_i),
\]

and, when \(M_t\) clients are eligible, selects exactly \(k_t=\min(K_t,M_t)\) clients with the largest scores. For fixed \(\rho_i(t)\), this top-\(k_t\) rule exactly maximizes \(\sum_{i\in\mathcal S_t}\Gamma_i(t)\) over all subsets of cardinality \(k_t\). Eligibility uses availability and a residual-energy threshold; the current code does **not** enforce the stronger hard constraint \(E_i^{\mathrm{train}}+E_i^{\mathrm{tx}}\le E_i^{\mathrm{res}}\) before selection.

The score is **drift-plus-penalty inspired rather than an exact canonical Lyapunov minimizer**. In particular, the implementation normalizes route cost, energy scarcity, and relay pressure each round, and it uses the normalized path queue pressure inside \(C_i\) rather than the unnormalized term \(\sum_r Z_r E_{ir}\) that appears in the raw Lyapunov drift bound. This distinction is retained explicitly in the theory claims.

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

over a routing substrate that supplies \(\mathcal P_i(t)\) and route state. The executed implementation obeys

\[
\sum_i x_i(t)=k_t\le K_t,
\qquad
x_i(t)=0\ \text{when client }i\text{ is unavailable or }E_i^{\mathrm{res}}(t)\le E_{\min},
\]

\[
0\le s_i(t)\le s_{\max},
\qquad \rho_i(t)\in\mathcal R.
\]

Residual-energy scarcity is priced in the scheduling cost and actual training/transmission energy is debited after selection. Thus a strict pre-selection energy-feasibility inequality is **not** claimed for the current code. Long-term participation-share and relay-energy targets are represented through \(Q_i\) and \(Z_r\), respectively.

## 9. Exact theory supported by the implementation

Let

\[
L(t)=\frac12\sum_i Q_i^2(t)+\frac12\sum_r Z_r^2(t).
\]

Define \(d_i(t)=\pi_i(t)-a_i(t)\) and \(h_r(t)=E_r^{\mathrm{relay}}(t)-\bar E_r\). From \(([q+y]^+)^2\le q^2+y^2+2qy\),

\[
L(t+1)-L(t)
\le
B(t)+\sum_iQ_i(t)d_i(t)+\sum_r Z_r(t)h_r(t),
\]

where

\[
B(t)=\frac12\sum_i d_i^2(t)+\frac12\sum_r h_r^2(t).
\]

If per-round relay energy is bounded, then \(B(t)\le B_{\max}<\infty\). Two exact sample-path consequences follow directly from telescoping the queue recursions:

\[
\frac1T\sum_{t<T} a_i(t)
\ge
\frac1T\sum_{t<T}\pi_i(t)-\frac{Q_i(T)-Q_i(0)}{T},
\]

and

\[
\frac1T\sum_{t<T}E_r^{\mathrm{relay}}(t)
\le
\bar E_r+\frac{Z_r(T)-Z_r(0)}{T}.
\]

Hence rate stability of \(Q_i\) implies satisfaction of the long-term participation-share target, and rate stability of \(Z_r\) implies satisfaction of the relay-energy budget.

For compression, enumeration over the finite candidate set \(\mathcal R\) returns the exact minimizer of the stated **compression surrogate** \(J_i^{\mathrm{comp}}\). For selection, the top-\(k_t\) operation is the exact optimizer of the implemented additive score once candidate compression ratios are fixed.

The implementation also uses error feedback. If \(e_i(t)\) is the residual, \(u_i(t)\) the raw update, and \(c_i(t)\) the transmitted sparse update, then

\[
e_i(t+1)=u_i(t)+e_i(t)-c_i(t),
\]

so

\[
\sum_{t=0}^{T-1}c_i(t)
=
\sum_{t=0}^{T-1}u_i(t)+e_i(0)-e_i(T).
\]

Thus discarded coordinates are conserved in the residual rather than permanently erased; this identity alone is not a convergence theorem.

### 9.1 Claims deliberately not made

Classical Lyapunov optimization can yield an \(O(1/V)\) time-average penalty gap with an \(O(V)\) queue trade-off when a controller directly minimizes an appropriate drift-plus-penalty bound under the required feasibility/slack assumptions (see M. J. Neely, *Stochastic Network Optimization with Application to Communication and Queueing Systems*, 2010, DOI 10.2200/S00271ED1V01Y201006CNT007). The executed controller does not satisfy those conditions exactly because it normalizes queue-derived pressures and separately chooses compression through a distortion surrogate. Moreover, the participation targets sum to one, so a uniform strict-Slater slack for all representation queues is generally unavailable. Therefore **no \(O(1/V)\)/\(O(V)\) performance theorem is claimed for the executed policy**.

Likewise, the present work does **not** claim a complete non-convex FL convergence theorem simultaneously covering biased selection, Top-k error feedback, hierarchical aggregation, packet loss, and staleness. The proven statements are limited to the queue implications, one-step drift bound, finite-set compression optimality, top-\(k\) score optimality, and error-feedback conservation above.

## 10. Computational complexity

For \(N\) eligible clients, \(|\mathcal R|\) candidate compression ratios, and model dimension \(d\):

- client scoring/compression-ratio search: \(O(N|\mathcal R|)\),
- ranking for top-\(K\): \(O(N\log N)\) in the current implementation,
- Top-k sparsification: \(O(d)\) expected using partial selection,
- aggregation: \(O(Kd)\),
- routing is external/prior infrastructure and is not charged as a novel algorithmic component.

This formulation is the frozen basis for the reconstructed manuscript and future theorem development.
