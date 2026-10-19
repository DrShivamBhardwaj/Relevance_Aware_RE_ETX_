#!/usr/bin/env python3
"""Analyse executed Cooja manifests. Configuration-only folders are rejected."""
import argparse
import itertools
import json
import math
from pathlib import Path
import numpy as np
from scipy import stats

POLICIES=['adaptive','shuffled','balanced','full','temporal_matched','full_without_context',
          'adaptive_etx_replay','shuffled_etx_replay','rd_local','rd_shuffled']


def holm(values):
    p=np.asarray(values,float)
    if not np.isfinite(p).all():raise ValueError('Non-finite p-values')
    order=np.argsort(p);out=np.empty(len(p))
    out[order]=np.minimum(1,np.maximum.accumulate(p[order]*np.arange(len(p),0,-1)))
    return out


def exact_signflip(d):
    d=np.asarray(d,float);n=len(d)
    if n>20:raise ValueError('Exact enumeration is limited to 20 pairs')
    observed=abs(d.mean());count=0
    for start in range(0,2**n,16384):
        integers=np.arange(start,min(start+16384,2**n),dtype=np.uint32)
        signs=((integers[:,None]>>np.arange(n))&1)*2.0-1.0
        count+=int(np.count_nonzero(abs(signs@d/n)>=observed-1e-14))
    return count/(2**n)


def paired(a,b):
    d=np.asarray(a)-np.asarray(b);n=len(d)
    if n<2 or not np.isfinite(d).all():raise ValueError('Need at least two finite seed pairs')
    sd=float(d.std(ddof=1));mean=float(d.mean());half=stats.t.ppf(.975,n-1)*sd/math.sqrt(n)
    p=1.0 if sd==0 and mean==0 else (0.0 if sd==0 else float(stats.ttest_1samp(d,0).pvalue))
    return dict(n=n,mean_difference=mean,ci95_low=mean-half,ci95_high=mean+half,
                paired_t_p=p,exact_signflip_p=exact_signflip(d),
                cohen_dz=mean/sd if sd else None)


def analyse(folder,minimum_seeds=20):
    records={}
    fingerprints=set()
    for file in Path(folder).rglob('manifest.json'):
        item=json.loads(file.read_text())
        if item.get('status')!='executed and accounting checks passed':continue
        fingerprints.add((item.get('design_sha256'),json.dumps(item.get('study_sources_sha256'),sort_keys=True)))
        r=item['summary'];key=(r['case'],r['seed'],r['policy'])
        if key in records:raise ValueError(f'Duplicate run {key}')
        records[key]=r
    if not records:raise ValueError('No executed Cooja study results; configurations are not evidence')
    if len(fingerprints)!=1:raise ValueError('Mixed study designs or source versions')
    result={'scope':'paired seed-level results; radio energy excludes sensing/CPU and is not hardware measurement','cases':{}}
    for case in sorted({k[0] for k in records}):
        seeds=sorted({k[1] for k in records if k[0]==case})
        required=minimum_seeds if case=='primary' else min(4,minimum_seeds)
        if len(seeds)<max(2,required):raise ValueError(f'{case}: {len(seeds)} seeds; minimum {max(2,required)}')
        for seed in seeds:
            if any((case,seed,p) not in records for p in POLICIES):raise ValueError('Incomplete policy family')
        rows=[]
        for policy in POLICIES[1:]:
            for metric in ['receiver_rmse','on_time_pdr','nominal_radio_energy_j']:
                a=[records[case,s,'adaptive'][metric] for s in seeds]
                b=[records[case,s,policy][metric] for s in seeds]
                row=paired(a,b);row.update(contrast=f'adaptive_minus_{policy}',metric=metric)
                row['role']='primary' if policy=='shuffled' and metric=='receiver_rmse' and case=='primary' else 'secondary_or_exploratory'
                rows.append(row)
        for metric in ['receiver_rmse','on_time_pdr','nominal_radio_energy_j']:
            # Fixed offered schedules across both routing treatments: no online-policy claim for ETX replay.
            allocation=[records[case,s,'adaptive'][metric]-records[case,s,'shuffled'][metric] for s in seeds]
            etx_allocation=[records[case,s,'adaptive_etx_replay'][metric]-records[case,s,'shuffled_etx_replay'][metric] for s in seeds]
            row=paired(allocation,etx_allocation)
            row.update(contrast='allocation_by_routing_interaction',metric=metric,role='secondary_or_exploratory')
            rows.append(row)
            row=paired([records[case,s,'rd_local'][metric] for s in seeds],
                       [records[case,s,'rd_shuffled'][metric] for s in seeds])
            row.update(contrast='rd_local_minus_own_shuffled',metric=metric,role='secondary_or_exploratory')
            rows.append(row)
        secondary=[r for r in rows if r['role']!='primary']
        for r,pt,ps in zip(secondary,holm([r['paired_t_p'] for r in secondary]),holm([r['exact_signflip_p'] for r in secondary])):
            r['holm_t_p']=float(pt);r['holm_signflip_p']=float(ps)
        result['cases'][case]={'seeds':seeds,'tests':rows}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--minimum-seeds',type=int,default=20);a=p.parse_args()
    a.output.write_text(json.dumps(analyse(a.folder,a.minimum_seeds),indent=2,allow_nan=False)+'\n')
