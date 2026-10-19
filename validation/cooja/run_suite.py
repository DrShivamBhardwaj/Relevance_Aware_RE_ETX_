#!/usr/bin/env python3
"""Generate, execute, and audit isolated Cooja runs. No simulated output is fabricated."""
import argparse
import collections
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

from patch_mrhof import patch
HERE=Path(__file__).resolve().parent
DESIGN=json.loads((HERE/'design.json').read_text())
MODES={'adaptive':0,'full':1,'shuffled':2,'balanced':3,'temporal_matched':4,'full_without_context':1,
       'adaptive_etx_replay':2,'shuffled_etx_replay':2,'rd_local':5,'rd_shuffled':2}
PATTERN=re.compile(r'(META|TX|RX|ACT|BAD_CODEC|BAD|NO_ROUTE|DONE),[^\r\n]*')


def schedule_for(records,nodes,rounds,seed,policy):
    """Exact offered-size multiset for shuffling and temporal matching.

    This is an offline replay control, explicitly not an online distributed policy.
    """
    out=[[0]*(nodes+2) for _ in range(rounds)]
    rng=random.Random(seed+6000003)
    by_round=collections.defaultdict(dict)
    for row in records:
        by_round[int(row['round'])][int(row['node'])]=row
    for r in range(rounds):
        observed=by_round[r]
        if set(observed)!=set(range(2,nodes+2)):
            raise ValueError(f'Incomplete adaptive trace at round {r}')
        ids=list(range(2,nodes+2))
        depths=[int(observed[i]['bits']) for i in ids]
        if policy=='shuffled':
            rng.shuffle(depths)
            for i,b in zip(ids,depths):out[r][i]=b
        elif policy=='temporal_matched':
            ids.sort(key=lambda i:(int(observed[i]['zt']),i))
            for i,b in zip(ids,sorted(depths)):out[r][i]=b
        elif policy=='balanced':
            units=sum(depths)//4
            low,extra=divmod(units,nodes)
            rng.shuffle(ids)
            for k,i in enumerate(ids):out[r][i]=4*(low+(k<extra))
        else:raise ValueError(policy)
        if sum(out[r])!=sum(depths):raise AssertionError('Report budget changed')
        if policy!='balanced' and sorted(out[r][i] for i in ids)!=sorted(depths):
            raise AssertionError('Payload multiset changed')
        if r<10 and any(out[r][i]!=16 for i in ids):raise AssertionError('Warm-up mismatch')
    return out


def positions(nodes,seed):
    side=math.ceil(math.sqrt(nodes))
    xy={1:((side-1)*10,side*20+10)}
    rng=random.Random(seed)
    for k,i in enumerate(range(2,nodes+2)):
        # Small fixed jitter avoids many artificial equal-cost ties; spacing is retained.
        xy[i]=((k%side)*20+rng.randint(-2,2),(k//side)*20+rng.randint(-2,2))
    return xy


def make_config(folder,contiki,case,policy,replay=None):
    folder.mkdir(parents=True,exist_ok=True)
    for name in ['allocation.c','codec.c','codec.h','Makefile','project-conf.h']:
        shutil.copy2(HERE/name,folder/name)
    n=case['nodes'];rounds=case['rounds'];xy=positions(n,case['seed'])
    values={
        'NODES':n,'ROUNDS':rounds,'SEED':case['seed'],'PERIOD':case['period'],
        'SCENARIO':case['scenario'],'AMPLITUDE':case['amplitude'],
        'MODE':MODES[policy],'BEACONS':int(case.get('beacons',True)),
        'FAILURES':int(case.get('failures',False)),
        'ENERGY_AWARE':int(not policy.endswith('_etx_replay'))}
    text='/* Generated immutable run input, not research output. */\n'
    for key,value in values.items():text+=f'#define STUDY_{key} {value}\n'
    for axis,j in [('x',0),('y',1)]:
        vals=[0]+[xy[i][j] for i in range(1,n+2)]
        text+=f'static const int study_{axis}[STUDY_NODES+2] = {{'+','.join(map(str,vals))+'};\n'
    if replay is None:replay=[[16]*(n+2) for _ in range(rounds)]
    text+='static const unsigned char study_schedule[STUDY_ROUNDS][STUDY_NODES+2] = {\n'
    text+=',\n'.join('{'+','.join(map(str,row))+'}' for row in replay)+'\n};\n'
    (folder/'generated.h').write_text(text)
    # Reuse the interface definitions from the pinned upstream native-mote test.
    template=ET.parse(contiki/'tests/07-simulation-base/08-ipv6-unicast.csc')
    interfaces=[el.text.strip() for el in template.findall('.//motetype')[0].findall('moteinterface')]
    root=ET.Element('simconf',version='2022112801');sim=ET.SubElement(root,'simulation')
    ET.SubElement(sim,'title').text=f'Payload allocation {policy} seed {case["seed"]}'
    ET.SubElement(sim,'randomseed').text=str(case['seed'])
    ET.SubElement(sim,'motedelay_us').text='0'
    radio=ET.SubElement(sim,'radiomedium');radio.text='org.contikios.cooja.radiomediums.UDGM'
    for key,value in [('transmitting_range',34),('interference_range',68),('success_ratio_tx',1),('success_ratio_rx',case.get('prr',.98))]:ET.SubElement(radio,key).text=str(value)
    typ=ET.SubElement(sim,'motetype');typ.text='org.contikios.cooja.contikimote.ContikiMoteType'
    ET.SubElement(typ,'identifier').text='allocation'
    ET.SubElement(typ,'description').text='Progressive source with live context'
    ET.SubElement(typ,'source').text=str(folder/'allocation.c')
    ET.SubElement(typ,'commands').text=f'make -j2 allocation.cooja TARGET=cooja CONTIKI={contiki} STUDY_ROUTING={values["ENERGY_AWARE"]}'
    for value in interfaces:ET.SubElement(typ,'moteinterface').text=value
    for i,(x,y) in xy.items():
        mote=ET.SubElement(typ,'mote')
        config=ET.SubElement(mote,'interface_config');config.text='org.contikios.cooja.interfaces.Position'
        ET.SubElement(config,'pos',x=str(x),y=str(y))
        config=ET.SubElement(mote,'interface_config');config.text='org.contikios.cooja.contikimote.interfaces.ContikiMoteID'
        ET.SubElement(config,'id').text=str(i)
    plugin=ET.SubElement(root,'plugin');plugin.text='org.contikios.cooja.plugins.ScriptRunner'
    config=ET.SubElement(plugin,'plugin_config')
    timeout=(60+(rounds+3)*case['period'])*1000
    script=f'''TIMEOUT({timeout});
var done = 0;
while(true) {{
  log.log(time + ":" + id + ":" + msg + "\\n");
  if(msg.indexOf("DONE,") == 0) {{ done++; if(done == {n+1}) GENERATE_MSG({case['period']*1000}, "STUDY_DRAIN"); }}
  if(msg.equals("STUDY_DRAIN")) log.testOK();
  YIELD();
}}'''
    ET.SubElement(config,'script').text=script;ET.SubElement(config,'active').text='true'
    ET.indent(root)
    ET.ElementTree(root).write(folder/'simulation.csc',encoding='UTF-8',xml_declaration=True)
    return values


def parse_log(text,nodes,rounds,period):
    tx={};rx={};activity={};clock=None
    for match in PATTERN.finditer(text):
        p=match.group().split(',');kind=p[0]
        if kind in ['BAD','BAD_CODEC']:raise ValueError('Receiver rejected packet: '+match.group())
        if kind=='META':clock=int(p[4])
        if kind=='TX':
            names=['node','round','bits','bytes','mean','zt','zs','neighbours','zero_sse']
            row=dict(zip(names,map(int,p[1:])));key=(row['node'],row['round'])
            if key in tx and tx[key]!=row:raise ValueError('Conflicting TX records')
            tx[key]=row
        elif kind=='RX':
            names=['node','round','bits','bytes','sse','delay_ticks','hops']
            row=dict(zip(names,map(int,p[1:])));key=(row['node'],row['round'])
            if key not in rx or rx[key]['delay_ticks']>row['delay_ticks']:rx[key]=row
        elif kind=='ACT':
            row=list(map(int,p[1:]));activity[row[0]]=row
    expected={(i,r) for i in range(2,nodes+2) for r in range(rounds)}
    if set(tx)!=expected:raise ValueError(f'Expected {len(expected)} offered reports, observed {len(tx)}')
    for t in tx.values():
        if t['bits'] not in [4,8,12,16] or t['bytes']!=16+250*t['bits']//8 or t['zero_sse']<0:
            raise ValueError('Invalid offered-report accounting')
        if t['round']<10 and t['bits']!=16:raise ValueError('Warm-up depth mismatch')
    if clock is None or clock<=0:raise ValueError('Missing or invalid clock metadata')
    if not set(rx).issubset(expected):raise ValueError('Unknown reports at receiver')
    if set(activity)!=set(range(1,nodes+2)):raise ValueError('Missing activity records')
    if any(a[1]!=rounds or a[6]<=0 or min(a[2:6])<0 for a in activity.values()):
        raise ValueError('Missing final or invalid activity accounting')
    sse=0;delivered=0;delays=[];hops=[];offered=0;app_bytes=0
    for key,t in tx.items():
        if t['round']<10:continue
        offered+=1;app_bytes+=t['bytes']-16
        r=rx.get(key)
        if r is not None and (r['bits']!=t['bits'] or r['bytes']!=t['bytes']):raise ValueError('Encoded packet mismatch')
        if r is not None and (r['sse']<0 or r['delay_ticks']<0 or r['hops']<1):raise ValueError('Invalid receiver accounting')
        if r is not None and r['delay_ticks']<=clock*period:
            sse+=r['sse'];delivered+=1;delays.append(r['delay_ticks']/clock);hops.append(r['hops'])
        else:sse+=t['zero_sse']
    if offered==0:raise ValueError('No evaluation reports after warm-up')
    # Include full-run radio activity and control overhead; never present this as total-device energy.
    tx_s=sum(a[4]/a[6] for i,a in activity.items() if i!=1)
    rx_s=sum(a[5]/a[6] for i,a in activity.items() if i!=1)
    result={'offered_reports':offered,'on_time_delivered':delivered,'on_time_pdr':delivered/offered,
            'receiver_rmse':math.sqrt(sse/(offered*250))/4096,
            'offered_application_bytes':app_bytes,'radio_tx_seconds':tx_s,'radio_listen_seconds':rx_s,
            'nominal_radio_energy_j':3*(.0174*tx_s+.0188*rx_s),
            'mean_delivered_delay_s':sum(delays)/len(delays) if delays else None,
            'mean_delivered_hops':sum(hops)/len(hops) if hops else None,
            'scope':'native Cooja network simulation; full-run nominal radio energy; no CPU/sensing energy or battery-lifetime claim'}
    return list(tx.values()),result


def execute(contiki,out,case,policy,replay,dry_run=False):
    folder=(out/f'{case["name"]}_s{case["seed"]}_{policy}').resolve()
    if (folder/'manifest.json').exists():raise FileExistsError(f'Refusing to overwrite previous run: {folder}')
    values=make_config(folder,contiki,case,policy,replay)
    meta={'case':case,'policy':policy,'definitions':values,'design_sha256':hashlib.sha256((HERE/'design.json').read_bytes()).hexdigest(),
          'study_sources_sha256':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['allocation.c','codec.c','codec.h','project-conf.h','run_suite.py','analyse.py']},
          'status':'configured, not executed','platform':platform.platform(),'python':sys.version}
    (folder/'manifest.json').write_text(json.dumps(meta,indent=2))
    if dry_run:return None,None
    jar=contiki/'tools/cooja/build/libs/cooja.jar'
    if not jar.exists():raise FileNotFoundError('Build the pinned Cooja JAR before running simulations')
    cmd=['java','-Xmx2048m','-XX:-UseCompressedOops','-XX:-UseCompressedClassPointers',
         '--enable-native-access=ALL-UNNAMED','--add-modules=jdk.incubator.foreign',
         '-jar',str(jar),'--no-gui',f'--contiki={contiki}',f'--cooja={contiki}/tools/cooja',
         f'--javac={shutil.which("javac") or HERE/"javac-shim"}',
         f'--logdir={folder}',str(folder/'simulation.csc')]
    meta['command']=cmd
    with (folder/'console.log').open('w') as log:
        run=subprocess.run(cmd,cwd=contiki/'tools/cooja',stdout=log,stderr=subprocess.STDOUT,timeout=600)
    logs='\n'.join(p.read_text(errors='replace') for p in folder.glob('*.testlog'))
    meta['raw_testlogs_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.glob('*.testlog')}
    if run.returncode or 'TEST OK' not in logs:
        meta['status']='failed';(folder/'manifest.json').write_text(json.dumps(meta,indent=2))
        raise RuntimeError(f'Cooja execution failed: {folder}')
    trace,result=parse_log(logs,case['nodes'],case['rounds'],case['period'])
    result.update(seed=case['seed'],case=case['name'],policy=policy)
    meta['status']='executed and accounting checks passed';meta['summary']=result
    (folder/'manifest.json').write_text(json.dumps(meta,indent=2))
    (folder/'summary.json').write_text(json.dumps(result,indent=2))
    with (folder/'offered_trace.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=trace[0]);w.writeheader();w.writerows(trace)
    return trace,result


def main():
    p=argparse.ArgumentParser();p.add_argument('--contiki',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--profile',choices=['smoke','primary','all'],default='smoke')
    p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args();contiki=a.contiki.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if not 0<=a.shard<a.shards:raise ValueError('Invalid shard')
    provenance=patch(contiki);provenance['cooja_commit']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=contiki/'tools/cooja',text=True).strip()
    if provenance['cooja_commit']!='33d41ae9f8acd6075fb903b0bcd5b4122bad8d8f':raise RuntimeError('Cooja revision mismatch')
    provenance['status']='configuration only' if a.dry_run else 'execution requested'
    (out/'provenance.json').write_text(json.dumps(provenance,indent=2))
    seeds=[1001] if a.profile=='smoke' else DESIGN['primary_seeds'][a.shard::a.shards]
    cases=[]
    for seed in seeds:
        cases.append(dict(name='smoke' if a.profile=='smoke' else 'primary',seed=seed,nodes=4 if a.profile=='smoke' else 25,
                          rounds=12 if a.profile=='smoke' else 60,period=10,scenario=0,amplitude=4096))
    if a.profile=='all':
        for seed in DESIGN['primary_seeds'][:4][a.shard::a.shards]:
            for name,kwargs in [('weak',dict(amplitude=512)),('persistent',dict(scenario=1)),('drift',dict(scenario=2)),
                                ('bias',dict(scenario=3)),('outage',dict(failures=True)),('scale100',dict(nodes=100)),('fast',dict(period=5))]:
                c=dict(name=name,seed=seed,nodes=25,rounds=60,period=10,scenario=0,amplitude=4096);c.update(kwargs);cases.append(c)
    summaries=[]
    for case in cases:
        print(f'RUN {case}',flush=True)
        trace,result=execute(contiki,out,case,'adaptive',None,a.dry_run)
        if result:summaries.append(result)
        if a.dry_run:
            # Only adaptive configurations can be generated without actual adaptive traces.
            continue
        rd_trace=None
        for policy in ['shuffled','balanced','full','temporal_matched','full_without_context',
                       'adaptive_etx_replay','shuffled_etx_replay','rd_local','rd_shuffled']:
            replay=None
            if policy=='adaptive_etx_replay':
                replay=[[0]*(case['nodes']+2) for _ in range(case['rounds'])]
                for row in trace:replay[row['round']][row['node']]=row['bits']
            elif policy in ['shuffled','balanced','temporal_matched','shuffled_etx_replay','rd_shuffled']:
                source=rd_trace if policy=='rd_shuffled' else trace
                control=policy if policy in ['balanced','temporal_matched'] else 'shuffled'
                replay=schedule_for(source,case['nodes'],case['rounds'],case['seed'],control)
            run_case=dict(case)
            if policy=='full_without_context':run_case['beacons']=False
            policy_trace,result=execute(contiki,out,run_case,policy,replay)
            if policy=='rd_local':rd_trace=policy_trace
            if result:summaries.append(result)
        (out/'summaries.json').write_text(json.dumps(summaries,indent=2))
    print(f'Completed {len(summaries)} executed runs; dry_run={a.dry_run}',flush=True)

if __name__=='__main__':main()
