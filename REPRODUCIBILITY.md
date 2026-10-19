# Reproducing the evidence

Run commands from the package root unless stated otherwise. Install `requirements.txt` in an isolated Python 3.12 environment. Raw-evidence verification needs temporary disk space beyond the compressed archives.

## Archived Cooja results

```bash
python tools/verify_package.py --raw
```

This checks SHA-256 integrity, run identities and counts, independently regenerates source truth and decoder error from the raw evidence, checks denominators and matched controls, and reruns paired inference. The regenerated audit and analysis must match the archived JSON exactly. No new simulator execution is involved. Primary and exploratory raw evidence are kept separate.

For inspection or plotting, extract both archives into a fresh directory:

```bash
mkdir -p /tmp/relevance-evidence
tar -xJf results/cooja_v2/primary_evidence.tar.xz -C /tmp/relevance-evidence
tar -xJf results/cooja_v2/exploratory_evidence.tar.xz -C /tmp/relevance-evidence
python validation/cooja/analyse.py /tmp/relevance-evidence/primary --output /tmp/relevance-primary.json
python validation/cooja/audit_outputs.py /tmp/relevance-evidence/primary --output /tmp/relevance-primary-audit.json
python tools/plot_cooja_results.py /tmp/relevance-evidence/primary --analysis /tmp/relevance-primary.json --audit /tmp/relevance-primary-audit.json --output /tmp/relevance-plots
```

The plotting utility produces numerical Cooja figures in several formats. Original document figures are retained in `figures/`; regenerating plots may change styling. Figure 1 has an editable SVG. The table CSVs preserve displayed values; full-precision results are under `results/`.

## New Cooja executions

Use a connected Linux environment with Git, Java 17, GCC and Make. Obtain the exact upstream versions:

```bash
git clone https://github.com/contiki-ng/contiki-ng.git /tmp/relevance-contiki-ng
git -C /tmp/relevance-contiki-ng checkout c20b12cd2db707d6c07918f8b26cfeb52cf298ca
git -C /tmp/relevance-contiki-ng submodule update --init --recursive
git -C /tmp/relevance-contiki-ng/tools/cooja checkout 33d41ae9f8acd6075fb903b0bcd5b4122bad8d8f
export CONTIKI_DIR=/tmp/relevance-contiki-ng
COOJA_OUTPUT=/tmp/relevance-new-smoke bash validation/cooja/RUN_COOJA.sh smoke
COOJA_OUTPUT=/tmp/relevance-new-primary bash validation/cooja/RUN_COOJA.sh primary
COOJA_OUTPUT=/tmp/relevance-new-all bash validation/cooja/RUN_COOJA.sh all
```

Use separate fresh output paths. `primary` runs 20 seeds and ten policies; `all` also includes the seven four-seed exploratory cases. Do not count smoke runs or deterministic replay copies as independent research replicates. See `validation/cooja/README.md` for routing and radio accounting. Source hashes in a new run will reflect this packaged layout; canonical archive manifests retain the executed source hashes.

## Historical evidence

```bash
python tools/audit_submission_evidence.py
```

This reproduces all 49 archived primary paired p-values from the 70 control rows and writes the retrospective global-Holm sensitivity audit. It preserves the frozen original statistics.

Historical batch scripts use relative paths and call sibling scripts. Run them in an isolated copy of `historical/`, with that copy as the working directory:

```bash
mkdir -p /tmp/relevance-historical
cp -R historical/. /tmp/relevance-historical/
cd /tmp/relevance-historical
python run_control_multiseed.py
python analyze_control_results.py
```

Other runners cover residual-energy weights, event quality, targeting and topology sensitivity. Topology C5 budgets are 1744, 1648 and 1568 bits for shallow, medium and deep regimes; retain the calibration/correction procedure in the archived scripts. To analyze existing historical outputs without rerunning, copy the packaged `results/master_validation/` into the isolated copy's `results/master_validation/` first. Some batch runners skip existing results, so use a fresh directory for a new experiment. Historical environment snapshots are retained with the archived results; cross-version stochastic reruns are not guaranteed to be bit-identical.

## Component tests

```bash
python -m unittest discover -s tests -v
```

These test progressive packing and decoding, distortion-based allocation, exact shuffled budgets, missing-report accounting and physical-work accounting on transmission failures. They do not replace the raw-log audit or constitute additional experimental evidence.
