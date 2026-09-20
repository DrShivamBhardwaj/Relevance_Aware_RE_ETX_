import csv
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parent
FINAL=ROOT/'figures/final'
FINAL.mkdir(parents=True,exist_ok=True)
MAIN=['resource','resource_adaptive','fedcg_adapted','proposed_fixed_comp','proposed']
LABELS=['Resource','Resource+adapt.','FedCG-adapt.','Proposed fixed','Proposed']


def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))

def save(fig,path):
    fig.savefig(path,bbox_inches='tight',dpi=600)
    plt.close(fig)

def c09(path):
    return {r['method']:r for r in read(path) if abs(float(r['correlation'])-.9)<1e-12}

def intel():
    by=c09(ROOT/'results/intel_lab/aggregate_summary.csv')
    fig,axs=plt.subplots(1,3,figsize=(12,3.7))
    vals=[float(by[m]['rmse_c_mean']) for m in MAIN]
    err=[float(by[m]['rmse_c_ci95']) for m in MAIN]
    axs[0].bar(range(len(MAIN)),vals,yerr=err,capsize=2)
    axs[0].set_ylabel('RMSE (°C)');axs[0].set_title('Learning error')
    vals=[float(by[m]['effective_bits_mean'])/1e6 for m in MAIN]
    err=[float(by[m]['effective_bits_ci95'])/1e6 for m in MAIN]
    axs[1].bar(range(len(MAIN)),vals,yerr=err,capsize=2)
    axs[1].set_ylabel('Effective traffic (Mbit)');axs[1].set_title('Communication')
    vals=[float(by[m]['utility_target_js_mean']) for m in MAIN]
    err=[float(by[m]['utility_target_js_ci95']) for m in MAIN]
    axs[2].bar(range(len(MAIN)),vals,yerr=err,capsize=2)
    axs[2].set_ylabel('Utility-target JS');axs[2].set_title('Target alignment')
    for ax in axs:
        ax.set_xticks(range(len(MAIN)),LABELS,rotation=35,ha='right');ax.grid(axis='y',alpha=.25)
    fig.suptitle('Intel Berkeley Lab WSN — held-out evaluation, c = 0.9')
    fig.tight_layout()
    save(fig,FINAL/'07_intel_berkeley_results.png')

def har():
    by=c09(ROOT/'results/uci_har/aggregate_summary.csv')
    fig,axs=plt.subplots(1,3,figsize=(12,3.7))
    vals=[100*float(by[m]['accuracy_mean']) for m in MAIN]
    err=[100*float(by[m]['accuracy_ci95']) for m in MAIN]
    axs[0].bar(range(len(MAIN)),vals,yerr=err,capsize=2)
    axs[0].set_ylabel('Accuracy (%)');axs[0].set_title('Blocked holdout accuracy')
    vals=[float(by[m]['effective_bits_mean'])/1e6 for m in MAIN]
    err=[float(by[m]['effective_bits_ci95'])/1e6 for m in MAIN]
    axs[1].bar(range(len(MAIN)),vals,yerr=err,capsize=2)
    axs[1].set_ylabel('Effective traffic (Mbit)');axs[1].set_title('Communication')
    vals=[float(by[m]['utility_target_js_mean']) for m in MAIN]
    err=[float(by[m]['utility_target_js_ci95']) for m in MAIN]
    axs[2].bar(range(len(MAIN)),vals,yerr=err,capsize=2)
    axs[2].set_ylabel('Utility-target JS');axs[2].set_title('Target alignment')
    for ax in axs:
        ax.set_xticks(range(len(MAIN)),LABELS,rotation=35,ha='right');ax.grid(axis='y',alpha=.25)
    fig.suptitle('UCI HAR — overlap-safe held-out evaluation, c = 0.9')
    fig.tight_layout()
    save(fig,FINAL/'06_uci_har_results.png')

def ablation():
    irows={r['variant']:r for r in read(ROOT/'results/intel_lab/ablation_summary.csv')}
    hrows={r['variant']:r for r in read(ROOT/'results/uci_har/ablation_summary.csv')}
    variants=['proposed','proposed_no_rep','proposed_fixed_comp','proposed_no_relay']
    labels=['Full','No deficit','Fixed 50%','No relay']
    fig,axs=plt.subplots(2,2,figsize=(9.5,7))
    axs[0,0].bar(range(4),[float(irows[v]['effective_bits_mean'])/1e6 for v in variants]);axs[0,0].set_ylabel('Intel traffic (Mbit)')
    axs[0,1].bar(range(4),[float(irows[v]['utility_target_js_mean']) for v in variants]);axs[0,1].set_ylabel('Intel utility-target JS')
    axs[1,0].bar(range(4),[float(hrows[v]['effective_bits_mean'])/1e6 for v in variants]);axs[1,0].set_ylabel('HAR traffic (Mbit)')
    axs[1,1].bar(range(4),[100*float(hrows[v]['accuracy_mean']) for v in variants]);axs[1,1].set_ylabel('HAR accuracy (%)')
    for ax in axs.flat:
        ax.set_xticks(range(4),labels,rotation=25,ha='right');ax.grid(axis='y',alpha=.25)
    fig.suptitle('Component ablation on held-out evaluation seeds')
    fig.tight_layout()
    save(fig,FINAL/'04_ablation.png')

def tradeoff():
    cases=[('Intel',ROOT/'results/intel_lab/aggregate_summary.csv','rmse_c_mean','RMSE (°C)',False),
           ('UCI HAR',ROOT/'results/uci_har/aggregate_summary.csv','accuracy_mean','Accuracy (%)',True)]
    fig,axs=plt.subplots(1,2,figsize=(9.5,4.0))
    for ax,(title,path,key,ylabel,percent) in zip(axs,cases):
        by=c09(path)
        for m,label in zip(MAIN,LABELS):
            x=float(by[m]['effective_bits_mean'])/1e6
            y=float(by[m][key])*(100 if percent else 1)
            s=55+500*float(by[m]['max_relay_energy_j_mean'])/(max(float(by[z]['max_relay_energy_j_mean']) for z in MAIN)+1e-12)
            ax.scatter([x],[y],s=s,alpha=.8);ax.annotate(label,(x,y),xytext=(5,4),textcoords='offset points',fontsize=7)
        ax.set_xlabel('Effective traffic (Mbit)');ax.set_ylabel(ylabel);ax.set_title(title);ax.grid(alpha=.25)
    fig.suptitle('Held-out learning–communication trade-off; marker size ∝ max relay energy')
    fig.tight_layout()
    save(fig,FINAL/'05_learning_communication_tradeoff.png')

def ns3():
    rows=read(ROOT/'validation/ns3_47_hfl/results/ns3_group_summary.csv')
    methods=['random','resource','utility','proposed']; labels=['Random','Resource','Utility','Proposed']
    conds=['dense_nominal','scale_nominal']
    fig,axs=plt.subplots(1,2,figsize=(8.5,3.8))
    x=np.arange(len(conds));width=.18
    for j,(m,label) in enumerate(zip(methods,labels)):
        vals=[];delay=[]
        for c in conds:
            r=next(z for z in rows if z['mapping']=='hop' and z['condition']==c and z['method']==m)
            vals.append(float(r['report_rdr_pct_mean']));delay.append(float(r['mean_delivered_report_delay_ms_mean']))
        axs[0].bar(x+(j-1.5)*width,vals,width,label=label)
        axs[1].bar(x+(j-1.5)*width,delay,width,label=label)
    axs[0].set_ylabel('Report delivery ratio (%)');axs[1].set_ylabel('Delivered-report delay (ms)')
    for ax in axs:
        ax.set_xticks(x,['Dense nominal','24-sensor nominal']);ax.grid(axis='y',alpha=.25)
    axs[0].legend(fontsize=7)
    fig.suptitle('ns-3.47 LR-WPAN replay — hop-equivalent held-out traffic')
    fig.tight_layout()
    save(fig,FINAL/'03_ns3_validation.png')

if __name__=='__main__':
    intel();har();ablation();tradeoff();ns3();print('updated held-out result figures in',FINAL)
