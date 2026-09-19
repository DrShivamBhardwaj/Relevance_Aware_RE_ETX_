import csv, hashlib, json, math, statistics, sys, time
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from wsn_hfl.config import SimConfig
from wsn_hfl.har import simulate_har

METHODS=('random','resource','utility','proposed')
SEEDS=(7,11,19,23,29,31,37,41,43,47)
CORRELATIONS=(0.0,0.5,0.9)


def msci(vals):
    vals=[float(v) for v in vals]; m=statistics.fmean(vals); sd=statistics.stdev(vals) if len(vals)>1 else 0.0
    return m,sd,1.96*sd/math.sqrt(len(vals)) if len(vals)>1 else 0.0


def write(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)


def main():
    data=ROOT/'data/uci_har'; out=ROOT/'results/uci_har'
    cfg=replace(SimConfig(),num_clients=30,num_gateways=4,num_classes=6,feature_dim=561,rounds=25,clients_per_round=8,local_steps=1,learning_rate=.02,l2=.001,bandwidth_bps=250000.0,round_slot_s=.25,compression_distortion_weight=.1,relay_budget_j_per_round=.004,relay_pressure_weight=3.0)
    raw=[]; hist=[]; start=time.time()
    for corr in CORRELATIONS:
        for method in METHODS:
            for seed in SEEDS:
                s,h=simulate_har(method,replace(cfg,seed=seed),data,corr); raw.append(s); hist.extend({'seed':seed,**r} for r in h)
            g=[r for r in raw if r['method']==method and r['correlation']==corr]
            print(f"corr={corr:.1f} method={method:8s} acc={statistics.fmean(r['accuracy'] for r in g):.4f} macroF1={statistics.fmean(r['macro_f1'] for r in g):.4f} repJS={statistics.fmean(r['representation_js'] for r in g):.4f}")
    numeric=['accuracy','macro_f1','worst_client_accuracy','p10_client_accuracy','client_accuracy_sd','effective_bits','compressed_bits','raw_selected_bits','mean_selected_hops','mean_selected_etx','energy_j','min_residual_energy_j','max_relay_energy_j','participation_jain','representation_js','class_coverage_js']
    agg=[]
    for corr in CORRELATIONS:
        for method in METHODS:
            rows=[r for r in raw if r['method']==method and r['correlation']==corr]; o={'method':method,'correlation':corr,'n':len(rows)}
            for k in numeric:
                m,sd,ci=msci([r[k] for r in rows]); o[k+'_mean']=m;o[k+'_sd']=sd;o[k+'_ci95']=ci
            agg.append(o)
    write(out/'raw_summary.csv',raw); write(out/'round_history.csv',hist); write(out/'aggregate_summary.csv',agg)
    zipfile=data/'har.zip'; manifest={'dataset':'UCI Human Activity Recognition Using Smartphones','doi':'10.24432/C54S4K','source':'https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones','task':'subject-as-client six-class activity recognition','methods':METHODS,'seeds':SEEDS,'correlations':CORRELATIONS,'config':cfg.__dict__,'runtime_s':time.time()-start,'har_zip_sha256':hashlib.sha256(zipfile.read_bytes()).hexdigest()}
    (out/'run_manifest.json').write_text(json.dumps(manifest,indent=2,default=list)); print('completed',round(manifest['runtime_s'],2),'s')
if __name__=='__main__': main()
