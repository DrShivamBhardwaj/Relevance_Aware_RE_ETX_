#!/usr/bin/env python3
"""Publication figures from completed, independently audited Cooja evidence."""
import argparse,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import t

p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--analysis',type=Path,required=True);p.add_argument('--audit',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
analysis=json.loads(a.analysis.read_text());audit=json.loads(a.audit.read_text())
records={}
for file in a.folder.rglob('manifest.json'):
 d=json.loads(file.read_text())
 if d.get('status')=='executed and accounting checks passed':
  r=d['summary'];records[r['case'],r['seed'],r['policy']]=r
seeds=analysis['cases']['primary']['seeds']
if len(seeds)!=20:raise ValueError('Figures require the full twenty-seed primary study')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.linewidth':.8,'svg.fonttype':'none','pdf.fonttype':42,'ps.fonttype':42})
colours=['#2A6F97','#D56B26','#7B8794','#6A4C93']
def save(fig,name):
 fig.savefig(a.output/(name+'.svg'),bbox_inches='tight')
 fig.savefig(a.output/(name+'.pdf'),bbox_inches='tight')
 fig.savefig(a.output/(name+'.eps'),bbox_inches='tight')
 fig.savefig(a.output/(name+'.png'),dpi=600,bbox_inches='tight');plt.close(fig)

policies=['adaptive','shuffled','balanced','rd_local','full']
labels=['Relevance','Shuffled','Balanced','Local RD','Full']
fig,axes=plt.subplots(1,3,figsize=(10.5,3.25),layout='constrained')
for ax,metric,title in zip(axes,['receiver_rmse','on_time_pdr','nominal_radio_energy_j'],['(a) Receiver RMSE','(b) On-time delivery','(c) Nominal radio energy']):
 values=np.array([[records['primary',s,policy][metric] for s in seeds] for policy in policies])
 for k,row in enumerate(values):
  jitter=np.linspace(-.12,.12,len(row));ax.scatter(k+jitter,row,s=14,facecolor='white',edgecolor='#52616B',linewidth=.65,zorder=2)
  mean=row.mean();ci=t.ppf(.975,len(row)-1)*row.std(ddof=1)/np.sqrt(len(row))
  ax.errorbar(k,mean,yerr=ci,fmt='o',color='#202020',capsize=4,markersize=4,zorder=4)
 ax.set_xticks(range(len(labels)),labels,rotation=35,ha='right');ax.set_title(title,loc='left',fontsize=11)
 if metric=='nominal_radio_energy_j':ax.set_ylim(bottom=0)
 ax.set_ylabel({'receiver_rmse':'Signal units','on_time_pdr':'Proportion of offered reports','nominal_radio_energy_j':'J, radio model only'}[metric]);ax.grid(axis='y',alpha=.17)
save(fig,'cooja_primary_outcomes')

rows=analysis['cases']['primary']['tests']
choices=[('adaptive_minus_shuffled','Relevance minus shuffled'),('adaptive_minus_balanced','Relevance minus balanced'),('adaptive_minus_temporal_matched','Relevance minus temporal'),('adaptive_minus_rd_local','Relevance minus local RD'),('allocation_by_routing_interaction','Allocation by routing interaction')]
fig,ax=plt.subplots(figsize=(7,3.6),layout='constrained')
for y,(key,label) in enumerate(choices):
 row=next(r for r in rows if r['contrast']==key and r['metric']=='receiver_rmse')
 m=row['mean_difference'];ax.errorbar(m,y,xerr=[[m-row['ci95_low']],[row['ci95_high']-m]],fmt='o',capsize=4,color='#2A6F97')
ax.axvline(0,color='#444444',ls='--',lw=1);ax.set_yticks(range(len(choices)),[x[1] for x in choices]);ax.invert_yaxis();ax.set_xlabel('Paired RMSE difference with 95% interval, signal units');ax.grid(axis='x',alpha=.17)
save(fig,'cooja_paired_effects')

lookup={(r['case'],r['seed'],r['policy']):r for r in audit['results']}
fig,ax=plt.subplots(figsize=(7,3.4),layout='constrained')
for i,policy in enumerate(['adaptive','shuffled','rd_local','full']):
 vals=np.array([[lookup['primary',s,policy][k] for s in seeds] for k in ['receiver_rmse','hold_receiver_rmse']])
 for j,estimate in enumerate(['Zero on missing','Hold on missing']):
  ax.scatter(np.full(len(seeds),i+(-.13 if j==0 else .13)),vals[j],s=14,alpha=.6,color=colours[j],marker='o' if j==0 else 's',label=estimate if i==0 else None)
  ax.plot(i+(-.13 if j==0 else .13),vals[j].mean(),'_',markersize=13,color='#111111')
reference=np.mean([lookup['primary',s,'adaptive']['no_transmission_zero_rmse'] for s in seeds])
ax.axhline(reference,ls='--',color='#666666',lw=1,label='Always zero reference mean');ax.set_xticks(range(4),['Relevance','Shuffled','Local RD','Full']);ax.set_ylabel('Receiver RMSE, signal units');ax.legend(frameon=False,fontsize=9);ax.grid(axis='y',alpha=.17)
save(fig,'cooja_estimator_sensitivity')
print('Saved three figures in SVG, PDF and 600 dpi PNG')
