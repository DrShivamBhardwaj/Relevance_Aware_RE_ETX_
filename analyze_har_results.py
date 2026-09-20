import csv
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'validation/real_data/UCI_HAR_REPORT.md'

def read(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))

def main():
    agg=read(ROOT/'results/uci_har/aggregate_summary.csv')
    abl=read(ROOT/'results/uci_har/ablation_summary.csv')
    rows=[r for r in agg if abs(float(r['correlation'])-.9)<1e-12]
    order=['random','resource','utility','random_adaptive','resource_adaptive','utility_adaptive','proposed_fixed_comp','fedcg_adapted','proposed']
    by={r['method']:r for r in rows}
    report=[
        '# UCI HAR held-out evaluation report','',
        'The official UCI train/test partitions are recombined because each subject is modeled as a persistent FL client. '
        'Within each subject, ordered windows are assigned to contiguous 10-window blocks; one of every five blocks is held out, '
        'and one adjacent window is purged from training at each test boundary to prevent 50%-overlap leakage. This is a '
        'within-client blocked holdout, not the canonical unseen-subject UCI benchmark. Final comparisons use 10 evaluation seeds '
        'that are disjoint from the 10 tuning seeds.','',
        '| Method | Accuracy | Macro-F1 | Worst-client acc. | Effective Mbit | Energy (J) | Max relay E (J) | Utility-target JS | Class-coverage JS | Jain |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|'
    ]
    for m in order:
        r=by[m]
        report.append(
            f"| {m} | {float(r['accuracy_mean']):.4f} ± {float(r['accuracy_ci95']):.4f} | "
            f"{float(r['macro_f1_mean']):.4f} ± {float(r['macro_f1_ci95']):.4f} | "
            f"{float(r['worst_client_accuracy_mean']):.4f} ± {float(r['worst_client_accuracy_ci95']):.4f} | "
            f"{float(r['effective_bits_mean'])/1e6:.3f} | {float(r['energy_j_mean']):.2f} | "
            f"{float(r['max_relay_energy_j_mean']):.3f} | {float(r['utility_target_js_mean']):.4f} | "
            f"{float(r['class_coverage_js_mean']):.6f} | {float(r['participation_jain_mean']):.4f} |"
        )
    report += ['', '## Matched-compression interpretation','',
        'The adaptive controls receive the same client-specific Top-k ratio rule as the proposed controller. '
        'proposed_fixed_comp isolates the selector/queue mechanisms at a fixed 50% Top-k ratio. '
        'fedcg_adapted is a favorable gradient-diversity/capability comparator inspired by FedCG and is explicitly not claimed '
        'as an exact reproduction of its original single-level communication model.','',
        '## Ablation','',
        '| Variant | Accuracy | Effective Mbit | Energy (J) | Max relay E (J) | Utility-target JS | Class-coverage JS |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for r in abl:
        report.append(
            f"| {r['variant']} | {float(r['accuracy_mean']):.4f} | {float(r['effective_bits_mean'])/1e6:.3f} | "
            f"{float(r['energy_j_mean']):.2f} | {float(r['max_relay_energy_j_mean']):.3f} | "
            f"{float(r['utility_target_js_mean']):.4f} | {float(r['class_coverage_js_mean']):.6f} |"
        )
    report += ['', 'Paired held-out-seed exact sign-flip tests and Holm-adjusted p-values are stored in validation/statistics/statistical_tests.csv.']
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text('\n'.join(report))
    print('\n'.join(report[:35]));print('wrote',OUT)

if __name__=='__main__':main()
