import csv, math, statistics, sys, time
from dataclasses import replace
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from wsn_hfl.config import SimConfig
from wsn_hfl.har import simulate_har
from wsn_hfl.intel_lab import simulate_intel

SEEDS=(7,11,19,23,29,31,37,41,43,47)
RELAY_WEIGHTS=(1.0,2.0,3.0,5.0)
DISTORTION_WEIGHTS=(0.2,0.4,0.8)
CORR=0.9


def msci(vals):
    vals=[float(v) for v in vals]; m=statistics.fmean(vals); sd=statistics.stdev(vals) if len(vals)>1 else 0.0
    return m,sd,1.96*sd/math.sqrt(len(vals)) if len(vals)>1 else 0.0


def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=[]
    for row in rows:
        for key in row:
            if key not in fields: fields.append(key)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)


def aggregate(runs, metrics, dataset, rp, beta):
    o={'dataset':dataset,'relay_pressure_weight':rp,'compression_distortion_weight':beta,'n':len(runs)}
    for k in metrics:
        m,sd,ci=msci([r[k] for r in runs]); o[k+'_mean']=m;o[k+'_sd']=sd;o[k+'_ci95']=ci
    return o


def pareto(rows, maximize, minimize):
    fronts=[]
    for i,a in enumerate(rows):
        dominated=False
        for j,b in enumerate(rows):
            if i==j: continue
            no_worse=all(float(b[k])>=float(a[k])-1e-12 for k in maximize) and all(float(b[k])<=float(a[k])+1e-12 for k in minimize)
            strictly=any(float(b[k])>float(a[k])+1e-12 for k in maximize) or any(float(b[k])<float(a[k])-1e-12 for k in minimize)
            if no_worse and strictly:
                dominated=True; break
        if not dominated: fronts.append(a)
    return fronts


def main():
    outdir=ROOT/'results/sensitivity'; start=time.time(); allrows=[]
    har_base=replace(SimConfig(),num_clients=30,num_gateways=4,num_classes=6,feature_dim=561,rounds=25,clients_per_round=8,local_steps=1,learning_rate=.02,l2=.001,bandwidth_bps=250000.,round_slot_s=.25,relay_budget_j_per_round=.004)
    intel_base=replace(SimConfig(),num_clients=54,num_gateways=4,rounds=30,clients_per_round=10,local_steps=1,learning_rate=.01,l2=.01,round_slot_s=.2,relay_budget_j_per_round=.004)
    har_metrics=['accuracy','macro_f1','worst_client_accuracy','p10_client_accuracy','effective_bits','energy_j','max_relay_energy_j','representation_js','participation_jain']
    intel_metrics=['rmse_c','mae_c','worst_client_rmse_c','p90_client_rmse_c','effective_bits','energy_j','max_relay_energy_j','representation_js','participation_jain']
    for rp in RELAY_WEIGHTS:
        for beta in DISTORTION_WEIGHTS:
            hr=[]
            for seed in SEEDS:
                cfg=replace(har_base,seed=seed,relay_pressure_weight=rp,compression_distortion_weight=beta)
                s,_=simulate_har('proposed',cfg,ROOT/'data/uci_har',CORR); hr.append(s)
            row=aggregate(hr,har_metrics,'uci_har',rp,beta); allrows.append(row)
            print('HAR',rp,beta,'acc',round(row['accuracy_mean'],4),'bits',round(row['effective_bits_mean']),'E',round(row['energy_j_mean'],2),'relay',round(row['max_relay_energy_j_mean'],3),'rep',round(row['representation_js_mean'],4),flush=True)
            ir=[]
            for seed in SEEDS:
                cfg=replace(intel_base,seed=seed,relay_pressure_weight=rp,compression_distortion_weight=beta)
                s,_=simulate_intel('proposed',cfg,ROOT/'data/intel_lab',CORR); ir.append(s)
            row=aggregate(ir,intel_metrics,'intel_lab',rp,beta); allrows.append(row)
            print('INTEL',rp,beta,'rmse',round(row['rmse_c_mean'],4),'bits',round(row['effective_bits_mean']),'E',round(row['energy_j_mean'],3),'relay',round(row['max_relay_energy_j_mean'],4),'rep',round(row['representation_js_mean'],4),flush=True)
    write(outdir/'sensitivity_grid.csv',allrows)

    har=[r for r in allrows if r['dataset']=='uci_har']
    intel=[r for r in allrows if r['dataset']=='intel_lab']
    hp=pareto(har,['accuracy_mean','macro_f1_mean'],['effective_bits_mean','energy_j_mean','max_relay_energy_j_mean','representation_js_mean'])
    ip=pareto(intel,[],['rmse_c_mean','effective_bits_mean','energy_j_mean','max_relay_energy_j_mean','representation_js_mean'])
    for r in hp:r['pareto']='yes'
    for r in har:
        if 'pareto' not in r:r['pareto']='no'
    for r in ip:r['pareto']='yes'
    for r in intel:
        if 'pareto' not in r:r['pareto']='no'
    write(outdir/'har_sensitivity.csv',har); write(outdir/'intel_sensitivity.csv',intel)
    print('HAR Pareto:',[(r['relay_pressure_weight'],r['compression_distortion_weight']) for r in hp])
    print('INTEL Pareto:',[(r['relay_pressure_weight'],r['compression_distortion_weight']) for r in ip])
    print('runtime_s',round(time.time()-start,2))

if __name__=='__main__':main()
