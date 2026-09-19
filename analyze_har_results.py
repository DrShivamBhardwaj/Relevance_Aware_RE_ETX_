import csv,itertools,statistics
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RES=ROOT/'results/uci_har'; VAL=ROOT/'validation/real_data'

def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))

def pflip(ds):
    ds=[float(x) for x in ds]; obs=abs(statistics.fmean(ds)); n=0;t=0
    for s in itertools.product((-1.,1.),repeat=len(ds)):
        if abs(statistics.fmean(a*b for a,b in zip(s,ds)))>=obs-1e-15:n+=1
        t+=1
    return n/t

def main():
    raw=read(RES/'raw_summary.csv'); agg=read(RES/'aggregate_summary.csv'); corr=.9
    prop={int(r['seed']):r for r in raw if r['method']=='proposed' and float(r['correlation'])==corr}
    metrics=['accuracy','macro_f1','worst_client_accuracy','p10_client_accuracy','effective_bits','energy_j','max_relay_energy_j','representation_js']
    out=[]
    for b in ['random','resource','utility']:
        base={int(r['seed']):r for r in raw if r['method']==b and float(r['correlation'])==corr}
        for m in metrics:
            d=[float(prop[s][m])-float(base[s][m]) for s in sorted(prop)]
            bm=statistics.fmean(float(base[s][m]) for s in sorted(prop))
            out.append({'baseline':b,'metric':m,'n':len(d),'proposed_minus_baseline_mean':statistics.fmean(d),'percent_change_vs_baseline':100*statistics.fmean(d)/bm if bm else 0,'exact_signflip_p':pflip(d)})
    with (RES/'paired_contrasts.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(out[0].keys()));w.writeheader();w.writerows(out)
    def row(m): return next(r for r in agg if r['method']==m and float(r['correlation'])==corr)
    p=row('proposed'); b=row('resource')
    report=['# UCI HAR real-IoT sensing validation','',
    '## Dataset and partitioning','',
    'The experiment uses the UCI Human Activity Recognition Using Smartphones dataset (DOI: 10.24432/C54S4K): 30 human subjects, six activities, and 561 time/frequency features derived from smartphone accelerometer and gyroscope windows. Each subject is treated as one federated client. The original train/test files are recombined and then split 80/20 within each subject using a fixed partition seed so that every client has local train and held-out test data.','',
    '## Experimental design','',
    '- 30 subject-clients; synthetic multi-hop WSN/IoT communication substrate with four edge gateways.',
    '- 25 federated rounds; 8 clients selected per round.',
    '- Resource-data correlation: 0.0, 0.5, 0.9.',
    '- 10 paired seeds for every method/condition.',
    '- Linear softmax classifier with Top-k update sparsification and error feedback.',
    '', '## Results at correlation = 0.9','',
    '| Method | Accuracy | Macro-F1 | Worst-client acc. | Effective bits | Energy (J) | Rep. JS | Jain |',
    '|---|---:|---:|---:|---:|---:|---:|---:|']
    for m in ['random','resource','utility','proposed']:
        r=row(m)
        report.append(f"| {m} | {float(r['accuracy_mean']):.4f} +/- {float(r['accuracy_ci95']):.4f} | {float(r['macro_f1_mean']):.4f} | {float(r['worst_client_accuracy_mean']):.4f} | {float(r['effective_bits_mean']):.0f} | {float(r['energy_j_mean']):.2f} | {float(r['representation_js_mean']):.4f} | {float(r['participation_jain_mean']):.4f} |")
    def pct(key):return 100*(float(p[key])-float(b[key]))/float(b[key])
    report+=['','Against the resource-only baseline at correlation 0.9:','',
      f"- Accuracy: {pct('accuracy_mean'):+.2f}% relative ({float(p['accuracy_mean'])-float(b['accuracy_mean']):+.4f} absolute).",
      f"- Macro-F1: {pct('macro_f1_mean'):+.2f}%.",
      f"- Worst-client accuracy: {pct('worst_client_accuracy_mean'):+.2f}%.",
      f"- Effective communication burden: {pct('effective_bits_mean'):+.2f}% (negative is lower).",
      f"- Modeled energy: {pct('energy_j_mean'):+.2f}%.",
      f"- Representation divergence: {pct('representation_js_mean'):+.2f}%.",
      '', 'Exact paired sign-flip p-values across the 10 matched seeds are stored in `results/uci_har/paired_contrasts.csv`.','',
      '## Evidence boundary','',
      'This validates the learning side on a real inertial-sensing dataset. Its communication topology is simulated; the Intel Lab experiment separately provides real WSN topology/connectivity plus real sensor readings. Together they test different sides of the claimed cross-layer coupling.']
    VAL.mkdir(exist_ok=True,parents=True); (VAL/'UCI_HAR_REPORT.md').write_text('\n'.join(report)); print('\n'.join(report[:30]));print('wrote reports')
if __name__=='__main__':main()
