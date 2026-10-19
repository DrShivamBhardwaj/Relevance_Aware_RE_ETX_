# Reproducibility and evidence generations

The historical ten-seed C1–C7 outputs remain in `results/master_validation/`. They were produced before the absent-route bug fix and before the new progressive codec. They must not be relabelled as Cooja results.

`tools/audit_submission_evidence.py` checks the historical primary statistics and writes retrospective t-test and exact sign-flip Holm sensitivities to `results/cooja_preflight/historical_audit/`. No historical raw output is overwritten.

`validation/cooja/` contains the new firmware, source codec, receiver observer, live-context mechanism, RPL-Lite objective-function hook, simulation generator, exact offered-budget controls and prospective analysis design. Its README gives commands, scope boundaries and pinned sources.

`results/cooja_preflight/` records unit tests, native firmware compilation and configuration checks. These are executed component checks. They are not executed Cooja network experiments.

The public push and GitHub Actions run were blocked pending explicit publication approval. The user's Desktop Commander device was offline. Gradle could not be downloaded in the current restricted network. Therefore this branch contains no newly measured Cooja utility or delivery results, and the manuscript has not been declared ready for submission.
