# Final consistency audit

Date: 2026-09-19

## Audit decision

**PASS after cleanup.** The active implementation, experiment manifests, principal result tables, manuscript claims, ns-3 summary, and committed dataset checksums are mutually consistent for the frozen submission configuration.

The authoritative manuscript source is:

- `MANUSCRIPT_RECONSTRUCTION.md`

The authoritative mathematical definition is:

- `FINAL_FORMULATION.md`

The executable audit is:

- `audit_consistency.py`

## Frozen operating point

- `relay_pressure_weight = 3.0`
- `compression_distortion_weight = 0.10`
- `drift_v = 0.5`
- `staleness_lambda = 0.35`
- `utility_staleness_mu = 0.80`
- Top-k candidate ratios: `{0.15, 0.30, 0.50, 0.75, 1.0}`

These values agree across `SimConfig`, Intel/HAR experiment drivers, 10-seed manifests, the formulation, parameter-freeze note, evidence summary, and manuscript.
## Result synchronization checks

The root synthetic results are byte-identical to the final 10-seed synthetic result set.

At strong resource-data correlation `c=0.9`, recomputation from CSV gives:

### Synthetic stress test

- resource-only accuracy: 0.9363
- proposed accuracy: 0.9364
- resource-only effective bits: 1.544 M
- proposed effective bits: 0.544 M
- proposed representation JS: 0.0202

### Intel Berkeley Lab WSN

Proposed relative to resource-only:

- effective communication: **-55.67%**
- modeled energy: **-45.06%**
- maximum relay energy: **-29.94%**
- representation divergence: **-81.21%**

Intel RMSE is statistically comparable rather than claimed as a universal win; the manuscript preserves that qualification.
### UCI HAR

Proposed relative to resource-only:

- accuracy: **+3.08 percentage points**
- effective communication: **-60.75%**
- modeled energy: **-56.38%**
- representation divergence: **-79.97%**

These values agree with the manuscript, evidence summary, real-data reports, and statistical robustness report.

### ns-3.47 hop-equivalent replay

For the dense-nominal condition:

- resource-only RDR: **86.49%**
- proposed RDR: **99.47%**
- resource-only delay: **37.45 ms**
- proposed delay: **12.02 ms**
- mapped payloads: 3476 bits (resource) and 1219 bits (proposed)

The manuscript correctly describes this as communication-profile validation, not execution of the Python HFL optimizer inside ns-3.
## Dataset integrity

The audit recomputes SHA-256 checksums of the committed compressed datasets and verifies them against the experiment manifests:

- Intel `data.txt.gz`
- Intel `mote_locs.txt`
- Intel `connectivity.txt`
- UCI HAR `har.zip`

All checksums pass.

## Cleanup performed

To remove ambiguity before manuscript reconstruction:

- the old generic `MANUSCRIPT_DRAFT.md` is removed from the active tree;
- obsolete duplicate sensitivity scripts/report are removed;
- duplicate legacy figure names are removed in favor of the final publication figure set;
- the 3-seed synthetic result set is archived at `archive/results/final_synthetic_3seed/`;
- the pre-tuning synthetic result set is archived at `archive/results/pre_tuning/`;
- the active synthetic results are the 10-seed final set;
- final sensitivity figures are generated from the per-dataset `joint_grid.csv` files.

Git history preserves all removed material.
## Remaining non-consistency limitations

These are not audit failures, but they remain manuscript limitations:

1. No physical IEEE 802.15.4/MCU sensor-node experiment has been performed.
2. Energy values are modeled rather than measured on sensor hardware.
3. A complete convergence theorem jointly covering biased selection, Top-k error feedback, hierarchy, and staleness is not yet established.
4. Citation/reference integrity requires a separate source-by-source literature audit before submission.

## Reproduction

Run:

```bash
.venv/bin/python audit_consistency.py
.venv/bin/pytest -q
```

A submission build should proceed only if both commands pass.
