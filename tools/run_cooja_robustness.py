#!/usr/bin/env python3
"""Execute only the seven already-declared exploratory cases; no primary reruns."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'validation/cooja'))
import run_suite as rs

p=argparse.ArgumentParser();p.add_argument('--contiki',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--shard',type=int,required=True);a=p.parse_args()
if not 0<=a.shard<4:raise ValueError('Use shard 0..3')
contiki=a.contiki.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
provenance=rs.patch(contiki);provenance['scope']='four seeds per exploratory scenario; primary plan unchanged'
(out/'provenance.json').write_text(json.dumps(provenance,indent=2))
seed=rs.DESIGN['primary_seeds'][a.shard]
for name,kwargs in [('weak',dict(amplitude=512)),('persistent',dict(scenario=1)),('drift',dict(scenario=2)),('bias',dict(scenario=3)),('outage',dict(failures=True)),('scale100',dict(nodes=100)),('fast',dict(period=5))]:
 case=dict(name=name,seed=seed,nodes=25,rounds=60,period=10,scenario=0,amplitude=4096);case.update(kwargs)
 print('RUN',case,flush=True)
 trace,_=rs.execute(contiki,out,case,'adaptive',None)
 rd_trace=None
 for policy in ['shuffled','balanced','full','temporal_matched','full_without_context','adaptive_etx_replay','shuffled_etx_replay','rd_local','rd_shuffled']:
  replay=None
  if policy=='adaptive_etx_replay':
   replay=[[0]*(case['nodes']+2) for _ in range(case['rounds'])]
   for row in trace:replay[row['round']][row['node']]=row['bits']
  elif policy in ['shuffled','balanced','temporal_matched','shuffled_etx_replay','rd_shuffled']:
   replay=rs.schedule_for(rd_trace if policy=='rd_shuffled' else trace,case['nodes'],case['rounds'],seed,policy if policy in ['balanced','temporal_matched'] else 'shuffled')
  c=dict(case)
  if policy=='full_without_context':c['beacons']=False
  rows,_=rs.execute(contiki,out,c,policy,replay)
  if policy=='rd_local':rd_trace=rows
print('Completed 70 exploratory runs',flush=True)
