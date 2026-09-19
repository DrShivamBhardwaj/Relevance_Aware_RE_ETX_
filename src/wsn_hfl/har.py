from collections import defaultdict
import math
from pathlib import Path

import numpy as np

from .config import SimConfig
from .data import class_coverage, js_divergence
from .model import accuracy, cosine_novelty, local_train, loss_and_grad, macro_f1, topk_compress
from .scheduler import schedule
from .topology import WSNTopology

_HAR_CACHE = {}


def _load_matrix(path):
    return np.loadtxt(path, dtype=float)


def prepare_har(data_dir: Path, split_seed=2026):
    key=(str(Path(data_dir).resolve()),split_seed)
    if key in _HAR_CACHE:
        return _HAR_CACHE[key]
    base=Path(data_dir)/'unpacked'/'UCI HAR Dataset'
    X=np.vstack([_load_matrix(base/'train/X_train.txt'),_load_matrix(base/'test/X_test.txt')])
    y=np.concatenate([np.loadtxt(base/'train/y_train.txt',dtype=int),np.loadtxt(base/'test/y_test.txt',dtype=int)])-1
    subj=np.concatenate([np.loadtxt(base/'train/subject_train.txt',dtype=int),np.loadtxt(base/'test/subject_test.txt',dtype=int)])-1
    rng=np.random.default_rng(split_seed)
    splits={}; train_parts=[]
    for i in range(30):
        idx=np.flatnonzero(subj==i)
        rng.shuffle(idx)
        cut=max(20,int(.8*len(idx))); cut=min(cut,len(idx)-10)
        tr,te=idx[:cut],idx[cut:]
        splits[i]=[X[tr].copy(),y[tr].copy(),X[te].copy(),y[te].copy()]
        train_parts.append(X[tr])
    pooled=np.vstack(train_parts); mean=pooled.mean(axis=0); std=pooled.std(axis=0); std[std<1e-8]=1.0
    for i in splits:
        xtr,ytr,xte,yte=splits[i]
        splits[i]=((xtr-mean)/std,ytr,(xte-mean)/std,yte)
    _HAR_CACHE[key]=(splits,mean,std)
    return _HAR_CACHE[key]


def _norm(x):
    x=np.asarray(x,float); lo,hi=float(x.min()),float(x.max())
    return np.full_like(x,.5) if hi-lo<1e-12 else (x-lo)/(hi-lo)


def _jain(x):
    x=np.asarray(x,float); den=len(x)*float(np.sum(x*x))
    return 1.0 if den<1e-12 else float(np.sum(x)**2/den)


def _charge_path(cfg, topology, route, bits, residual_energy, relay_energy):
    spent=0.0
    for u,v in zip(route.nodes[:-1],route.nodes[1:]):
        if v<topology.n: etx=float(topology.sensor_etx[u,v])
        else: etx=float(topology.gateway_etx[u,v-topology.n])
        if u<topology.n:
            tx=bits*cfg.tx_energy_per_bit_j*etx; residual_energy[u]-=tx; spent+=tx
            if u!=route.nodes[0]: relay_energy[u]+=tx
        if v<topology.n:
            rx=bits*cfg.rx_energy_per_bit_j*etx; residual_energy[v]-=rx; spent+=rx; relay_energy[v]+=rx
    np.maximum(residual_energy,0.0,out=residual_energy)
    return spent


def evaluate_clients(w,splits,num_classes):
    allx=[]; ally=[]; ca=[]
    for xtr,ytr,xte,yte in splits.values():
        allx.append(xte); ally.append(yte); ca.append(accuracy(w,xte,yte))
    X=np.vstack(allx); Y=np.concatenate(ally); ca=np.asarray(ca)
    return {
        'accuracy':accuracy(w,X,Y),'macro_f1':macro_f1(w,X,Y,num_classes),
        'worst_client_accuracy':float(ca.min()),'p10_client_accuracy':float(np.quantile(ca,.1)),
        'client_accuracy_sd':float(ca.std()),
    }


def simulate_har(method: str, cfg: SimConfig, data_dir: Path, correlation=0.5):
    rng=np.random.default_rng(cfg.seed)
    splits,_,_=prepare_har(data_dir)
    topology=WSNTopology(cfg,rng)
    initial=rng.uniform(cfg.energy_initial_j-cfg.energy_jitter,cfg.energy_initial_j+cfg.energy_jitter,size=cfg.num_clients)
    residual=initial.copy(); init_routes=topology.all_routes(residual,initial)
    w=np.zeros((561+1,6),dtype=float)

    # Natural subject rarity: feature-centroid deviation + label-distribution deviation.
    global_cent=np.mean(np.vstack([v[0] for v in splits.values()]),axis=0)
    global_label=np.mean(np.vstack([np.bincount(v[1],minlength=6)/len(v[1]) for v in splits.values()]),axis=0)
    rarity=np.zeros(cfg.num_clients); client_probs=np.zeros((cfg.num_clients,6))
    for i,(xtr,ytr,_,_) in splits.items():
        p=np.bincount(ytr,minlength=6).astype(float); p/=p.sum(); client_probs[i]=p
        rarity[i]=np.linalg.norm(xtr.mean(axis=0)-global_cent)/math.sqrt(xtr.shape[1]) + js_divergence(p+1e-9,global_label+1e-9)
    rarity=_norm(rarity)
    initial*=1.0-0.35*correlation*rarity; residual=initial.copy()
    avail=np.clip(cfg.availability_prob-0.25*correlation*rarity,.45,.99)

    errbuf=[np.zeros_like(w) for _ in range(cfg.num_clients)]
    util_hist=np.full(cfg.num_clients,.5); deficit=np.zeros(cfg.num_clients); relay_queue=np.zeros(cfg.num_clients); relay_cum=np.zeros(cfg.num_clients)
    participation=np.zeros(cfg.num_clients); influence=np.zeros(cfg.num_clients); target_cum=np.zeros(cfg.num_clients); global_ema=np.zeros_like(w); pending=[]
    total_eff=total_comp=total_raw=total_energy=0.0; total_hops=total_etx=0.0; total_updates=0
    full_bits=cfg.header_bits+w.size*(cfg.model_bits+cfg.index_bits); history=[]
    for t in range(cfg.rounds):
        routes=topology.all_routes(residual,initial)
        losses=np.array([loss_and_grad(w,*splits[i][:2],cfg.l2)[0] for i in range(cfg.num_clients)])
        utility=.55*_norm(losses)+.45*_norm(util_hist)
        target=utility+1e-6; target/=target.sum(); target_cum+=target
        eligible=(residual>.05)&(rng.random(cfg.num_clients)<avail)
        selected,ratios=schedule(method,cfg,rng,eligible,utility,routes,residual,initial,deficit,relay_queue)
        share=np.zeros(cfg.num_clients)
        if selected: share[selected]=1.0/len(selected)
        deficit=np.maximum(0.0,deficit+target-share); relay_round=np.zeros(cfg.num_clients)
        for i in selected:
            participation[i]+=1; xtr,ytr,_,_=splits[i]
            train_e=cfg.local_steps*cfg.local_step_energy_j; residual[i]=max(0.0,residual[i]-train_e); total_energy+=train_e
            upd,before,after=local_train(w,xtr,ytr,cfg.local_steps,cfg.learning_rate,cfg.l2)
            novelty=cosine_novelty(upd,global_ema); improve=max(before-after,0.0); imp=1.0-math.exp(-4.0*improve)
            actual=float(np.clip(.55*novelty+.45*imp,0,1)); util_hist[i]=cfg.utility_ema*util_hist[i]+(1-cfg.utility_ema)*actual
            rho=float(ratios.get(i,cfg.fixed_compression_ratio)); comp,newres,k=topk_compress(upd,rho,errbuf[i]); errbuf[i]=newres
            bits=cfg.header_bits+k*(cfg.model_bits+cfg.index_bits); route=routes[i]
            total_comp+=bits; total_raw+=full_bits; total_eff+=bits*route.etx_sum; total_hops+=route.hops; total_etx+=route.etx_sum; total_updates+=1
            total_energy+=_charge_path(cfg,topology,route,bits,residual,relay_round)
            latency=cfg.local_steps*.012+route.hops*cfg.base_hop_delay_s+bits*route.etx_sum/cfg.bandwidth_bps
            delay=int(min(cfg.max_staleness,max(0,math.floor(latency/cfg.round_slot_s))))
            if rng.random()>=cfg.dropout_prob:
                pending.append({'arrival':t+delay,'generated':t,'gateway':route.gateway,'client':i,'update':comp,'utility':actual,'samples':len(ytr)})
        relay_cum+=relay_round; relay_queue=np.maximum(0.0,relay_queue+relay_round-cfg.relay_budget_j_per_round)
        arrivals=[e for e in pending if e['arrival']<=t]; pending=[e for e in pending if e['arrival']>t]; by_g=defaultdict(list)
        for e in arrivals:
            if t-e['generated']<=cfg.max_staleness: by_g[e['gateway']].append(e)
        edge_delta=[]; edge_weight=[]; accepted=[]
        for g,events in by_g.items():
            rw=[]
            for e in events:
                age=t-e['generated']; a=math.exp(-cfg.staleness_lambda*age)
                if method.startswith('proposed') and method != 'proposed_age_only': a*=1.0+cfg.utility_staleness_mu*e['utility']
                rw.append(a*e['samples'])
            rw=np.asarray(rw,float)
            if rw.sum()<=0: continue
            nw=rw/rw.sum(); edge_delta.append(sum(a*e['update'] for a,e in zip(nw,events))); edge_weight.append(float(rw.sum())); accepted.extend((float(a),e) for a,e in zip(nw,events))
        if edge_delta:
            ew=np.asarray(edge_weight); ew/=ew.sum(); cloud=sum(a*d for a,d in zip(ew,edge_delta)); w+=cloud; global_ema=.7*global_ema+.3*cloud
            for a,e in accepted: influence[e['client']]+=a
        m=evaluate_clients(w,splits,6); cov=class_coverage(client_probs,influence+1e-9)
        history.append({'round':t+1,'method':method,'correlation':correlation,**m,'effective_bits':total_eff,'energy_j':total_energy,'representation_js':js_divergence(influence+1e-9,target_cum+1e-9),'class_coverage_js':js_divergence(cov,client_probs.mean(axis=0)),'participation_jain':_jain(participation),'max_relay_energy_j':float(relay_cum.max())})
    m=evaluate_clients(w,splits,6); cov=class_coverage(client_probs,influence+1e-9)
    return {'method':method,'seed':cfg.seed,'correlation':correlation,**m,'effective_bits':total_eff,'compressed_bits':total_comp,'raw_selected_bits':total_raw,'mean_selected_hops':total_hops/max(total_updates,1),'mean_selected_etx':total_etx/max(total_updates,1),'energy_j':total_energy,'min_residual_energy_j':float(residual.min()),'max_relay_energy_j':float(relay_cum.max()),'participation_jain':_jain(participation),'representation_js':js_divergence(influence+1e-9,target_cum+1e-9),'class_coverage_js':js_divergence(cov,client_probs.mean(axis=0))},history
