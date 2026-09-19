import csv
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True)

def read(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))

def save(fig,name):
    for ext in ('pdf','png'): fig.savefig(FIG/f'{name}.{ext}',bbox_inches='tight',dpi=300)
    plt.close(fig)

def bars():
    cases=[('Intel Lab',ROOT/'results/intel_lab/aggregate_summary.csv','rmse_c_mean','RMSE (°C)'),('UCI HAR',ROOT/'results/uci_har/aggregate_summary.csv','accuracy_mean','Accuracy')]
    for title,path,metric,ylabel in cases:
        rows=[r for r in read(path) if abs(float(r['correlation'])-.9)<1e-9]; methods=['random','resource','utility','proposed']
        for key,label,suffix,scale in [(metric,ylabel,'performance_bar',1),('effective_bits_mean','Effective bits (million)','communication_bar',1e6),('representation_js_mean','JS divergence','representation_bar',1)]:
            fig,ax=plt.subplots(figsize=(6.3,3.5)); vals=[float(next(r for r in rows if r['method']==m)[key])/scale for m in methods]
            ax.bar(methods,vals); ax.set_title(f'{title}: {label} at correlation 0.9'); ax.set_ylabel(label); ax.grid(axis='y',alpha=.3)
            save(fig,f'{title.lower().replace(" ","_")}_{suffix}')

def sensitivity():
    for dataset in ['intel_lab','uci_har']:
        rows=read(ROOT/f'results/{dataset}/joint_grid.csv')
        for metric,label in [('effective_bits_mean','Effective bits'),('representation_js_mean','Representation JS'),('max_relay_energy_j_mean','Max relay energy')]:
            fig,ax=plt.subplots(figsize=(6.8,4.0)); xs=sorted({float(r['relay_pressure_weight']) for r in rows}); betas=sorted({float(r['compression_distortion_weight']) for r in rows})
            for beta in betas:
                ys=[]
                for x in xs:
                    rr=next(z for z in rows if float(z['relay_pressure_weight'])==x and float(z['compression_distortion_weight'])==beta)
                    y=float(rr[metric]); y=y/1e6 if 'bits' in metric else y; ys.append(y)
                ax.plot(xs,ys,marker='o',label=f'beta={beta}')
            ax.set_xlabel('Relay-pressure coefficient'); ax.set_ylabel(label+(' (million)' if 'bits' in metric else '')); ax.set_title(f'{dataset}: cross-layer sensitivity'); ax.grid(alpha=.3); ax.legend(fontsize=8)
            save(fig,f'{dataset}_{metric}_sensitivity')

def pareto():
    for dataset,path,metric,label in [('intel_lab',ROOT/'results/intel_lab/aggregate_summary.csv','rmse_c_mean','RMSE (°C)'),('uci_har',ROOT/'results/uci_har/aggregate_summary.csv','accuracy_mean','Accuracy')]:
        rows=[r for r in read(path) if abs(float(r['correlation'])-.9)<1e-9]
        fig,ax=plt.subplots(figsize=(5.5,4))
        for rr in rows:
            x=float(rr['effective_bits_mean'])/1e6; y=float(rr[metric]); ax.scatter(x,y,s=75); ax.annotate(rr['method'],(x,y),xytext=(5,5),textcoords='offset points')
        ax.set_xlabel('Effective bits (million)'); ax.set_ylabel(label); ax.set_title(f'{dataset}: communication-learning trade-off'); ax.grid(alpha=.3); save(fig,f'{dataset}_pareto_comm_perf')

def ns3():
    rows=read(ROOT/'validation/ns3_47_hfl/results/ns3_group_summary.csv'); methods=['random','resource','utility','proposed']; conditions=['dense_fast','dense_nominal','scale_nominal']
    for metric,label,name in [('report_rdr_pct_mean','Report delivery ratio (%)','ns3_rdr'),('mean_delivered_report_delay_ms_mean','Mean delivered-report delay (ms)','ns3_delay')]:
        fig,ax=plt.subplots(figsize=(7.2,4.0)); width=.18; pos=list(range(len(conditions)))
        for j,m in enumerate(methods):
            vals=[]
            for c in conditions:
                rr=next(r for r in rows if r['mapping']=='hop' and r['condition']==c and r['method']==m); vals.append(float(rr[metric]))
            ax.bar([x+(j-1.5)*width for x in pos],vals,width=width,label=m)
        ax.set_xticks(pos,conditions); ax.set_ylabel(label); ax.set_title('ns-3.47 LR-WPAN hop-equivalent validation'); ax.grid(axis='y',alpha=.3); ax.legend(fontsize=8); save(fig,name)

def synthetic():
    rows=[r for r in read(ROOT/'results/aggregate_summary.csv') if abs(float(r['correlation'])-.9)<1e-9]
    fig,ax=plt.subplots(figsize=(5.5,4))
    for rr in rows:
        x=float(rr['effective_bits_mean'])/1e6; y=float(rr['accuracy_mean']); ax.scatter(x,y,s=75); ax.annotate(rr['method'],(x,y),xytext=(5,5),textcoords='offset points')
    ax.set_xlabel('Effective bits (million)'); ax.set_ylabel('Accuracy'); ax.set_title('Synthetic correlated heterogeneity: trade-off'); ax.grid(alpha=.3); save(fig,'synthetic_tradeoff')

if __name__=='__main__':
    bars(); sensitivity(); pareto(); ns3(); synthetic(); print(f'wrote final figures to {FIG}')
