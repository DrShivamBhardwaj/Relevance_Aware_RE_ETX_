import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'validation/real_data/INTEL_LAB_REPORT.md'

def read(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))

def main():
    agg=read(ROOT/'results/intel_lab/aggregate_summary.csv')
    abl=read(ROOT/'results/intel_lab/ablation_summary.csv')
    rows=[r for r in agg if abs(float(r['correlation'])-.9)<1e-12]
    order=['random','resource','utility','random_adaptive','resource_adaptive','utility_adaptive','proposed_fixed_comp','fedcg_adapted','proposed']
    by={r['method']:r for r in rows}
    report=[
        '# Intel Berkeley Lab WSN held-out evaluation report','',
        'Final comparisons use 10 evaluation seeds that are disjoint from the 10 tuning seeds. '
        'Utility-target JS uses corrected cloud-level client coefficients after both edge and cloud normalization. '
        'Temperature-coverage JS is independent of the controller target and measures how the cloud-influence-weighted '
        'client temperature distribution matches the pooled training distribution.','',
        '| Method | RMSE (C) | MAE (C) | Effective Mbit | Energy (J) | Max relay E (J) | Utility-target JS | Temp.-coverage JS | Jain |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|'
    ]
    for m in order:
        r=by[m]
        report.append(
            f"| {m} | {float(r['rmse_c_mean']):.4f} ± {float(r['rmse_c_ci95']):.4f} | "
            f"{float(r['mae_c_mean']):.4f} ± {float(r['mae_c_ci95']):.4f} | "
            f"{float(r['effective_bits_mean'])/1e6:.3f} | {float(r['energy_j_mean']):.3f} | "
            f"{float(r['max_relay_energy_j_mean']):.4f} | {float(r['utility_target_js_mean']):.4f} | "
            f"{float(r['temperature_coverage_js_mean']):.5f} | {float(r['participation_jain_mean']):.4f} |"
        )
    report += ['', '## Matched-compression interpretation','',
        'The adaptive controls use the same client-specific Top-k ratio rule as the proposed method while preserving '
        'their original random/resource/utility selection logic. proposed_fixed_comp fixes the proposed selector at 50% Top-k. '
        'fedcg_adapted is a favorable gradient-diversity/capability comparator inspired by FedCG; it is not represented as an exact '
        'reproduction because FedCG does not assume this multi-hop HFL topology.','',
        '## Ablation','',
        '| Variant | RMSE | Effective Mbit | Energy (J) | Max relay E (J) | Utility-target JS | Temp.-coverage JS |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r in abl:
        report.append(
            f"| {r['variant']} | {float(r['rmse_c_mean']):.4f} | {float(r['effective_bits_mean'])/1e6:.3f} | "
            f"{float(r['energy_j_mean']):.3f} | {float(r['max_relay_energy_j_mean']):.4f} | "
            f"{float(r['utility_target_js_mean']):.4f} | {float(r['temperature_coverage_js_mean']):.5f} |"
        )
    report += ['', 'Paired held-out-seed exact sign-flip tests and Holm-adjusted p-values are stored in validation/statistics/statistical_tests.csv.']
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(report))
    print('\n'.join(report[:35]));print('wrote',OUT)

if __name__=='__main__':main()
