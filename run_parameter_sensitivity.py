import csv, json, math, statistics, sys, time
from dataclasses import replace
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from wsn_hfl.config import SimConfig
from wsn_hfl.har import simulate_har
from wsn_hfl.intel_lab import simulate_intel

SEEDS=(7,11,19,23,29,31,37,41,43,47)
CORR=0.9

DATASETS={
    'intel_lab': {'func':simulate_intel, 'data':ROOT/'data/intel_lab', 'cfg':replace(SimConfig(),num_clients=54,num_gateways=4,rounds=30,clients_per_round=10,local_steps=1,learning_rate=.01,l2=.01,round_slot_s=.20,relay_budget_j_per_round=.004,compression_distortion_weight=.4)},
    'uci_har': {'func':simulate_har, 'data':ROOT/'data/uci_har', 'cfg':replace(SimConfig(),num_clients=30,num_gateways=4,num_classes=6,feature_dim=561,rounds=25,clients_per_round=8,local_steps=1,learning_rate=.02,l2=.001,bandwidth_bps=250000.,round_slot_s=.25,relay_budget_j_per_round=.004,compression_distortion_weight=.4)},
}

SWEEPS={
    'relay_pressure_weight':[0,1,2,3,5,8],
    'compression_distortion_weight':[0.1,0.2,0.4,0.8,1.2,2.0],
    'drift_v':[0.25,0.5,1,2,4],
}

METRICS=['rmse_c','accuracy','macro_f1','effective_bits','energy_j','max_relay_energy_j','representation_js','participation_jain']


def mean_sd_ci(vals):
    vals=[float(v) for v in vals if v is not None]
    if not vals: return None,None,None
    mean=statistics.fmean(vals)
    sd=statistics.stdev(vals) if len(vals)>1 else 0.0
    ci=1.96*sd/math.sqrt(len(vals)) if len(vals)>1 else 0.0
    return mean,sd,ci


def main():
    outdir=ROOT/'results/sensitivity'; outdir.mkdir(parents=True,exist_ok=True)
    raw=[]; agg=[]; start=time.time()
    for dname, spec in DATASETS.items():
        for sweep, vals in SWEEPS.items():
            for val in vals:
                runs=[]
                for seed in SEEDS:
                    cfg=replace(spec['cfg'], seed=seed, **{sweep:val})
                    summary,_=spec['func']('proposed', cfg, spec['data'], CORR)
                    rec={'dataset':dname,'sweep':sweep,'value':val,**summary}
                    raw.append(rec); runs.append(rec)
                row={'dataset':dname,'sweep':sweep,'value':val,'n':len(runs)}
                for m in METRICS:
                    if m in runs[0]:
                        mean,sd,ci=mean_sd_ci([r.get(m) for r in runs])
                        row[m+'_mean']=mean; row[m+'_sd']=sd; row[m+'_ci95']=ci
                agg.append(row)
                mainmetric='rmse_c_mean' if dname=='intel_lab' else 'accuracy_mean'
                print(f"{dname:9s} {sweep:30s}={val:<4} {mainmetric}={row.get(mainmetric):.4f} bits={row['effective_bits_mean']:.0f} rep={row['representation_js_mean']:.4f}")
    for name, rows in [('raw_sensitivity.csv',raw),('aggregate_sensitivity.csv',agg)]:
        keys=[]
        for r in rows:
            for k in r.keys():
                if k not in keys: keys.append(k)
        with (outdir/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(rows)
    (outdir/'sensitivity_manifest.json').write_text(json.dumps({'seeds':SEEDS,'correlation':CORR,'sweeps':SWEEPS,'runtime_s':time.time()-start},indent=2,default=list))
    print(f"completed sensitivity in {time.time()-start:.2f}s -> {outdir}")

if __name__=='__main__': main()
