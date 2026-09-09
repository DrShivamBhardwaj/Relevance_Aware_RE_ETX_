#!/usr/bin/env python3
import csv, subprocess, pathlib, sys, time
BASE=pathlib.Path('/Users/shivambhardwaj/ns3-validation/ns-3.47')
BIN=BASE/'build/scratch/ns3.47-j4j5j6-lrwpan-validation-optimized'
OUTDIR=pathlib.Path('/Users/shivambhardwaj/ns3-validation/j4j5j6_results')
OUTDIR.mkdir(parents=True, exist_ok=True)
OUT=OUTDIR/'ns3_j4j5j6_20seed_load_sweep.csv'
SEEDS=[11,23,42,67,101,137,173,211,257,307,349,401,457,503,557,601,653,701,757,809]
J5={
11:1675.564439990506,23:1726.3470855360322,42:1711.0817538604556,67:1728.0356386906226,
101:1689.3454407869845,137:1769.6952678986763,173:1717.31080007812,211:1730.2709027194533,
257:1768.281637096537,307:1711.340556867,349:1707.152077620755,401:1763.7197717796796,
457:1726.7075530786242,503:1720.0677812923634,557:1701.9037039954833,601:1700.4690427947835,
653:1730.1607513251902,701:1717.524579871808,757:1671.411535048802,809:1722.874773139746}
PERIODS=[2.5,5.0,10.0]
MODES=['J4','J5','J6']
FIELDS='mode,seed,report_period_s,payload_bits,frames_per_report,generated_reports,delivered_reports,report_rdr_pct,frame_confirms,frame_success,frame_rdr_pct,mean_delivered_report_delay_ms,mean_retries_per_frame,mean_csma_cycles_per_frame,channel_access_failures,no_ack,other_failures,overlap_drops,sim_time_s'.split(',')

def payload(mode,seed):
    return 4000.0 if mode=='J4' else (J5[seed] if mode=='J5' else 1712.0)

def run_one(mode,seed,period):
    cmd=[str(BIN),f'--mode={mode}',f'--seed={seed}',f'--payloadBits={payload(mode,seed)}',f'--reportPeriod={period}','--simTime=40','--header=0']
    p=subprocess.run(cmd,cwd=BASE,text=True,capture_output=True,check=True,timeout=120)
    lines=[x.strip() for x in p.stdout.splitlines() if x.strip()]
    if not lines: raise RuntimeError('no output '+repr(p.stderr))
    vals=next(csv.reader([lines[-1]]))
    if len(vals)!=len(FIELDS): raise RuntimeError(f'bad fields {len(vals)}: {lines[-1]}')
    return dict(zip(FIELDS,vals))

existing=set()
rows=[]
if OUT.exists():
    with OUT.open() as f:
        for r in csv.DictReader(f):
            rows.append(r); existing.add((r['mode'],int(r['seed']),float(r['report_period_s'])))

total=len(PERIODS)*len(MODES)*len(SEEDS); done=len(existing)
print(f'RESUME {done}/{total}',flush=True)
for period in PERIODS:
    for mode in MODES:
        for seed in SEEDS:
            key=(mode,seed,period)
            if key in existing: continue
            t=time.time(); r=run_one(mode,seed,period); rows.append(r); existing.add(key); done+=1
            rows.sort(key=lambda x:(float(x['report_period_s']), x['mode'], int(x['seed'])))
            tmp=OUT.with_suffix('.tmp')
            with tmp.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
            tmp.replace(OUT)
            print(f'DONE {done}/{total} period={period} mode={mode} seed={seed} rdr={r["report_rdr_pct"]} delay={r["mean_delivered_report_delay_ms"]} sec={time.time()-t:.2f}',flush=True)
print('COMPLETE',OUT,flush=True)
