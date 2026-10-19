"""Audit the archived C1-C7 study without changing frozen experiment outputs.

Run from the repository root: python tools/audit_submission_evidence.py
This is a retrospective multiplicity sensitivity analysis, not a new experiment.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'results/master_validation/statistics'
OUT = ROOT / 'results/cooja_preflight/historical_audit'
SEEDS = {11, 23, 42, 67, 101, 137, 173, 211, 257, 307}
METRICS = ['FND', 'HND', 'LND', 'PDR_percent', 'average_delay_ms',
           'energy_per_delivered_j', 'retries_per_generated']
CONTRASTS = [('C1', 'C2'), ('C1', 'C3'), ('C3', 'C4'), ('C1', 'C5'),
             ('C5', 'C3'), ('C6', 'C3'), ('C3', 'C7')]


def holm(p):
    p = np.asarray(p, dtype=float)
    if not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError('Invalid p-values')
    order = np.argsort(p)
    result = np.empty(len(p))
    result[order] = np.minimum(1, np.maximum.accumulate(
        p[order] * np.arange(len(p), 0, -1)))
    return result


def main():
    raw = pd.read_csv(SOURCE / 'control_multiseed_raw.csv')
    if raw.duplicated(['mode', 'seed']).any() or len(raw) != 70:
        raise ValueError('Expected 70 unique mode/seed observations')
    for mode in [f'C{i}' for i in range(1, 8)]:
        if set(raw.loc[raw['mode'] == mode, 'seed']) != SEEDS:
            raise ValueError(f'Missing or unexpected seed in {mode}')
    if not np.isfinite(raw[METRICS].to_numpy()).all():
        raise ValueError('Non-finite primary observations')
    if not ((raw.FND <= raw.HND) & (raw.HND <= raw.LND) & (raw.LND < 5000)).all():
        raise ValueError('Invalid or censored death milestones')
    archived = pd.read_csv(SOURCE / 'planned_paired_tests_holm.csv')
    rows = []
    for baseline, treatment in CONTRASTS:
        a = raw[raw['mode'] == baseline].set_index('seed').sort_index()
        b = raw[raw['mode'] == treatment].set_index('seed').sort_index()
        for metric in METRICS:
            delta = b[metric].to_numpy() - a[metric].to_numpy()
            p = float(stats.ttest_rel(b[metric], a[metric]).pvalue)
            name = f'{baseline}_to_{treatment}'
            old = archived[(archived.contrast == name) & (archived.metric == metric)]
            if len(old) != 1 or not np.isclose(p, old.paired_t_p.iloc[0], rtol=1e-7, atol=1e-14):
                raise ValueError(f'Archived p-value mismatch: {name} {metric}')
            half = stats.t.ppf(.975, 9) * stats.sem(delta)
            rows.append(dict(contrast=name, metric=metric, n=10,
                             mean_difference=delta.mean(), ci95_low=delta.mean()-half,
                             ci95_high=delta.mean()+half, paired_t_p=p))
    result = pd.DataFrame(rows)
    result['holm_p_all_49'] = holm(result.paired_t_p)
    result['significant_all_49'] = result.holm_p_all_49 < .05
    exact = archived.set_index(['contrast','metric']).loc[
        list(zip(result.contrast,result.metric)), 'exact_signflip_p'].to_numpy()
    result['exact_signflip_p'] = exact
    result['holm_signflip_all_49'] = holm(exact)
    OUT.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT / 'network_tests_global_holm.csv', index=False)
    summary = dict(unique_control_runs=len(raw), paired_tests=len(result),
                   all_archived_primary_pvalues_reproduced=True,
                   analysis='Retrospective sensitivity; one Holm family of 49 network tests',
                   limitations=['No new simulation runs', 'No equivalence test',
                                'No held-out calibration seeds', 'Intervals are marginal'])
    (OUT / 'audit_summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary, indent=2))
    print(result[result.contrast == 'C5_to_C3'][['metric', 'holm_p_all_49', 'significant_all_49']].to_string(index=False))


if __name__ == '__main__':
    main()
