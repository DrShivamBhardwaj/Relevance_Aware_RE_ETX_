"""Capture observation and delivery traces from the frozen simulator."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import itertools
import os
import subprocess
import sys

SEEDS = (11, 23, 42, 67, 101, 137, 173, 211, 257, 307)
PROFILES = {
    'receiver': (100, 150, 30, 1744, ('C3', 'C5', 'C6')),
    'shallow': (150, 200, 25, 1744, ('C3', 'C5')),
    'medium': (400, 450, 45, 1648, ('C3', 'C5')),
    'deep': (600, 650, 60, 1568, ('C3', 'C5')),
}
ROUNDS = 300

def instrument(text):
    changes = [
        ('    mode = config.experiment_mode', '''    config.max_rounds = int(os.environ["AUDIT_ROUNDS"])
    trace_shape = (config.max_rounds, config.num_nodes)
    trace_observations = np.full(trace_shape, np.nan)
    trace_truth = np.zeros(trace_shape, dtype=bool)
    trace_generated = np.zeros(trace_shape, dtype=bool)
    trace_bits = np.zeros(trace_shape, dtype=np.uint16)
    trace_lag = np.full(trace_shape, np.nan)
    trace_event_onset = np.full(config.max_rounds, -1, dtype=np.int16)
    trace_airtime = np.zeros(config.max_rounds)
    previous_center = None
    active_onset = -1

    mode = config.experiment_mode'''),
        ('        event_truth = sensing.event_truth()', '''        event_truth = sensing.event_truth()
        row = round_id - 1
        trace_observations[row] = current_observation
        trace_truth[row] = event_truth
        if sensing.event_active:
            if sensing.event_center is not previous_center:
                active_onset = row
            trace_event_onset[row] = active_onset
        previous_center = sensing.event_center'''),
        ('        generated_round = int(', '''        trace_generated[row, schedule] = True
        generated_round = int('''),
        ('            result = transmitter.transmit(', '''            trace_bits[row, source] = semantic_payload_bits[source]
            result = transmitter.transmit('''),
        ('                metrics.register_delivered(', '''                trace_lag[row, source] = delay
                metrics.register_delivered('''),
        ('        elapsed_channel_time += (', '''        trace_airtime[row] = round_airtime
        elapsed_channel_time += ('''),
        ('    if lnd is not None:\n        assert (', '''    np.savez_compressed(
        "trace.npz", observations=trace_observations, truth=trace_truth,
        generated=trace_generated, bits=trace_bits, lag=trace_lag,
        event_onset=trace_event_onset, airtime=trace_airtime,
    )

    if lnd is not None:
        assert ('''),
    ]
    for old, new in changes:
        if text.count(old) != 1:
            raise ValueError(f'Instrumentation anchor mismatch: {old}')
        text = text.replace(old, new, 1)
    return text

def main():
    args = argparse.ArgumentParser()
    args.add_argument('--workers', type=int, default=5)
    args.add_argument('--profile', choices=PROFILES)
    args.add_argument('--seed', type=int, choices=SEEDS)
    opts = args.parse_args()
    root = Path(__file__).resolve().parent
    source = root/'source'
    driver = source/'instrumented.py'
    driver.write_text(instrument((source/'run_semantic_re_etx.py').read_text()))
    jobs = [
        (name, mode, seed)
        for (name, (_, _, _, _, modes)), seed in itertools.product(PROFILES.items(), SEEDS)
        if (opts.profile is None or name == opts.profile) and (opts.seed is None or seed == opts.seed)
        for mode in modes
    ]

    def run(job):
        name, mode, seed = job
        height, sink_y, radius, c5, _ = PROFILES[name]
        dest = root/'runs'/name/f'{mode}_{seed}'
        dest.mkdir(parents=True, exist_ok=True)
        inputs = dict(
            AUDIT_ROUNDS=ROUNDS, EXPERIMENT_MODE=mode, SEMANTIC_SEED=seed, NUM_NODES=100,
            AREA_WIDTH_M=100, AREA_HEIGHT_M=height, BS_X_M=50, BS_Y_M=sink_y,
            MAX_SENSOR_LINK_DISTANCE_M=radius, EQUAL_BUDGET_PAYLOAD_BITS=c5,
            SHUFFLE_SEED_OFFSET=6000003, OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=1,
            MKL_NUM_THREADS=1,
        )
        env = os.environ | {k:str(v) for k,v in inputs.items()}
        result = subprocess.run([sys.executable, str(driver)], env=env, cwd=dest,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        (dest/'simulator.log').write_text(result.stdout)
        if result.returncode or 'All dynamic minimum-ETX checks PASSED.' not in result.stdout:
            raise RuntimeError(f'{job} failed: {result.stdout[-2000:]}')
        return job

    with ThreadPoolExecutor(max_workers=opts.workers) as executor:
        for job in executor.map(run, jobs):
            print(*job, 'completed', flush=True)

if __name__ == '__main__':
    main()
