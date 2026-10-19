# Payload allocation and receiver reconstruction

This branch contains the archived ten-seed C1–C7 experiment and a separate executed Contiki-NG/Cooja validation. It maintains code, configurations and numerical evidence.

The Cooja study completed **200 primary runs** (20 seeds × 10 policies) and **280 exploratory runs** (seven cases × four seeds × ten policies). Independent source, decoder, raw-log, denominator and executed-control audits passed all 480 runs. Twenty-one component tests passed.

The primary result challenges the relevance rule: at identical within-round offered payload-size multisets, mean receiver RMSE is 0.227772 for relevance and 0.223023 for shuffling. The paired difference is +0.004750, with 95% interval [0.000117, 0.009383]. Positive differences mean worse reconstruction. Neither a new superior protocol nor device-lifetime savings is established.

See [the retained Cooja evidence](results/cooja_v2/README.md), [reproduction instructions](REPRODUCIBILITY.md), and [the implementation](validation/cooja/README.md). Historical results remain separately under `results/master_validation/`; they are not Cooja results. The executed Cooja source is commit `8c99e28f1732c494e58d27ab2a3ecf9b3b511efa`.
