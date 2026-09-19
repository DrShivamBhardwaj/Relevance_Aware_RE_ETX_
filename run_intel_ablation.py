import csv
import math
import statistics
import sys
from dataclasses import replace
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from wsn_hfl.config import SimConfig
from wsn_hfl.intel_lab import simulate_intel

METHODS=('proposed','proposed_no_rep','proposed_fixed_comp','proposed_age_only','proposed_no_relay')
SEEDS=(7,11,19,23,29,31,37,41,43,47)


def stats(vals):
    vals=[float(v) for v in vals]; m=statistics.fmean(vals)
    sd=statistics.stdev(vals) if len(vals)>1 else 0.0
    return m,sd,1.96*sd/math.sqrt(len(vals)) if len(vals)>1 else 0.0


def main():
    cfg=replace(SimConfig(),num_clients=54,num_gateways=4,rounds=30,clients_per_round=10,
                local_steps=1,learning_rate=.01,l2=.01,round_slot_s=.2,
                relay_budget_j_per_round=.004,relay_pressure_weight=3.0,compression_distortion_weight=.1)
    data=ROOT/'data/intel_lab'; rows=[]
    for method in METHODS:
        runs=[]
        for seed in SEEDS:
            s,_=simulate_intel(method,replace(cfg,seed=seed),data,.9)
            runs.append(s)
        out={'variant':method,'n':len(runs)}
        for key in ['rmse_c','mae_c','effective_bits','energy_j','max_relay_energy_j','participation_jain','representation_js']:
            m,sd,ci=stats([x[key] for x in runs]); out[key+'_mean']=m; out[key+'_sd']=sd; out[key+'_ci95']=ci
        rows.append(out)
        print(method,'RMSE',round(out['rmse_c_mean'],4),'bits',round(out['effective_bits_mean']),'E',round(out['energy_j_mean'],3),'repJS',round(out['representation_js_mean'],4),'relay',round(out['max_relay_energy_j_mean'],4))
    outdir=ROOT/'results/intel_lab'; p=outdir/'ablation_summary.csv'
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print('wrote',p)

if __name__=='__main__': main()
