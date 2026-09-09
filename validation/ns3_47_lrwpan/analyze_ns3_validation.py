#!/usr/bin/env python3
import json, math, hashlib, pathlib
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

BASE=pathlib.Path('/Users/shivambhardwaj/ns3-validation')
RES=BASE/'j4j5j6_results'
CSV=RES/'ns3_j4j5j6_20seed_load_sweep.csv'
df=pd.read_csv(CSV)
for c in df.columns:
    if c not in ('mode',):
        df[c]=pd.to_numeric(df[c], errors='coerce')
df['access_fail_per_report']=df['channel_access_failures']/df['generated_reports']
df['no_ack_per_report']=df['no_ack']/df['generated_reports']
metrics=[
 ('report_rdr_pct','Report RDR (pp)'),
 ('mean_delivered_report_delay_ms','Delivered-report delay (ms)'),
 ('mean_retries_per_frame','MAC retries/frame'),
 ('mean_csma_cycles_per_frame','CSMA cycles/frame'),
 ('access_fail_per_report','Channel-access failures/report'),
]

def ci95(x):
    x=np.asarray(x,float); n=len(x); m=x.mean(); sd=x.std(ddof=1); h=stats.t.ppf(.975,n-1)*sd/math.sqrt(n)
    return m,sd,m-h,m+h
rows=[]
for (period,mode),g in df.groupby(['report_period_s','mode']):
    row={'report_period_s':period,'mode':mode,'n':len(g)}
    for m,_ in metrics:
        mean,sd,lo,hi=ci95(g[m]); row[m+'_mean']=mean; row[m+'_sd']=sd; row[m+'_ci_lo']=lo; row[m+'_ci_hi']=hi
    rows.append(row)
summary=pd.DataFrame(rows).sort_values(['report_period_s','mode'])
summary.to_csv(RES/'ns3_group_summary.csv',index=False)

def holm(ps):
    ps=np.asarray(ps,float); n=len(ps); order=np.argsort(ps); adj=np.empty(n); running=0
    for rank,idx in enumerate(order):
        val=(n-rank)*ps[idx]; running=max(running,val); adj[idx]=min(1.0,running)
    return adj
contrasts=[]
for period in sorted(df.report_period_s.unique()):
    d=df[df.report_period_s==period]
    for label,a,b in [('J5-J4','J5','J4'),('J5-J6','J5','J6')]:
        ga=d[d['mode']==a].set_index('seed').sort_index(); gb=d[d['mode']==b].set_index('seed').sort_index()
        tmp=[]
        for m,desc in metrics:
            x=ga[m]-gb[m]; n=len(x); mean=x.mean(); sd=x.std(ddof=1); se=sd/math.sqrt(n); h=stats.t.ppf(.975,n-1)*se
            t,p=stats.ttest_rel(ga[m],gb[m])
            try: w,pw=stats.wilcoxon(x,alternative='two-sided',zero_method='wilcox')
            except Exception: w,pw=np.nan,np.nan
            dz=mean/sd if sd>0 else np.nan
            tmp.append({'report_period_s':period,'contrast':label,'metric':m,'metric_label':desc,'mean_diff':mean,'ci_lo':mean-h,'ci_hi':mean+h,'dz':dz,'t_stat':t,'p_t':p,'wilcoxon_stat':w,'p_wilcoxon':pw})
        adj=holm([r['p_t'] for r in tmp])
        for r,q in zip(tmp,adj): r['p_holm']=q; r['holm_significant_0_05']=bool(q<.05); contrasts.append(r)
contr=pd.DataFrame(contrasts)
contr.to_csv(RES/'ns3_paired_contrasts.csv',index=False)

# Plots, separate figures, vector PDF + 600 dpi PNG
for metric,ylabel,stem in [
 ('report_rdr_pct','Report delivery ratio (%)','fig_ns3_rdr_load'),
 ('mean_delivered_report_delay_ms','Delivered-report service delay (ms)','fig_ns3_delay_load'),
 ('mean_retries_per_frame','MAC retries per frame','fig_ns3_retries_load'),
 ('mean_csma_cycles_per_frame','CSMA/CA cycles per frame','fig_ns3_csma_load')]:
    plt.figure(figsize=(6.8,4.5))
    for mode in ['J4','J5','J6']:
        s=summary[summary['mode']==mode].sort_values('report_period_s')
        x=s.report_period_s.to_numpy(); y=s[metric+'_mean'].to_numpy(); lo=s[metric+'_ci_lo'].to_numpy(); hi=s[metric+'_ci_hi'].to_numpy()
        plt.errorbar(x,y,yerr=[y-lo,hi-y],marker='o',capsize=3,label=mode)
    plt.xlabel('Report period per sensor (s)'); plt.ylabel(ylabel); plt.grid(True,alpha=.25); plt.legend(); plt.tight_layout()
    plt.savefig(RES/(stem+'.pdf'),bbox_inches='tight'); plt.savefig(RES/(stem+'.png'),dpi=600,bbox_inches='tight'); plt.close()

central=summary[summary.report_period_s==5.0].set_index('mode')
c5=contr[contr.report_period_s==5.0]

def fmt(x,n=3): return f'{x:.{n}f}'
md=[]
md += ['# Executed ns-3.47 LR-WPAN validation report','',
'## Status','',
'- ns-3 version: 3.47, optimized Apple Silicon build.','- Official LR-WPAN unit suites: 11/11 passed before the custom experiment.','- Custom validation: 180/180 runs completed (20 paired seeds x J4/J5/J6 x 3 report periods).','- This is an independent IEEE 802.15.4 MAC/PHY contention validation, not a reproduction of the original full multihop WSN simulator.','',
'## Design','',
'- 100 sensor nodes plus one sink in a controlled single-contention-domain geometry.','- Unslotted CSMA/CA with macMinBE=3, macMaxBE=5, macMaxCSMABackoffs=4.','- ACK requested; macMaxFrameRetries=3.','- Paper framing retained as 800 payload bits per fragment. A 16-byte synthetic non-MAC header plus ns-3 MAC/FCS overhead approximates the paper\'s 216-bit per-frame overhead while respecting the IEEE 802.15.4 PHY frame-size ceiling.','- Paired seeds use identical node geometry/report phases across J4, J5, and J6. J5 uses the reconstructed seed-specific mean payload; J4 uses 4000 bits and J6 uses 1712 bits.','- Report periods 2.5, 5, and 10 s provide high, central, and low offered-load conditions.','',
'## Central 5 s/report results','',
'| Mode | Report RDR (%) | Delay (ms) | Retries/frame | CSMA cycles/frame | Access failures/report |','|---|---:|---:|---:|---:|---:|']
for mode in ['J4','J5','J6']:
    r=central.loc[mode]
    md.append(f"| {mode} | {fmt(r['report_rdr_pct_mean'])} | {fmt(r['mean_delivered_report_delay_ms_mean'])} | {fmt(r['mean_retries_per_frame_mean'],4)} | {fmt(r['mean_csma_cycles_per_frame_mean'],4)} | {fmt(r['access_fail_per_report_mean'],4)} |")
md += ['', '## Paired central contrasts', '', '| Contrast | Metric | Mean difference | 95% CI | Holm p | dz |', '|---|---|---:|---:|---:|---:|']
for _,r in c5.iterrows():
    md.append(f"| {r['contrast']} | {r['metric_label']} | {fmt(r['mean_diff'],4)} | [{fmt(r['ci_lo'],4)}, {fmt(r['ci_hi'],4)}] | {r['p_holm']:.3g} | {fmt(r['dz'],3)} |")
md += ['', '## Interpretation', '',
'At the central loa, J5 retains a large delivery advantage over J4 and materially reduces delivered-report service delay, retry burden, CSMA/CA access cycles, and channel-access failures. J6 remains close to J5 because both generate three IEEE 802.15.4 data frames per report under this framing. This independently supports the paper\'s attribution that broad contention gains arise mainly from source-traffic reduction rather than relevance-directed source mapping.','',
'Absolute ns-3 values are not expected to equal the paper\'s earlier contention abstraction because this experiment uses the ns-3 LR-WPAN MAC/PHY implementation, built-in ACK/retry timing, a controlled one-hop contention domain, and an IEEE 802.15.4 frame-size ceiling. The validation target is robustness of the causal direction under an independent protocol stack, not numerical reproduction of the abstraction.','',
'## Claim boundary','',
'This experiment supports an executed ns-3.47 IEEE 802.15.4/LR-WPAN contention-validation claim. It does not constitute physical-hardware validation, a complete emulation of the paper\'s multihop clustering/routing dynamics, or a radio-energy validation. The ns-3 LR-WPAN module does not provide the paper\'s full radio-energy ledger; therefore energy outcomes remain sourced from the original simulator and analytical sensitivities.']
(RES/'NS3_VALIDATION_REPORT.md').write_text('\n'.join(md)+'\n')

manifest={
 'ns3_version':'3.47','build_profile':'optimized','architecture':'arm64','runs_completed':int(len(df)),
 'seeds':sorted(map(int,df.seed.unique())),'report_periods_s':sorted(map(float,df.report_period_s.unique())),
 'modes':['J4','J5','J6'],'primary_period_s':5.0,
 'scenario_source':'ns-3.47/scratch/j4j5j6-lrwpan-validation.cc',
 'raw_results':str(CSV),'analysis_script':'analyze_ns3_validation.py',
 'claim_boundary':'Independent ns-3 LR-WPAN contention validation; not physical hardware and not full multihop reproduction.'}
(RES/'NS3_EXECUTION_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(summary.to_string(index=False))
print('\nCENTRAL CONTRASTS\n',c5[['contrast','metric','mean_diff','ci_lo','ci_hi','p_holm','dz']].to_string(index=False))
