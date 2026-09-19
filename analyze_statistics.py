import csv, math, statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'validation/statistics'; OUT.mkdir(parents=True,exist_ok=True)

CASES=[('intel_lab',ROOT/'results/intel_lab/raw_summary.csv',['rmse_c','mae_c','effective_bits','energy_j','max_relay_energy_j','representation_js']),('uci_har',ROOT/'results/uci_har/raw_summary.csv',['accuracy','macro_f1','worst_client_accuracy','p10_client_accuracy','effective_bits','energy_j','max_relay_energy_j','representation_js'])]

def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))

def cliffs_delta(x,y):
    more=less=0
    for a in x:
        for b in y:
            if a>b: more+=1
            elif a<b: less+=1
    return (more-less)/(len(x)*len(y))

def cohen_d(diffs):
    if len(diffs)<2: return 0.0
    sd=statistics.stdev(diffs)
    return 0.0 if sd==0 else statistics.fmean(diffs)/sd

def bootstrap_ci(diffs,B=20000,seed=2026):
    import random
    rnd=random.Random(seed)
    vals=[]; n=len(diffs)
    for _ in range(B): vals.append(statistics.fmean(diffs[rnd.randrange(n)] for _ in range(n)))
    vals.sort(); return vals[int(.025*B)], vals[int(.975*B)]

def holm(ps):
    order=sorted(range(len(ps)),key=lambda i:ps[i])
    adj=[0.0]*len(ps); prev=0.0; m=len(ps)
    for rank,i in enumerate(order):
        val=min(1.0,(m-rank)*ps[i]); prev=max(prev,val); adj[i]=prev
    return adj

def exact_signflip_p(diffs):
    import itertools
    obs=abs(statistics.fmean(diffs)); cnt=tot=0
    for s in itertools.product((-1.0,1.0),repeat=len(diffs)):
        if abs(statistics.fmean(a*b for a,b in zip(s,diffs)))>=obs-1e-15: cnt+=1
        tot+=1
    return cnt/tot

def main():
    allrows=[]
    for dataset,path,metrics in CASES:
        raw=read(path); corr=0.9
        prop={int(r['seed']):r for r in raw if r['method']=='proposed' and float(r['correlation'])==corr}
        for base in ['random','resource','utility']:
            brow={int(r['seed']):r for r in raw if r['method']==base and float(r['correlation'])==corr}
            temp=[]; ps=[]
            for metric in metrics:
                seeds=sorted(set(prop)&set(brow))
                pv=[float(prop[s][metric]) for s in seeds]; bv=[float(brow[s][metric]) for s in seeds]
                diffs=[a-b for a,b in zip(pv,bv)]
                p=exact_signflip_p(diffs); ps.append(p)
                lo,hi=bootstrap_ci(diffs,B=5000)
                temp.append({'dataset':dataset,'baseline':base,'metric':metric,'n':len(seeds),'mean_proposed':statistics.fmean(pv),'mean_baseline':statistics.fmean(bv),'mean_diff':statistics.fmean(diffs),'percent_change_vs_baseline':100*statistics.fmean(diffs)/statistics.fmean(bv) if statistics.fmean(bv) else 0.0,'bootstrap95_low':lo,'bootstrap95_high':hi,'signflip_p':p,'cohen_d_paired':cohen_d(diffs),'cliffs_delta_unpaired':cliffs_delta(pv,bv)})
            adj=holm(ps)
            for r,a in zip(temp,adj): r['holm_p']=a; allrows.append(r)
    with (OUT/'statistical_tests.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(allrows[0].keys())); w.writeheader(); w.writerows(allrows)
    lines=['# Statistical robustness report','','All tests use paired seed-level comparisons at correlation 0.9. Exact sign-flip p-values are paired permutation tests over 10 seeds; Holm correction is applied within each dataset-baseline family. Bootstrap intervals are percentile 95% intervals for the paired mean difference.','']
    for dataset in ['intel_lab','uci_har']:
        lines += [f'## {dataset}','']
        for base in ['resource']:
            lines += [f'### Proposed vs {base}','', '| Metric | Proposed | Baseline | Diff | % change | p | Holm p | 95% bootstrap CI |', '|---|---:|---:|---:|---:|---:|---:|---:|']
            for r in [x for x in allrows if x['dataset']==dataset and x['baseline']==base]:
                lines.append(f"| {r['metric']} | {r['mean_proposed']:.4g} | {r['mean_baseline']:.4g} | {r['mean_diff']:.4g} | {r['percent_change_vs_baseline']:.2f}% | {r['signflip_p']:.4f} | {r['holm_p']:.4f} | [{r['bootstrap95_low']:.4g}, {r['bootstrap95_high']:.4g}] |")
            lines.append('')
    (OUT/'STATISTICAL_ROBUSTNESS_REPORT.md').write_text('\n'.join(lines))
    print('\n'.join(lines[:50])); print('wrote',OUT)
if __name__=='__main__':main()
