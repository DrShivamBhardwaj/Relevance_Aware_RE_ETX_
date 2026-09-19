# Theory note for the executed cross-layer WSN-HFL controller

This document states only results that are supported by the implemented queue recursions and finite-set decisions. It deliberately separates exact statements from classical Lyapunov results that would require a different, canonical drift-minimizing controller.

## 1. Definitions

At round \(t\), let \(\mathcal E_t\) be the eligible client set and

\[
k_t=\min(K_t,|\mathcal E_t|).
\]

For client \(i\),

\[
x_i(t)\in\{0,1\},
\qquad
a_i(t)=
\begin{cases}
x_i(t)/k_t,&k_t>0,\\
0,&k_t=0.
\end{cases}
\]

The statistical target \(\pi_i(t)\ge0\) satisfies \(\sum_i\pi_i(t)=1\). The participation-deficit queue is

\[
Q_i(t+1)=[Q_i(t)+\pi_i(t)-a_i(t)]^+.
\]

For forwarding node \(r\), with per-round relay energy \(E_r(t)\ge0\) and budget \(\bar E_r\),

\[
Z_r(t+1)=[Z_r(t)+E_r(t)-\bar E_r]^+.
\]

The executed scheduler uses normalized utility and normalized system-state features. Its selection score is

\[
\Gamma_i(t)=V\widetilde U_i(t)+Q_i(t)-VC_i(t,\rho_i(t)).
\]
## 2. Lemma 1 — finite-horizon participation-deficit bound

For every client \(i\) and horizon \(T\ge1\),

\[
\sum_{t=0}^{T-1}(\pi_i(t)-a_i(t))
\le
Q_i(T)-Q_i(0).
\]

Equivalently,

\[
\frac1T\sum_{t<T}a_i(t)
\ge
\frac1T\sum_{t<T}\pi_i(t)
-
\frac{Q_i(T)-Q_i(0)}{T}.
\]

**Proof.** Since \([y]^+\ge y\),

\[
Q_i(t+1)\ge Q_i(t)+\pi_i(t)-a_i(t).
\]

Summing from \(t=0\) to \(T-1\) telescopes. □

### Corollary 1

If \(Q_i(T)/T\to0\), then

\[
\liminf_{T\to\infty}
\frac1T\sum_{t<T}
[a_i(t)-\pi_i(t)]
\ge0.
\]

Thus rate stability implies that the long-run **participation share** does not fall below the long-run statistical target.

This corollary does not imply that aggregation influence equals \(\pi_i\). Final influence is also affected by update compression, loss/drop events, staleness, sample-size weighting, and hierarchical normalization.
## 3. Lemma 2 — finite-horizon relay-budget bound

For every relay \(r\),

\[
\sum_{t=0}^{T-1}[E_r(t)-\bar E_r]
\le
Z_r(T)-Z_r(0),
\]

hence

\[
\frac1T\sum_{t<T}E_r(t)
\le
\bar E_r+
\frac{Z_r(T)-Z_r(0)}{T}.
\]

**Proof.** Identical to Lemma 1 using the relay virtual-queue recursion. □

### Corollary 2

If \(Z_r(T)/T\to0\), then

\[
\limsup_{T\to\infty}
\frac1T\sum_{t<T}E_r(t)
\le \bar E_r.
\]

Thus rate stability of the relay queue is sufficient for satisfying the long-run relay-energy budget.
## 4. Lemma 3 — one-step quadratic drift bound

Define

\[
L(t)=\frac12\sum_iQ_i^2(t)+\frac12\sum_rZ_r^2(t),
\]

\[
d_i(t)=\pi_i(t)-a_i(t),
\qquad
h_r(t)=E_r(t)-\bar E_r.
\]

Then for every sample path,

\[
L(t+1)-L(t)
\le
B(t)
+
\sum_iQ_i(t)d_i(t)
+
\sum_rZ_r(t)h_r(t),
\]

where

\[
B(t)=
\frac12\sum_i d_i^2(t)
+
\frac12\sum_r h_r^2(t).
\]

**Proof.** Apply

\[
([q+y]^+)^2\le q^2+y^2+2qy
\]

to every \(Q_i\) and \(Z_r\), sum, and divide by two. □

If \(0\le E_r(t)\le E_r^{\max}\), then \(|d_i(t)|\le1\) and

\[
B(t)\le
\frac{|\mathcal C|}{2}
+
\frac12\sum_r
\max\{E_r^{\max},\bar E_r\}^2
=:B_{\max}<\infty.
\]
## 5. Proposition 1 — exact finite-set compression decision

For every eligible client, the implementation evaluates every retained-fraction candidate

\[
\rho\in\mathcal R=
\{0.15,0.30,0.50,0.75,1.0\}
\]

that satisfies \(\rho\ge\rho_{\min}\), and chooses

\[
\rho_i^*(t)
\in
\arg\min_{\rho\in\mathcal R}
\left[
\rho A_i(t)+
\beta\widetilde U_i(t)(1-\rho)^2
\right],
\]

where

\[
A_i(t)=
\widetilde C_i^{\rm route}(t)
+0.5\widetilde S_i(t)
+\eta_R\widetilde R_i(t).
\]

Because \(\mathcal R\) is finite and exhaustively enumerated, the returned \(\rho_i^*(t)\) is a global minimizer **of this surrogate over \(\mathcal R\)**. This does not assert that the quadratic term equals the true model-update distortion.
## 6. Proposition 2 — exact top-k score optimization

After the candidate compression ratios have been fixed, define \(\Gamma_i(t)\) for each eligible client. The implementation chooses the \(k_t\) largest scores. Therefore

\[
\mathcal S_t
\in
\arg\max_{
\substack{\mathcal S\subseteq\mathcal E_t\\|\mathcal S|=k_t}
}
\sum_{i\in\mathcal S}\Gamma_i(t).
\]

**Proof.** For an additive cardinality-constrained objective, replacing any selected item by an unselected item with a larger score strictly increases the objective. The maximum is therefore attained by the \(k_t\) largest entries. □

This proposition concerns the implemented surrogate score, not the canonical unnormalized Lyapunov drift expression.
## 7. Proposition 3 — error-feedback conservation

Let \(u_i(t)\) be the raw local update, \(e_i(t)\) the error-feedback residual before compression, and

\[
c_i(t)=\mathcal C_{\rho_i(t)}(u_i(t)+e_i(t))
\]

the transmitted sparse update. The implementation updates

\[
e_i(t+1)=u_i(t)+e_i(t)-c_i(t).
\]

Hence

\[
c_i(t)+e_i(t+1)=u_i(t)+e_i(t),
\]

and telescoping gives

\[
\sum_{t=0}^{T-1}c_i(t)
=
\sum_{t=0}^{T-1}u_i(t)
+e_i(0)-e_i(T).
\]

If \(e_i(0)=0\) and \(\|e_i(T)\|/T\to0\), the average cumulative discrepancy between raw and transmitted updates vanishes. This is a conservation statement; by itself it does not prove optimization convergence.
## 8. Proposition 4 — bounded positive staleness weight

For accepted updates,

\[
\omega_i^{\rm raw}(t)
=
n_i e^{-\lambda_s s_i}
(1+\mu U_i),
\]

with \(0\le U_i\le1\), \(0\le s_i\le s_{\max}\), \(\lambda_s\ge0\), and \(\mu\ge0\). Therefore

\[
n_i e^{-\lambda_s s_{\max}}
\le
\omega_i^{\rm raw}(t)
\le
n_i(1+\mu).
\]

Thus every accepted update receives a strictly positive raw aggregation weight; utility can partially compensate for age but cannot reverse the exponential age factor without bound.
## 9. Why the classical O(1/V)-O(V) theorem is not claimed here

A canonical drift-plus-penalty controller minimizes an upper bound containing the **unnormalized** queue terms

\[
-\sum_iQ_i(t)a_i(t)
+
\sum_r Z_r(t)E_r(t)
+
V p(t).
\]

Under suitable boundedness and feasibility assumptions, classical Lyapunov optimization gives time-average penalty/backlog trade-offs of order \(O(1/V)\) and \(O(V)\); see M. J. Neely, *Stochastic Network Optimization with Application to Communication and Queueing Systems*, 2010, DOI 10.2200/S00271ED1V01Y201006CNT007.

The executed WSN-HFL controller is not identical to that canonical policy:

1. route cost, scarcity, and relay pressure are normalized each round;
2. relay pressure uses a normalized path sum of \(Z_r\), not the raw product \(Z_rE_{ir}\);
3. compression is chosen in a separate finite-set distortion surrogate;
4. the representation targets sum to one, so a uniform strict-Slater slack for every participation queue is generally unavailable.

Consequently, the manuscript must **not** transfer the canonical \(O(1/V)\)/\(O(V)\) theorem to the executed policy. The Lyapunov derivation is used to justify the queue construction and expose the constraint-pressure terms; the exact guarantees are Lemmas 1–3 and Propositions 1–4 above.
## 10. What remains open

The current theory does not prove global convergence of the federated-learning iterates under the simultaneous presence of:

- resource-dependent and availability-dependent client selection,
- Top-k compression with error feedback,
- two-level edge/cloud aggregation,
- packet drops,
- bounded asynchronous staleness,
- time-varying non-IID statistical utility.

A complete convergence result would require additional assumptions on smoothness, stochastic-gradient variance, compressor contraction/error-feedback residuals, participation probability lower bounds, and staleness. Those assumptions are not silently imposed in the present experimental paper.

## 11. Reviewer-safe theorem language

Safe wording:

> The virtual queues yield exact finite-horizon bounds on participation-share deficit and relay-energy budget violation. Their rate stability is sufficient for satisfying the corresponding time-average constraints. The implemented finite-set compression and top-k selection steps exactly optimize their stated per-round surrogates.

Avoid:

> The proposed algorithm is globally optimal.

Avoid:

> The executed controller is guaranteed to achieve an O(1/V) optimality gap with O(V) backlog.

Avoid:

> Error feedback guarantees convergence under our complete hierarchical non-IID setting.
