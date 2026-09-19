import argparse,csv,math,statistics,sys,time
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from wsn_hfl.config import SimConfig
from wsn_hfl.har import simulate_har
from wsn_hfl.intel_lab import simulate_intel
SEEDS=(7,11,19,23,29,31,37,41,43,47)
RPS=(1.0,2.0,3.0,5.0)
BETAS=(0.1,0.2,0.4)

def msci(vals):
 vals=[float(v) for v in vals];m=statistics.fmean(vals);sd=statistics.stdev(vals) if len(vals)>1 else 0.;return m,sd,1.96*sd/math.sqrt(len(vals)) if len(vals)>1 else 0.
def write(p,rows):
 with p.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset',choices=['intel','har'],required=True);a=ap.parse_args()
 if a.dataset=='intel':
  base=replace(SimConfig(),num_clients=54,num_gateways=4,rounds=30,clients_per_round=10,local_steps=1,learning_rate=.01,l2=.01,round_slot_s=.2,relay_budget_j_per_round=.004)
  fn=lambda c:simulate_intel('proposed',c,ROOT/'data/intel_lab',.9)[0];out=ROOT/'results/intel_lab/joint_grid.csv';metrics=['rmse_c','effective_bits','energy_j','max_relay_energy_j','representation_js','participation_jain']
 else:
  base=replace(SimConfig(),num_clients=30,num_gateways=4,num_classes=6,feature_dim=561,rounds=25,clients_per_round=8,local_steps=1,learning_rate=.02,l2=.001,bandwidth_bps=250000.,round_slot_s=.25,relay_budget_j_per_round=.004)
  fn=lambda c:simulate_har('proposed',c,ROOT/'data/uci_har',.9)[0];out=ROOT/'results/uci_har/joint_grid.csv';metrics=['accuracy','macro_f1','effective_bits','energy_j','max_relay_energy_j','representation_js','participation_jain']
 rows=[];t=time.time()
 for rp in RPS:
  for beta in BETAS:
   runs=[fn(replace(base,seed=s,relay_pressure_weight=rp,compression_distortion_weight=beta)) for s in SEEDS]
   o={'relay_pressure_weight':rp,'compression_distortion_weight':beta,'n':len(runs)}
   for k in metrics:
    m,sd,ci=msci([x[k] for x in runs]);o[k+'_mean']=m;o[k+'_sd']=sd;o[k+'_ci95']=ci
   rows.append(o);print(a.dataset,'rp',rp,'beta',beta)
 out.parent.mkdir(parents=True,exist_ok=True);write(out,rows);print('completed',a.dataset,'in',round(time.time()-t,2),'s')
if __name__=='__main__':main()
