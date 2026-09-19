import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "tables"
OUT.mkdir(exist_ok=True)


def rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def write_csv(name, data):
    path = OUT / name
    fieldnames = []
    seen = set()
    for row in data:
        for key in row:
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(data)
    return path


def row_for(data, method, corr=0.9):
    return next(r for r in data if r["method"] == method and abs(float(r["correlation"]) - corr) < 1e-12)


def fmt_pm(mean, ci, digits=4):
    return f"{float(mean):.{digits}f} ± {float(ci):.{digits}f}"


def mbits(x):
    return float(x) / 1e6


def ci_from_sd(sd, n):
    return 1.96 * float(sd) / math.sqrt(int(n))


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def pct(new, old):
    return 100.0 * (float(new) - float(old)) / float(old)


def main():
    src = {
        "synthetic": ROOT / "results/final_synthetic_10seed/aggregate_summary.csv",
        "intel": ROOT / "results/intel_lab/aggregate_summary.csv",
        "har": ROOT / "results/uci_har/aggregate_summary.csv",
        "stats": ROOT / "validation/statistics/statistical_tests.csv",
        "intel_ablation": ROOT / "results/intel_lab/ablation_summary.csv",
        "har_ablation": ROOT / "results/uci_har/ablation_summary.csv",
        "ns3": ROOT / "validation/ns3_47_hfl/results/ns3_group_summary.csv",
        "intel_grid": ROOT / "results/intel_lab/joint_grid.csv",
        "har_grid": ROOT / "results/uci_har/joint_grid.csv",
    }
    syn, intel, har = rows(src["synthetic"]), rows(src["intel"]), rows(src["har"])
    stats = rows(src["stats"])
    ia, ha, ns3 = rows(src["intel_ablation"]), rows(src["har_ablation"]), rows(src["ns3"])

    table1 = [
        {"evidence_layer":"Synthetic stress test","clients":"24","task":"5-class synthetic classification","rounds":"40","clients_per_round":"6","resource_data_corr":"0, 0.5, 0.9","seeds":"10","network_evidence":"multi-hop simulated WSN"},
        {"evidence_layer":"Intel Berkeley Lab","clients":"48 learning + 4 gateways","task":"next-temperature regression","rounds":"30","clients_per_round":"10","resource_data_corr":"0, 0.5, 0.9","seeds":"10","network_evidence":"real mote locations + measured connectivity"},
        {"evidence_layer":"UCI HAR","clients":"30 subjects","task":"6-class activity recognition","rounds":"25","clients_per_round":"8","resource_data_corr":"0, 0.5, 0.9","seeds":"10","network_evidence":"real sensing data + simulated multi-hop substrate"},
        {"evidence_layer":"ns-3.47 LR-WPAN","clients":"traffic replay","task":"IEEE 802.15.4 delivery/latency","rounds":"n/a","clients_per_round":"n/a","resource_data_corr":"frozen traffic profiles","seeds":"10","network_evidence":"MAC/PHY CSMA/CA + ACK + retransmission"},
    ]
    write_csv("table1_experimental_design.csv", table1)

    methods = ["random","resource","utility","proposed"]
    table2=[]
    for m in methods:
        r=row_for(intel,m)
        table2.append({
            "method":m,
            "rmse_c_95ci":fmt_pm(r["rmse_c_mean"],r["rmse_c_ci95"],4),
            "mae_c_95ci":fmt_pm(r["mae_c_mean"],r["mae_c_ci95"],4),
            "effective_mbit_95ci":fmt_pm(mbits(r["effective_bits_mean"]),mbits(r["effective_bits_ci95"]),3),
            "energy_j_95ci":fmt_pm(r["energy_j_mean"],r["energy_j_ci95"],3),
            "max_relay_energy_j_95ci":fmt_pm(r["max_relay_energy_j_mean"],r["max_relay_energy_j_ci95"],4),
            "representation_js_95ci":fmt_pm(r["representation_js_mean"],r["representation_js_ci95"],4),
            "jain_95ci":fmt_pm(r["participation_jain_mean"],r["participation_jain_ci95"],4),
        })
    write_csv("table2_intel_main.csv",table2)

    table3=[]
    for m in methods:
        r=row_for(har,m)
        table3.append({
            "method":m,
            "accuracy_95ci":fmt_pm(r["accuracy_mean"],r["accuracy_ci95"],4),
            "macro_f1_95ci":fmt_pm(r["macro_f1_mean"],r["macro_f1_ci95"],4),
            "worst_client_acc_95ci":fmt_pm(r["worst_client_accuracy_mean"],r["worst_client_accuracy_ci95"],4),
            "effective_mbit_95ci":fmt_pm(mbits(r["effective_bits_mean"]),mbits(r["effective_bits_ci95"]),3),
            "energy_j_95ci":fmt_pm(r["energy_j_mean"],r["energy_j_ci95"],2),
            "max_relay_energy_j_95ci":fmt_pm(r["max_relay_energy_j_mean"],r["max_relay_energy_j_ci95"],3),
            "representation_js_95ci":fmt_pm(r["representation_js_mean"],r["representation_js_ci95"],4),
            "jain_95ci":fmt_pm(r["participation_jain_mean"],r["participation_jain_ci95"],4),
        })
    write_csv("table3_har_main.csv",table3)

    keep = {
        "intel_lab":["rmse_c","mae_c","effective_bits","energy_j","max_relay_energy_j","representation_js"],
        "uci_har":["accuracy","macro_f1","worst_client_accuracy","effective_bits","energy_j","max_relay_energy_j","representation_js"],
    }
    table4=[]
    for r in stats:
        if r["baseline"]!="resource" or r["metric"] not in keep.get(r["dataset"],[]):
            continue
        table4.append({
            "dataset":r["dataset"],
            "metric":r["metric"],
            "proposed_mean":r["mean_proposed"],
            "resource_mean":r["mean_baseline"],
            "difference":r["mean_diff"],
            "percent_change":r["percent_change_vs_baseline"],
            "bootstrap95_low":r["bootstrap95_low"],
            "bootstrap95_high":r["bootstrap95_high"],
            "signflip_p":r["signflip_p"],
            "holm_p":r["holm_p"],
            "paired_cohen_d":r["cohen_d_paired"],
        })
    write_csv("table4_resource_contrasts.csv",table4)

    table5=[]
    for dataset, data, learning_key in [("Intel",ia,"rmse_c_mean"),("UCI HAR",ha,"accuracy_mean")]:
        for r in data:
            table5.append({
                "dataset":dataset,
                "variant":r["variant"],
                "learning_metric":learning_key.replace("_mean",""),
                "learning_mean":r[learning_key],
                "effective_mbit":mbits(r["effective_bits_mean"]),
                "energy_j":r["energy_j_mean"],
                "max_relay_energy_j":r["max_relay_energy_j_mean"],
                "representation_js":r["representation_js_mean"],
            })
    write_csv("table5_ablation.csv",table5)

    primary_conditions=["dense_nominal","scale_nominal"]
    table6=[]
    for cond in primary_conditions:
        for m in methods:
            r=next(x for x in ns3 if x["mapping"]=="hop" and x["condition"]==cond and x["method"]==m)
            n=int(r["n"])
            table6.append({
                "condition":cond,
                "method":m,
                "mapped_payload_bits":r["mapped_payload_bits"],
                "report_rdr_pct_95ci":fmt_pm(r["report_rdr_pct_mean"],ci_from_sd(r["report_rdr_pct_sd"],n),2),
                "delay_ms_95ci":fmt_pm(r["mean_delivered_report_delay_ms_mean"],ci_from_sd(r["mean_delivered_report_delay_ms_sd"],n),2),
                "channel_access_failures_95ci":fmt_pm(r["channel_access_failures_mean"],ci_from_sd(r["channel_access_failures_sd"],n),1),
            })
    write_csv("table6_ns3_primary.csv",table6)

    table_s1=[]
    for r in syn:
        n=int(r["n"])
        table_s1.append({
            "correlation":r["correlation"],"method":r["method"],
            "accuracy_95ci":fmt_pm(r["accuracy_mean"],ci_from_sd(r["accuracy_sd"],n),4),
            "macro_f1_95ci":fmt_pm(r["macro_f1_mean"],ci_from_sd(r["macro_f1_sd"],n),4),
            "effective_mbit_95ci":fmt_pm(mbits(r["effective_bits_mean"]),mbits(ci_from_sd(r["effective_bits_sd"],n)),3),
            "energy_j_95ci":fmt_pm(r["energy_j_mean"],ci_from_sd(r["energy_j_sd"],n),3),
            "max_relay_energy_j_95ci":fmt_pm(r["max_relay_energy_j_mean"],ci_from_sd(r["max_relay_energy_j_sd"],n),4),
            "representation_js_95ci":fmt_pm(r["representation_js_mean"],ci_from_sd(r["representation_js_sd"],n),4),
        })
    write_csv("table_s1_synthetic_all.csv",table_s1)

    def compact_all(data, dataset):
        out=[]
        for r in data:
            base={"correlation":r["correlation"],"method":r["method"]}
            if dataset=="intel":
                base.update({"learning":r["rmse_c_mean"],"effective_bits":r["effective_bits_mean"],"energy_j":r["energy_j_mean"],"max_relay_energy_j":r["max_relay_energy_j_mean"],"representation_js":r["representation_js_mean"]})
            else:
                base.update({"learning":r["accuracy_mean"],"effective_bits":r["effective_bits_mean"],"energy_j":r["energy_j_mean"],"max_relay_energy_j":r["max_relay_energy_j_mean"],"representation_js":r["representation_js_mean"]})
            out.append(base)
        return out
    write_csv("table_s2_intel_all_correlations.csv",compact_all(intel,"intel"))
    write_csv("table_s3_har_all_correlations.csv",compact_all(har,"har"))

    selected=[]
    for dataset,key in [("Intel",src["intel_grid"]),("UCI HAR",src["har_grid"])]:
        grid=rows(key)
        for r in grid:
            if float(r["relay_pressure_weight"]) in (2.0,3.0,4.0) and float(r["compression_distortion_weight"]) in (0.1,0.2):
                selected.append({"dataset":dataset,**r})
    write_csv("table_s4_sensitivity_neighborhood.csv",selected)

    ir, ip = row_for(intel,"resource"), row_for(intel,"proposed")
    hr, hp = row_for(har,"resource"), row_for(har,"proposed")
    claims = {
        "intel_c0.9_vs_resource":{
            "rmse_percent":pct(ip["rmse_c_mean"],ir["rmse_c_mean"]),
            "mae_percent":pct(ip["mae_c_mean"],ir["mae_c_mean"]),
            "effective_bits_percent":pct(ip["effective_bits_mean"],ir["effective_bits_mean"]),
            "energy_percent":pct(ip["energy_j_mean"],ir["energy_j_mean"]),
            "max_relay_energy_percent":pct(ip["max_relay_energy_j_mean"],ir["max_relay_energy_j_mean"]),
            "representation_js_percent":pct(ip["representation_js_mean"],ir["representation_js_mean"]),
        },
        "har_c0.9_vs_resource":{
            "accuracy_pp":100*(float(hp["accuracy_mean"])-float(hr["accuracy_mean"])),
            "macro_f1_pp":100*(float(hp["macro_f1_mean"])-float(hr["macro_f1_mean"])),
            "worst_client_accuracy_pp":100*(float(hp["worst_client_accuracy_mean"])-float(hr["worst_client_accuracy_mean"])),
            "effective_bits_percent":pct(hp["effective_bits_mean"],hr["effective_bits_mean"]),
            "energy_percent":pct(hp["energy_j_mean"],hr["energy_j_mean"]),
            "max_relay_energy_percent":pct(hp["max_relay_energy_j_mean"],hr["max_relay_energy_j_mean"]),
            "representation_js_percent":pct(hp["representation_js_mean"],hr["representation_js_mean"]),
        },
    }

    generated = sorted(OUT.glob("*.csv"))
    manifest = {
        "status":"FROZEN",
        "policy":"Main text uses c=0.9 as the predeclared strongest correlated-heterogeneity stress condition; all c levels remain in supplementary tables. Resource-only is the primary contrast because it isolates the cost of network-only scheduling. Negative trade-offs are retained.",
        "source_sha256":{str(p.relative_to(ROOT)):sha256(p) for p in src.values()},
        "generated_sha256":{str(p.relative_to(ROOT)):sha256(p) for p in generated},
        "frozen_claims":claims,
    }
    (OUT/"TABLE_FREEZE_MANIFEST.json").write_text(json.dumps(manifest,indent=2))
    print(json.dumps(claims,indent=2))
    print(f"Wrote {len(generated)} CSV tables and manifest to {OUT}")


if __name__=="__main__":
    main()
