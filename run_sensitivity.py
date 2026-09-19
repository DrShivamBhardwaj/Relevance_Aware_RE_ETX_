import argparse,csv,math,statistics,sys,time
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from wsn_hfl.config import SimConfig
from wsn_hfl.har import simulate_har
from wsn_hfl.intel_lab import simulate_intel

SEEDS=(7,11,19,23,29,31,37,41,43,47)
RELAY_WEIGHTS=(0.0,1.0,2.0,3.0,5.0,8.0)
COMP_WEIGHTS=(0.1,0.2,0.4,0.8,1.2)


def msci(vals):
    vals=[float(v) for v in vals]; m=statistics.fmean(vals); sd=statistics.stdev(vals) if len(vals)>1 else 0.0
    return m,sd,1.96*sd/math.sqrt(len(vals)) if len(vals)>1 else 0.0

def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)

def aggregate(label,value,runs,metrics):
    o={'parameter':label,'value':value,'n':len(runs)}
    for k in metrics:
        m,sd,ci=msci([x[k] for x in runs]);o[k+'_mean']=m;o[k+'_sd']=sd;o[k+'_ci95']=ci
    return o

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',choices=['intel','har'],required=True);args=ap.parse_args()
    if args.dataset=='intel':
        base=replace(SimConfig(),num_clients=54,num_gateways=4,rounds=30,clients_per_round=10,local_steps=1,learning_rate=.01,l2=.01,round_slot_s=.2,relay_budget_j_per_round=.004,compression_distortion_weight=.4)
        fn=lambda c,s: simulate_intel('proposed',c,ROOT/'data/intel_lab',.9)[0]
        out=ROOT/'results/intel_lab';metrics=['rmse_c','mae_c','effective_bits','energy_j','max_relay_energy_j','representation_js','participation_jain']
    else:
        base=replace(SimConfig(),num_clients=30,num_gateways=4,num_classes=6,feature_dim=561,rounds=25,clients_per_round=8,local_steps=1,learning_rate=.02,l2=.001,bandwidth_bps=250000.,round_slot_s=.25,compression_distortion_weight=.4,relay_budget_j_per_round=.004)
        fn=lambda c,s: simulate_har('proposed',c,ROOT/'data/uci_har',.9)[0]
        out=ROOT/'results/uci_har';metrics=['accuracy','macro_f1','worst_client_accuracy','effective_bits','energy_j','max_relay_energy_j','representation_js','participation_jain']
    rows=[];start=time.time()
    for v in RELAY_WEIGHTS:
        runs=[]
        for seed in SEEDS:
            cfg=replace(base,seed=seed,relay_pressure_weight=v,compression_distortion_weight=.4)
            runs.append(fn(cfg,seed))
        rows.append(aggregate('relay_pressure_weight',v,runs,metrics));print(args.dataset,'relay',v)
    for v in COMP_WEIGHTS:
        runs=[]
        for seed in SEEDS:
            cfg=replace(base,seed=seed,relay_pressure_weight=3.0,compression_distortion_weight=v)
            runs.append(fn(cfg,seed))
        rows.append(aggregate('compression_distortion_weight',v,runs,metrics));print(args.dataset,'compression',v)
    write(out/'sensitivity_summary.csv',rows)
    print('completed',args.dataset,'in',round(time.time()-start,2),'s')
if __name__=='__main__':main()
