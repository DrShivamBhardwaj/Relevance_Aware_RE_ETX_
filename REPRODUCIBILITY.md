# Reproducibility and evidence generations

The historical ten-seed C1–C7 outputs remain in `results/master_validation/`, from archived source `b5d5ac75c981b1eff0171a8cb885ef5764183d85`. They predate the absent-route fix and progressive codec. `tools/audit_submission_evidence.py` retains retrospective t-test and exact sign-flip multiplicity sensitivities under `results/cooja_preflight/historical_audit/`.

The independent Cooja experiment executes source commit `8c99e28f1732c494e58d27ab2a3ecf9b3b511efa`. Its frozen revision-2 design is in `validation/cooja/design.json`. Subsequent archival commits add reports and reproduction helpers without changing that executed core.

All 200 primary runs succeeded on [GitHub Actions run 39206635771](https://github.com/DrShivamBhardwaj/Relevance_Aware_RE_ETX_/actions/runs/39206635771). All four jobs also passed the component, upstream IPv6 and ten-policy smoke checks. The seven declared exploratory cases completed another 280 local runs against the same pinned core. The archived independent audits passed 200 primary and 280 exploratory runs. Ninety-seven duplicate local primary outcomes agree exactly with the canonical GitHub outcomes; these are replication checks, not extra seeds.

## Reanalyse retained evidence

```bash
python3 -m pip install -r validation/cooja/requirements-analysis.txt
mkdir evidence
# Both archives contain unique run folders, not smoke duplicates.
tar -xJf results/cooja_v2/primary_evidence.tar.xz -C evidence
tar -xJf results/cooja_v2/exploratory_evidence.tar.xz -C evidence
python3 validation/cooja/audit_outputs.py evidence/primary --output primary-audit.json
python3 validation/cooja/analyse.py evidence/primary --output primary-analysis.json
python3 validation/cooja/audit_outputs.py evidence/exploratory --output exploratory-audit.json
python3 validation/cooja/analyse.py evidence/exploratory --output exploratory-analysis.json
```

The independent audit compiles the retained portable C codec using GCC. It verifies every source block and received SSE, raw-log hashes, offered denominators, exact-size permutations and fixed routing schedules. The post-hoc hold estimator and no-transmission diagnostic do not replace the frozen zero-imputation primary endpoint. `results/cooja_v2/README.md` describes raw evidence and limitations.

To execute new runs, follow `validation/cooja/README.md` using pinned Contiki-NG/Cooja. Never overwrite an existing run. `tools/run_cooja_robustness.py` executes only the seven declared stress cases. `tools/resume_cooja.py` archives incomplete infrastructure attempts before resuming; it does not discard valid zero-delivery outcomes.

`results/cooja_preflight/` is a historical pre-execution checkpoint. Its zero-run status is retained as provenance, not the current execution status. No hardware, MCU timing, battery-life or total-device energy result is claimed.
