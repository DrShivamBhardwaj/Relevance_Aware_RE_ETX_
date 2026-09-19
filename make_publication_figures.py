import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True)


def read(path):
    with path.open(newline='') as f: return list(csv.DictReader(f))


def save(fig,name):
    for ext in ('pdf','png'):
        fig.savefig(FIG/f'{name}.{ext}',bbox_inches='tight',dpi=300)
    plt.close(fig)


def main_bars():
    datasets=[('Intel Lab',ROOT/'results/intel_lab/aggregate_summary.csv','rmse_c_mean','RMSE (°C)',True),('UCI HAR',ROOT/'results/uci_har/aggregate_summary.csv','accuracy_mean','Accuracy',False)]
    for title,path,metric,ylabel,lower in datasets:
        rows=[r for r in read(path) if abs(float(r['correlation'])-0.9)<1e-9]
        methods=['random','resource','utility','proposed']
        fig,ax=plt.subplots(figsize=(6.3,3.5)); vals=[float(next(r for r in rows if r['method']==m)[metric]) for m in methods]
        ax.bar(methods,vals)
        ax.set_title(f'{title}: learning performance at correlation 0.9')
        ax.set_ylabel(ylabel); ax.grid(axis='y',alpha=.3)
        save(fig,f'{title.lower().replace(" ","_")}_performance_bar')
        fig,ax=plt.subplots(figsize=(6.3,3.5)); vals=[float(next(r for r in rows if r['method']==m)['effective_bits_mean'])/1e6 for m in methods]
        ax.bar(methods,vals); ax.set_title(f'{title}: effective communication at correlation 0.9')
        ax.set_ylabel('Effective bits (million)'); ax.grid(axis='y',alpha=.3)
        save(fig,f'{title.lower().replace(" ","_")}_communication_bar')
        fig,ax=plt.subplots(figsize=(6.3,3.5)); vals=[float(next(r for r in rows if r['method']==m)['representation_js_mean']) for m in methods]
        ax.bar(methods,vals); ax.set_title(f'{title}: representation divergence')
        ax.set_ylabel('JS divergence'); ax.grid(axis='y',alpha=.3)
        save(fig,f'{title.lower().replace(" ","_")}_representation_bar')


def sensitivity_plots():
    rows=read(ROOT/'results/sensitivity/sensitivity_grid.csv')
    for dataset in ['intel_lab','uci_har']:
        sub=[r for r in rows if r['dataset']==dataset]
        for metric,label in [('effective_bits_mean','Effective bits'),('representation_js_mean','Representation JS'),('max_relay_energy_j_mean','Max relay energy')]:
            fig,ax=plt.subplots(figsize=(6.8,4.0))
            xs=sorted({float(r['relay_pressure_weight']) for r in sub})
            betas=sorted({float(r['compression_distortion_weight']) for r in sub})
            for beta in betas:
                ys=[]
                for x in xs:
                    r=next(z for z in sub if abs(float(z['relay_pressure_weight'])-x)<1e-9 and abs(float(z['compression_distortion_weight'])-beta)<1e-9)
                    y=float(r[metric])
                    if 'bits' in metric: y/=1e6
                    ys.append(y)
                ax.plot(xs,ys,marker='o',label=f'beta={beta}')
            ax.set_xlabel('Relay-pressure weight'); ax.set_ylabel(label + (' (M)' if 'bits' in metric else ''))
            ax.set_title(f'{dataset}: sensitivity of {label}')
            ax.grid(alpha=.3); ax.legend(fontsize=8)
            save(fig,f'{dataset}_{metric}_sensitivity')


def pareto():
    for dataset,path,perf_metric,perf_label in [('intel_lab',ROOT/'results/intel_lab/aggregate_summary.csv','rmse_c_mean','RMSE (lower)'),('uci_har',ROOT/'results/uci_har/aggregate_summary.csv','accuracy_mean','Accuracy')]:
        rows=[r for r in read(path) if abs(float(r['correlation'])-.9)<1e-9]
        fig,ax=plt.subplots(figsize=(5.5,4))
        for r in rows:
            ax.scatter(float(r['effective_bits_mean'])/1e6,float(r[perf_metric]),s=80)
            ax.annotate(r['method'],(float(r['effective_bits_mean'])/1e6,float(r[perf_metric])),xytext=(5,5),textcoords='offset points')
        ax.set_xlabel('Effective bits (million)'); ax.set_ylabel(perf_label)
        ax.set_title(f'{dataset}: communication-performance frontier')
        ax.grid(alpha=.3); save(fig,f'{dataset}_pareto_comm_perf')

if __name__=='__main__':
    main_bars(); sensitivity_plots(); pareto(); print(f'wrote figures to {FIG}')
