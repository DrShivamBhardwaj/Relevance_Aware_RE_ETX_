# Relevance-guided payload allocation: code and evidence

Research artifacts for the updated relevance-guided payload-allocation study in wireless sensor networks. This package connects the historical traffic and routing experiments with an explicit Contiki-NG/Cooja codec evaluation.

The historical study measures traffic reduction and statistical targeting. The Cooja study measures reconstruction utility with exact within-round payload-size controls. In the primary Cooja comparison, relevance-guided allocation has higher receiver RMSE than its shuffled control: 0.227772 versus 0.223023 across 20 paired seeds. Statistical targeting therefore does not establish reconstruction benefit in this workload. The local distortion-price reference selects eight bits throughout the primary evaluation and uses a different byte budget; it is not an exact-budget adaptive improvement.

## Contents

| Directory | Contents |
|---|---|
| `historical/` | Historical Python simulator, configurations, experiment runners and analysis code |
| `validation/cooja/` | C firmware, progressive codec, allocation controls, study design, Cooja runner and independent audit |
| `inputs/` | Input definitions, pinned source versions and figure/table provenance |
| `results/master_validation/` | Historical control, weight-sweep, event-targeting and topology results, including compressed round data |
| `results/cooja_v2/` | All 200 primary and 280 exploratory outcomes, raw evidence archives, analyses and audits |
| `results/cooja_preflight/historical_audit/` | Reproduced historical p-values and retrospective multiplicity sensitivity |
| `figures/` | Nine original figure PNGs from the updated document; editable SVG for Figure 1 |
| `tables/` | Ten numbered tables as UTF-8 CSV, retaining displayed precision and multiline cells |
| `tests/`, `simulator/` | 21 component tests and the current transmission-accounting components they exercise |
| `tools/` | Evidence verification, analysis, plotting and execution utilities |

The full manuscript, author metadata and journal submission files are excluded. Table 1 is a descriptive comparison, not experimental output. Figure 1 is conceptual. The algorithm layout table is not a numbered results table. See `inputs/artifact_sources.json` for the mapping to evidence.

## Verify and reproduce

Use Python 3.12 and a C compiler for the component tests:

```bash
python -m pip install -r requirements.txt
python tools/verify_package.py
python -m unittest discover -s tests -v
python tools/verify_package.py --raw
```

The first command verifies every packaged file against `SHA256SUMS` and checks the result structure. `--raw` also extracts both Cooja archives into temporary directories and reruns the independent audit and paired analysis for all 480 outcomes. It compares the regenerated JSON with the archived JSON. This reanalysis does not execute new simulations.

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for simulation, historical analysis and figure regeneration. `results/package_verification.json` records the checks performed when this package was prepared.

## Provenance and interpretation

Historical source is preserved from commit `b5d5ac75c981b1eff0171a8cb885ef5764183d85`; the executed Cooja source is `8c99e28f1732c494e58d27ab2a3ecf9b3b511efa`. Both belong to [the original repository](https://github.com/DrShivamBhardwaj/Relevance_Aware_RE_ETX_). Exact upstream versions and the successful primary Actions run are recorded in `inputs/software_versions.json`.

The two implementations use different source representations and context models. Their controls and denominators must be interpreted within each experiment. The current components in root `simulator/` support regression tests; the historical evidence uses `historical/simulator/`. `results/master_validation/base_commit.txt` is the original archive-start marker, not the historical scientific-source identifier above.

Cooja RMSE includes every evaluation source/round; missing or late reports use the declared zero reconstruction. Hold reconstruction and always-zero comparisons are post-hoc diagnostics. Exploratory cases have four seeds each and do not establish equivalence. Radio energy is a nominal TX/listen calculation through final source snapshots, excluding sink, CPU, sensing and later radio activity. See the detailed evidence README for accounting limits.
