# Executed Cooja revision-2 evidence

Executed source: `8c99e28f1732c494e58d27ab2a3ecf9b3b511efa`. Primary results come from successful [Actions run 39206635771](https://github.com/DrShivamBhardwaj/Relevance_Aware_RE_ETX_/actions/runs/39206635771), four shards, 20 paired seeds and ten policies (200 runs). The exploratory archive retains seven predeclared cases, four paired seeds each and ten policies (280 runs). Smoke outcomes are excluded from the research analysis.

`primary_evidence.tar.xz` and `exploratory_evidence.tar.xz` contain raw Cooja test/console logs, offered traces, generated configurations, source headers, summaries and manifests. Full build dependencies and firmware objects are omitted; source and raw-log hashes are retained. Extract each into a common evidence directory, then follow the package-root `REPRODUCIBILITY.md`. Archive SHA256 values are in `status.json`.

Analysis JSON files retain all paired tests, effect sizes and secondary Holm adjustments. Seed CSVs contain all 480 policy outcomes. Independent audit JSONs reproduce source truth, decoder SSE, denominators, raw-log hashes and offered control schedules. Hold-imputation and always-zero diagnostics are explicitly post-hoc. The 97 local primary replicas agree exactly with canonical GitHub results and are not extra replicates. Routing-object verification is recorded separately.

Two exploratory raw logs were found damaged during audit. Exact configuration replay recovered both original hashes and summary values; `raw_log_recovery_audit.json` preserves the event. Outcomes were not selected by performance and expected hashes were not redefined.

## Interpretation

Mean primary RMSE is 0.227772 for relevance and 0.223023 for its exact within-round size-matched shuffle. The paired difference +0.004750 has 95% interval [0.000117, 0.009383], t p = 0.0450 and exact sign-flip p = 0.0321. The relevance rule performs worse in this regime. Delivery improvement does not survive secondary correction. The routing-interaction interval crosses zero. All seven exploratory RMSE intervals cross zero; four seeds do not establish equivalence or general robustness.

The local distortion-price reference chooses eight bits in every primary evaluation block. It is a fixed-rate outcome with 2.88% fewer data bytes than relevance, not an exact-budget demonstration of adaptive improvement. A zero no-transmission estimator has mean RMSE 0.217203; 33.848% of relevance-allocated offered blocks are coded worse than zero. Codec range and missing-data estimation matter.

Nominal radio joules use 3 V and CC2420 TX/RX currents of 17.4/18.8 mA. Activity ends at final source snapshots, before the simulation drain, and includes setup/warm-up. Sink, CPU, sensing and later radio work are excluded. Always-listening CSMA dominates this accounting; no total-device energy, MCU timing or battery-life claim follows. Native node-indexed tables and offline replay arrays do not establish embedded scalability. Bias is included in reconstruction truth; scaling and shorter periods change more than one workload factor.
