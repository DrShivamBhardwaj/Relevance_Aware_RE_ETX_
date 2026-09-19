import csv
import itertools
import math
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parent
RES=ROOT/'results/intel_lab'
VAL=ROOT/'validation/real_data'


def read_csv(p):
    with p.open(newline='') as f: return list(csv.DictReader(f))


def exact_signflip_p(diffs):
    diffs=[float(d) for d in diffs]
    obs=abs(statistics.fmean(diffs))
    count=0; total=0
    for signs in itertools.product((-1.0,1.0), repeat=len(diffs)):
        m=abs(statistics.fmean(s*d for s,d in zip(signs,diffs)))
        if m >= obs-1e-15: count+=1
        total+=1
    return count/total


def main():
    raw=read_csv(RES/'raw_summary.csv')
    agg=read_csv(RES/'aggregate_summary.csv')
    abl=read_csv(RES/'ablation_summary.csv')
    corr=0.9
    metrics=['rmse_c','mae_c','effective_bits','energy_j','max_relay_energy_j','representation_js']
    proposed={int(r['seed']):r for r in raw if r['method']=='proposed' and float(r['correlation'])==corr}
    contrasts=[]
    for baseline in ['random','resource','utility']:
        base={int(r['seed']):r for r in raw if r['method']==baseline and float(r['correlation'])==corr}
        for metric in metrics:
            diffs=[float(proposed[s][metric])-float(base[s][metric]) for s in sorted(proposed)]
            bmean=statistics.fmean(float(base[s][metric]) for s in sorted(proposed))
            dmean=statistics.fmean(diffs)
            pct=100*dmean/bmean if bmean else 0.0
            contrasts.append({'baseline':baseline,'metric':metric,'n':len(diffs),'proposed_minus_baseline_mean':dmean,'percent_change_vs_baseline':pct,'exact_signflip_p':exact_signflip_p(diffs)})
    with (RES/'paired_contrasts.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(contrasts[0].keys())); w.writeheader(); w.writerows(contrasts)

    def row(method,c): return next(r for r in agg if r['method']==method and abs(float(r['correlation'])-c)<1e-9)
    p=row('proposed',0.9); b=row('resource',0.9)
    def reduction(pk,bk): return 100*(float(b[bk])-float(p[pk]))/float(b[bk])
    report=[
        '# Intel Berkeley Lab real-WSN validation report','',
        '## Dataset and task','',
        'The experiment uses the Intel Berkeley Research Lab deployment: 54 Mica2Dot motes with measured temperature, humidity, light, voltage, physical locations, and aggregate directed connectivity probabilities. The original source is `https://db.csail.mit.edu/labdata/labdata.html`.','',
        'The learning task is **per-mote next-temperature regression**. Each sample uses a 16-step history of temperature, humidity, log-light and voltage (64 input features) to predict the next temperature. Clients are physical motes; four spatially distributed high-connectivity motes (10, 26, 48, 38) are treated as edge gateways. Gateway nodes are not learning clients.','',
        'Measured bidirectional packet-delivery probabilities are converted to ETX-style link costs using `1/(p_uv*p_vu)` when the product is at least 0.01. This is a benchmarking substrate, not a new routing contribution.','',
        '## Experimental design','',
        '- 48 learning clients after gateway exclusion/data sufficiency filtering.',
        '- 30 federated rounds, 10 clients selected per round.',
        '- Four policies: random, resource-only, statistical-utility-only, and proposed cross-layer orchestration.',
        '- Resource-data correlation levels: 0.0, 0.5, 0.9.',
        '- 10 paired random seeds per condition.',
        '- Local model: regularized linear next-temperature predictor; Top-k update sparsification uses error feedback.',
        '',
        '## Main result at correlation = 0.9','',
        '| Method | RMSE (C) | Effective bits | Energy (J) | Max relay energy (J) | Representation JS | Participation Jain |',
        '|---|---:|---:|---:|---:|---:|---:|'
    ]
    for m in ['random','resource','utility','proposed']:
        r=row(m,0.9)
        report.append(f"| {m} | {float(r['rmse_c_mean']):.4f} +/- {float(r['rmse_c_ci95']):.4f} | {float(r['effective_bits_mean']):.0f} | {float(r['energy_j_mean']):.3f} | {float(r['max_relay_energy_j_mean']):.4f} | {float(r['representation_js_mean']):.4f} | {float(r['participation_jain_mean']):.4f} |")
    report += ['', 'Against the resource-only baseline at correlation 0.9, the proposed method changes:', '',
               f"- RMSE: {100*(float(p['rmse_c_mean'])-float(b['rmse_c_mean']))/float(b['rmse_c_mean']):+.2f}% (negative is better).",
               f"- Effective communication burden: {-reduction('effective_bits_mean','effective_bits_mean'):+.2f}% (negative means fewer effective bits).",
               f"- Total modeled energy: {-reduction('energy_j_mean','energy_j_mean'):+.2f}%.",
               f"- Maximum relay energy: {-reduction('max_relay_energy_j_mean','max_relay_energy_j_mean'):+.2f}%.",
               f"- Representation divergence: {-reduction('representation_js_mean','representation_js_mean'):+.2f}%.",
               '', '## Ablation at correlation = 0.9','',
               '| Variant | RMSE (C) | Effective bits | Energy (J) | Rep. JS | Max relay energy (J) |',
               '|---|---:|---:|---:|---:|---:|']
    for r in abl:
        report.append(f"| {r['variant']} | {float(r['rmse_c_mean']):.4f} | {float(r['effective_bits_mean']):.0f} | {float(r['energy_j_mean']):.3f} | {float(r['representation_js_mean']):.4f} | {float(r['max_relay_energy_j_mean']):.4f} |")
    report += ['', 'The ablation supports three distinct roles: removing the representation-deficit term roughly doubles representation divergence; fixing compression materially increases communication/energy; removing relay pressure substantially increases relay-energy concentration. Utility-aware staleness has a smaller effect in this dataset because most model updates arrive within low staleness.', '',
               '## Statistical contrasts','',
               'Exact paired sign-flip permutation p-values (10 paired seeds, correlation 0.9) are stored in `results/intel_lab/paired_contrasts.csv`. These tests are reported as evidence about repeatability, not as proof of external validity.','',
               '## Evidence boundary','',
               'This is a real WSN **dataset/topology/connectivity** validation executed on the implementation. It is not a replay on the original 2004 Mica2Dot hardware. Physical-node radio/MCU measurements remain a separate future validation layer.']
    VAL.mkdir(parents=True,exist_ok=True)
    (VAL/'INTEL_LAB_REPORT.md').write_text('\n'.join(report))
    print('\n'.join(report[:35]))
    print('wrote',VAL/'INTEL_LAB_REPORT.md', 'and', RES/'paired_contrasts.csv')

if __name__=='__main__': main()
