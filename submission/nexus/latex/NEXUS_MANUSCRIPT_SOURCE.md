# Cross-Layer Utility-Aware Hierarchical Federated Learning for Multi-Hop IoT Sensor Networks

**Abhinandan Tripathi¹, Vijay Kumar Tiwari², Mohd. Arif³, Abhishek Kumar Pandey⁴*, Shivam Bhardwaj⁵**

¹Department of Computer Science and Engineering, Buddha Institute of Technology, Gorakhpur, India

²Department of Information Technology, Madan Mohan Malaviya University of Technology (MMMUT), Gorakhpur, India

³Department of Computer Science and Engineering, Galgotias University, Greater Noida, India

⁴Department of Computer Science and Engineering, Bennett University, Greater Noida, India

⁵United Institute of Management, Prayagraj, India

Emails: ¹abhinandan282@bit.ac.in; ²vktitca@mmmut.ac.in; ³md.arif@galgotiasuniversity.edu.in; ⁴abhishek.pandey2@bennett.edu.in; ⁵shibambhardwaj@gmail.com

ORCID: Abhishek Kumar Pandey — 0000-0003-3799-9754; Shivam Bhardwaj — 0009-0005-4554-7397

*Corresponding author: Abhishek Kumar Pandey (abhishek.pandey2@bennett.edu.in)

All authors contributed equally to this work.

## Highlights

- Two-level cloud influence is tracked after edge and cloud normalization
- Held-out evaluation separates parameter tuning from final inference
- Matched controls isolate adaptive compression from client scheduling
- Utility-target alignment improves at an explicit network-cost trade-off

## In brief

Tripathi et al. study how hierarchical federated-learning decisions change when model updates traverse multi-hop sensor routes. Their controller coordinates utility-target participation, update fidelity, relay pressure, and staleness, and is evaluated with held-out seeds, compression-matched controls, real sensing data, and low-power wireless replay.

## Broader context

Edge intelligence increasingly supports environmental monitoring, infrastructure observation, industrial sensing, and personal activity recognition, often where communication capacity and battery energy are limited. In these deployments, selecting a learning client also selects the route and relays that must transport its model update. The resulting design problem is not simply to minimize traffic: inexpensive clients can dominate training while remote or difficult-to-reach clients contribute less often. This study develops and audits a cross-layer controller that makes that trade-off explicit. Importantly, the revised experiments separate parameter tuning from held-out evaluation and compare selection policies under matched compression. The evidence therefore supports a Pareto interpretation rather than a claim of universal network or statistical superiority. Such transparent trade-offs are relevant when distributed intelligence must operate over low-power sensing infrastructure without overstating sustainability or population-representativeness claims.

## Abstract

Hierarchical federated learning (HFL) reduces repeated cloud communication through intermediate edge aggregation, but in multi-hop wireless sensor and Internet of Things networks the learning decision also determines which routes and relays carry model traffic. This coupling can place statistically useful clients behind costly paths and can make apparent communication gains depend more on update compression than on client scheduling. We develop a cross-layer HFL controller that combines a utility-target participation-deficit queue, route and residual-energy cost, relay-pressure feedback, adaptive Top-k sparsification with error feedback, and utility-aware staleness weighting. The revised evaluation corrects hierarchical influence accounting by applying both within-edge and cloud-level aggregation coefficients, separates 10 tuning seeds from 10 held-out evaluation seeds, uses an overlap-safe blocked split for UCI HAR, and adds compression-matched controls plus a FedCG-inspired gradient-diversity comparator. On Intel Berkeley Lab WSN data at strong resource-data correlation, the proposed controller achieves 1.7348 °C RMSE with 0.992 Mbit effective traffic; its learning and systems metrics are statistically comparable to the FedCG-adapted comparator, while utility-target influence divergence is 87.1% lower. A resource-adaptive control obtains lower RMSE and 8.3% less traffic, showing that the proposed method is not a universal networking optimum. On blocked UCI HAR, the proposed controller reaches 88.67% accuracy, 1.16 percentage points above resource-adaptive and 1.07 points above FedCG-adapted, but uses 26.8% and 20.9% more traffic, respectively. Independent temperature- and class-coverage metrics do not establish universal distributional superiority. Adaptive update fidelity is the dominant traffic-saving mechanism: relative to the same proposed selector at fixed 50% Top-k, it cuts traffic by 58.2% on Intel and 64.0% on HAR. ns-3.47 IEEE 802.15.4 replay confirms that the lower synthetic offered load materially improves delivery under contention. The evidence therefore supports a Pareto-oriented cross-layer controller rather than claims of statistical representativeness or resource sustainability.

**Keywords:** hierarchical federated learning; wireless sensor networks; Internet of Things; non-IID data; client selection; adaptive compression; ETX; relay energy; staleness; utility-target participation.

## 1. Introduction

Federated learning (FL) enables distributed devices to train a shared model without centralizing raw observations. In wireless sensor network (WSN) and Internet of Things (IoT) deployments, however, a client update may traverse several lossy links and shared relays before reaching an edge gateway. The communication path is therefore part of the learning system rather than a neutral transport layer. A decision to select one client instead of another changes not only the data that influence training but also the radio traffic, relay burden, delay, and residual-energy trajectory of the network.

Hierarchical FL reduces repeated end-to-cloud exchanges by introducing edge aggregation, but it does not remove this systems-learning coupling. A scheduler that always favors clients with cheap routes can concentrate learning on an easily reachable subset. Conversely, a scheduler that considers only current model loss or update utility can repeatedly use expensive routes and create relay hotspots. Compression adds a second coupling: changing the retained model-update fraction can dominate the traffic and energy outcome even when the selected client set is unchanged.

The present study addresses this narrower problem: **how should an HFL controller jointly decide which eligible clients participate, what update fidelity they use, and how delayed updates are weighted when multi-hop route burden, relay pressure, utility history, and participation deficit interact?** The ETX/residual-energy routing layer itself is treated as prior infrastructure rather than a new contribution.

The revised study is deliberately conservative about what its metrics establish. The participation queue tracks a utility-derived target share, not an externally defined population distribution. We therefore use the term **utility-target alignment** for the corresponding Jensen-Shannon (JS) divergence. Independent coverage measures are reported separately: temperature-distribution coverage for Intel and class-distribution coverage for HAR. The implementation also records each client's true cloud-level influence only after both within-edge and cloud-level normalization.

The principal contributions are:

1. A cross-layer HFL formulation for multi-hop sensing networks in which participation decisions price route burden, residual-energy scarcity, and relay-pressure externalities while retaining a utility-target deficit term.
2. A client-specific finite-set Top-k fidelity rule with error feedback, coupled to the same route, scarcity, and relay-pressure state used by the scheduler.
3. Correct two-level aggregation-influence accounting and a clear separation between utility-target alignment, equal-frequency fairness, and independent data-distribution coverage.
4. A held-out evaluation protocol with disjoint tuning and evaluation seeds, compression-matched controls, a FedCG-inspired external comparator, component ablations, and exact paired statistical tests.
5. Validation using synthetic correlated heterogeneity, the Intel Berkeley Lab WSN dataset, UCI HAR with an overlap-safe blocked within-client holdout, and ns-3.47 IEEE 802.15.4/LR-WPAN traffic replay.

## 2. Related Work and Positioning

Client-edge-cloud HFL was formalized by Liu et al. [1], and resource-aware client selection for IoT FL predates the present study [2]. Dynamic client-edge association and resource allocation have also been optimized jointly [3]. Long-term participation under volatile clients has been studied explicitly [4], while recent fairness-oriented analysis further distinguishes participation equality from distributional and performance fairness [13]. These results make hierarchy, multicriteria resource scoring, and participation-aware selection established ingredients rather than sufficient novelty claims.

Synchronization and heterogeneity have likewise been studied extensively. HiFlash couples adaptive staleness control with heterogeneity-aware client-edge association [5]. ShapeFL reduces communication by shaping edge-level data distributions [7], while cost-efficient HFL formulations jointly optimize selection and wireless resource allocation [8]. Recent graph-based HFL also combines client clustering with communication-resource allocation under non-IID data [17], learning-topology co-optimization has been studied for device-to-device HFL [18], and multi-job HFL jointly addresses client selection and resource allocation for consumer-grade UAVs [19]. Energy-efficient HFL has additionally been developed for marine IoT settings [20].

A related line of work focuses on selection diversity and compression. FedCG combines representative gradient-based client selection with adaptive compression [6]. Because its original communication model is not the multi-hop client-edge-cloud topology used here, we implement a clearly labeled **FedCG-adapted** comparator: a greedy facility-location selector over current client gradients with capability cost and adaptive compression. This is a favorable comparator because it has access to current gradient vectors for eligible clients; its information-acquisition overhead is not added to traffic accounting. It is not presented as an exact reproduction of FedCG.

Multi-hop FL itself is also established. Prior studies consider in-network aggregation with routing and spectrum allocation [9], network-accelerated FL over physical wireless edge systems [10], and multi-hop HFL grouping/resource allocation [11]. A topology-aware FL survey summarizes this broader design space [12]. The present work therefore does **not** claim novelty for ETX routing, multi-hop FL, fairness, compression, staleness, or hierarchy individually. Its research object is the joint control of utility-target participation, model-update fidelity, route burden, relay pressure, and staleness under a measured WSN substrate and held-out evaluation.

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

The learning problem is therefore not equivalent to selecting clients with minimum route cost. A high-loss or historically informative client can have a poor route, while cheap clients can dominate repeated selections. The controller is designed to expose rather than hide this trade-off.

[[FIGURE:0]]

## 4. Cross-Layer Utility-Aware HFL

### 4.1 Executed utility signal

Conceptually, a client utility can contain novelty, learning difficulty, and distribution information:

\[
U_i(t)=\alpha_gG_i(t)+\alpha_lL_i(t)+\alpha_hH_i(t),
\]

where \(G_i\) denotes update novelty, \(L_i\) learning difficulty/progress, and \(H_i\) an optional rarity term. The **executed pre-selection utility** is more specific: it is 0.55 times the per-round min-max-normalized current local loss plus 0.45 times the min-max-normalized exponentially smoothed utility history. No distribution-rarity term is used directly in the executed scheduling score. After a selected client trains, its history is updated from cosine novelty and non-negative local improvement. The improvement transform uses task-specific saturation constants documented in the repository. Raw examples remain local, but scalar loss/utility metadata are assumed available to the scheduler; this is not a formal privacy guarantee.

The normalized desired utility-target participation share is

\[
\pi_i(t)=\frac{U_i(t)+\epsilon}{\sum_j(U_j(t)+\epsilon)}.
\]

### 4.2 Utility-target participation-deficit queue

A virtual queue tracks the difference between desired and realized participation share:

\[
Q_i(t+1)=\left[Q_i(t)+\pi_i(t)-a_i(t)\right]^+.
\]

Here \(a_i(t)=x_i(t)/k_t\) for a selected set of size \(k_t>0\), and \(a_i(t)=0\) when no client is selected. The mechanism does not enforce equal-frequency participation. Instead, persistent shortfall relative to the utility-derived target increases future scheduling pressure. Directly from the recursion,

\[
\frac1T\sum_{t<T}a_i(t)
\ge
\frac1T\sum_{t<T}\pi_i(t)
-
\frac{Q_i(T)-Q_i(0)}{T}.
\]

Rate stability of \(Q_i\) is therefore sufficient for the long-run **participation-share** target. It does not prove equality between the target and final cloud influence, because compression, drops, staleness, edge normalization, and cloud normalization occur after selection.

### 4.3 Relay-energy queue

For relay \(r\),

\[
Z_r(t+1)=\left[Z_r(t)+E_r^{\mathrm{relay}}(t)-\bar E_r\right]^+,
\]

and route pressure for client \(i\) is

\[
R_i(t)=\sum_{r\in\mathcal P_i(t)}Z_r(t).
\]

The term increases when repeated model traffic funnels through the same relay corridor.

### 4.4 Adaptive update fidelity

Let \(\rho_i(t)\) denote the retained Top-k fraction. The controller exhaustively evaluates the finite candidate set and minimizes

\[
J_i^{\mathrm{comp}}(\rho)=
\rho\left(\widetilde C_i^{\mathrm{route}}+\eta_E\widetilde S_i+\eta_R\widetilde R_i\right)
+\beta U_i(t)(1-\rho)^2.
\]

In the executed implementation, the scarcity term is the min-max-normalized value of max(initial-energy/residual-energy - 1, 0), and its coefficient eta_E is fixed at 0.5. Route cost and relay pressure are also min-max normalized each round. The revised held-out protocol selects eta_R = 5 and beta = 0.10 using tuning seeds only; the selection rule is described in Section 5.2. Error feedback carries omitted coordinates into later updates.

### 4.5 Queue-informed scheduling score

For each eligible client,

\[
\Gamma_i(t)=V\widetilde U_i(t)+Q_i(t)-V\rho_i(t)
\left(\widetilde C_i^{\mathrm{route}}+\eta_E\widetilde S_i+\eta_R\widetilde R_i\right).
\]

The executed controller uses eta_E = 0.5, eta_R = 5, and V = 0.5. If \(M_t\) clients are eligible, it selects exactly \(k_t=\min(K_t,M_t)\) clients with the largest \(\Gamma_i(t)\). Eligibility uses availability and a residual-energy threshold; the implementation does not impose a hard prospective training-plus-transmission energy constraint.

The score is drift-plus-penalty inspired but is not an exact canonical Lyapunov minimizer. Normalization is performed each round, compression is selected through a separate distortion surrogate, and relay pressure enters as a normalized path feature rather than the unnormalized queue-energy product from the raw drift bound.

### 4.6 Utility-aware staleness

If an update generated at round \(t_i\) arrives at round \(t\), its staleness is \(s_i=t-t_i\). Edge aggregation uses

\[
\omega_i(t)=n_i e^{-\lambda_s s_i}\left(1+\mu U_i(t_i)\right),
\]

followed by normalization. Age penalizes delayed updates, while the utility term allows a high-value delayed update to retain additional weight.

### 4.7 Correct hierarchical influence accounting and evaluation metrics

Within an edge gateway, client weights are normalized to sum to one. Edge aggregates are then weighted again at the cloud. The revised implementation records a client's cloud influence as the product of its within-edge normalized coefficient and the normalized cloud coefficient of that edge. A dedicated unit test verifies a known two-edge example and that the resulting cloud coefficients sum to one. This corrects the earlier diagnostic implementation that accumulated only within-edge coefficients.

Two different JS metrics are intentionally separated. **Utility-target JS** compares cumulative true cloud influence with the cumulative utility-derived target. It measures controller-target alignment and is partly endogenous to the controller. It is not treated as an independent population-representativeness metric. **Independent coverage JS** compares the cloud-influence-weighted empirical data distribution with a pooled training-data reference: a 10-bin temperature distribution for Intel and the six-class activity distribution for HAR.

### 4.8 Exact queue and decision guarantees

**Proposition 1 (finite-horizon queue guarantees).** Define

\[
\mathcal L(t)=\frac12\sum_iQ_i^2(t)+\frac12\sum_rZ_r^2(t).
\]

Let \(d_i(t)=\pi_i(t)-a_i(t)\) and \(h_r(t)=E_r^{\mathrm{relay}}(t)-\bar E_r\). Using \(([q+y]^+)^2\le q^2+y^2+2qy\),

\[
\mathcal L(t+1)-\mathcal L(t)
\le
B(t)+\sum_iQ_i(t)d_i(t)+\sum_rZ_r(t)h_r(t),
\]

where \(B(t)=\frac12\sum_i d_i^2(t)+\frac12\sum_r h_r^2(t)\). Telescoping gives

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

Thus rate stability of the corresponding queues is sufficient for the long-run participation-share and relay-energy constraints.

**Proposition 2 (per-round decision exactness).** Exhaustive enumeration of the finite compression set returns the exact minimizer of the stated compression surrogate, and the top-k operation exactly maximizes the implemented additive client score over eligible subsets of the required cardinality. These are statements about the implemented surrogates, not global optimality of the end-to-end FL objective.

**Lemma 1 (error-feedback conservation).** For raw update \(u_i(t)\), residual \(e_i(t)\), and transmitted sparse update \(c_i(t)\),

\[
e_i(t+1)=u_i(t)+e_i(t)-c_i(t),
\]

which implies

\[
\sum_{t<T}c_i(t)=\sum_{t<T}u_i(t)+e_i(0)-e_i(T).
\]

Hence omitted coordinates are retained in the residual rather than permanently discarded.

These guarantees remain narrower than the classical Lyapunov result of an \(O(1/V)\) time-average penalty gap with \(O(V)\) backlog [14]. The executed normalized controller does not directly minimize the canonical drift-plus-penalty bound, and the utility-target participation shares sum to one. We therefore do not transfer the classical scaling theorem to this policy and do not claim a complete non-convex convergence theorem for the coupled selection-compression-hierarchy-staleness process.

## 5. Experimental Methodology

### 5.1 Protocol and parameter summary

**Table 1. Reproducible experimental protocol and executed controller parameters.**

| Item | Value | Role |
|---|---|---|
| Tuning seeds | 7, 11, 19, 23, 29, 31, 37, 41, 43, 47 | parameter selection only |
| Held-out evaluation seeds | 53, 59, 61, 67, 71, 73, 79, 83, 89, 97 | final comparisons and inference |
| Resource-data correlation | 0, 0.5, 0.9 | controlled stress levels |
| Relay-pressure coefficient | 5.0 | selected on tuning seeds |
| Compression-distortion coefficient | 0.10 | selected on tuning seeds |
| Drift parameter | 0.5 | scheduling score |
| Top-k candidates | 0.15, 0.30, 0.50, 0.75, 1.0 | adaptive fidelity |
| Fixed-compression controls | 0.50 | matched ablation/control |
| Scarcity coefficient | 0.5 | scheduler and compression surrogate |
| Staleness decay / utility coefficient | 0.35 / 0.80 | aggregation |
| Tx / Rx energy per bit | 1.5e-6 / 8.0e-7 J | modeled radio energy |
| Local-step energy | 0.004 J | modeled local training energy |
| Relay energy budget | 0.004 J per round | relay virtual queue |
| Header / value / index bits | 96 / 32 / 16 | traffic accounting |
| Intel rounds / selected clients / lr / L2 | 30 / 10 / 0.010 / 0.010 | regression |
| HAR rounds / selected clients / lr / L2 | 25 / 8 / 0.020 / 0.001 | classification |
| HAR holdout | 10-window blocks; one-in-five test; one-neighbor purge | overlap-safe within-client validation |

### 5.2 Tuning and held-out evaluation

The 12-point grid combines relay-pressure values 1, 2, 3, and 5 with compression-distortion values 0.1, 0.2, and 0.4. Only the 10 tuning seeds are used for this grid. A point is considered learning-feasible when Intel RMSE is within 0.010 °C of the best tuning-grid RMSE and HAR accuracy is within 0.5 percentage points of the best tuning-grid accuracy. Among feasible points, the selected setting minimizes an equal-weight min-max-normalized systems score over effective bits, total modeled energy, and maximum relay energy on both datasets. Utility-target JS and independent coverage metrics are excluded from parameter selection and reserved for evaluation. This protocol selects relay-pressure 5 and compression-distortion 0.10. All final comparisons and statistical tests use the disjoint held-out evaluation seeds.

### 5.3 Synthetic correlated heterogeneity

The controlled simulator uses 24 clients, four gateways, multi-hop ETX/residual-energy-aware routes, non-IID class distributions, adaptive Top-k compression, and explicit source/relay energy accounting. Correlation levels 0, 0.5, and 0.9 progressively couple statistical rarity with poorer availability and energy state. Random, resource-only, utility-only, and proposed policies use the same held-out 10-seed set.

### 5.4 Intel Berkeley Lab WSN

The Intel Berkeley Research Lab dataset [15] contains sensor readings, locations, and a measured directed connectivity matrix for 54 Mica2Dot motes. Four spatially distributed high-connectivity motes are treated as edge gateways and excluded from learning, leaving 48 learning clients. The task is per-mote next-temperature regression from a 16-step history of temperature, humidity, log-light, and voltage. Data are temporally partitioned within each mote. Measured bidirectional delivery probabilities determine link ETX; a disconnected-path fallback is assigned a conservative ETX of 100.

[[FIGURE:1]]

### 5.5 UCI Human Activity Recognition

UCI HAR contains smartphone inertial features for 30 subjects and six activities [16]. Each subject is treated as a persistent FL client. Because the original benchmark separates subjects between train and test, the files are recombined before constructing per-subject local datasets. The original HAR windows overlap by 50%; a random within-subject split can therefore leak overlapping signal content. The revised protocol preserves window order, partitions each subject record into contiguous 10-window blocks, assigns one of every five blocks to test using a deterministic subject-specific offset, and removes the immediately adjacent training window at each test boundary. This yields an approximately 80/20 overlap-safe within-client holdout. It is **not** the canonical unseen-subject UCI HAR benchmark.

### 5.6 Baselines and matched controls

The core fixed-compression baselines are random, resource-only, and utility-only selection. To isolate the role of compression, random-adaptive, resource-adaptive, and utility-adaptive controls receive the same client-specific Top-k ratio rule as the proposed controller while retaining their original selection logic. The proposed-fixed-compression ablation applies the proposed selection rule at a fixed 50% Top-k ratio.

The FedCG-adapted comparator uses current eligible-client gradient vectors in a greedy facility-location selection objective with a capability-cost penalty, followed by adaptive compression. Because this is a favorable adaptation with gradient access and because the original FedCG topology differs from the multi-hop HFL system, results are labeled FedCG-adapted rather than FedCG.

### 5.7 Metrics and statistical analysis

Learning metrics are RMSE/MAE for Intel and accuracy/Macro-F1 plus worst-client and 10th-percentile accuracy for HAR. Systems metrics include expected transmitted bits, modeled local-plus-radio energy, maximum relay energy, residual energy, route hops, and ETX. Jain's index describes selection-frequency equality. Utility-target JS evaluates corrected cloud-influence alignment with the controller target. Temperature-coverage JS and class-coverage JS are independent distributional diagnostics.

Final real-data comparisons use exact paired sign-flip tests on the 10 held-out seeds, percentile bootstrap 95% confidence intervals for paired mean differences, paired effect sizes, and Holm correction within each dataset-baseline metric family.

### 5.8 ns-3.47 communication replay

Synthetic held-out traffic profiles are replayed in ns-3.47 LR-WPAN with CSMA/CA, acknowledgments, retries, and contention. The primary hop-equivalent mapping multiplies compressed update bits by mean selected hops and lets ns-3 generate its own MAC retransmissions. An ETX-equivalent mapping is retained as a stress sensitivity because ETX already contains expected transmission attempts. Five load/scaling conditions, four policies, two mappings, and 10 held-out seeds yield 400 ns-3 runs. The HFL optimizer itself is not executed inside ns-3.

### 5.9 Reproducibility campaign

The editorial revision executes 240 tuning-grid HFL runs, 540 held-out real-data comparison runs, 100 held-out ablation runs, and 120 held-out synthetic runs: 1,000 HFL simulations in total, plus 400 ns-3 runs. A regression test was added specifically for two-level aggregation influence, and the revised frozen-table integrity checks bring the Python test suite to 13 passing tests. Dataset checksums, seed lists, parameter-selection rules, raw per-seed outputs, and statistical contrasts are retained in the repository.

## 6. Results

### 6.1 Synthetic stress test

At correlation 0.9, held-out mean accuracy is 93.90% for random, 94.12% for resource-only, 93.93% for utility-only, and 93.97% for the proposed controller. The corresponding proposed effective traffic is 0.532 Mbit compared with 1.468 Mbit for resource-only. Utility-target JS is 0.0076 for proposed versus 0.0669 for resource-only. However, independent class-coverage JS is 0.00869 for proposed and 0.00728 for resource-only, reinforcing that target alignment and data-distribution coverage are different quantities.

### 6.2 Intel WSN held-out evaluation

**Table 2. Intel Berkeley Lab WSN results at correlation 0.9. Values are mean ± 95% confidence interval over 10 held-out evaluation seeds.**

| Method | RMSE (°C) ↓ | MAE (°C) ↓ | Effective Mbit ↓ | Energy (J) ↓ | Max relay E (J) ↓ | Utility-target JS ↓ | Temp.-coverage JS ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Resource | 1.7473 ± 0.0018 | 0.8369 ± 0.0048 | 2.230 ± 0.010 | 6.328 ± 0.022 | 0.1378 ± 0.0050 | 0.1057 ± 0.0045 | 0.00082 ± 0.00008 |
| Resource-adaptive | **1.7285 ± 0.0034** | **0.7638 ± 0.0114** | **0.916 ± 0.013** | **3.307 ± 0.031** | **0.0902 ± 0.0026** | 0.0843 ± 0.0044 | 0.00034 ± 0.00003 |
| FedCG-adapted | 1.7362 ± 0.0023 | 0.7903 ± 0.0065 | 0.980 ± 0.013 | 3.454 ± 0.030 | 0.0964 ± 0.0016 | 0.0911 ± 0.0033 | **0.00027 ± 0.00003** |
| Proposed-fixed 50% | 1.7369 ± 0.0029 | 0.8048 ± 0.0080 | 2.373 ± 0.010 | 6.658 ± 0.022 | 0.1430 ± 0.0047 | 0.0283 ± 0.0023 | 0.00258 ± 0.00021 |
| Proposed | 1.7348 ± 0.0030 | 0.7790 ± 0.0060 | 0.992 ± 0.021 | 3.482 ± 0.049 | 0.0969 ± 0.0024 | **0.0118 ± 0.0013** | 0.00375 ± 0.00019 |

[[FIGURE:2]]

Relative to the fixed-compression resource baseline, the proposed controller reduces traffic by 55.5% and modeled energy by 45.0%, but the matched resource-adaptive control shows that those headline savings cannot be attributed to scheduling alone. Resource-adaptive uses 8.3% less traffic and 5.3% less modeled energy than proposed and obtains lower RMSE and MAE. The proposed controller instead reduces utility-target JS by 86.0% relative to resource-adaptive. Its temperature-coverage JS is worse, not better. Against FedCG-adapted, RMSE, traffic, energy, and maximum relay energy are statistically comparable after Holm correction, while utility-target JS is 87.1% lower. This result supports a target-alignment trade-off rather than statistical-representativeness superiority.

### 6.3 UCI HAR held-out evaluation

**Table 3. UCI HAR results at correlation 0.9 using the overlap-safe blocked within-client holdout. Values are mean ± 95% confidence interval over 10 held-out evaluation seeds.**

| Method | Accuracy ↑ | Macro-F1 ↑ | Worst-client acc. ↑ | Effective Mbit ↓ | Energy (J) ↓ | Max relay E (J) ↓ | Utility-target JS ↓ | Class-coverage JS ↓ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Resource | 0.8641 ± 0.0114 | 0.8565 ± 0.0140 | 0.5467 ± 0.0227 | 28.785 ± 0.898 | 44.73 ± 1.44 | **0.459 ± 0.088** | 0.1716 ± 0.0207 | 0.000081 ± 0.000032 |
| Resource-adaptive | 0.8751 ± 0.0047 | 0.8698 ± 0.0057 | 0.5567 ± 0.0254 | **8.872 ± 0.363** | **14.34 ± 0.57** | **0.170 ± 0.036** | 0.1553 ± 0.0203 | 0.000075 ± 0.000038 |
| FedCG-adapted | 0.8760 ± 0.0033 | 0.8705 ± 0.0041 | 0.5367 ± 0.0270 | 9.311 ± 0.389 | 15.34 ± 0.65 | 0.643 ± 0.135 | 0.1341 ± 0.0199 | 0.000070 ± 0.000024 |
| Proposed-fixed 50% | 0.7947 ± 0.0253 | 0.7570 ± 0.0392 | 0.5032 ± 0.0512 | 31.232 ± 1.001 | 49.26 ± 1.98 | 0.807 ± 0.322 | 0.1010 ± 0.0191 | 0.000078 ± 0.000020 |
| Proposed | **0.8867 ± 0.0012** | **0.8827 ± 0.0011** | **0.5683 ± 0.0294** | 11.253 ± 0.352 | 19.20 ± 0.75 | 1.242 ± 0.275 | **0.0275 ± 0.0034** | **0.000064 ± 0.000018** |

[[FIGURE:3]]

The proposed controller improves held-out accuracy by 1.16 percentage points over resource-adaptive and by 1.07 points over FedCG-adapted; both differences remain significant after Holm correction. The gain is purchased with additional network cost: relative to resource-adaptive, proposed traffic increases 26.8%, modeled energy 33.9%, and maximum relay energy 628.9%. Against FedCG-adapted, traffic increases 20.9%, energy 25.1%, and maximum relay energy 93.0%. Utility-target JS is 82.3% lower than resource-adaptive and 79.5% lower than FedCG-adapted. In contrast, class-coverage JS differences are small and non-significant. This is exactly the distinction intended by the revised metric terminology.

### 6.4 Compression and component ablations

On Intel, adaptive fidelity reduces proposed traffic from 2.373 Mbit at fixed 50% compression to 0.992 Mbit, a 58.2% reduction, and modeled energy falls by 47.7%; RMSE changes only from 1.7369 to 1.7348 °C. Removing the participation-deficit queue increases utility-target JS from 0.0118 to 0.0318. Removing relay pressure increases maximum relay energy from 0.0969 J to 0.1062 J.

On HAR, adaptive fidelity reduces proposed traffic from 31.232 Mbit to 11.253 Mbit, a 64.0% reduction, and energy falls from 49.26 J to 19.20 J. Accuracy simultaneously rises from 79.47% to 88.67% because the fixed-compression traffic incurs larger latency/staleness and dropout consequences in the modeled system. Removing the participation-deficit queue lowers network cost but increases utility-target JS from 0.0275 to 0.0854 and reduces accuracy from 88.67% to 88.39%. Removing relay pressure lowers utility-target JS but raises maximum relay energy from 1.242 J to 1.599 J, illustrating that individual terms can improve one objective while worsening another.

[[FIGURE:4]]

### 6.5 ns-3 communication replay

Under the primary hop-equivalent dense-nominal condition, proposed held-out synthetic traffic maps to 1,204 payload bits per report-equivalent update, compared with 3,431 for resource-only. The mean report delivery ratio is 99.47% for proposed and 85.79% for resource-only; mean delivered-report delay is 12.26 ms versus 35.99 ms. At the 24-sensor scale-nominal condition, report delivery is 96.56% for proposed versus 57.72% for resource-only. These differences validate the communication consequence of lower offered load, not the superiority of the learning scheduler in isolation. The traffic reduction itself is strongly influenced by adaptive compression.

[[FIGURE:5]]

### 6.6 Cross-dataset interpretation

The held-out results reject a simple “best method” interpretation. On Intel, resource-adaptive offers the strongest resource/learning point among the matched controls, while proposed most closely matches its own utility-derived target. FedCG-adapted is statistically comparable to proposed on Intel RMSE and systems cost. On HAR, proposed achieves the strongest mean accuracy and Macro-F1 among the main controls but spends substantially more traffic and relay energy than resource-adaptive and FedCG-adapted. Independent coverage metrics do not mirror utility-target JS, confirming that target alignment is not equivalent to representativeness.

[[FIGURE:6]]

The practical design implication is that adaptive fidelity and client scheduling should be evaluated separately. A fixed-compression baseline can make a coupled controller appear dramatically more communication-efficient even when most of the reduction comes from the compression rule. Conversely, a pure resource controller can minimize traffic and hotspot energy while accepting weaker alignment with the utility target. The revised evaluation makes these trade-offs explicit.

## 7. Discussion

The strongest evidence from the revision is methodological. First, corrected two-level influence accounting materially changes the interpretation of the JS metric: it is now the true cloud coefficient accumulated across hierarchy, but it remains an endogenous utility-target diagnostic. Second, held-out tuning prevents parameter-selection outcomes from being reused as inferential evidence. Third, compression-matched controls show that adaptive update fidelity is the principal source of the large communication reductions previously attributed to the combined controller.

The Intel result is particularly important for claim discipline. Resource-adaptive achieves lower error, traffic, energy, and relay hotspot than proposed. That does not invalidate the proposed mechanism; it shows that utility-target alignment carries a measurable opportunity cost. Similarly, the independent temperature-coverage metric favors FedCG-adapted/resource-adaptive over proposed. The appropriate conclusion is therefore that the controller supplies a tunable systems-learning trade-off, not a universal definition of statistical representativeness.

HAR presents a different regime. With the overlap-safe blocked holdout, proposed gains about one percentage point of accuracy over both resource-adaptive and FedCG-adapted while substantially improving utility-target alignment. Yet the network cost is higher, especially maximum relay energy. This is a useful cross-layer result because it demonstrates why a deployment must choose an operating point according to whether prediction quality, route efficiency, hotspot avoidance, or target-aligned participation is the dominant requirement.

The broader relevance to low-power edge intelligence is consequently not a claim that the current simulator proves sustainability. Rather, it demonstrates how learning objectives can be audited together with the network externalities they impose. Environmental monitoring, infrastructure sensing, and wearable activity systems all face variants of this coupling, but deployment-specific hardware measurements are still necessary before translating modeled joules into lifetime or sustainability outcomes.

## 8. Limitations

First, energy is modeled rather than measured on physical IEEE 802.15.4 sensor hardware. No claim is made about MCU current draw, radio current, RSSI/LQI, battery lifetime, or embodied/environmental sustainability. Second, Intel uses historical measured connectivity and sensing traces; the original motes do not execute the FL process. Third, the HAR protocol is a blocked within-client holdout designed for subject-as-client FL and should not be compared directly with the canonical unseen-subject benchmark.

Fourth, the utility target is controller-defined. Low utility-target JS proves alignment with that target, not independent population representativeness. The independent coverage metrics are intentionally reported to expose this distinction. Fifth, the pre-selection utility assumes scalar local-loss metadata from all candidate clients each round; downlink model dissemination and metadata reporting are not fully charged in the current communication-energy accounting. Reported energy therefore refers to the implemented local-training and model-update transport model rather than complete device energy.

Sixth, FedCG-adapted is not an exact reimplementation of FedCG. It uses a gradient-diversity facility-location principle and adaptive compression under the current candidate pool, but the original algorithm's topology and optimization assumptions differ. The comparator also receives current eligible-client gradients without charging their acquisition cost, making it a deliberately favorable reference rather than an unfairly weak baseline.

Seventh, the local predictors are linear and intentionally lightweight. Larger TinyML models may change computation, compression sensitivity, and update geometry. Eighth, the theory establishes finite-horizon queue bounds, finite-set compression optimality, top-k score optimality, and error-feedback conservation, but not a complete non-convex convergence result for the coupled process. Finally, the current revision does not implement every recent HFL architecture or optimizer family; FedProx, FedAdam/FedOpt, server momentum, graph-based HFL [17], and learning-topology co-optimization [18] remain additional comparisons rather than claimed completed experiments.

## 9. Conclusion

This study develops a cross-layer HFL controller for multi-hop IoT sensing networks and, more importantly, subjects that controller to a stricter evaluation protocol. Correct cloud-level influence accounting, disjoint tuning/evaluation seeds, overlap-safe HAR validation, compression-matched controls, and a FedCG-adapted comparator change the central claim from dominance to trade-off. Adaptive fidelity is the principal source of traffic reduction. The participation-deficit mechanism strongly improves alignment with its utility-derived target, but independent coverage metrics do not establish universal statistical representativeness. On Intel, a resource-adaptive control provides a stronger pure resource/learning point; on HAR, the proposed controller improves held-out accuracy at additional traffic and relay cost. These results support utility-aware cross-layer orchestration as a configurable Pareto mechanism rather than as a universally optimal scheduler.

## Author contributions

All authors contributed equally to the conceptualization, methodology, investigation, validation, formal analysis, interpretation of results, manuscript preparation, critical revision, and final approval of the work.

## Funding

This research received no external funding.

## Conflict of interest

The authors declare no conflict of interest.

## Declaration of generative AI and AI-assisted technologies in the writing process

During the preparation of this manuscript, the authors used generative AI tools to support the literature-review process and language editing. All AI-assisted material was critically reviewed, verified, and edited by the authors, who take full responsibility for the accuracy, integrity, citations, and final content of the manuscript.

## Resource availability

### Lead contact

Requests concerning the manuscript should be directed to the corresponding author, Abhishek Kumar Pandey (abhishek.pandey2@bennett.edu.in).

### Materials availability

This computational study did not generate new physical materials.

### Data and code availability

Code, experiment manifests, tuning and held-out seed lists, raw per-seed outputs, statistical analyses, and manuscript figures are available in the public project repository: https://github.com/DrShivamBhardwaj/Relevance_Aware_RE_ETX_/tree/wsn-hfl-crosslayer-final. Intel Berkeley Lab sensor data and UCI HAR are publicly available from their original providers. The repository records the operating-point selection rule and the corrected hierarchical-influence test.

## References

[1] L. Liu, J. Zhang, S. H. Song, and K. B. Letaief, “Client-Edge-Cloud Hierarchical Federated Learning,” IEEE International Conference on Communications, 2020. DOI: 10.1109/ICC40277.2020.9148862.

[2] S. AbdulRahman, H. Tout, A. Mourad, and C. Talhi, “FedMCCS: Multicriteria Client Selection Model for Optimal IoT Federated Learning,” IEEE Internet of Things Journal, 8, 4723–4735, 2021. DOI: 10.1109/JIOT.2020.3028742.

[3] W. Y. B. Lim, J. S. Ng, Z. Xiong, D. Niyato, C. Miao, and D. I. Kim, “Dynamic Edge Association and Resource Allocation in Self-Organizing Hierarchical Federated Learning Networks,” IEEE Journal on Selected Areas in Communications, 39(12), 3640–3653, 2021. DOI: 10.1109/JSAC.2021.3118401.

[4] T. Huang, W. Lin, L. Shen, K. Li, and A. Y. Zomaya, “Stochastic Client Selection for Federated Learning With Volatile Clients,” IEEE Internet of Things Journal, 9(20), 20055–20070, 2022. DOI: 10.1109/JIOT.2022.3172113.

[5] X. Chen, T. Ouyang, Z. Zhou, X. Zhang, S. Yang, and J. Zhang, “HiFlash: Communication-Efficient Hierarchical Federated Learning With Adaptive Staleness Control and Heterogeneity-Aware Client-Edge Association,” IEEE Transactions on Parallel and Distributed Systems, 2023. DOI: 10.1109/TPDS.2023.3238049.

[6] Z. Jiang, Y. Xu, H.-Z. Xu, Z. Wang, and C. Qian, “Heterogeneity-Aware Federated Learning with Adaptive Client Selection and Gradient Compression,” IEEE INFOCOM, 2023. DOI: 10.1109/INFOCOM53939.2023.10229029.

[7] Y. Deng, F. Lyu, T. Xia, Y. Zhou, Y. Zhang, J. Ren, and Y. Yang, “A Communication-Efficient Hierarchical Federated Learning Framework via Shaping Data Distribution at Edge,” IEEE/ACM Transactions on Networking, 32(3), 2600–2615, 2024. DOI: 10.1109/TNET.2024.3363916.

[8] B. Wu, F. Fang, X. Wang, D. Cai, S. Fu, and Z. Ding, “Client Selection and Cost-Efficient Joint Optimization for NOMA-Enabled Hierarchical Federated Learning,” IEEE Transactions on Wireless Communications, 23(10), 14289–14303, 2024. DOI: 10.1109/TWC.2024.3411479.

[9] X. Chen, G. Zhu, Y. Deng, and Y. M. Fang, “Federated Learning Over Multihop Wireless Networks With In-Network Aggregation,” IEEE Transactions on Wireless Communications, 2022. DOI: 10.1109/TWC.2022.3168538.

[10] P. Pinyoanuntapong, P. Janakaraj, R. Balakrishnan, M. Lee, C. Chen, and P. Wang, “EdgeML: Towards Network-Accelerated Federated Learning over Wireless Edge,” Computer Networks, 218, 109396, 2022. DOI: 10.1016/j.comnet.2022.109396.

[11] T. V. Nguyen, N. D. Ho, H. T. Hoang, C. D. Do, and K.-S. Wong, “Toward Efficient Hierarchical Federated Learning Design Over Multi-Hop Wireless Communications Networks,” IEEE Access, 10, 111910–111922, 2022. DOI: 10.1109/ACCESS.2022.3215758.

[12] J. Wu, F. Dong, H. Leung, Z. Zhu, J. Zhou, and S. Drew, “Topology-Aware Federated Learning in Edge Computing: A Comprehensive Survey,” ACM Computing Surveys, 56(10), Article 262, 1–41, 2024. DOI: 10.1145/3659205.

[13] M. Alsofyani, I. Al-Turaiki, and H. Mathkour, “A Fairness Perspective on Client Selection and Aggregation Methods for Non-IID Mitigation in Federated Learning: A Survey,” Electronics, 2026. DOI: 10.3390/electronics15143178.

[14] M. J. Neely, Stochastic Network Optimization with Application to Communication and Queueing Systems, Morgan & Claypool, 2010. DOI: 10.2200/S00271ED1V01Y201006CNT007.

[15] Intel Berkeley Research Lab sensor dataset. Available: https://db.csail.mit.edu/labdata/labdata.html.

[16] UCI Machine Learning Repository, “Human Activity Recognition Using Smartphones.” DOI: 10.24432/C54S4K.

[17] E. Yu, S. Liu, Q. Li, H. Chen, H. V. Poor, and S. Shamai, “Graph-Based Joint Client Clustering and Resource Allocation for Wireless Distributed Learning: A New Hierarchical Federated Learning Framework With Non-IID Data,” IEEE Transactions on Mobile Computing, 24(5), 3579–3596, 2025. DOI: 10.1109/TMC.2024.3515037.

[18] M. Wu, M. Boban, and F. Dressler, “Hierarchical Federated Learning in Device-to-Device Networks With Learning-Topology Co-Optimization,” IEEE Transactions on Mobile Computing, 25(8), 12488–12505, 2026. DOI: 10.1109/TMC.2026.3673393.

[19] W. Hu, Y. Yu, X. Hao, X. Cai, Y. Qian, L. Guo, and Y. Li, “Multi-Job Hierarchical Federated Learning for Consumer-Grade UAVs: A Joint Client Selection and Resource Allocation Approach,” IEEE Transactions on Consumer Electronics, 71(3), 8021–8032, 2025. DOI: 10.1109/TCE.2025.3587021.

[20] “Joint Communication and Computing Resource Allocation for Energy Efficient Hierarchical Federated Learning in Marine Internet of Things,” IEEE Transactions on Network Science and Engineering, 12(5), 4114–4127, 2025. DOI: 10.1109/TNSE.2025.3568875.
