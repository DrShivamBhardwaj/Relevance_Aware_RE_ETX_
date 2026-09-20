import csv,math,statistics,sys
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from wsn_hfl.config import EVALUATION_SEEDS, SimConfig
from wsn_hfl.har import simulate_har
METHODS=('proposed','proposed_no_rep','proposed_fixed_comp','proposed_age_only','proposed_no_relay')
SEEDS=EVALUATION_SEEDS

def stats(vals):
 vals=[float(v) for v in vals];m=statistics.fmean(vals);sd=statistics.stdev(vals) if len(vals)>1 else 0.;return m,sd,1.96*sd/math.sqrt(len(vals)) if len(vals)>1 else 0.
def main():
 cfg=replace(SimConfig(),num_clients=30,num_gateways=4,num_classes=6,feature_dim=561,rounds=25,clients_per_round=8,local_steps=1,learning_rate=.02,l2=.001,bandwidth_bps=250000.,round_slot_s=.25,relay_budget_j_per_round=.004)
 rows=[]
 for method in METHODS:
  runs=[simulate_har(method,replace(cfg,seed=s),ROOT/'data/uci_har',.9)[0] for s in SEEDS]
  out={'variant':method,'n':len(runs),'seed_role':'evaluation'}
  for key in ['accuracy','macro_f1','worst_client_accuracy','effective_bits','energy_j','max_relay_energy_j','participation_jain','utility_target_js','class_coverage_js']:
   m,sd,ci=stats([x[key] for x in runs]);out[key+'_mean']=m;out[key+'_sd']=sd;out[key+'_ci95']=ci
  rows.append(out);print(method,'acc',round(out['accuracy_mean'],4),'bits',round(out['effective_bits_mean']),'E',round(out['energy_j_mean'],2),'utilityJS',round(out['utility_target_js_mean'],4),'relay',round(out['max_relay_energy_j_mean'],3))
 p=ROOT/'results/uci_har/ablation_summary.csv'
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
 print('wrote',p)
if __name__=='__main__':main()
