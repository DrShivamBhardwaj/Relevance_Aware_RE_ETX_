"""Evaluate payload-dependent decoding and timestamped event reception."""
from pathlib import Path
import csv
from functools import lru_cache
import json
import platform
import struct
import sys

import numpy as np
import scipy
from scipy.stats import t, wilcoxon

from run_reviewer_experiments import PROFILES, SEEDS, ROUNDS

ROOT = Path(__file__).resolve().parent
WINDOW = 160
HEADER = struct.Struct('<HBBI')
EVENT_THRESHOLD = 0.5
PERIODS = (2.0, 5.0, 10.0)
DEADLINE = 5.0

@lru_cache(None)
def positions(window, count):
    return np.rint(np.linspace(0, window - 1, count)).astype(int)

def encode(values, bits, round_index):
    nbytes = bits // 8
    n = min(len(values), (nbytes - HEADER.size) // 2)
    assert bits % 8 == 0 and n >= 2
    offsets = positions(len(values), n)
    knots = np.rint(256 * values[offsets]).clip(-32768, 32767).astype('<i2')
    message = HEADER.pack(len(values), n, 0, round_index) + knots.tobytes()
    return message.ljust(nbytes, b'\0')

def decode(message):
    window, n, _, round_index = HEADER.unpack_from(message)
    knots = np.frombuffer(message, '<i2', count=n, offset=HEADER.size) / 256
    return np.interp(np.arange(window), positions(window, n), knots), round_index

def trace(profile, mode, seed):
    with np.load(ROOT/'runs'/profile/f'{mode}_{seed}'/'trace.npz') as f:
        return {k:f[k] for k in f.files}

def common_arrays(traces):
    baseline = traces[0]
    for run in traces[1:]:
        if np.isnan(run['observations']).any() or np.isnan(baseline['observations']).any():
            raise ValueError('At least one profile stopped before the study horizon')
        for field in ('observations', 'truth', 'event_onset'):
            np.testing.assert_array_equal(run[field], baseline[field])
    return baseline['observations'], baseline['truth']

def receiver(seed):
    modes = ('C3', 'C5', 'C6')
    runs = [trace('receiver', mode, seed) for mode in modes]
    observations, truth = common_arrays(runs)
    common = np.isfinite([run['lag'] for run in runs]).all(axis=0)
    common[:WINDOW-1] = False
    indices = np.argwhere(common)
    event_windows = truth[common].sum()
    assert event_windows > 0
    rows = []
    for mode, run in zip(modes, runs):
        sq = 0.0
        tp = fp = fn = 0
        for i, source in indices:
            x = observations[i+1-WINDOW:i+1,source]
            y = truth[i+1-WINDOW:i+1,source]
            bits = int(run['bits'][i,source])
            message = encode(x, bits, int(i))
            assert len(message)*8 == bits
            reconstruction, end = decode(message)
            assert end == i
            sq += float(np.sum((x-reconstruction)**2))
            prediction = reconstruction >= EVENT_THRESHOLD
            tp += int(np.sum(y & prediction))
            fp += int(np.sum(~y & prediction))
            fn += int(np.sum(y & ~prediction))
        attempted = run['bits'] > 0
        rows.append(dict(
            seed=seed, mode=mode, common_reports=len(indices), event_active_report_windows=int(event_windows),
            warmup_rounds=WINDOW-1, matched_window_rmse=np.sqrt(sq/(len(indices)*WINDOW)),
            matched_window_f1=2*tp/(2*tp+fp+fn), true_positive=tp, false_positive=fp, false_negative=fn,
            mean_attempted_bits=float(run['bits'][attempted].mean()),
            total_generated=int(run['generated'].sum()), total_delivered=int(np.isfinite(run['lag']).sum()),
            mean_matched_bits=float(run['bits'][common].mean()),
        ))
    return rows

def episodes(run):
    viable = {}
    for row, source in np.argwhere(run['truth'] & run['generated']):
        onset = int(run['event_onset'][row])
        assert 0 <= onset <= row
        if onset > ROUNDS - 10:
            continue
        key = (onset, int(source))
        viable.setdefault(key, (np.inf, np.inf))
        lag = run['lag'][row,source]
        if np.isfinite(lag) and not np.isfinite(viable[key][0]):
            viable[key] = (int(row)-onset, float(lag))
    return viable

def queue_time(run, period):
    last_arrival = np.max(np.nan_to_num(run['lag'], nan=0.0), axis=1)
    round_service = np.maximum(run['airtime'], last_arrival)
    wait = np.zeros(ROUNDS)
    for i in range(1, ROUNDS):
        wait[i] = max(0.0, wait[i-1] + round_service[i-1] - period)
    return wait

def topology(profile, seed):
    runs = [trace(profile, mode, seed) for mode in ('C3','C5')]
    common_arrays(runs)
    all_events = [episodes(run) for run in runs]
    keyset = set(all_events[0]) & set(all_events[1])
    assert keyset
    keys = sorted(keyset)
    joint = [k for k in keys if all(np.isfinite(event[k][0]) for event in all_events)]
    assert joint
    max_service = max(float(np.nanmax(r['lag'])) for r in runs)
    max_airtime = max(float(r['airtime'].max()) for r in runs)
    out = []
    timestamps = []
    for t_s in PERIODS:
        mode_arrivals = {}
        for mode, ep, run in zip(('C3','C5'),all_events,runs):
            wait = queue_time(run,t_s)
            arrivals = {}
            for key in keys:
                intervals, lag = ep[key]
                arrivals[key] = (intervals * t_s + wait[key[0] + intervals] + lag
                                 if np.isfinite(intervals) else np.inf)
            mode_arrivals[mode] = arrivals
            joint_delays = [arrivals[k] for k in joint]
            deadline_met = sum(value <= DEADLINE for value in arrivals.values())
            successful = sum(np.isfinite(value) for value in arrivals.values())
            out.append(dict(
                profile=profile, seed=seed, mode=mode, sample_period_s=t_s, common_episodes=len(keys),
                jointly_delivered_episodes=len(joint), mean_joint_first_arrival_s=np.mean(joint_delays),
                delivery_on_common_episodes=successful/len(keys), deadline_miss_rate=1-deadline_met/len(keys),
                events_delivered_own_support=sum(np.isfinite(e[0]) for e in ep.values()),
                event_episodes_own_support=len(ep), max_round_service_s=max_service, max_round_airtime_s=max_airtime,
                max_queue_wait_s=float(wait.max()),
            ))
        for onset, sensor in keys:
            origin = onset * t_s
            key = (onset, sensor)
            c3, c5 = (mode_arrivals[m][key] for m in ('C3','C5'))
            timestamps.append(dict(
                profile=profile, seed=seed, period_s=t_s, sensor=sensor, event_onset_round=onset+1,
                event_onset_timestamp_s=origin,
                C3_first_delivery_timestamp_s=origin+c3 if np.isfinite(c3) else '',
                C5_first_delivery_timestamp_s=origin+c5 if np.isfinite(c5) else '',
            ))
    return out, timestamps

def save(path, rows):
    with (ROOT/path).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def paired(rows, label, metric, control):
    treatment = {r['seed']:r[metric] for r in rows if r['mode']=='C3'}
    baseline = {r['seed']:r[metric] for r in rows if r['mode']==control}
    assert tuple(treatment) == tuple(baseline) == SEEDS
    x, y = np.array(list(treatment.values())), np.array(list(baseline.values()))
    delta = x-y
    mean = np.mean(delta)
    radius = t.ppf(.975,len(delta)-1)*np.std(delta,ddof=1)/np.sqrt(len(delta))
    p = 1.0 if np.all(delta==0) else wilcoxon(delta,method='auto').pvalue
    return dict(profile=label, metric=metric, contrast=f'C3-{control}', seeds=len(delta), C3_mean=x.mean(),
                control_mean=y.mean(), difference=mean, ci_low=mean-radius, ci_high=mean+radius,
                p_raw=p, p_holm=None)

def holm(rows):
    order = sorted(rows,key=lambda r:r['p_raw'])
    running = 0
    for k, row in enumerate(order):
        running = max(running, min(1.0,(len(rows)-k)*row['p_raw']))
        row['p_holm'] = running
    return rows

def main():
    for profile, (_,_,_,_,modes) in PROFILES.items():
        for seed in SEEDS:
            for mode in modes:
                log = ROOT/'runs'/profile/f'{mode}_{seed}'/'simulator.log'
                assert 'All dynamic minimum-ETX checks PASSED.' in log.read_text()
    rec = [r for seed in SEEDS for r in receiver(seed)]
    topology_results = [topology(profile,seed) for profile in ('shallow','medium','deep') for seed in SEEDS]
    top = [r for rows, _ in topology_results for r in rows]
    timestamps = [r for _, rows in topology_results for r in rows]
    save('event_timestamps_simulated.csv',timestamps)
    save('receiver_seed_metrics.csv',rec)
    save('topology_seed_metrics.csv',top)
    rec_tests = holm([paired(rec,'receiver',m,c) for c in ('C5','C6')
                      for m in ('matched_window_rmse','matched_window_f1')])
    main_top = [r for r in top if r['sample_period_s']==5]
    top_tests = holm([paired([r for r in main_top if r['profile']==p],p,m,'C5')
                      for p in ('shallow','medium','deep')
                      for m in ('mean_joint_first_arrival_s','deadline_miss_rate')])
    save('receiver_paired.csv',rec_tests)
    save('topology_paired_5s.csv',top_tests)
    (ROOT/'execution_environment.json').write_text(json.dumps(dict(
        python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
        platform=platform.platform(), architecture=platform.machine(),
        source_ref='submission-ready-v1', source_commit='b5d5ac75c981b1eff0171a8cb885ef5764183d85',
        rounds=ROUNDS, seeds=SEEDS, runs=90,
    ),indent=2)+'\n')
    print('Validated 90 simulation logs and wrote both paired analyses.')

if __name__ == '__main__':
    main()
