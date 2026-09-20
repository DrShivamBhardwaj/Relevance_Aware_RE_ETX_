import csv, hashlib, json, math
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'tables';OUT.mkdir(exist_ok=True)
MAIN_METHODS=['resource','resource_adaptive','fedcg_adapted','proposed_fixed_comp','proposed']
ALL_METHODS=['random','resource','utility','random_adaptive','resource_adaptive','utility_adaptive','proposed_fixed_comp','fedcg_adapted','proposed']


def rows(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))

def write(name,data):
    p=OUT/name
    fields=[]
    for r in data:
        for k in r:
            if k not in fields:fields.append(k)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(data)
    return p

def row_for(data,method,c=.9):
    return next(r for r in data if r['method']==method and abs(float(r['correlation'])-c)<1e-12)

def pm(r,key,d=4,scale=1.0):
    return f"{float(r[key+'_mean'])/scale:.{d}f} ± {float(r[key+'_ci95'])/scale:.{d}f}"

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()

def main():
    src={
      'intel':ROOT/'results/intel_lab/aggregate_summary.csv',
      'har':ROOT/'results/uci_har/aggregate_summary.csv',
      'intel_ablation':ROOT/'results/intel_lab/ablation_summary.csv',
      'har_ablation':ROOT/'results/uci_har/ablation_summary.csv',
      'stats':ROOT/'validation/statistics/statistical_tests.csv',
      'intel_grid':ROOT/'results/intel_lab/joint_grid.csv',
      'har_grid':ROOT/'results/uci_har/joint_grid.csv',
      'selection':ROOT/'results/OPERATING_POINT_SELECTION.json',
      'control_plane':ROOT/'validation/control_plane/metadata_summary.csv',
    }
    intel,har=rows(src['intel']),rows(src['har'])
    table1=[
      {'parameter':'Tuning seeds','value':'7, 11, 19, 23, 29, 31, 37, 41, 43, 47','role':'parameter selection only'},
      {'parameter':'Held-out evaluation seeds','value':'53, 59, 61, 67, 71, 73, 79, 83, 89, 97','role':'all final comparisons/inference'},
      {'parameter':'Resource-data correlation','value':'0, 0.5, 0.9','role':'controlled stress levels'},
      {'parameter':'Relay-pressure coefficient eta_R','value':'5.0','role':'selected on tuning seeds'},
      {'parameter':'Compression-distortion beta','value':'0.10','role':'selected on tuning seeds'},
      {'parameter':'Drift V','value':'0.5','role':'controller'},
      {'parameter':'Top-k candidates','value':'0.15, 0.30, 0.50, 0.75, 1.0','role':'adaptive fidelity'},
      {'parameter':'Fixed-compression controls','value':'0.50','role':'matched ablation/control'},
      {'parameter':'Scarcity coefficient','value':'0.5','role':'executed scheduler/compression surrogate'},
      {'parameter':'Staleness lambda / utility coefficient mu','value':'0.35 / 0.80','role':'aggregation'},
      {'parameter':'Tx / Rx energy per bit','value':'1.5e-6 / 8.0e-7 J','role':'modeled communication energy'},
      {'parameter':'Local-step energy','value':'0.004 J','role':'modeled local training energy'},
      {'parameter':'Relay-pressure reference','value':'0.004 J/round','role':'virtual-queue reference, not hard cap'},
      {'parameter':'Header / model / index bits','value':'96 / 32 / 16','role':'model-update traffic accounting'},
      {'parameter':'Candidate metadata packet','value':'168 bits = 21 bytes','role':'header + loss + residual-energy estimate + availability'},
      {'parameter':'Intel: rounds / K / lr / L2 / slot','value':'30 / 10 / 0.010 / 0.010 / 0.20 s','role':'regression'},
      {'parameter':'HAR: rounds / K / lr / L2 / slot','value':'25 / 8 / 0.020 / 0.001 / 0.25 s','role':'classification'},
      {'parameter':'HAR split','value':'10-window blocks; 1-in-5 test; 1-neighbor purge','role':'overlap-safe within-client holdout'},
    ]
    write('table1_protocol_parameters.csv',table1)

    t2=[]
    for m in MAIN_METHODS:
        r=row_for(intel,m)
        t2.append({'method':m,'rmse_c_95ci':pm(r,'rmse_c'),'mae_c_95ci':pm(r,'mae_c'),
                   'effective_mbit_95ci':pm(r,'effective_bits',3,1e6),'energy_j_95ci':pm(r,'energy_j',3),
                   'max_relay_energy_j_95ci':pm(r,'max_relay_energy_j',4),
                   'utility_target_js_95ci':pm(r,'utility_target_js',4),
                   'temperature_coverage_js_95ci':pm(r,'temperature_coverage_js',5),
                   'jain_95ci':pm(r,'participation_jain',4)})
    write('table2_intel_main.csv',t2)

    t3=[]
    for m in MAIN_METHODS:
        r=row_for(har,m)
        t3.append({'method':m,'accuracy_95ci':pm(r,'accuracy'),'macro_f1_95ci':pm(r,'macro_f1'),
                   'worst_client_accuracy_95ci':pm(r,'worst_client_accuracy'),
                   'effective_mbit_95ci':pm(r,'effective_bits',3,1e6),'energy_j_95ci':pm(r,'energy_j',2),
                   'max_relay_energy_j_95ci':pm(r,'max_relay_energy_j',3),
                   'utility_target_js_95ci':pm(r,'utility_target_js',4),
                   'class_coverage_js_95ci':pm(r,'class_coverage_js',6),
                   'jain_95ci':pm(r,'participation_jain',4)})
    write('table3_har_main.csv',t3)

    t4=[]
    for dataset,data in [('Intel',intel),('UCI HAR',har)]:
        for m in ALL_METHODS:
            r=row_for(data,m)
            out={'dataset':dataset,'method':m}
            if dataset=='Intel':
                out.update({'learning':r['rmse_c_mean'],'effective_bits':r['effective_bits_mean'],'energy_j':r['energy_j_mean'],
                            'max_relay_energy_j':r['max_relay_energy_j_mean'],'utility_target_js':r['utility_target_js_mean'],
                            'independent_coverage_js':r['temperature_coverage_js_mean']})
            else:
                out.update({'learning':r['accuracy_mean'],'effective_bits':r['effective_bits_mean'],'energy_j':r['energy_j_mean'],
                            'max_relay_energy_j':r['max_relay_energy_j_mean'],'utility_target_js':r['utility_target_js_mean'],
                            'independent_coverage_js':r['class_coverage_js_mean']})
            t4.append(out)
    write('table_s1_all_controls_c09.csv',t4)

    t5=[]
    for dataset,p in [('Intel',src['intel_ablation']),('UCI HAR',src['har_ablation'])]:
        for r in rows(p):t5.append({'dataset':dataset,**r})
    write('table_s2_ablation.csv',t5)

    t6=[]
    for dataset,p in [('Intel',src['intel_grid']),('UCI HAR',src['har_grid'])]:
        for r in rows(p):t6.append({'dataset':dataset,**r})
    write('table_s3_tuning_grid.csv',t6)

    if src['stats'].exists():
        write('table4_heldout_contrasts.csv',rows(src['stats']))
    if src['control_plane'].exists():
        write('table5_control_plane_metadata.csv', rows(src['control_plane']))

    generated=sorted(OUT.glob('table*.csv'))
    manifest={
      'status':'FROZEN',
      'metric_policy':'utility_target_js uses corrected cloud-level aggregation coefficients; independent coverage metrics are temperature_coverage_js (Intel) and class_coverage_js (HAR).',
      'selection_protocol':json.loads(src['selection'].read_text())['protocol'],
      'source_sha256':{str(p.relative_to(ROOT)):sha(p) for k,p in src.items() if p.exists()},
      'generated_sha256':{str(p.relative_to(ROOT)):sha(p) for p in generated},
    }
    (OUT/'TABLE_FREEZE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
    print('wrote',len(generated),'tables')

if __name__=='__main__':main()
