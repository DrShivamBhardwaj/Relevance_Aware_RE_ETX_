import csv, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
INTEL_RMSE_TOL_C=0.010
HAR_ACC_TOL=0.005


def read(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))


def minmax(vals,value):
    vals=[float(v) for v in vals];lo=min(vals);hi=max(vals)
    return 0.0 if hi-lo<1e-12 else (float(value)-lo)/(hi-lo)


def main():
    intel=read(ROOT/'results/intel_lab/joint_grid.csv')
    har=read(ROOT/'results/uci_har/joint_grid.csv')
    hmap={(float(r['relay_pressure_weight']),float(r['compression_distortion_weight'])):r for r in har}
    best_intel=min(float(r['rmse_c_mean']) for r in intel)
    best_har=max(float(r['accuracy_mean']) for r in har)
    ranking=[]
    for ir in intel:
        key=(float(ir['relay_pressure_weight']),float(ir['compression_distortion_weight']))
        hr=hmap[key]
        feasible=(
            float(ir['rmse_c_mean']) <= best_intel + INTEL_RMSE_TOL_C
            and float(hr['accuracy_mean']) >= best_har - HAR_ACC_TOL
        )
        comps={
            'intel_bits':minmax([r['effective_bits_mean'] for r in intel],ir['effective_bits_mean']),
            'intel_energy':minmax([r['energy_j_mean'] for r in intel],ir['energy_j_mean']),
            'intel_relay':minmax([r['max_relay_energy_j_mean'] for r in intel],ir['max_relay_energy_j_mean']),
            'har_bits':minmax([r['effective_bits_mean'] for r in har],hr['effective_bits_mean']),
            'har_energy':minmax([r['energy_j_mean'] for r in har],hr['energy_j_mean']),
            'har_relay':minmax([r['max_relay_energy_j_mean'] for r in har],hr['max_relay_energy_j_mean']),
        }
        score=sum(comps.values())/len(comps)
        ranking.append({
            'relay_pressure_weight':key[0],'compression_distortion_weight':key[1],
            'feasible_learning':feasible,'systems_score':score,'components':comps,
            'intel_rmse':float(ir['rmse_c_mean']),'har_accuracy':float(hr['accuracy_mean'])
        })
    ranking.sort(key=lambda r:(not r['feasible_learning'],r['systems_score']))
    selected=next(r for r in ranking if r['feasible_learning'])
    out={
        'protocol':(
            'Tune only on the 10 tuning seeds. A grid point is learning-feasible when Intel RMSE is within '
            f'{INTEL_RMSE_TOL_C:.3f} C of the best tuning-grid RMSE and HAR accuracy is within '
            f'{100*HAR_ACC_TOL:.1f} percentage points of the best tuning-grid accuracy. Among feasible points, '
            'select the lowest equal-weight min-max normalized systems score over effective bits, total modeled '
            'energy, and maximum relay energy on both datasets. Utility-target and independent coverage metrics '
            'are excluded from tuning and reserved for held-out evaluation.'
        ),
        'best_tuning_learning':{'intel_rmse_c':best_intel,'har_accuracy':best_har},
        'selected':selected,'ranking':ranking,
    }
    p=ROOT/'results/OPERATING_POINT_SELECTION.json';p.write_text(json.dumps(out,indent=2))
    print(json.dumps(selected,indent=2));print('wrote',p)


if __name__=='__main__':main()
