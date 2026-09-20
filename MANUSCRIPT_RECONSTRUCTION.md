# Statistical-Utility-Aware Cross-Layer Hierarchical Federated Learning for Multi-Hop WSN-IoT Networks

## Abstract

Hierarchical federated learning (HFL) reduces cloud-facing communication by aggregating client updates at edge servers, but resource-aware participation can create a systems-learning conflict in wireless sensor network (WSN)-based Internet of Things (IoT) deployments. Clients with reliable links, short routes, and favorable energy states are inexpensive to schedule, whereas clients carrying statistically informative non-IID observations may be located behind lossy multi-hop paths or energy-constrained relays. Repeatedly optimizing only network cost can therefore improve communication efficiency while suppressing statistically valuable clients. This work studies that coupling rather than proposing a new ETX-family routing metric. We formulate a cross-layer HFL controller that combines statistical update utility, a representation-deficit virtual queue, route-dependent communication cost, relay-energy pressure, adaptive Top-k model-update sparsification with error feedback, and utility-aware staleness weighting. The controller operates above an existing ETX/residual-energy-aware routing substrate and explicitly accounts for relay-energy externalities created by model traffic. Validation spans correlated synthetic heterogeneity, the Intel Berkeley Lab WSN deployment, UCI smartphone human-activity sensing, and ns-3.47 IEEE 802.15.4/LR-WPAN communication replay. Under strong resource-data correlation in the Intel WSN experiment, the proposed policy reduces expected communication burden by 55.7%, modeled energy by 45.1%, maximum relay energy by 29.9%, and representation divergence by 81.2% relative to resource-only scheduling, while temperature RMSE is statistically comparable and slightly lower. On UCI HAR, it improves accuracy from 87.54% to 90.61% while reducing communication by 60.7% and energy by 56.4%. ns-3 replay of the resulting traffic profile increases dense-nominal report delivery from 86.5% to 99.5% and reduces mean delivered-report delay from 37.5 ms to 12.0 ms. The results support a Pareto-oriented view of WSN-HFL orchestration in which network efficiency and statistical representation are jointly controlled rather than optimized independently.

**Keywords:** hierarchical federated learning; wireless sensor networks; Internet of Things; non-IID data; client selection; adaptive compression; ETX; relay energy; staleness; representation.

## 1. Introduction

Federated learning (FL) enables distributed devices to train a shared model without centralizing raw observations. In WSN-IoT systems, however, the communication path between a learning-capable sensor/gateway and the cloud is rarely a cost-free abstraction. Updates may traverse lossy links and shared relays, compete for low-rate wireless capacity, and consume energy at intermediate nodes that are not themselves selected FL clients. Hierarchical federated learning reduces the need for repeated end-to-cloud exchanges by introducing edge aggregation, but it does not remove the interaction between learning decisions and network state.

A common systems strategy is to preferentially select clients with favorable bandwidth, latency, computation, or energy. This is rational from a short-term communication perspective, but under non-IID sensing data the statistically useful clients need not be the cheapest clients to reach. Environmental events may be geographically localized; activity patterns may be client-specific; and rare sensing conditions may originate in remote regions of the network. Consequently, a resource-efficient scheduler can repeatedly under-sample exactly those clients that contribute complementary statistical information.

Recent literature already addresses substantial pieces of this problem. Client-edge-cloud HFL is established; resource-aware client selection is established; adaptive staleness and heterogeneity-aware association have been studied; communication-efficient HFL can shape edge-level data distributions; and adaptive compression can be conditioned on heterogeneous device capabilities. Therefore, the research gap is not the independent existence of hierarchy, selection, compression, or asynchronous aggregation. The unresolved systems-learning coupling studied here is narrower: **how should an HFL controller decide whose update is worth transporting, at what fidelity, and with what aggregation influence when multi-hop route burden, relay energy, statistical utility, and participation history interact?**

This paper treats the underlying ETX/residual-energy-aware routing mechanism as prior infrastructure. The new contribution is the learning-layer orchestration placed above it. The controller maintains a statistical participation deficit, prices route and relay burden, adapts update fidelity through Top-k sparsification with error feedback, and modulates staleness according to learning value. This design makes it possible to distinguish three concepts that are frequently conflated: network-efficient participation, statistically useful participation, and equal participation.

The principal contributions are:

1. A cross-layer HFL formulation for multi-hop WSN-IoT networks in which client participation explicitly accounts for expected route traffic and the relay-energy externality created by model transport.
2. A representation-deficit mechanism that targets statistical influence rather than naive equal-frequency client fairness, reducing persistent exclusion of informative but resource-poor clients.
3. A utility-conditioned model-update fidelity mechanism that balances Top-k compression distortion against route and relay cost, with error feedback to retain discarded coordinates across rounds.
4. A utility-aware staleness weighting rule that allows delayed but informative updates to retain influence instead of relying solely on hard deadlines or age decay.
5. A multi-layer validation campaign using synthetic correlated heterogeneity, a real 54-mote WSN dataset and connectivity matrix, a real 30-subject inertial-sensing dataset, 10-seed paired statistical testing, component ablations, sensitivity analysis, and ns-3.47 IEEE 802.15.4/LR-WPAN replay.

## 2. Related Work and Positioning

Client-edge-cloud hierarchical FL was formalized by Liu et al. [1], establishing that intermediate aggregation can reduce cloud communication while changing the convergence/communication trade-off. Resource-aware client selection predates the present work; FedMCCS, for example, uses multiple client criteria in IoT FL [2]. Dynamic client-edge association and resource allocation have also been jointly optimized in HFL [3]. These studies mean that neither hierarchy nor a multicriteria resource score is sufficient as a new contribution.

The synchronization and heterogeneity dimensions are similarly active. HiFlash combines adaptive staleness control with heterogeneity-aware client-edge association [5], while asynchronous HFL variants reduce blocking due to heterogeneous completion times. Communication-efficient HFL has additionally been studied through data-distribution shaping at the edge [7]. Recent HFL formulations jointly optimize client selection, edge scheduling, radio resources, and semi-synchronous operation [8].

A second literature branch shows that biased client selection can affect statistical coverage under non-IID data. Fairness-aware client-selection work introduces long-term participation considerations [4], and recent surveys emphasize that system heterogeneity can restrict the participation or influence of clients that possess valuable but resource-constrained data [9]. Adaptive compression also overlaps with statistical heterogeneity: FedCG-type methods combine representative client selection with capability-aware gradient compression [6].

The present study therefore does **not** claim novelty for ETX routing, resource-aware selection, compression, or staleness individually. Its contribution is their cross-layer coupling with **statistical representation and relay-energy externality** in a multi-hop WSN-HFL setting, evaluated with both real sensing data and measured WSN connectivity.

## 3. System Model and Problem Definition

Consider a WSN-IoT graph \(G=(\mathcal V,\mathcal E)\), a set of learning-capable clients \(\mathcal C\), edge gateways \(\mathcal G\), and a cloud server. Client \(i\) owns local data \(D_i\sim P_i(X,Y)\), where generally \(P_i\neq P_j\). At communication round \(t\), a binary variable \(x_i(t)\) determines whether client \(i\) participates.

The network layer supplies a route \(\mathcal P_i(t)\) from client \(i\) to an edge gateway. For link \((u,v)\), let \(\operatorname{ETX}_{uv}(t)\) be its expected transmission count. Route burden is

\[
C_i^{\mathrm{route}}(t)=\sum_{(u,v)\in\mathcal P_i(t)}\operatorname{ETX}_{uv}(t).
\]

If \(b_i(t)\) update bits are transmitted, expected traffic is

\[
B_i^{\mathrm{eff}}(t)=x_i(t)b_i(t)C_i^{\mathrm{route}}(t).
\]

Unlike a single-hop abstraction, the same update consumes energy on intermediate relays. The cumulative burden on relay \(r\) is

\[
E_r^{\mathrm{cum}}(T)=\sum_{t=1}^{T}\sum_i x_i(t)\mathbf 1[r\in\mathcal P_i(t)]E_{ir}^{\mathrm{relay}}(t).
\]

The learning problem is therefore not equivalent to selecting the clients with minimum route cost. A statistically informative client can have a poor route, and repeatedly suppressing that client can bias long-run aggregation influence. The controller must balance statistical utility, communication cost, relay-energy depletion, and staleness.

## 4. Cross-Layer Statistical-Utility-Aware HFL

### 4.1 Statistical utility

For each client, the controller maintains a privacy-compatible learning-value estimate. Conceptually,

\[
U_i(t)=\alpha_gG_i(t)+\alpha_lL_i(t)+\alpha_hH_i(t),
\]

where \(G_i\) represents update novelty, \(L_i\) learning progress/difficulty, and \(H_i\) an optional distribution-rarity term when available. In the executed implementation, the **pre-selection** score uses normalized current local loss and the exponentially smoothed utility history; update novelty and observed local improvement become available only after a client trains and are then used to update that history and to modulate staleness weighting. Raw client examples are not exposed to the scheduler.

The normalized desired statistical participation target is

\[
\pi_i(t)=\frac{U_i(t)+\epsilon}{\sum_j(U_j(t)+\epsilon)}.
\]

### 4.2 Representation-deficit queue

A virtual queue tracks the difference between desired and realized participation share:

\[
Q_i(t+1)=\left[Q_i(t)+\pi_i(t)-a_i(t)\right]^+.
\]

Here \(a_i(t)=x_i(t)/k_t\) for a selected set of size \(k_t>0\), and \(a_i(t)=0\) when no client is selected. This is deliberately different from enforcing identical selection frequency. Clients are allowed unequal participation when their statistical value differs, but persistent starvation creates queue pressure that increases their future scheduling priority. Directly from the queue recursion,

\[
\frac1T\sum_{t<T}a_i(t)
\ge
\frac1T\sum_{t<T}\pi_i(t)
-
\frac{Q_i(T)-Q_i(0)}{T}.
\]

Thus rate stability of \(Q_i\) is sufficient for meeting the long-run **participation-share** target. It does not guarantee equality of final aggregation influence with \(\pi_i\), because compression, drops, staleness and hierarchical weighting intervene after selection.

### 4.3 Relay-energy queue

For relay \(r\),

\[
Z_r(t+1)=\left[Z_r(t)+E_r^{\mathrm{relay}}(t)-\bar E_r\right]^+,
\]

and route pressure for client \(i\) is

\[
R_i(t)=\sum_{r\in\mathcal P_i(t)}Z_r(t).
\]

This term captures the funneling effect caused by repeatedly transporting model updates through the same relay corridor.

### 4.4 Adaptive update fidelity

Let \(\rho_i(t)\) be the retained Top-k fraction. The controller evaluates a finite set of compression ratios and minimizes

\[
J_i^{\mathrm{comp}}(\rho)=
\rho\left(\widetilde C_i^{\mathrm{route}}+\eta_E\widetilde S_i+\eta_R\widetilde R_i\right)
+\beta U_i(t)(1-\rho)^2.
\]

The first term prices network burden; the second discourages aggressive compression of statistically important updates. Error feedback accumulates omitted coordinates for subsequent rounds. After a 10-seed sensitivity sweep on both real datasets, the common operating point is frozen at \(\eta_R=3\) and \(\beta=0.1\).

### 4.5 Queue-informed drift-plus-penalty surrogate

For each eligible client,

\[
\Gamma_i(t)=V\widetilde U_i(t)+Q_i(t)-V\rho_i(t)
\left(\widetilde C_i^{\mathrm{route}}+\eta_E\widetilde S_i+\eta_R\widetilde R_i\right).
\]

If \(M_t\) clients are eligible, the executed controller selects exactly \(k_t=\min(K_t,M_t)\) clients with the largest \(\Gamma_i(t)\). For fixed candidate compression ratios this top-\(k_t\) operation exactly maximizes the additive score over all subsets of cardinality \(k_t\). Eligibility is determined by availability and a residual-energy threshold; the implementation does not impose a stronger hard pre-selection constraint requiring the full prospective training-plus-transmission energy to be below the residual battery.

The score is motivated by the Lyapunov drift terms but is not an exact canonical drift-plus-penalty minimizer: route cost, energy scarcity and relay pressure are normalized each round, and relay pressure enters as a normalized path-queue feature rather than the unnormalized product \(Z_rE_{ir}\) in the raw drift bound. This distinction limits the theoretical claims below.

### 4.6 Utility-aware staleness

If an update generated at round \(t_i\) arrives at round \(t\), its staleness is \(s_i=t-t_i\). Edge aggregation uses

\[
\omega_i(t)=n_i e^{-\lambda_s s_i}\left(1+\mu U_i(t_i)\right),
\]

followed by normalization. Thus age still penalizes stale updates, but a statistically valuable delayed update is not discarded solely because it is slow.

### 4.7 Exact queue and decision guarantees

**Proposition 1 (finite-horizon queue guarantees).** Define the quadratic virtual-queue Lyapunov function

\[
\mathcal L(t)=\frac12\sum_iQ_i^2(t)+\frac12\sum_rZ_r^2(t).
\]

Let \(d_i(t)=\pi_i(t)-a_i(t)\) and \(h_r(t)=E_r^{\mathrm{relay}}(t)-\bar E_r\). Using \(([q+y]^+)^2\le q^2+y^2+2qy\),

\[
\mathcal L(t+1)-\mathcal L(t)
\le
B(t)+\sum_iQ_i(t)d_i(t)+\sum_rZ_r(t)h_r(t),
\]

where \(B(t)=\frac12\sum_i d_i^2(t)+\frac12\sum_r h_r^2(t)\), which is bounded whenever per-round relay energy is bounded. Telescoping the virtual queues gives the exact finite-horizon bounds

\[
\frac1T\sum_{t<T}a_i(t)
\ge
\frac1T\sum_{t<T}\pi_i(t)
-
\frac{Q_i(T)-Q_i(0)}{T},
\]

and

\[
\frac1T\sum_{t<T}E_r^{\mathrm{relay}}(t)
\le
\bar E_r+
\frac{Z_r(T)-Z_r(0)}{T}.
\]

Therefore rate stability of \(Q_i\) and \(Z_r\) is sufficient for satisfying the corresponding long-run participation-share and relay-energy constraints. The proof follows directly from \(([q+y]^+)^2\le q^2+y^2+2qy\) and telescoping the two queue recursions.

**Proposition 2 (per-round decision exactness).** Exhaustive enumeration of the finite compression set returns the exact minimizer of the stated compression surrogate, and the top-\(k_t\) step exactly maximizes the implemented additive client score over all eligible subsets of size \(k_t\). These are exact statements about the implemented surrogates, not global optimality claims for the end-to-end FL objective.

**Lemma 1 (error-feedback conservation).** For Top-k error feedback, with raw update \(u_i(t)\), residual \(e_i(t)\), and transmitted sparse update \(c_i(t)\),

\[
e_i(t+1)=u_i(t)+e_i(t)-c_i(t),
\]

which implies

\[
\sum_{t<T}c_i(t)=\sum_{t<T}u_i(t)+e_i(0)-e_i(T).
\]

Hence omitted coordinates are conserved in the residual rather than permanently discarded.

These guarantees are intentionally narrower than the classical Lyapunov-optimization result of an \(O(1/V)\) time-average penalty gap with \(O(V)\) backlog [12]. That theorem requires direct minimization of the relevant drift-plus-penalty bound under suitable feasibility/slack assumptions. The executed controller instead normalizes queue-derived pressures and separately chooses compression through a distortion surrogate; moreover, the participation targets sum to one, so uniform strict slack for all participation queues is generally unavailable. We therefore do **not** transfer the canonical \(O(1/V)\)/\(O(V)\) guarantee to the executed policy, nor do we claim a complete non-convex FL convergence theorem for the joint selection-compression-hierarchy-staleness process.

## 5. Experimental Methodology

### 5.1 Synthetic correlated heterogeneity

The controlled simulator uses 24 clients, four edge gateways, multi-hop ETX/residual-energy-aware paths, Top-k model-update compression, relay energy accounting, and three resource-data correlation levels \(c\in\{0,0.5,0.9\}\). Four policies are compared under the same training budget: random selection, resource-only selection, utility-only selection, and the proposed cross-layer controller. Final synthetic results use 10 seeds.

### 5.2 Intel Berkeley Lab WSN

The Intel Berkeley Research Lab dataset contains readings and deployment information from 54 Mica2Dot motes. Temperature, humidity, light, and voltage are used as sensing variables; measured directed connectivity probabilities and physical mote locations provide a real WSN substrate. Four spatially distributed high-connectivity motes are treated as edge gateways and excluded from learning, leaving 48 learning clients.

The task is per-mote next-temperature regression. A 16-step history of temperature, humidity, log-light, and voltage forms 64 input features. Data are partitioned temporally within each mote. The experiment uses 30 federated rounds, 10 clients per round, three resource-data correlation settings, and 10 paired seeds.

### 5.3 UCI Human Activity Recognition

The UCI HAR dataset contains smartphone inertial measurements from 30 subjects performing six activities. Each subject is treated as one FL client. The original train and test files are recombined and then split 80/20 within each subject using a fixed partition seed, preserving client identity and providing local held-out evaluation. A regularized linear softmax model is trained over 561 standardized features. Experiments use 25 rounds, eight clients per round, three resource-data correlation settings, and 10 paired seeds.

### 5.4 ns-3.47 IEEE 802.15.4 validation

The learning-layer traffic profile is replayed through ns-3.47 LR-WPAN with CSMA/CA, ACKs, retransmissions, and contention. The primary hop-equivalent mapping converts compressed update bits and selected hop count into offered traffic while allowing ns-3 to generate its own retransmissions. An ETX-equivalent mapping is retained only as a stress sensitivity because ETX already represents expected transmission attempts. The final campaign executes 400 ns-3 runs across five load/scaling conditions, two mappings, four policies, and 10 paired seeds. Eleven official ns-3 LR-WPAN test suites pass with zero failures.

### 5.5 Metrics and statistics

Learning metrics include global accuracy/Macro-F1 or RMSE/MAE, worst-client performance, and dispersion across clients. Systems metrics include expected transmitted bits, modeled energy, maximum relay energy, residual energy, selected-route ETX/hops, and ns-3 report delivery/delay. Participation is summarized with Jain's index, while statistical influence mismatch is measured with Jensen-Shannon divergence. Real-data comparisons use 10 paired seeds, exact paired sign-flip permutation tests, bootstrap 95% confidence intervals for paired differences, paired effect sizes, and Holm correction across the reported metric family.

## 6. Results

### 6.1 Synthetic stress test

At correlation \(c=0.9\), resource-only scheduling reaches 93.63% accuracy with 1.544 M expected transmitted bits, 6.291 J modeled energy, and representation divergence 0.0744. The proposed controller reaches 93.64% accuracy with 0.544 M bits, 4.732 J, and representation divergence 0.0202. Thus the final tuned controller preserves the learning result while sharply reducing communication and representation mismatch.

### 6.2 Intel WSN results

At \(c=0.9\), the Intel WSN experiment gives mean ± 95% confidence interval over 10 paired seeds:

| Method | RMSE (°C) ↓ | MAE (°C) ↓ | Effective Mbit ↓ | Energy (J) ↓ | Max relay energy (J) ↓ | Representation JS ↓ |
|---|---:|---:|---:|---:|---:|---:|
| Random | 1.7381 ± 0.0028 | 0.8021 ± 0.0074 | 2.515 ± 0.050 | 6.986 ± 0.116 | 0.2736 ± 0.0247 | 0.0749 ± 0.0060 |
| Resource-only | 1.7451 ± 0.0030 | 0.8297 ± 0.0087 | 2.217 ± 0.014 | 6.298 ± 0.031 | 0.1393 ± 0.0060 | 0.1231 ± 0.0068 |
| Utility-only | **1.7293 ± 0.0015** | **0.7786 ± 0.0055** | 2.692 ± 0.019 | 7.392 ± 0.045 | 0.3136 ± 0.0178 | 0.0561 ± 0.0025 |
| Proposed | 1.7417 ± 0.0052 | 0.7968 ± 0.0113 | **0.983 ± 0.019** | **3.460 ± 0.043** | **0.0976 ± 0.0024** | **0.0231 ± 0.0023** |

Relative to resource-only scheduling, the proposed controller reduces expected communication by 55.67%, total modeled energy by 45.06%, maximum relay energy by 29.94%, and representation divergence by 81.21%. MAE improves by 3.96%; these five improvements remain significant after Holm correction (Holm-adjusted \(p=0.0117\)). The RMSE difference is small (-0.19%) and is not statistically significant (exact paired sign-flip and Holm-adjusted \(p=0.2246\)); it is therefore described as comparable rather than superior. Utility-only obtains the lowest RMSE but at markedly higher communication, total energy, and relay burden.

### 6.3 UCI HAR results

At \(c=0.9\), mean ± 95% confidence interval over 10 paired seeds is:

| Method | Accuracy ↑ | Macro-F1 ↑ | Worst-client accuracy ↑ | Effective Mbit ↓ | Energy (J) ↓ | Max relay energy (J) ↓ | Representation JS ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Random | 0.8216 ± 0.0345 | 0.7949 ± 0.0489 | 0.6479 ± 0.0409 | 41.416 ± 3.318 | 70.83 ± 7.38 | 3.812 ± 1.189 | 0.0590 ± 0.0103 |
| Resource-only | 0.8754 ± 0.0196 | 0.8724 ± 0.0226 | 0.6814 ± 0.0173 | 29.651 ± 1.154 | 45.92 ± 1.80 | **0.458 ± 0.091** | 0.1634 ± 0.0302 |
| Utility-only | 0.7188 ± 0.0303 | 0.6626 ± 0.0406 | 0.5682 ± 0.0270 | 42.334 ± 2.904 | 72.35 ± 6.54 | 5.036 ± 1.102 | 0.0763 ± 0.0101 |
| Proposed | **0.9061 ± 0.0022** | **0.9060 ± 0.0024** | **0.7169 ± 0.0150** | **11.639 ± 0.713** | **20.03 ± 1.57** | 1.415 ± 0.344 | **0.0327 ± 0.0078** |

Against resource-only scheduling, accuracy improves by 3.08 percentage points, Macro-F1 by 3.36 points, worst-client accuracy by 3.55 points, expected communication decreases by 60.75%, total modeled energy decreases by 56.38%, and representation divergence decreases by 79.97%. These differences remain significant after Holm correction (Holm-adjusted \(p=0.0156\)). However, maximum relay energy increases from 0.458 J to 1.415 J, a 209.28% increase relative to resource-only (Holm-adjusted \(p=0.0156\)). This negative trade-off is retained explicitly: resource-only scheduling minimizes the relay hotspot by strongly favoring cheap paths, whereas the proposed controller spends more relay energy to preserve statistical participation while still using substantially less relay energy than random or utility-only scheduling.

### 6.4 Ablation

On Intel WSN, removing the representation-deficit term increases representation divergence from 0.0231 to 0.0401. Replacing adaptive compression with fixed 50% compression increases traffic from 0.983 M to 2.419 M bits and energy from 3.460 J to 6.763 J. Removing relay pressure increases maximum relay energy from 0.0976 J to 0.1089 J. Utility-aware staleness has a smaller effect in this dataset because most updates arrive with limited staleness.

On UCI HAR, removing the representation queue increases representation divergence from 0.0327 to 0.0665. Fixed compression reduces accuracy to 79.12% and increases traffic to 33.62 M bits. Removing relay pressure increases maximum relay energy from 1.415 J to 1.654 J. These ablations show that representation control, adaptive update fidelity, and relay pressure serve distinct functions.

### 6.5 ns-3 communication validation

Under the primary hop-equivalent dense-nominal condition, resource-only traffic obtains an 86.49% report delivery ratio with 37.45 ms mean delivered-report delay. The final proposed traffic profile obtains 99.47% delivery with 12.02 ms mean delay. At the scaled 24-sensor nominal condition, the proposed profile also remains markedly more deliverable because its compressed updates place substantially less offered load on the LR-WPAN channel. These results validate the communication consequences of the learned traffic profile, but they do not mean the Python HFL optimization itself is executed inside ns-3.

## 7. Discussion

The experiments support the central premise that network-efficient clients and statistically valuable clients are not interchangeable. Resource-only scheduling consistently lowers some route costs, but it also produces substantially higher representation divergence in the real-data experiments. Utility-only selection has the opposite failure mode: it can overuse expensive routes and relays. The proposed controller operates between these extremes by introducing explicit pressure from participation deficit, route cost, relay queues, and compression distortion.

The Intel experiment is particularly useful because the proposed controller does not win the lowest regression error. Utility-only selection achieves slightly lower RMSE, but at substantially higher communication, energy, and relay burden. This prevents an inappropriate “best on every metric” claim and motivates a Pareto interpretation. In contrast, UCI HAR exhibits a regime in which the systems-learning coupling improves both learning quality and overall communication/energy efficiency, because the representation deficit prevents resource-only scheduling from repeatedly concentrating on a restricted client subset. The exception is maximum relay energy: resource-only scheduling achieves the lowest relay hotspot (0.458 J versus 1.415 J for the proposed controller). This is not contradictory to the objective; it exposes the cost of preserving statistically valuable participation instead of always choosing the cheapest routes.

The sensitivity study further shows that the relay-pressure coefficient and compression-distortion coefficient are genuine control parameters. Excessively high compression-distortion penalties increase traffic and energy, while too little relay pressure creates hotspot burden. A common operating point \((\eta_R,\beta)=(3,0.1)\) is frozen across datasets to avoid dataset-specific tuning.

## 8. Limitations

The current evidence is stronger than the original simulation-only manuscript but remains incomplete in several respects. First, the host implementation runs on an Apple M1 computer; no physical IEEE 802.15.4 sensor mote was available during the experiment, so MCU training time, radio current draw, RSSI/LQI, and hardware PDR are not claimed. Second, the Intel dataset provides real historical connectivity but the FL process itself is a replay over those measurements rather than execution on the original Mica2Dot nodes. Third, the local models are intentionally lightweight linear predictors/classifiers; larger TinyML models should be tested before making model-complexity claims. Fourth, the theory now provides exact finite-horizon virtual-queue bounds, a one-step drift inequality, finite-set compression optimality, top-k score optimality, and error-feedback conservation; however, a complete non-convex convergence proof jointly covering biased selection, Top-k error feedback, hierarchy, packet loss, and staleness remains future work.

## 9. Conclusion

This study reframes communication-efficient HFL for WSN-IoT systems as a joint statistical-representation and network-resource problem. Instead of introducing another routing metric, the proposed controller uses route state as an input to learning orchestration and coordinates client participation, update fidelity, relay pressure, and staleness-aware aggregation. Real WSN data, real IoT sensing data, repeated statistical tests, ablations, sensitivity analysis, and ns-3 LR-WPAN replay show that the approach can substantially reduce communication and total modeled energy while preserving or improving learning quality and reducing representation mismatch. Relay-hotspot energy is also reduced in the Intel WSN experiment and relative to random/utility scheduling on UCI HAR, but it is not universally lower than the resource-only baseline. The remaining step for a complete systems paper is physical sensor-node validation and a full convergence treatment of the coupled learning dynamics.

## References used for positioning

[1] L. Liu, J. Zhang, S. H. Song, and K. B. Letaief, “Client-Edge-Cloud Hierarchical Federated Learning,” IEEE ICC, 2020. DOI: 10.1109/ICC40277.2020.9148862.

[2] A. AbdulRahman et al., “FedMCCS: Multicriteria Client Selection Model for Optimal IoT Federated Learning,” IEEE Internet of Things Journal. DOI: 10.1109/JIOT.2020.3028742.

[3] Dynamic edge association/resource allocation work in hierarchical FL, IEEE JSAC. DOI: 10.1109/JSAC.2021.3118401.

[4] Long-term fairness-aware client selection in FL, IEEE Internet of Things Journal. DOI: 10.1109/JIOT.2022.3172113.

[5] Q. Wu, X. Chen, T. Ouyang et al., “HiFlash: Communication-Efficient Hierarchical Federated Learning With Adaptive Staleness Control and Heterogeneity-Aware Client-Edge Association,” IEEE TPDS, 2023. DOI: 10.1109/TPDS.2023.3238049.

[6] Heterogeneity-aware representative client selection with adaptive gradient compression, IEEE INFOCOM 2023. DOI: 10.1109/INFOCOM53939.2023.10229029.

[7] Y. Deng, F. Lyu, T. Xia et al., “A Communication-Efficient Hierarchical Federated Learning Framework via Shaping Data Distribution at Edge,” IEEE/ACM Transactions on Networking, 2024. DOI: 10.1109/TNET.2024.3363916.

[8] Client selection, edge scheduling, and resource allocation in semi-synchronous HFL, IEEE Transactions on Wireless Communications, 2024. DOI: 10.1109/TWC.2024.3411479.

[9] M. Alsofyani, I. Al-Turaiki, and H. Mathkour, “A Fairness Perspective on Client Selection and Aggregation Methods for Non-IID Mitigation in Federated Learning: A Survey,” Electronics, 2026. DOI: 10.3390/electronics15143178.

[10] Intel Berkeley Research Lab sensor dataset: https://db.csail.mit.edu/labdata/labdata.html.

[11] UCI Human Activity Recognition Using Smartphones dataset. DOI: 10.24432/C54S4K.

[12] M. J. Neely, *Stochastic Network Optimization with Application to Communication and Queueing Systems*, Morgan & Claypool, 2010. DOI: 10.2200/S00271ED1V01Y201006CNT007.

## Final manuscript figure set

The manuscript must use **only** the following user-approved final figures. Superseded figure versions are not to be reinserted.

1. `figures/final/01_network_topology.png` — WSN deployment/topology illustration.
2. `figures/final/02_system_architecture.png` — cloud–edge–cluster-head/relay–sensor/client architecture.
3. `figures/final/03_ns3_validation.png` — ns-3.47 LR-WPAN validation.
4. `figures/final/04_ablation.png` — Intel and UCI HAR ablation results.
5. `figures/final/05_learning_communication_tradeoff.png` — Intel/UCI HAR learning–communication trade-off.
6. `figures/final/06_uci_har_results.png` — UCI HAR comparative results.
7. `figures/final/07_intel_berkeley_results.png` — Intel Berkeley Lab comparative results.

Figure numbers/captions are intentionally excluded from the PNG artwork and must be typeset explicitly in the manuscript. All seven PNG files are stored with 600 dpi metadata.
