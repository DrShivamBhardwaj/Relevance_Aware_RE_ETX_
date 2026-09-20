import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import numpy as np

ROOT = Path(__file__).resolve().parent
FINAL = ROOT / "figures" / "final"
FINAL.mkdir(parents=True, exist_ok=True)

NAVY = "#073B7A"
GRAY = "#666666"
BLUE = "#0B4FE8"
PURPLE = "#7C2BE8"
ORANGE = "#F36B16"
GREEN = "#0B8F24"
RED = "#E31A1C"
BLACK = "#111111"
GRID = "#D8DDE5"

MAIN = ["resource", "resource_adaptive", "fedcg_adapted", "proposed_fixed_comp", "proposed"]
LABELS = ["Resource", "Resource-adapt.", "FedCG-adapt.", "Proposed fixed", "Proposed"]
COLORS = [GRAY, BLUE, PURPLE, ORANGE, GREEN]
MARKERS = ["o", "s", "D", "P", "^"]

plt.rcParams.update({
    "font.family": "Times New Roman",
    "font.size": 10,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "axes.labelweight": "bold",
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

def read(path):
    with Path(path).open(newline="") as f:
        return list(csv.DictReader(f))

def c09(path):
    return {r["method"]: r for r in read(path) if abs(float(r["correlation"]) - 0.9) < 1e-12}

def save(fig, name):
    path = FINAL / name
    fig.savefig(path, dpi=600, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path

def style_axis(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8, linestyle="--", alpha=0.9)
    ax.set_axisbelow(True)

def add_value_table(fig, ax, columns, rows, col_widths=None, fontsize=8.4):
    ax.axis("off")
    table = ax.table(
        cellText=rows,
        colLabels=columns,
        cellLoc="center",
        colLoc="center",
        loc="center",
        colWidths=col_widths,
    )
    table.auto_set_font_size(False)
    table.set_fontsize(fontsize)
    table.scale(1, 1.55)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#333333")
        cell.set_linewidth(0.55)
        if r == 0:
            cell.set_facecolor(NAVY)
            cell.get_text().set_color("white")
            cell.get_text().set_weight("bold")
        elif c == 0:
            cell.get_text().set_weight("bold")
    return table

def normalized_result_figure(dataset, out_name):
    if dataset == "intel":
        by = c09(ROOT / "results/intel_lab/aggregate_summary.csv")
        title = "Intel Berkeley Lab Results at c = 0.9"
        metrics = [
            ("RMSE (°C)", "rmse_c_mean", 1.0, "{:.4f}"),
            ("Uplink Traffic\n(Mbit)", "effective_bits_mean", 1e-6, "{:.3f}"),
            ("Modeled Energy\n(J)", "energy_j_mean", 1.0, "{:.3f}"),
            ("Max Relay Energy\n(J)", "max_relay_energy_j_mean", 1.0, "{:.4f}"),
            ("Utility-target\nJS", "utility_target_js_mean", 1.0, "{:.4f}"),
        ]
    else:
        by = c09(ROOT / "results/uci_har/aggregate_summary.csv")
        title = "UCI HAR Results at c = 0.9"
        metrics = [
            ("Accuracy", "accuracy_mean", 1.0, "{:.4f}"),
            ("Macro-F1", "macro_f1_mean", 1.0, "{:.4f}"),
            ("Worst-client\nAccuracy", "worst_client_accuracy_mean", 1.0, "{:.4f}"),
            ("Uplink Traffic\n(Mbit)", "effective_bits_mean", 1e-6, "{:.3f}"),
            ("Modeled Energy\n(J)", "energy_j_mean", 1.0, "{:.2f}"),
            ("Max Relay\nEnergy (J)", "max_relay_energy_j_mean", 1.0, "{:.3f}"),
            ("Utility-target\nJS", "utility_target_js_mean", 1.0, "{:.4f}"),
        ]

    raw = np.array([[float(by[m][key]) * scale for _, key, scale, _ in metrics] for m in MAIN], float)
    normalized = raw / np.maximum(raw.max(axis=0, keepdims=True), 1e-15) * 100.0

    fig = plt.figure(figsize=(14, 9 if dataset == "intel" else 9.5))
    gs = fig.add_gridspec(2, 1, height_ratios=[3.45, 1.42], hspace=0.10)
    ax = fig.add_subplot(gs[0])
    x = np.arange(len(metrics))

    for i, (m, lab, color, marker) in enumerate(zip(MAIN, LABELS, COLORS, MARKERS)):
        ax.plot(x, normalized[i], marker=marker, markersize=8.5, linewidth=2.0,
                color=color, markeredgecolor=BLACK, markeredgewidth=0.55, label=lab)
        for j, (_, _, _, fmt) in enumerate(metrics):
            dy = 4.0 if (i + j) % 2 == 0 else -7.0
            ax.annotate(fmt.format(raw[i, j]), (x[j], normalized[i, j]),
                        xytext=(0, dy), textcoords="offset points", ha="center",
                        va="bottom" if dy > 0 else "top", fontsize=7.8,
                        color=color, fontweight="bold")

    ax.set_title(title, pad=12, fontsize=18)
    ax.set_ylabel("Value (% of within-metric maximum)\n[visual scaling only]")
    ax.set_ylim(0, 118)
    ax.set_xticks(x, [m[0] for m in metrics])
    style_axis(ax)
    ax.legend(ncol=len(MAIN), loc="upper center", bbox_to_anchor=(0.5, 1.10),
              frameon=True, edgecolor=BLACK, fancybox=True)

    tab_ax = fig.add_subplot(gs[1])
    columns = ["Method"] + [m[0].replace("\n", " ") for m in metrics]
    rows = []
    for i, lab in enumerate(LABELS):
        rows.append([lab] + [metrics[j][3].format(raw[i, j]) for j in range(len(metrics))])
    table = add_value_table(fig, tab_ax, columns, rows, fontsize=8.3)
    for i, color in enumerate(COLORS, start=1):
        table[(i, 0)].get_text().set_color(color)

    fig.text(0.5, 0.008,
             "Raw held-out means are annotated; normalization is per metric and is not a composite performance score.",
             ha="center", va="bottom", fontsize=8.5, style="italic")
    return save(fig, out_name)

def tradeoff():
    fig, axs = plt.subplots(1, 2, figsize=(13.5, 6.5))
    cases = [
        ("Intel Berkeley Lab", ROOT / "results/intel_lab/aggregate_summary.csv",
         "rmse_c_mean", "RMSE (°C)", False),
        ("UCI HAR", ROOT / "results/uci_har/aggregate_summary.csv",
         "accuracy_mean", "Accuracy", False),
    ]
    for ax, (title, path, ykey, ylabel, pct) in zip(axs, cases):
        by = c09(path)
        relay_max = max(float(by[m]["max_relay_energy_j_mean"]) for m in MAIN)
        for m, lab, color, marker in zip(MAIN, LABELS, COLORS, MARKERS):
            x = float(by[m]["effective_bits_mean"]) / 1e6
            y = float(by[m][ykey]) * (100 if pct else 1)
            relay = float(by[m]["max_relay_energy_j_mean"])
            s = 120 + 720 * relay / max(relay_max, 1e-12)
            ax.scatter(x, y, s=s, color=color, marker=marker, edgecolor=BLACK,
                       linewidth=0.8, alpha=0.88, zorder=3)
            ax.annotate(lab, (x, y), xytext=(7, 7), textcoords="offset points",
                        fontsize=9, fontweight="bold")
        ax.set_title(title + ":\nLearning–Communication Trade-off", fontsize=16)
        ax.set_xlabel("Uplink model-update traffic (Mbit)")
        ax.set_ylabel(ylabel)
        style_axis(ax)

    handles = [plt.Line2D([0], [0], marker=mk, color="w", markerfacecolor=c,
                          markeredgecolor=BLACK, markersize=9, label=l)
               for l, c, mk in zip(LABELS, COLORS, MARKERS)]
    fig.legend(handles=handles, ncol=5, loc="lower center", bbox_to_anchor=(0.5, 0.01),
               frameon=True, edgecolor=BLACK)
    fig.text(0.5, 0.09, "Bubble area scales with maximum relay energy; c = 0.9 held-out means.",
             ha="center", fontsize=9, fontweight="bold")
    fig.tight_layout(rect=(0, 0.12, 1, 1))
    return save(fig, "05_learning_communication_tradeoff.png")

def ablation():
    irows = {r["variant"]: r for r in read(ROOT / "results/intel_lab/ablation_summary.csv")}
    hrows = {r["variant"]: r for r in read(ROOT / "results/uci_har/ablation_summary.csv")}
    variants = ["proposed", "proposed_no_rep", "proposed_fixed_comp", "proposed_age_only", "proposed_no_relay"]
    labels = ["Proposed", "No deficit", "Fixed comp.", "Age-only", "No relay"]
    colors = [GREEN, "#2CA02C", PURPLE, BLUE, RED]
    markers = ["o", "s", "D", "^", "*"]

    fig = plt.figure(figsize=(14, 10))
    outer = fig.add_gridspec(2, 1, hspace=0.20)

    def block(subspec, title, rows, specs):
        sub = subspec.subgridspec(2, 3, height_ratios=[2.25, 1.15], hspace=0.16, wspace=0.28)
        axes = [fig.add_subplot(sub[0, j]) for j in range(3)]
        for ax, (panel_title, key, scale, fmt, ylabel) in zip(axes, specs):
            vals = [float(rows[v][key]) * scale for v in variants]
            for j, (val, c, mk) in enumerate(zip(vals, colors, markers)):
                ax.plot(j, val, marker=mk, markersize=8, color=c, markeredgecolor=BLACK, linewidth=1.6)
                ax.annotate(fmt.format(val), (j, val), xytext=(0, 6), textcoords="offset points",
                            ha="center", fontsize=8, color=c, fontweight="bold")
            ax.set_xticks(range(len(labels)), labels, rotation=0)
            ax.set_title(panel_title, fontsize=12)
            ax.set_ylabel(ylabel)
            style_axis(ax)

        tax = fig.add_subplot(sub[1, :])
        cols = ["Variant"] + [x[0] for x in specs]
        data = []
        for v, lab in zip(variants, labels):
            data.append([lab] + [sp[3].format(float(rows[v][sp[1]]) * sp[2]) for sp in specs])
        table = add_value_table(fig, tax, cols, data, fontsize=8.5)
        for i, c in enumerate(colors, start=1):
            table[(i, 0)].get_text().set_color(c)
        axes[1].text(0.5, 1.32, title, transform=axes[1].transAxes, ha="center",
                     fontsize=17, fontweight="bold")
        return axes

    block(outer[0], "Intel Ablation Study at c = 0.9", irows, [
        ("RMSE (°C)", "rmse_c_mean", 1.0, "{:.4f}", "RMSE (°C)"),
        ("Uplink Traffic (Mbit)", "effective_bits_mean", 1e-6, "{:.3f}", "Mbit"),
        ("Max Relay Energy (J)", "max_relay_energy_j_mean", 1.0, "{:.4f}", "J"),
    ])
    block(outer[1], "UCI HAR Ablation Study at c = 0.9", hrows, [
        ("Accuracy", "accuracy_mean", 1.0, "{:.4f}", "Accuracy"),
        ("Uplink Traffic (Mbit)", "effective_bits_mean", 1e-6, "{:.3f}", "Mbit"),
        ("Max Relay Energy (J)", "max_relay_energy_j_mean", 1.0, "{:.3f}", "J"),
    ])
    return save(fig, "04_ablation.png")

def ns3():
    rows = read(ROOT / "validation/ns3_47_hfl/results/ns3_group_summary.csv")
    methods = ["random", "resource", "utility", "proposed"]
    labels = ["Random", "Resource-only", "Utility-only", "Proposed"]
    colors = [GRAY, BLUE, ORANGE, GREEN]
    markers = ["o", "s", "D", "^"]
    conds = ["dense_nominal", "scale_nominal"]
    clabs = ["Dense nominal", "24-sensor nominal"]

    def row(c, m):
        return next(r for r in rows if r["mapping"] == "hop" and r["condition"] == c and r["method"] == m)

    fig = plt.figure(figsize=(14, 8))
    gs = fig.add_gridspec(2, 3, height_ratios=[3.2, 1.45], hspace=0.15, wspace=0.27)
    specs = [
        ("Report RDR (%)", "report_rdr_pct_mean", "Report RDR (%)", "{:.2f}"),
        ("Delay (ms)", "mean_delivered_report_delay_ms_mean", "Delay (ms)", "{:.2f}"),
        ("Channel-access failures", "channel_access_failures_mean", "Access failures", "{:.1f}"),
    ]
    for k, (title, key, ylabel, fmt) in enumerate(specs):
        ax = fig.add_subplot(gs[0, k])
        for m, lab, color, marker in zip(methods, labels, colors, markers):
            vals = [float(row(c, m)[key]) for c in conds]
            ax.plot(range(2), vals, color=color, marker=marker, markersize=8.5,
                    linewidth=1.8, markeredgecolor=BLACK, markeredgewidth=0.5, label=lab)
            for j, val in enumerate(vals):
                ax.annotate(fmt.format(val), (j, val), xytext=(0, 6 if m != "utility" else -11),
                            textcoords="offset points", ha="center", fontsize=8,
                            color=color, fontweight="bold")
        ax.set_xticks(range(2), clabs)
        ax.set_title(title, fontsize=14)
        ax.set_ylabel(ylabel)
        style_axis(ax)

    fig.axes[0].legend(ncol=4, loc="upper center", bbox_to_anchor=(1.75, 1.22),
                       frameon=True, edgecolor=BLACK)

    tax = fig.add_subplot(gs[1, :])
    columns = ["Method",
               "RDR dense", "RDR 24-sensor",
               "Delay dense", "Delay 24-sensor",
               "Failures dense", "Failures 24-sensor"]
    data = []
    for m, lab in zip(methods, labels):
        rd = row("dense_nominal", m); rs = row("scale_nominal", m)
        data.append([lab,
                     f"{float(rd['report_rdr_pct_mean']):.2f}", f"{float(rs['report_rdr_pct_mean']):.2f}",
                     f"{float(rd['mean_delivered_report_delay_ms_mean']):.2f}", f"{float(rs['mean_delivered_report_delay_ms_mean']):.2f}",
                     f"{float(rd['channel_access_failures_mean']):.1f}", f"{float(rs['channel_access_failures_mean']):.1f}"])
    table = add_value_table(fig, tax, columns, data, fontsize=8.3)
    for i, c in enumerate(colors, start=1):
        table[(i, 0)].get_text().set_color(c)
    fig.suptitle("ns-3.47 LR-WPAN Replay — Hop-equivalent Held-out Traffic", fontsize=18, fontweight="bold", y=0.985)
    return save(fig, "03_ns3_validation.png")

def architecture():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14); ax.set_ylim(0, 10); ax.axis("off")

    layers = [
        (7.55, 2.05, "#EDF6FF", "#135DA8", "Cloud Layer"),
        (5.20, 1.75, "#F2FAF1", "#2C7E38", "Edge Layer"),
        (3.00, 1.65, "#FFF6EA", "#E36C0A", "Multi-hop\nRelay Layer"),
        (0.55, 1.95, "#F5F0FF", "#6B42B5", "Sensor / Client\nLayer"),
    ]
    for y, h, fill, side, label in layers:
        ax.add_patch(FancyBboxPatch((0.15, y), 13.7, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=fill, edgecolor=side, linewidth=1.0, linestyle="--"))
        ax.add_patch(Rectangle((0.15, y), 2.35, h, facecolor=side, edgecolor=side))
        ax.text(1.325, y+h/2, label, color="white", fontsize=19, fontweight="bold",
                ha="center", va="center")

    # cloud
    for cx, cy, rr in [(6.45,8.55,.28),(6.75,8.70,.36),(7.10,8.72,.42),(7.45,8.58,.30)]:
        ax.add_patch(Circle((cx, cy), rr, facecolor="white", edgecolor="#145CAA", linewidth=2.0))
    ax.add_patch(FancyBboxPatch((6.30, 8.28), 1.55, 0.42, boxstyle="round,pad=0.02,rounding_size=0.18",
                                facecolor="white", edgecolor="#145CAA", linewidth=2.0))
    ax.text(7.0, 8.00, "Cloud Server", fontsize=15, fontweight="bold", ha="center")

    gx = [4.0, 6.25, 8.5, 10.75]
    for i, x in enumerate(gx, start=1):
        ax.add_patch(FancyBboxPatch((x-0.5, 5.65), 1.0, 0.62, boxstyle="round,pad=0.04",
                                    facecolor="#CFE6FF", edgecolor="#17375E", linewidth=1.5))
        ax.text(x, 5.96, "GW", fontsize=12, fontweight="bold", ha="center", va="center")
        ax.text(x, 5.43, f"Edge Gateway {i}", fontsize=11, fontweight="bold", ha="center")
        ax.plot([x, x], [6.27, 7.35], color=BLACK, lw=1.1)
        ax.plot([x, 7], [7.35, 7.35], color=BLACK, lw=1.1)

    rx = [4.0, 6.25, 8.5, 10.75]
    for i, x in enumerate(rx, start=1):
        ax.add_patch(FancyBboxPatch((x-0.48, 3.55), 0.96, 0.56, boxstyle="round,pad=0.04",
                                    facecolor="#D8ECF8", edgecolor="#17375E", linewidth=1.5))
        ax.text(x, 3.83, "R", fontsize=13, fontweight="bold", ha="center", va="center")
        ax.text(x, 3.33, f"Relay {i}", fontsize=11, fontweight="bold", ha="center")
        if i < 4:
            ax.add_patch(FancyArrowPatch((x+0.55, 3.83), (rx[i]-0.55, 3.83),
                                        arrowstyle="<->", mutation_scale=11, lw=1.1,
                                        color="#27415C", linestyle="--"))

    sx = [4.0, 6.25, 8.5, 10.75]
    slabels = ["WSN Nodes", "IoT Devices", "Environmental Sensors", "Industrial IoT"]
    for x, lab in zip(sx, slabels):
        ax.add_patch(FancyBboxPatch((x-0.9, 1.0), 1.8, 0.95, boxstyle="round,pad=0.08,rounding_size=0.12",
                                    facecolor="white", edgecolor="#8A5CF6", linewidth=1.2, linestyle="--"))
        for dx, rr in [(-0.35,0.06),(0.0,0.08),(0.35,0.06)]:
            ax.add_patch(Circle((x+dx, 1.58), rr, facecolor="#2D7FF9", edgecolor=BLACK, linewidth=0.5))
        ax.text(x, 1.20, lab, fontsize=10.5, fontweight="bold", ha="center")

    for x in sx:
        ax.add_patch(FancyArrowPatch((x-0.12, 1.96), (x-0.12, 3.48), arrowstyle="-|>",
                                    mutation_scale=16, color=RED, linewidth=1.7, linestyle="--"))
        ax.add_patch(FancyArrowPatch((x+0.18, 3.48), (x+0.18, 1.96), arrowstyle="-|>",
                                    mutation_scale=16, color=BLUE, linewidth=1.7, linestyle="--"))
        ax.add_patch(FancyArrowPatch((x-0.12, 4.12), (x-0.12, 5.60), arrowstyle="-|>",
                                    mutation_scale=16, color=RED, linewidth=1.7, linestyle="--"))
        ax.add_patch(FancyArrowPatch((x+0.18, 5.60), (x+0.18, 4.12), arrowstyle="-|>",
                                    mutation_scale=16, color=BLUE, linewidth=1.7, linestyle="--"))
    ax.add_patch(FancyArrowPatch((6.7, 7.42), (6.7, 7.95), arrowstyle="-|>",
                                mutation_scale=18, color=RED, linewidth=1.8, linestyle="--"))
    ax.add_patch(FancyArrowPatch((7.3, 7.95), (7.3, 7.42), arrowstyle="-|>",
                                mutation_scale=18, color=BLUE, linewidth=1.8, linestyle="--"))
    ax.text(6.37, 7.69, "Uplink", color=RED, fontsize=11, fontweight="bold", ha="right")
    ax.text(7.63, 7.69, "Downlink", color=BLUE, fontsize=11, fontweight="bold", ha="left")
    ax.add_patch(Rectangle((0.02, 0.02), 13.96, 9.96, fill=False, edgecolor=BLACK, linewidth=1.8))
    return save(fig, "02_system_architecture.png")

def topology():
    from src.wsn_hfl.config import SimConfig
    from src.wsn_hfl.intel_lab import IntelLabTopology
    data_dir = ROOT / "data" / "intel_lab"
    topo = IntelLabTopology(data_dir, SimConfig())
    xy = topo.locations[:, 1:3]
    gateways = set(topo.gateway_nodes)
    fig, ax = plt.subplots(figsize=(14, 8.5))

    # show measured bidirectional-connectivity support with conservative threshold
    for i in range(topo.n):
        for j in range(i+1, topo.n):
            delivery = topo.p[i, j] * topo.p[j, i]
            if delivery >= 0.08:
                ax.plot([xy[i,0], xy[j,0]], [xy[i,1], xy[j,1]], linestyle="--",
                        color="#777777", linewidth=0.45, alpha=0.28, zorder=1)
    sensors = [i for i in range(topo.n) if i not in gateways]
    ax.scatter(xy[sensors,0], xy[sensors,1], s=42, c="#2D7FF9", edgecolors=BLACK,
               linewidths=0.45, label="Learning/sensor mote", zorder=3)
    gl = sorted(gateways)
    ax.scatter(xy[gl,0], xy[gl,1], s=105, marker="s", c=RED, edgecolors=BLACK,
               linewidths=0.7, label="Gateway mote", zorder=4)
    for g in gl:
        ax.annotate(f"G{topo.gateway_nodes.index(g)+1}\\n(mote {g+1})", (xy[g,0],xy[g,1]),
                    xytext=(6,6), textcoords="offset points", fontsize=8, fontweight="bold")
    ax.set_title("Intel Berkeley Lab WSN — Measured Topology Abstraction", fontsize=18, pad=12)
    ax.set_xlabel("Measured x-coordinate")
    ax.set_ylabel("Measured y-coordinate")
    ax.grid(color=GRID, linestyle="--", linewidth=0.7, alpha=0.7)
    ax.legend(loc="upper right", frameon=True, edgecolor=BLACK)
    ax.text(0.01, 0.015,
            "Dashed links show bidirectional measured-connectivity support (product ≥ 0.08); routing uses the full measured matrix.",
            transform=ax.transAxes, fontsize=8.5, style="italic", ha="left", va="bottom",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#777777", alpha=0.9))
    for sp in ax.spines.values():
        sp.set_linewidth(1.2); sp.set_color(BLACK)
    return save(fig, "01_network_topology.png")

if __name__ == "__main__":
    topology()
    architecture()
    ns3()
    ablation()
    tradeoff()
    normalized_result_figure("har", "06_uci_har_results.png")
    normalized_result_figure("intel", "07_intel_berkeley_results.png")
    print("Regenerated seven final-choice figures using current held-out results.")
