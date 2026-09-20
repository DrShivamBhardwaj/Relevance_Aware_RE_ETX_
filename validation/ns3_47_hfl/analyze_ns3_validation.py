import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path

VAL = Path(__file__).resolve().parent
RES = VAL / "results"
METHODS = ("random", "resource", "utility", "proposed")
METRICS = (
    "report_rdr_pct",
    "frame_rdr_pct",
    "mean_delivered_report_delay_ms",
    "mean_retries_per_frame",
    "mean_csma_cycles_per_frame",
    "channel_access_failures",
)


def load(mapping):
    path = RES / f"ns3_hfl_{mapping}_equivalent_sweep.csv"
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def mean_sd(values):
    vals = [float(x) for x in values]
    return statistics.fmean(vals), statistics.stdev(vals) if len(vals) > 1 else 0.0


def summarize(mapping, rows):
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r["condition"], r["mode"])].append(r)
    out = []
    for (condition, method), rs in sorted(grouped.items()):
        row = {"mapping": mapping, "condition": condition, "method": method, "n": len(rs)}
        for metric in METRICS:
            m, sd = mean_sd(r[metric] for r in rs)
            row[metric + "_mean"] = m
            row[metric + "_sd"] = sd
        row["mapped_payload_bits"] = float(rs[0]["mapped_payload_bits"])
        out.append(row)
    return out
def paired_contrasts(mapping, rows):
    by = {(r["condition"], r["mode"], int(r["seed"])): r for r in rows}
    conditions = sorted({r["condition"] for r in rows})
    seeds = sorted({int(r["seed"]) for r in rows})
    out = []
    for condition in conditions:
        for baseline in ("random", "resource", "utility"):
            rec = {"mapping": mapping, "condition": condition, "baseline": baseline, "n": len(seeds)}
            for metric in ("report_rdr_pct", "mean_delivered_report_delay_ms", "channel_access_failures"):
                diffs = [
                    float(by[(condition, "proposed", s)][metric]) -
                    float(by[(condition, baseline, s)][metric])
                    for s in seeds
                ]
                rec[metric + "_diff_mean"] = statistics.fmean(diffs)
                rec[metric + "_diff_sd"] = statistics.stdev(diffs) if len(diffs) > 1 else 0.0
                rec[metric + "_proposed_better_count"] = sum(
                    d > 0 if metric == "report_rdr_pct" else d < 0 for d in diffs
                )
            out.append(rec)
    return out


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
def report(summary, contrasts):
    lookup = {(r["mapping"], r["condition"], r["method"]): r for r in summary}
    lines = [
        "# ns-3.47 LR-WPAN validation report",
        "",
        "This report is generated from **executed ns-3.47 IEEE 802.15.4/LR-WPAN simulations** on the connected Mac.",
        "It is a communication-layer validation of the FL-derived traffic burden, not a full reproduction of the Python HFL optimizer inside ns-3.",
        "",
        "Two mappings are reported deliberately:",
        "",
        "- **Hop-equivalent**: compressed update bits × mean selected hop count. This avoids embedding ETX retransmission expectation before ns-3 applies its own MAC retries.",
        "- **ETX-equivalent**: HFL effective bits/update (compressed bits × route ETX sum). This is a conservative offered-load stress mapping and may double-count part of retransmission burden.",
        "",
        "All results use 10 paired seeds. Official ns-3 LR-WPAN unit suites were also executed separately.",
        "",
    ]
    for mapping in ("hop", "etx"):
        lines += [f"## {mapping.upper()}-equivalent mapping", ""]
        for condition in ("dense_fast", "dense_nominal", "dense_relaxed", "light_nominal", "scale_nominal"):
            lines += [f"### {condition}", "", "| Method | Payload bits | Report RDR % | Delay ms | Retries/frame | CSMA cycles/frame | Access failures |", "|---|---:|---:|---:|---:|---:|---:|"]
            for method in METHODS:
                r = lookup[(mapping, condition, method)]
                lines.append(
                    f"| {method} | {r['mapped_payload_bits']:.0f} | "
                    f"{r['report_rdr_pct_mean']:.2f} ± {r['report_rdr_pct_sd']:.2f} | "
                    f"{r['mean_delivered_report_delay_ms_mean']:.2f} ± {r['mean_delivered_report_delay_ms_sd']:.2f} | "
                    f"{r['mean_retries_per_frame_mean']:.3f} | {r['mean_csma_cycles_per_frame_mean']:.3f} | "
                    f"{r['channel_access_failures_mean']:.1f} |"
                )
            lines.append("")
    lines += [
        "## Interpretation boundary",
        "",
        "The hop-equivalent mapping is the more conservative primary network validation because it lets ns-3 generate MAC retransmissions itself.",
        "The ETX-equivalent mapping is retained as a sensitivity analysis because ETX is already an expected-transmission measure.",
        "Therefore, claims about absolute network superiority should be based on the hop-equivalent results; the ETX-equivalent results show sensitivity to the traffic mapping.",
        "",
        "The proposed learning policy is not expected to minimize every pure MAC metric: it deliberately trades some network cost for utility-target participation and relay-load control.",
        "The correct claim is therefore Pareto-oriented rather than an unconditional network-performance win.",
    ]
    (RES / "NS3_VALIDATION_REPORT.md").write_text("\n".join(lines))


def main():
    all_summary, all_contrasts = [], []
    for mapping in ("hop", "etx"):
        rows = load(mapping)
        all_summary += summarize(mapping, rows)
        all_contrasts += paired_contrasts(mapping, rows)
    write_csv(RES / "ns3_group_summary.csv", all_summary)
    write_csv(RES / "ns3_paired_contrasts.csv", all_contrasts)
    report(all_summary, all_contrasts)
    print("wrote", RES / "NS3_VALIDATION_REPORT.md")


if __name__ == "__main__":
    main()
