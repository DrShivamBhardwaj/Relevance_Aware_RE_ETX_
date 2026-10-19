#!/usr/bin/env python3
"""Independent accounting and declared post-hoc hold-estimator sensitivity.

This does not alter the frozen primary endpoint or control schedules.
"""
import argparse
import csv
import ctypes
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile
from run_suite import positions, PATTERN


def build_observer(directory):
    source=Path(__file__).resolve().parent/'codec.c'
    target=Path(directory)/'codec-observer.so'
    subprocess.run(['gcc','-std=c99','-O2','-shared','-fPIC',str(source),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target))
    lib.study_signal.argtypes=[ctypes.c_uint,ctypes.c_uint,ctypes.c_uint,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_uint,ctypes.POINTER(ctypes.c_int16)]
    coordinates={}
    def signal(case,node,round_index):
        key=case['nodes'],case['seed']
        if key not in coordinates:coordinates[key]=positions(*key)
        block=(ctypes.c_int16*250)();x,y=coordinates[key][node]
        lib.study_signal(node,round_index,case['seed'],x,y,case['amplitude'],case['scenario'],block)
        return list(block)
    return signal


def audit_run(folder,signal):
    item=json.loads((folder/'manifest.json').read_text());case=item['case']
    if item['status']!='executed and accounting checks passed':raise ValueError('Unexecuted run')
    for name,sha in item['raw_testlogs_sha256'].items():
        if hashlib.sha256((folder/name).read_bytes()).hexdigest()!=sha:raise ValueError('Raw log hash mismatch')
    expected=case['nodes']*case['rounds'];tx={};rx={};clock=None
    text='\n'.join(p.read_text() for p in folder.glob('*.testlog'))
    for m in PATTERN.finditer(text):
        p=m.group().split(',')
        if p[0]=='META':clock=int(p[4])
        if p[0]=='TX':tx[int(p[1]),int(p[2])]=list(map(int,p[1:]))
        if p[0]=='RX':
            row=list(map(int,p[1:]));key=tuple(row[:2])
            if key not in rx or row[5]<rx[key][5]:rx[key]=row
    if len(tx)!=expected:raise ValueError('Offered population incomplete')
    zero=hold=always_zero=codec_only=0;delivered=harmful=0
    for node in range(2,case['nodes']+2):
        previous=[0]*250
        for r in range(case['rounds']):
            truth=signal(case,node,r);t=tx[node,r];receipt=rx.get((node,r))
            if sum(x*x for x in truth)!=t[8]:raise ValueError('Observer does not reproduce source truth')
            shift=16-t[2]
            offered_reconstruction=[((((x+32768)>>shift)<<shift)+(1<<(shift-1) if shift else 0)-32768) for x in truth]
            offered_sse=sum((x-y)**2 for x,y in zip(truth,offered_reconstruction))
            on_time=receipt is not None and receipt[5]<=clock*case['period']
            if on_time:
                bits=receipt[2];shift=16-bits
                reconstruction=[((((x+32768)>>shift)<<shift)+(1<<(shift-1) if shift else 0)-32768) for x in truth]
                sse=sum((x-y)**2 for x,y in zip(truth,reconstruction))
                if sse!=receipt[4]:raise ValueError('Observer does not reproduce received SSE')
            else:
                reconstruction=previous
                sse=sum(x*x for x in truth)
            if r>=10:
                zero+=sse;hold+=sum((x-y)**2 for x,y in zip(truth,reconstruction));delivered+=int(on_time)
                always_zero+=t[8];codec_only+=offered_sse;harmful+=int(offered_sse>t[8])
            # Deliberately only accepted on-time blocks update this deadline-aware estimator.
            # Late arrivals do not update it; this is an estimator choice, not universal optimality.
            if on_time:previous=reconstruction
    count=case['nodes']*(case['rounds']-10)
    result=dict(case=case['name'],seed=case['seed'],policy=item['policy'],offered_reports=count,
                receiver_rmse=math.sqrt(zero/(count*250))/4096,
                hold_receiver_rmse=math.sqrt(hold/(count*250))/4096,on_time_pdr=delivered/count,
                no_transmission_zero_rmse=math.sqrt(always_zero/(count*250))/4096,
                offered_codec_only_rmse=math.sqrt(codec_only/(count*250))/4096,
                codec_worse_than_zero_fraction=harmful/count,
                hold_endpoint_role='post-hoc estimator sensitivity; not a second confirmatory primary endpoint')
    for k in ['receiver_rmse','on_time_pdr']:
        if abs(result[k]-item['summary'][k])>1e-12:raise ValueError('Independent accounting mismatch')
    return result,tx


def audit(folder):
    results=[];traces={}
    with tempfile.TemporaryDirectory() as d:
        signal=build_observer(d)
        for file in sorted(Path(folder).rglob('manifest.json')):
            result,trace=audit_run(file.parent,signal);results.append(result)
            traces[result['case'],result['seed'],result['policy']]=trace
    keys=sorted({k[:2] for k in traces})
    for case,seed in keys:
        reference=traces[case,seed,'adaptive'];shuffled=traces[case,seed,'shuffled']
        for r in sorted({k[1] for k in reference}):
            def depths(policy):return sorted(t[2] for (n,rr),t in traces[case,seed,policy].items() if rr==r)
            if depths('adaptive')!=depths('shuffled'):raise ValueError('Executed multiset mismatch')
            for a,b in [('adaptive','adaptive_etx_replay'),('shuffled','shuffled_etx_replay')]:
                if any(t[2]!=traces[case,seed,b][k][2] for k,t in traces[case,seed,a].items()):raise ValueError('Routing ablation changed offered schedule')
            if depths('rd_local')!=depths('rd_shuffled'):raise ValueError('RD multiset mismatch')
    return dict(status='independent source, decoder, denominator, raw-log and executed-control audit passed',runs=len(results),seed_cases=len(keys),results=results)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.write_text(json.dumps(audit(a.folder),indent=2)+'\n')
