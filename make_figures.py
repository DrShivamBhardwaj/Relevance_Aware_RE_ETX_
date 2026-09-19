import csv
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
FIG=ROOT/'figures'; FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.titlesize':11,'axes.labelsize':10,'legend.fontsize':9})

def read(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))

def save(fig,name):
    fig.tight_layout();fig.savefig(FIG/(name+'.png'),dpi=600,bbox_inches='tight');fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight');plt.close(fig)

def scatter_methods(rows,corr,xkey,ykey,xlabel,ylabel,title,name):
    rows=[r for r in rows if abs(float(r['correlation'])-corr)<1e-9]
    fig,ax=plt.subplots(figsize=(5.6,4.1))
    for r in rows:
        x=float(r[xkey]);y=float(r[ykey]);m=r['method']
        ax.scatter(x,y,s=55)
        ax.annotate(m,(x,y),xytext=(5,4),textcoords='offset points')
    ax.set_xlabel(xlabel);ax.set_ylabel(ylabel);ax.set_title(title);ax.grid(True,alpha=.25)
    save(fig,name)

syn=read(ROOT/'results/aggregate_summary.csv')
scatter_methods(syn,.9,'effective_bits_mean','accuracy_mean','Expected transmitted bits','Accuracy','Synthetic correlated heterogeneity (c=0.9)','fig_synthetic_tradeoff')
intel=read(ROOT/'results/intel_lab/aggregate_summary.csv')
scatter_methods(intel,.9,'effective_bits_mean','rmse_c_mean','Expected transmitted bits','Temperature RMSE (°C)','Intel Lab WSN: communication–error trade-off','fig_intel_tradeoff')
har=read(ROOT/'results/uci_har/aggregate_summary.csv')
scatter_methods(har,.9,'effective_bits_mean','accuracy_mean','Expected transmitted bits','Accuracy','UCI HAR: communication–accuracy trade-off','fig_har_tradeoff')

# Sensitivity: relay pressure coefficient
for ds,label,ykey,ylabel,name in [
 ('intel_lab','Intel Lab','max_relay_energy_j_mean','Maximum relay energy (J)','fig_intel_relay_sensitivity'),
 ('uci_har','UCI HAR','max_relay_energy_j_mean','Maximum relay energy (J)','fig_har_relay_sensitivity')]:
    rows=[r for r in read(ROOT/f'results/{ds}/sensitivity_summary.csv') if r['parameter']=='relay_pressure_weight']
    xs=[float(r['value']) for r in rows];ys=[float(r[ykey]) for r in rows]
    fig,ax=plt.subplots(figsize=(5.6,4.1));ax.plot(xs,ys,marker='o');ax.set_xlabel('Relay-pressure coefficient');ax.set_ylabel(ylabel);ax.set_title(f'{label}: relay-pressure sensitivity');ax.grid(True,alpha=.25);save(fig,name)

# Compression sensitivity: effective bits
for ds,label,name in [('intel_lab','Intel Lab','fig_intel_compression_sensitivity'),('uci_har','UCI HAR','fig_har_compression_sensitivity')]:
    rows=[r for r in read(ROOT/f'results/{ds}/sensitivity_summary.csv') if r['parameter']=='compression_distortion_weight']
    xs=[float(r['value']) for r in rows];ys=[float(r['effective_bits_mean']) for r in rows]
    fig,ax=plt.subplots(figsize=(5.6,4.1));ax.plot(xs,ys,marker='o');ax.set_xlabel('Compression-distortion coefficient β');ax.set_ylabel('Expected transmitted bits');ax.set_title(f'{label}: compression sensitivity');ax.grid(True,alpha=.25);save(fig,name)

# ns-3 dense nominal report delivery and delay as separate plots
ns=read(ROOT/'validation/ns3_47_hfl/results/ns3_group_summary.csv')
rows=[r for r in ns if r['mapping']=='hop' and r['condition']=='dense_nominal']
fig,ax=plt.subplots(figsize=(5.6,4.1))
for r in rows:
    ax.scatter(float(r['mapped_payload_bits']),float(r['report_rdr_pct_mean']),s=55);ax.annotate(r['method'],(float(r['mapped_payload_bits']),float(r['report_rdr_pct_mean'])),xytext=(5,4),textcoords='offset points')
ax.set_xlabel('Mapped payload per FL report (bits)');ax.set_ylabel('Report delivery ratio (%)');ax.set_title('ns-3.47 LR-WPAN: dense nominal condition');ax.grid(True,alpha=.25);save(fig,'fig_ns3_rdr')
fig,ax=plt.subplots(figsize=(5.6,4.1))
for r in rows:
    ax.scatter(float(r['mapped_payload_bits']),float(r['mean_delivered_report_delay_ms_mean']),s=55);ax.annotate(r['method'],(float(r['mapped_payload_bits']),float(r['mean_delivered_report_delay_ms_mean'])),xytext=(5,4),textcoords='offset points')
ax.set_xlabel('Mapped payload per FL report (bits)');ax.set_ylabel('Mean delivered-report delay (ms)');ax.set_title('ns-3.47 LR-WPAN: dense nominal condition');ax.grid(True,alpha=.25);save(fig,'fig_ns3_delay')

# HAR ablation representation divergence
abl=read(ROOT/'results/uci_har/ablation_summary.csv')
fig,ax=plt.subplots(figsize=(6.2,4.1));names=[r['variant'].replace('proposed_','') for r in abl];vals=[float(r['representation_js_mean']) for r in abl]
ax.bar(names,vals);ax.set_ylabel('Representation JS divergence');ax.set_title('UCI HAR ablation: representation effect');ax.tick_params(axis='x',rotation=25);ax.grid(True,axis='y',alpha=.25);save(fig,'fig_har_ablation_representation')
print('generated',len(list(FIG.glob('*.png'))),'PNG and',len(list(FIG.glob('*.pdf'))),'PDF figures')
