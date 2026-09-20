import csv,math,statistics,sys
from dataclasses import replace
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from wsn_hfl.config import EVALUATION_SEEDS, SimConfig
from wsn_hfl.intel_lab import simulate_intel
METHODS=('proposed','proposed_no_rep','proposed_fixed_comp','proposed_age_only','proposed_no_relay')
SEEDS=EVALUATION_SEEDS

def stats(vals):
 vals=[float(v) for v in vals];m=statistics.fmean(vals);sd=statistics.stdev(vals) if len(vals)>1 else 0.;return m,sd,1.96*sd/math.sqrt(len(vals)) if len(vals)>1 else 0.
def main():
 cfg=replace(SimConfig(),num_clients=54,num_gateways=4,rounds=30,clients_per_round=10,local_steps=1,learning_rate=.01,l2=.01,round_slot_s=.2,relay_budget_j_per_round=.004)
 data=ROOT/'data/intel_lab'; rows=[]
 for method in METHODS:
  runs=[simulate_intel(method,replace(cfg,seed=s),data,.9)[0] for s in SEEDS]
  out={'variant':method,'n':len(runs),'seed_role':'evaluation'}
  for key in ['rmse_c','mae_c','effective_bits','energy_j','max_relay_energy_j','participation_jain','utility_target_js','temperature_coverage_js']:
   m,sd,ci=stats([x[key] for x in runs]);out[key+'_mean']=m;out[key+'_sd']=sd;out[key+'_ci95']=ci
  rows.append(out);print(method,'RMSE',round(out['rmse_c_mean'],4),'bits',round(out['effective_bits_mean']),'E',round(out['energy_j_mean'],3),'utilityJS',round(out['utility_target_js_mean'],4),'relay',round(out['max_relay_energy_j_mean'],4))
 p=ROOT/'results/intel_lab/ablation_summary.csv'
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
 print('wrote',p)
if __name__=='__main__':main()
