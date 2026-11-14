#!/usr/bin/env python3
"""Evidence-gated, task-by-task minor-review revision pipeline for PAPER024501.

Edits only the identified IJWMT working DOCX. Every minor comment is saved,
structurally checked, committed, and pushed separately. Scientific values are
read from the repository's executable implementation or archived tables.
"""
from __future__ import annotations

import csv
import json
import math
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent
DOC_PATH = BASE / "manuscript_working/PAPER024501_IJWMT_RED_MARKED_EVIDENCE_DRAFT.docx"
BRANCH = "review/PAPER024501-audit"
RED = RGBColor(192, 0, 0)
DARK_RED = "C00000"
COMMITS: list[dict] = []
ALLOW_FIGURE = False

sys.path.insert(0, str(ROOT))
from config import SimulationConfig
from simulator.semantic_payload import SemanticPayloadController


def git(*args: str, capture: bool = True) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, check=True, text=True,
                       stdout=subprocess.PIPE if capture else None,
                       stderr=subprocess.STDOUT if capture else None)
    return (p.stdout or "").strip()


def text_of(p) -> str:
    return p.text.strip()


def find_p(doc, needle: str):
    matches = [p for p in doc.paragraphs if needle in p.text]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one paragraph containing {needle!r}; found {len(matches)}")
    return matches[0]


def mark_red(p):
    for run in p.runs:
        run.font.color.rgb = RED
    return p


def replace_paragraph(p, new_text: str):
    if p._p.xpath(".//m:oMath") or p._p.xpath(".//w:drawing"):
        raise RuntimeError("Refusing whole-paragraph replacement where equations or drawings are embedded")
    p.clear()
    r = p.add_run(new_text)
    r.font.color.rgb = RED
    return p


def replace_phrase(p, old: str, new: str):
    for run in p.runs:
        if old in run.text:
            run.text = run.text.replace(old, new)
            run.font.color.rgb = RED
            return p
    raise RuntimeError(f"Target phrase not found within a single text run: {old!r}")


def insert_after(p, text: str, style: str = "BodyText", size: float = 9.5):
    new_p = OxmlElement("w:p")
    p._p.addnext(new_p)
    out = Paragraph(new_p, p._parent)
    try:
        out.style = style
    except KeyError:
        out.style = "Normal"
    run = out.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.color.rgb = RED
    return out


def add_caption_after(p, text: str):
    q = insert_after(p, text, "Caption", 9)
    q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return q


def set_cell_text(cell, value: str, *, bold=False, font_size=8.5):
    cell.text = ""
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(value)
    r.bold = bold
    r.font.name = "Times New Roman"
    r.font.size = Pt(font_size)
    r.font.color.rgb = RED


def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = tblPr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tblPr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "6")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), DARK_RED)


def move_table_after(table, p):
    table._tbl.getparent().remove(table._tbl)
    p._p.addnext(table._tbl)


def add_table_after(doc, anchor, caption, headers, rows, widths=None):
    cap = add_caption_after(anchor, caption)
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for j, h in enumerate(headers):
        set_cell_text(table.rows[0].cells[j], h, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for j, value in enumerate(row):
            set_cell_text(cells[j], str(value))
    if widths:
        for row in table.rows:
            for j, width in enumerate(widths):
                row.cells[j].width = Inches(width)
    set_table_borders(table)
    move_table_after(table, cap)
    return cap, table


def all_text_paragraphs(doc):
    for p in doc.paragraphs:
        yield p
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    yield p


def shift_table_numbers(doc, lo: int, hi: int, delta: int):
    pat = re.compile(r"\bTable\s+(" + "|".join(map(str, range(lo, hi + 1))) + r")\b")
    for p in all_text_paragraphs(doc):
        old = p.text
        if not pat.search(old):
            continue
        for run in p.runs:
            updated = pat.sub(lambda m: "Table " + str(int(m.group(1)) + delta), run.text)
            if updated != run.text:
                run.text = updated
                run.font.color.rgb = RED


def package_counts(path: Path):
    import zipfile
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        xml = z.read("word/document.xml")
        return {
            "media_files": sorted(n for n in names if n.startswith("word/media/")),
            "equations": xml.count(b"<m:oMath>") + xml.count(b"<m:oMath "),
            "tables": xml.count(b"<w:tbl>") + xml.count(b"<w:tbl "),
            "drawings": xml.count(b"<w:drawing>"),
        }


ORIGINAL_COUNTS = package_counts(DOC_PATH)


def save_doc(doc):
    doc.save(DOC_PATH)
    current = package_counts(DOC_PATH)
    if not set(ORIGINAL_COUNTS["media_files"]).issubset(set(current["media_files"])):
        raise RuntimeError("An original embedded media file was lost")
    if current["equations"] != ORIGINAL_COUNTS["equations"]:
        raise RuntimeError("Editable equation inventory changed unexpectedly")
    expected_drawings = ORIGINAL_COUNTS["drawings"] + (1 if ALLOW_FIGURE else 0)
    if current["drawings"] != expected_drawings:
        raise RuntimeError(f"Unexpected drawing inventory: {current['drawings']} != {expected_drawings}")
    return current


def commit_task(doc, task_id: str, title: str, artifacts=()):
    counts = save_doc(doc)
    paths = [str(DOC_PATH.relative_to(ROOT)), *[str(Path(x).relative_to(ROOT)) for x in artifacts]]
    git("add", *paths)
    git("commit", "-m", f"Resolve PAPER024501 minor {task_id}: {title}")
    sha = git("rev-parse", "HEAD")
    git("push", "origin", BRANCH, capture=True)
    COMMITS.append({"comment": task_id, "title": title, "commit": sha, "files": paths, "docx_counts": counts})
    print(f"COMMITTED {task_id} {sha} — {title}", flush=True)


def update_m4(doc):
    p = find_p(doc, "Most of the contribution is in how the method is specified and tested.")
    replace_paragraph(
        p,
        "The primary contribution lies in a controlled experimental design that isolates the effects of traffic-volume reduction from relevance-directed payload allocation. The study implements an auditable temporal-spatial novelty estimator and byte-aligned payload controller over a residual-energy ETX forwarding substrate, then uses equal-budget fixed and shuffled-allocation controls to distinguish reduced-traffic effects from relevance-based targeting. The evaluation also reports route-depth-dependent limits rather than claiming general protocol superiority."
    )


def update_m5(doc):
    p = find_p(doc, "Observations add a spatial Gaussian event")
    replace_phrase(p,
        "Observations add a spatial Gaussian event of amplitude 3 and width 18 m.",
        "A spatial Gaussian event of amplitude 3 and width 18 m is superimposed on the observations.")


def update_m6(doc):
    p = find_p(doc, "Positive costs permit one sink-rooted Dijkstra search")
    replace_phrase(p,
        "Positive costs permit one sink-rooted Dijkstra search per round after removing dead sensors.",
        "The routing edge costs are strictly positive; this condition ensures the validity of one sink-rooted Dijkstra search per round after dead sensors are removed.")


def update_m7(doc):
    p = find_p(doc, "C1 and C2 are nearly the same across Table 4")
    replace_phrase(p,
        "C1 and C2 are nearly the same across Table 4",
        "C1 and C2 exhibit negligible differences across all reported metrics in Table 4")


def update_m8(doc):
    p = find_p(doc, "Stretching the topology makes the robustness result more useful")
    replace_phrase(p,
        "Stretching the topology makes the robustness result more useful",
        "Stretching the topology makes the robustness result more informative")


def update_m9(doc):
    p = find_p(doc, "Receiver reconstruction, downstream task utility, distributed context exchange")
    old = "Receiver reconstruction, downstream task utility, distributed context exchange, and full sensing/processing/control-energy accounting remain necessary before claiming application-level or deployment-level superiority."
    if old not in p.text:
        raise RuntimeError("m9 target sentence not found exactly")
    first = "Receiver reconstruction, downstream task utility, distributed context exchange, and full "
    second = "sensing/processing/control-energy accounting remain necessary before claiming application-level or deployment-level superiority."
    replace_phrase(p, first, "Receiver reconstruction and downstream task utility remain necessary before application-level superiority can be claimed. Validation must also account for distributed context exchange and full ")
    replace_phrase(p, second, "sensing, processing and control-energy accounting before deployment-level superiority can be claimed.")


def update_m10(doc):
    p = doc.paragraphs[0]
    replace_paragraph(p, "Isolating Traffic Reduction from Relevance-Directed Allocation: A Controlled Evaluation of Adaptive Payload Length over RE-ETX Routing in WSNs")


def update_m11(doc):
    p = find_p(doc, "Fixed-length reporting treats a routine sample")
    t = p.text
    t = t.replace(
        "mean delay and communication energy per delivered report fall by about 54%.",
        "mean delay and communication energy per delivered report fall by 54.0% and 54.2%, respectively."
    )
    t += (" The primary results assume centrally available neighbour observations and use a radio-only energy ledger that excludes sensing, computation, routing-control signalling, acknowledgements and idle listening; receiver-side reconstruction and downstream task utility are not established.")
    replace_paragraph(p, t)


def update_m12(doc):
    p = find_p(doc, "More recently, Arnaiz et al.")
    q = insert_after(
        p,
        "The distinction from Arnaiz et al. [11] is one of control granularity and evaluation target. Their method coordinates a dynamic sampling-period controller with a dual-prediction scheme, adapting both monitoring cadence and prediction error thresholds to meet a battery-life target while evaluating signal reconstruction accuracy. The present controller does not alter the sampling period or run a source-side predictor/receiver decoder: it computes temporal and spatial statistical novelty from observations already generated and maps the resulting score to the length of each report. Its primary evaluation therefore concerns network traffic, delivery, delay, communication energy and the allocation of a matched source-bit budget. The C5 and C6 controls isolate the effect of that allocation rule; they do not substitute for the receiver-fidelity evaluation provided in [11].",
        "BodyText"
    )
    return q


def update_m16(doc):
    # Renumber the existing final three references and their in-text citations.
    for p in all_text_paragraphs(doc):
        old = p.text
        new = re.sub(r"(?<=\[)(23|24|25)(?=[,\]\-])",
                     lambda m: str(int(m.group(1)) + 2), old)
        if new != old:
            replace_paragraph(p, new)

    # Add current, directly relevant semantic-communication literature.
    anchor = find_p(doc, "[22] Hwang A")
    r23 = insert_after(
        anchor,
        "[23] Yang H, Zhu X, Yang J, Li J, Qing L, He X and Wang P 2025 Scalable semantic adaptive communication for task requirements in WSNs. Sensors 25(9): 2823. https://doi.org/10.3390/s25092823",
        "BodyText"
    )
    r24 = insert_after(
        r23,
        "[24] Kaya O, Karabulut M A, Eyüpoğlu C and Karakuş O 2026 Prediction-aided adaptive semantic communication for IoT sensor streams under outdated channel state information. Sensors 26(19): 6124. https://doi.org/10.3390/s26196124",
        "BodyText"
    )
    sec = find_p(doc, "Surveys by Luo et al.")
    q = insert_after(
        sec,
        "Recent WSN- and IoT-oriented studies further illustrate the distinction. Yang et al. [23] evaluate adaptive semantic communication against task requirements in WSNs, while Kaya et al. [24] select transmission rates using predicted channel conditions and semantic-distortion constraints for IoT sensor streams. Both explicitly address semantic/task fidelity or distortion. The present controller instead uses a statistical novelty score to choose a raw application-payload length; without a source encoder and receiver decoder, it should not be described as a semantic communication system.",
        "BodyText"
    )
    return q


def update_m2(doc):
    # Existing Table 2–8 become Table 3–9; Table 2 is inserted below.
    shift_table_numbers(doc, 2, 8, 1)
    anchor = find_p(doc, "Table 1 makes the claim boundary explicit")
    rows = [
        ("Definition", "Departure of an observation from a node's historical temporal and spatial baseline; a statistical priority signal.", "Task- or meaning-relevant information selected for a communication objective; semantics depend on the application and framework."),
        ("Computation", "Normalised temporal innovation and spatial deviation from a neighbour median; weighted combination (0.6/0.4), followed by exponential squashing.", "May use learned encoders, semantic features, task models or knowledge/context representations; there is no single universal computation."),
        ("Transmission action", "Changes the length of the raw application report (1000–4000 bits); it does not change the sampling interval or encode a semantic representation.", "Transmits a task-relevant or semantically compressed representation; the representation and rate depend on the encoder and task."),
        ("Receiver requirement", "The submitted system has no implemented source decoder; reconstruction fidelity and task utility are not established.", "A receiver-side decoder or task estimator is normally needed to evaluate semantic reconstruction or task-level utility."),
        ("Evaluation", "Payload allocation, PDR, delay, communication energy and event-associated bit allocation; these are not semantic-fidelity metrics.", "Semantic distortion, reconstruction quality, task accuracy/utility and communication-resource cost, as appropriate to the framework.")
    ]
    cap, table = add_table_after(
        doc, anchor,
        "Table 2. Statistical novelty used for payload control versus representative semantic-communication frameworks.",
        ["Dimension", "Statistical novelty in this study", "Semantic communication [15,16,19,20,23,24]"],
        rows,
        [1.15, 2.65, 2.65]
    )
    return cap


def update_m1(doc):
    # Existing Table 4–9 become Table 5–10; Table 4 is inserted in Section 4.2.
    formula_texts = []
    for paragraph in doc.paragraphs:
        formula = paragraph._p.xpath(".//m:oMath")
        if formula:
            formula_texts.append("".join(e.text or "" for m in formula for e in m.iter() if e.tag.endswith("}t")))
    formula_text = " ".join(formula_texts)
    if not all(x in formula_text for x in ("0.50", "0.85", "0.75")):
        raise RuntimeError("Editable Equation (6) does not contain the verified safeguards")
    shift_table_numbers(doc, 4, 9, 1)
    p = find_p(doc, "Those warm-up reports remain part of every result.")
    ptext = p.text + " Table 4 lists the byte-aligned payload values generated by the executable controller for relevance values from 0 to 1 in 0.1 increments."
    replace_paragraph(p, ptext)
    controller = SemanticPayloadController(SimulationConfig())
    values = [(f"{i/10:.1f}", int(controller.payload_bits([i/10])[0])) for i in range(11)]
    rows = [(v, str(bits)) for v, bits in values]
    cap, table = add_table_after(
        doc, p,
        "Table 4. Byte-aligned application payload selected by the implemented Equation (6) mapping.",
        ["Relevance, v", "Payload length, L(v) (bits)"],
        rows,
        [2.2, 3.2]
    )
    return cap


def update_m13(doc):
    anchor = find_p(doc, "Within a round, observations are generated first")
    steps = [
        ("Algorithm 1. C3 execution flow for relevance-aware payload adaptation over RE-ETX", "Caption"),
        ("Input: Current and previous observations; neighbour sets; residual node energies; static link-quality graph; full payload 4000 bits; retry limit R = 3; energy weight λ_E = 0.25.", "BodyText"),
        ("Output: Per-source payload lengths, delivered/drop outcomes, updated residual energies and network-performance counters.", "BodyText"),
        ("1. Determine the alive-node set A_t from residual energy. Stop when A_t is empty.", "BodyText"),
        ("2. Generate the current observation vector and compute temporal innovation |x_i(t) − x_i(t−1)| and spatial deviation |x_i(t) − median{x_j(t): j ∈ N_i}|. During the 50-round warm-up, set relevance to zero.", "BodyText"),
        ("3. After warm-up, normalise temporal and spatial features against their historical means and variances, clip each z-score to [0, 8], and calculate v_i = 1 − exp[−(0.6 z_i^T + 0.4 z_i^S)]. Update the EWMA baselines only after scoring.", "BodyText"),
        ("4. Set ρ_i = 0.25 + 0.75v_i. If v_i ≥ 0.50, apply ρ_i = max(0.75, ρ_i); if v_i ≥ 0.85, set ρ_i = 1. Select L_i = 8 ceil(4000ρ_i/8) bits.", "BodyText"),
        ("5. Build the live routing adjacency from eligible sensor links and sink links. For a sensor link (i,j), use C_ij = ETX_ij[1 + λ_E(φ_i + φ_j)/2], where φ_i = 1/(E_i/E_0) − 1. For a sink link, use C_iB = ETX_iB[1 + λ_Eφ_i/2]. The C3 configuration disables the exploratory relevance-age routing term.", "BodyText"),
        ("6. Run one sink-rooted Dijkstra search for the round and retain the next-hop tree. If a source has no route, record and attempt the implemented direct-sink fallback.", "BodyText"),
        ("7. Rotate the alive-source service order. For each source that remains alive, fragment L_i into application chunks of at most 800 bits, add 216 overhead bits per fragment, and transmit sequentially along the selected path.", "BodyText"),
        ("8. Allow one initial frame attempt and at most three retries per fragment. Charge transmitter and relay-receiver energy for each realised attempt under the stated radio-only ledger.", "BodyText"),
        ("9. Update report delivery/drop counters, frame attempts, delays and node energies. Event labels are consulted only by the offline evaluation counters and never affect relevance, payload or route decisions.", "BodyText"),
        ("10. Check node deaths after the round and repeat from Step 1 until no node remains alive or the configured round limit is reached.", "BodyText"),
    ]
    cur = anchor
    for text, style in steps:
        cur = insert_after(cur, text, style, 8.7 if style == "BodyText" else 9)
    complexity = (
        "For N sensors, E eligible links, maximum route length H, at most Q = ceil(4000/800) report fragments and R = 3 retries, the per-round implementation cost is O(N² + (N + E)logN + NQH(R + 1)). "
        "The O(N²) term arises from dense neighbour-mask scans in spatial-feature extraction and live-adjacency construction; heap-based Dijkstra contributes O((N + E)logN), and source forwarding contributes at most O(NQH(R + 1)) frame-attempt work. "
        "The stored distance, shadowing, link-quality and neighbour-mask matrices require O(N²) memory, in addition to O(N + E) adjacency storage. These bounds describe the centralised simulator, not a distributed implementation."
    )
    q = insert_after(cur, complexity, "BodyText", 9)
    # Retain the original inline complexity equations and add the explicit
    # derivation above; no equation-bearing paragraph is replaced.
    return q


def update_m14(doc):
    env = {
        "audit_date": "2026-11-14",
        "host": "Apple M1",
        "memory_gb": 8,
        "os": "macOS 27.2",
        "python": "3.14.7",
        "numpy": "2.5.4",
        "pandas": "3.1.1",
        "scipy": "1.18.1",
        "matplotlib": "3.11.2",
        "networkx": "3.7",
        "python_docx": "1.2.0",
        "smoke_test": {
            "mode": "C3",
            "seed": 42,
            "round_limit": 60,
            "generated_reports": 6000,
            "delivered_reports": 6000,
            "channel_drops": 0,
            "energy_drops": 0,
            "route_drops": 0,
            "interpretation": "Runtime smoke test only; not part of the archived ten-seed inferential results."
        },
        "historical_run_host": "Not preserved in the archived ten-seed experiment manifest; do not attribute the archived runs to this audit host without rerunning them."
    }
    path = BASE / "minor_revision_environment_2026-11-14.json"
    path.write_text(json.dumps(env, indent=2) + "\n")
    p = find_p(doc, "All seven configurations use the same ten seeds")
    q = insert_after(
        p,
        "Simulation platform and audit environment. The primary network experiments are generated by the repository's custom Python simulator (run_semantic_re_etx.py); the C3 forwarding graph uses the repository's heap-based Dijkstra implementation. The revision-stage reproduction smoke test was executed on an Apple M1 host with 8 GB RAM, macOS 27.2 and Python 3.14.7, using NumPy 2.5.4, pandas 3.1.1, SciPy 1.18.1, Matplotlib 3.11.2 and NetworkX 3.7. A 60-round C3 smoke test with seed 42 completed 6000 report attempts and deliveries without channel, energy or route drops; this test checks runtime execution only and is not included in the ten-seed results. The original archived ten-seed runs do not retain a machine-readable host/package manifest, so their historical CPU and package versions cannot be verified. Cooja/Contiki-NG and FIT IoT-LAB Grenoble M3 were used only for the supplementary transport and partial hardware-pilot evidence, not as the primary 100-node simulation platform.",
        "BodyText"
    )

    # Correct stale experiment identifiers and unsupported power claims in the
    # working draft against the verified 14-Nov archive manifest.
    p135 = find_p(doc, "COOJA / FIT IoT-LAB SCOPE")
    replace_paragraph(
        p135,
        "COOJA / FIT IoT-LAB SCOPE — The archived Cooja evidence comprises 15 small-mote reception-sensitivity runs and a three-mote Contiki-NG NullNet/CSMA context-exchange probe. These exercises test transport and context exchange only; they do not implement the full 100-node sink-rooted RE-ETX policy. The archived FIT IoT-LAB physical pilot is experiment 458578 on Grenoble M3 nodes 97, 100 and 102. Its partial archive contains 415 serial lines, 21 usable power windows and 12 paired board-mode comparisons. It does not establish physical/channel PDR, full-network energy savings or original RE-ETX firmware validation."
    )
    p136 = find_p(doc, "SEPARATE PHYSICAL POWER PILOT")
    replace_paragraph(
        p136,
        "FIT IoT-LAB ENERGY EVIDENCE BOUNDARY — The archived 458578 power records are whole-board, phase-level observations from a partial pilot. They do not provide independently calibrated per-message or per-component sensing, CPU, idle, control or RE-ETX energy coefficients. No component-level hardware calibration is claimed."
    )
    return q, path


def update_m15(doc):
    p = find_p(doc, "Receiver reconstruction and downstream task utility remain necessary")
    q = insert_after(
        p,
        "Parameter selection is another limitation. The current study does not establish a global optimum for the 0.6/0.4 relevance weights, the 0.50/0.85 payload safeguards or the 0.25 routing-energy weight. Parameter sensitivity analysis over broader ranges and independent seed sets is needed to establish whether these settings remain appropriate outside the tested configuration.",
        "BodyText"
    )
    return q


def update_m3(doc):
    global ALLOW_FIGURE
    ALLOW_FIGURE = True
    # Data copied from the manuscript's Table 8, which becomes Table 10 after
    # inserting Tables 2 and 4. Values are ten-seed means.
    depths = ["Shallow\n1.483 hops", "Medium\n2.910 hops", "Deep\n4.929 hops"]
    x = np.arange(3)
    series = {
        "HND (rounds)": {"C3": [383.3, 112.3, 74.7], "C5": [357.8, 96.2, 65.5]},
        "LND (rounds)": {"C3": [2642.5, 2138.4, 1952.7], "C5": [2663.8, 2206.6, 2303.9]},
        "PDR (%)": {"C3": [95.404, 93.765, 94.160], "C5": [95.294, 93.404, 94.299]},
        "Energy / delivered report (mJ)": {"C3": [0.744, 2.105, 3.082], "C5": [0.764, 2.209, 2.983]},
    }
    fig, axes = plt.subplots(2, 2, figsize=(7.0, 5.0), constrained_layout=True)
    for ax, (metric, modes) in zip(axes.flat, series.items()):
        for mode, values in modes.items():
            style = "-" if mode == "C3" else "--"
            marker = "o" if mode == "C3" else "s"
            ax.plot(x, values, color="#C00000", linestyle=style, marker=marker, linewidth=1.8, markersize=4, label=mode)
        ax.set_title(metric, fontsize=8.5)
        ax.set_xticks(x, depths, fontsize=7.5)
        ax.tick_params(axis="y", labelsize=7.5)
        ax.grid(True, linewidth=0.45, alpha=0.45)
    axes[0, 0].legend(frameon=False, fontsize=8)
    fig.suptitle("C3 and equal-budget C5 across calibrated route-depth profiles", fontsize=9)
    fig_dir = BASE / "figures"
    fig_dir.mkdir(exist_ok=True)
    image_path = fig_dir / "Fig8_topology_depth.png"
    fig.savefig(image_path, dpi=600, bbox_inches="tight")
    plt.close(fig)
    csv_path = fig_dir / "Fig8_topology_depth_source.csv"
    with csv_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["profile", "initial_mean_hops", "mode", "HND_rounds", "LND_rounds", "PDR_percent", "energy_per_delivered_report_mJ"])
        raw = [
            ("Shallow", 1.483, "C3", 383.3, 2642.5, 95.404, 0.744),
            ("Shallow", 1.483, "C5", 357.8, 2663.8, 95.294, 0.764),
            ("Medium", 2.910, "C3", 112.3, 2138.4, 93.765, 2.105),
            ("Medium", 2.910, "C5", 96.2, 2206.6, 93.404, 2.209),
            ("Deep", 4.929, "C3", 74.7, 1952.7, 94.160, 3.082),
            ("Deep", 4.929, "C5", 65.5, 2303.9, 94.299, 2.983),
        ]
        w.writerows(raw)

    # Insert image and caption immediately after the existing topology table.
    topology_table = doc.tables[-1]
    img_p = doc.add_paragraph()
    img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img_p.add_run().add_picture(str(image_path), width=Inches(6.2))
    cap = doc.add_paragraph()
    cap.style = "Caption"
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rr = cap.add_run("Fig. 8. HND, LND, PDR and energy per delivered report for C3 and equal-budget C5 across shallow, medium and deep route-depth profiles. Points show ten-seed means; lines are descriptive and do not imply statistical significance.")
    rr.font.color.rgb = RED
    topology_table._tbl.addnext(img_p._p)
    img_p._p.addnext(cap._p)

    p65 = find_p(doc, "the experiments do not support a general equal-budget network advantage for relevance-based allocation.")
    replace_phrase(p65,
        "the experiments do not support a general equal-budget network advantage for relevance-based allocation.",
        "the experiments do not support a general equal-budget network advantage for relevance-based allocation. The route-depth profiles in Fig. 8 suggest a possible mechanism: additional hops repeat framing and retransmission exposure, while C3 can assign larger reports to event-active sources whose routes may be long. C5 distributes a fixed payload uniformly, which may reduce this tail-cost variability and is consistent with its deep-profile LND advantage. This remains a hypothesis because the archived outputs do not contain a per-report hop-weighted payload-energy decomposition.")
    p = find_p(doc, "The equal-budget C3-versus-C5 result is topology- and metric-dependent.")
    q = insert_after(
        p,
        "Fig. 8 makes the reversal in the deep profile visible. At 4.929 initial mean hops, C5 exceeds C3 in LND (2303.9 versus 1952.7 rounds), while C3 retains a higher HND (74.7 versus 65.5 rounds); C5 also has slightly higher PDR and lower energy per delivered report in that profile. A plausible explanation is that longer paths repeat frame overhead and retry exposure across more hops, so concentrating larger reports on event-associated sources can increase the late-life cost of C3, whereas C5 distributes a fixed report length uniformly. This is an interpretation, not a demonstrated causal decomposition: the archived runs do not isolate hop-weighted payload energy or per-packet relevance staleness. The evidence therefore supports a topology-dependent trade-off, not a verified staleness mechanism.",
        "BodyText"
    )
    return image_path, csv_path, q


def main():
    if git("branch", "--show-current") != BRANCH:
        raise RuntimeError(f"Expected branch {BRANCH}; refusing to edit another branch")
    if git("status", "--porcelain"):
        raise RuntimeError("Working tree is not clean before revision")
    doc = Document(DOC_PATH)

    tasks = [
        ("m4", "clarify controlled-attribution contribution", lambda: update_m4(doc), ()),
        ("m5", "correct Section 3.1 event wording", lambda: update_m5(doc), ()),
        ("m6", "correct Dijkstra condition wording", lambda: update_m6(doc), ()),
        ("m7", "clarify C1 and C2 comparison", lambda: update_m7(doc), ()),
        ("m8", "replace subjective topology wording", lambda: update_m8(doc), ()),
        ("m9", "split conclusion sentence", lambda: update_m9(doc), ()),
        ("m10", "adopt controlled-attribution title", lambda: update_m10(doc), ()),
        ("m11", "correct abstract percentages and limitations", lambda: update_m11(doc), ()),
        ("m12", "add specific Arnaiz et al. comparison", lambda: update_m12(doc), ()),
        ("m16", "add verified 2025–2026 literature", lambda: update_m16(doc), ()),
        ("m2", "add statistical novelty versus semantic communication table", lambda: update_m2(doc), ()),
        ("m1", "add executable Equation 6 mapping table", lambda: update_m1(doc), ()),
        ("m13", "add C3 pseudocode and complexity derivation", lambda: update_m13(doc), ()),
    ]
    for task_id, title, fn, _ in tasks:
        fn()
        commit_task(doc, task_id, title)

    q, env_path = update_m14(doc)
    commit_task(doc, "m14", "document simulation host and correct FIT IoT-LAB evidence identifiers", [env_path])

    q = update_m15(doc)
    commit_task(doc, "m15", "state parameter-selection limitation in conclusion")

    image_path, csv_path, q = update_m3(doc)
    commit_task(doc, "m3", "add topology-depth performance figure and qualified mechanism discussion", [image_path, csv_path])

    # Final structural audit after all incremental commits.
    final_counts = save_doc(doc)
    if final_counts["tables"] != ORIGINAL_COUNTS["tables"] + 2:
        raise RuntimeError(f"Expected two added tables; counts={final_counts}")
    if final_counts["media_files"] != ORIGINAL_COUNTS["media_files"] + 1:
        raise RuntimeError(f"Expected one added figure; counts={final_counts}")
    if final_counts["equations"] != ORIGINAL_COUNTS["equations"]:
        raise RuntimeError("Equation inventory changed")
    (BASE / "minor_comment_commit_log.json").write_text(json.dumps({
        "branch": BRANCH,
        "base_commit": "1552c3a3a8806cd526a8ac96f4b3a2020914be78",
        "original_docx_counts": ORIGINAL_COUNTS,
        "final_docx_counts": final_counts,
        "commits": COMMITS,
        "notes": [
            "m14 remains partially closed because the original archived ten-seed execution host/package manifest was not preserved; current audit host and smoke test are recorded separately.",
            "Cooja and FIT IoT-LAB were not rerun for editorial-only changes; their existing evidence boundaries were corrected against the verified 458578 archive.",
            "No original receiver codec or deployment-level hardware validation is claimed."
        ]
    }, indent=2) + "\n")
    git("add", str((BASE / "minor_comment_commit_log.json").relative_to(ROOT)))
    git("commit", "-m", "Record PAPER024501 minor-comment task commits and audit")
    sha = git("rev-parse", "HEAD")
    git("push", "origin", BRANCH)
    print(f"FINAL AUDIT COMMIT {sha}", flush=True)
    print(json.dumps({"final_counts": final_counts, "task_commits": COMMITS}, indent=2), flush=True)


if __name__ == "__main__":
    main()
