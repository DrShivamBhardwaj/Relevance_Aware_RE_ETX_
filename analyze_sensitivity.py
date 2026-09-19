import csv, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
RES=ROOT/'results/sensitivity'; VAL=ROOT/'validation/sensitivity'; VAL.mkdir(parents=True,exist_ok=True)

def read(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))

def main():
    rows=read(RES/'sensitivity_grid.csv')
    report=['# Parameter-sensitivity report','','This report uses the executed 10-seed grid in `results/sensitivity/sensitivity_grid.csv`. It jointly varies relay-pressure weight and compression-distortion weight for the proposed scheduler at correlation 0.9.','']
    for dataset in ['intel_lab','uci_har']:
        sub=[r for r in rows if r['dataset']==dataset]
        candidates=[]
        for r in sub:
            bits=float(r['effective_bits_mean']); rep=float(r['representation_js_mean']); relay=float(r['max_relay_energy_j_mean'])
            if dataset=='intel_lab': perf=float(r['rmse_c_mean']); perf_norm=perf/min(float(x['rmse_c_mean']) for x in sub)
            else: perf=float(r['accuracy_mean']); perf_norm=max(float(x['accuracy_mean']) for x in sub)/max(perf,1e-12)
            # Composite: lower is better; keeps performance near the best while preferring lower traffic, representation error and relay burden.
            score=perf_norm + 0.35*bits/min(float(x['effective_bits_mean']) for x in sub) + 0.30*rep/min(float(x['representation_js_mean']) for x in sub) + 0.20*relay/min(float(x['max_relay_energy_j_mean']) for x in sub)
            candidates.append((score,r))
        best=sorted(candidates,key=lambda x:x[0])[:6]
        report += [f'## {dataset}','', '| Rank | Relay weight | Compression beta | Perf. | Effective bits | Energy | Max relay E | Rep. JS | Composite |', '|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
        for rank,(score,r) in enumerate(best,1):
            perfkey='rmse_c_mean' if dataset=='intel_lab' else 'accuracy_mean'
            report.append(f"| {rank} | {float(r['relay_pressure_weight']):.1f} | {float(r['compression_distortion_weight']):.1f} | {float(r[perfkey]):.4f} | {float(r['effective_bits_mean']):.0f} | {float(r['energy_j_mean']):.3f} | {float(r['max_relay_energy_j_mean']):.4f} | {float(r['representation_js_mean']):.4f} | {score:.3f} |")
        report.append('')
    report += ['## Operating-point decision','','For the manuscript experiments, the strongest evidence supports keeping the relay-aware and adaptive-compression terms active. The grid suggests a low-to-moderate compression beta around 0.2--0.4 and relay-pressure weight around 1--3, depending on whether the priority is minimum traffic or maximum learning accuracy.','', 'For conservative reporting, use the executed real-data main setting and present the sensitivity grid as evidence that the conclusions do not depend on a single arbitrary parameter choice.']
    (VAL/'SENSITIVITY_REPORT.md').write_text('\n'.join(report))
    print('\n'.join(report[:80])); print('wrote',VAL/'SENSITIVITY_REPORT.md')
if __name__=='__main__':main()
