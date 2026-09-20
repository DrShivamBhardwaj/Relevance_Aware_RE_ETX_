from pathlib import Path
import re, shutil, zipfile, os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "submission" / "nexus"
LATEX = OUT / "latex"
OUT.mkdir(parents=True, exist_ok=True)
LATEX.mkdir(parents=True, exist_ok=True)
(LATEX / "figures").mkdir(parents=True, exist_ok=True)

TITLE = "Cross-Layer Edge Intelligence for Statistically Representative and Resource-Sustainable Federated Learning in Multi-Hop IoT Sensor Networks"
HIGHLIGHTS = [
    "Cross-layer scheduling links learning value to multi-hop network cost",
    "Virtual queues reduce persistent exclusion of informative clients",
    "Adaptive update fidelity cuts communication by 56-61% on real sensing data",
    "Lower model traffic improves low-power wireless delivery and delay",
]
IN_BRIEF = ("Pandey and Bhardwaj show that choosing federated-learning clients only because "
            "they are cheap to reach can distort which sensing data shape the model. Their "
            "cross-layer controller balances statistical value, update fidelity, multi-hop "
            "route burden, and relay energy across real sensing datasets and low-power wireless replay.")
BROADER = (
    "Edge intelligence is moving learning closer to the places where data are produced, including "
    "buildings, industrial sites, environmental deployments, and personal sensing devices. In these "
    "settings, the communication path is part of the learning system rather than a neutral transport "
    "layer. A model update from a remote or poorly connected device may consume several relay "
    "transmissions, yet that same device may hold observations that are rare elsewhere in the network. "
    "Scheduling only the cheapest devices can therefore save energy in the short term while narrowing "
    "the data that influence the model. This study treats that tension as a cross-layer design problem. "
    "The proposed controller considers learning value, participation history, multi-hop route burden, "
    "relay-energy pressure, update compression, and staleness together. The resulting trade-offs are "
    "tested with a real wireless-sensor deployment, a real human-activity dataset, controlled synthetic "
    "heterogeneity, and low-power wireless-network replay. The broader aim is resource-conscious edge "
    "intelligence that remains statistically inclusive when network conditions and data distributions "
    "are both uneven."
)

FIGURES = [
    ("figures/final/02_system_architecture.png", "Figure 1. Cross-layer hierarchical architecture used in this study. Learning-capable sensor clients exchange model updates through relay and edge layers before cloud aggregation."),
    ("figures/final/01_network_topology.png", "Figure 2. Network-topology abstraction used for the Intel Berkeley Lab WSN experiment. Gateway nodes form the edge layer, while measured connectivity informs route feasibility and cost."),
    ("figures/final/07_intel_berkeley_results.png", "Figure 3. Intel Berkeley Lab comparison under strong resource-data correlation (c = 0.9). Exact values and 95% confidence intervals are reported in Table 2."),
    ("figures/final/06_uci_har_results.png", "Figure 4. UCI HAR comparison under strong resource-data correlation (c = 0.9). The resource-only policy minimizes the relay hotspot, whereas the proposed policy improves learning, communication, total modeled energy, and representation."),
    ("figures/final/04_ablation.png", "Figure 5. Component ablation on the Intel WSN and UCI HAR experiments. Removing representation control, adaptive compression, or relay pressure changes different parts of the learning-network trade-off."),
    ("figures/final/03_ns3_validation.png", "Figure 6. ns-3.47 IEEE 802.15.4/LR-WPAN replay of the frozen traffic profiles. The replay validates communication consequences of the offered load; the HFL optimizer itself is not executed inside ns-3."),
    ("figures/final/05_learning_communication_tradeoff.png", "Figure 7. Learning-communication trade-off on the two real sensing datasets. Bubble size represents maximum relay energy and makes the relay-hotspot cost visible alongside model quality and traffic.")
]
def transform_source():
    src = (ROOT / "MANUSCRIPT_RECONSTRUCTION.md").read_text()
    src = re.sub(r"^# .*?\n", "", src, count=1)
    src = src.split("## Final manuscript figure set")[0].rstrip()
    src = src.replace("## References used for positioning", "## References")
    src = src.replace(
        "The synchronization and heterogeneity dimensions are similarly active. HiFlash combines adaptive staleness control with heterogeneity-aware client-edge association [5], while asynchronous HFL variants reduce blocking due to heterogeneous completion times. Communication-efficient HFL has additionally been studied through data-distribution shaping at the edge [7]. Recent HFL formulations jointly optimize client selection, edge scheduling, radio resources, and semi-synchronous operation [8].",
        "The synchronization and heterogeneity dimensions are similarly active. HiFlash combines adaptive staleness control with heterogeneity-aware client-edge association [5], while communication-efficient HFL has also been studied by shaping data distributions at edge aggregators [7]. Wu et al. jointly consider client selection, edge-side decisions, radio resources, and time-energy cost in NOMA-enabled HFL [8]. These studies leave little room for treating hierarchy, staleness control, or a generic resource score as stand-alone novelty."
    )
    src = src.replace(
        "A second literature branch shows that biased client selection can affect statistical coverage under non-IID data. Fairness-aware client-selection work introduces long-term participation considerations [4], and recent surveys emphasize that system heterogeneity can restrict the participation or influence of clients that possess valuable but resource-constrained data [9]. Adaptive compression also overlaps with statistical heterogeneity: FedCG-type methods combine representative client selection with capability-aware gradient compression [6].",
        "A second literature branch shows that biased client selection can affect statistical coverage under non-IID data. Huang et al. explicitly balance effective participation and fairness when clients are volatile [4], while FedCG combines representative client selection with adaptive gradient compression [6]. Recent fairness analyses likewise stress that system heterogeneity can restrict the participation or influence of clients whose data remain statistically useful [13]."
    )
    src = src.replace(
        "The present study therefore does **not** claim novelty for ETX routing, resource-aware selection, compression, or staleness individually. Its contribution is their cross-layer coupling with **statistical representation and relay-energy externality** in a multi-hop WSN-HFL setting, evaluated with both real sensing data and measured WSN connectivity.",
        "Multi-hop FL itself is also established. Prior work has considered in-network aggregation with routing and spectrum allocation [9], routing-aware acceleration on physical wireless-edge testbeds [10], and two-hop HFL with adaptive grouping and resource allocation [11]; a recent survey organizes these and related topology-aware designs [12]. The present study therefore does **not** claim novelty for ETX routing, multi-hop FL, resource-aware selection, compression, or staleness individually. Its contribution is the coupling of learning value and participation history with **statistical representation and relay-energy externality** in a multi-hop WSN-HFL setting, evaluated with real sensing data and measured WSN connectivity."
    )
    src = src.replace("For each client, the controller maintains a privacy-compatible learning-value estimate.",
                      "For each client, the controller maintains a learning-value estimate derived from model-side metadata.")
    src = src.replace("Raw client examples are not exposed to the scheduler.",
                      "Raw client examples remain local, although scalar loss/utility metadata are reported to the scheduler; this is not a formal privacy guarantee.")
    src = src.replace(
        "Fourth, the theory now provides exact finite-horizon virtual-queue bounds, a one-step drift inequality, finite-set compression optimality, top-k score optimality, and error-feedback conservation; however, a complete non-convex convergence proof jointly covering biased selection, Top-k error feedback, hierarchy, packet loss, and staleness remains future work.",
        "Fourth, the theory provides exact finite-horizon virtual-queue bounds, a one-step drift inequality, finite-set compression optimality, top-k score optimality, and error-feedback conservation; however, a complete non-convex convergence proof jointly covering biased selection, Top-k error feedback, hierarchy, packet loss, and staleness remains future work. Fifth, the experimental baselines isolate scheduling choices within one implementation rather than reproducing every recent external HFL system; direct re-implementations of stronger literature baselines remain an important next comparison.")
    inserts = [
        ("The learning problem is therefore not equivalent to selecting the clients with minimum route cost. A statistically informative client can have a poor route, and repeatedly suppressing that client can bias long-run aggregation influence. The controller must balance statistical utility, communication cost, relay-energy depletion, and staleness.", 0),
        ("The task is per-mote next-temperature regression. A 16-step history of temperature, humidity, log-light, and voltage forms 64 input features. Data are partitioned temporally within each mote. The experiment uses 30 federated rounds, 10 clients per round, three resource-data correlation settings, and 10 paired seeds.", 1),
        ("Utility-only obtains the lowest RMSE but at markedly higher communication, total energy, and relay burden.", 2),
        ("This negative trade-off is retained explicitly: resource-only scheduling minimizes the relay hotspot by strongly favoring cheap paths, whereas the proposed controller spends more relay energy to preserve statistical participation while still using substantially less relay energy than random or utility-only scheduling.", 3),
        ("These ablations show that representation control, adaptive update fidelity, and relay pressure serve distinct functions.", 4),
        ("These results validate the communication consequences of the learned traffic profile, but they do not mean the Python HFL optimization itself is executed inside ns-3.", 5),
        ("The proposed controller operates between these extremes by introducing explicit pressure from participation deficit, route cost, relay queues, and compression distortion.", 6),
    ]
    for marker, idx in inserts:
        src = src.replace(marker, marker + "\n\n[[FIGURE:%d]]" % idx)
    front = "# " + TITLE + "\n\n"
    front += "**Abhishek Kumar Pandey***  \nAssistant Professor, School of Computer Science Engineering and Technology, Bennett University  \nORCID: 0000-0003-3799-9754\n\n"
    front += "**Shivam Bhardwaj**  \nAssistant Professor, United Institute of Management, Prayagraj, India  \nORCID: 0009-0005-4554-7397\n\n"
    front += "*Corresponding author: abhishek.pandey2@bennett.edu.in  \nShivam Bhardwaj: shibambhardwaj@gmail.com\n\n"
    front += "## Highlights\n\n" + "\n".join("- " + h for h in HIGHLIGHTS) + "\n\n"
    front += "## In brief\n\n" + IN_BRIEF + "\n\n## Broader context\n\n" + BROADER + "\n\n"
    availability = """## Resource availability

### Lead contact

Requests concerning the manuscript should be directed to the corresponding author, Abhishek Kumar Pandey (abhishek.pandey2@bennett.edu.in).

### Materials availability

This computational study did not generate new physical materials.

### Data and code availability

Code, experiment manifests, processed outputs, statistical analyses, and the frozen manuscript figures are available in the public project repository: https://github.com/DrShivamBhardwaj/Relevance_Aware_RE_ETX_/tree/wsn-hfl-crosslayer-final. The Intel Berkeley Research Lab sensor data and UCI Human Activity Recognition Using Smartphones data are publicly available from their original providers. The repository records the exact seeds and frozen controller parameters used for the reported results; the full 360-run reproducibility rerun, including hashes and host timings, is documented in validation/OPTIMIZER_RERUN_REPORT.md.

"""
    src = src.replace("## References\n", availability + "\n## References\n")
    refs = """## References

[1] L. Liu, J. Zhang, S. H. Song, and K. B. Letaief, “Client-Edge-Cloud Hierarchical Federated Learning,” IEEE International Conference on Communications, 2020. DOI: 10.1109/ICC40277.2020.9148862.

[2] S. AbdulRahman, H. Tout, A. Mourad, and C. Talhi, “FedMCCS: Multicriteria Client Selection Model for Optimal IoT Federated Learning,” IEEE Internet of Things Journal, 8, 4723–4735, 2021. DOI: 10.1109/JIOT.2020.3028742.

[3] W. Y. B. Lim, J. S. Ng, Z. Xiong, D. Niyato, C. Miao, and D. I. Kim, “Dynamic Edge Association and Resource Allocation in Self-Organizing Hierarchical Federated Learning Networks,” IEEE Journal on Selected Areas in Communications, 39(12), 3640–3653, 2021. DOI: 10.1109/JSAC.2021.3118401.

[4] T. Huang, W. Lin, L. Shen, K. Li, and A. Y. Zomaya, “Stochastic Client Selection for Federated Learning With Volatile Clients,” IEEE Internet of Things Journal, 9(20), 20055–20070, 2022. DOI: 10.1109/JIOT.2022.3172113.

[5] X. Chen, T. Ouyang, Z. Zhou, X. Zhang, S. Yang, and J. Zhang, “HiFlash: Communication-Efficient Hierarchical Federated Learning With Adaptive Staleness Control and Heterogeneity-Aware Client-Edge Association,” IEEE Transactions on Parallel and Distributed Systems, 2023. DOI: 10.1109/TPDS.2023.3238049.

[6] Z. Jiang, Y. Xu, H.-Z. Xu, Z. Wang, and C. Qian, “Heterogeneity-Aware Federated Learning with Adaptive Client Selection and Gradient Compression,” IEEE INFOCOM, 2023. DOI: 10.1109/INFOCOM53939.2023.10229029.

[7] Y. Deng, F. Lyu, T. Xia, Y. Zhou, Y. Zhang, J. Ren, and Y. Yang, “A Communication-Efficient Hierarchical Federated Learning Framework via Shaping Data Distribution at Edge,” IEEE/ACM Transactions on Networking, 32(3), 2600–2615, 2024. DOI: 10.1109/TNET.2024.3363916.

[8] B. Wu, F. Fang, X. Wang, D. Cai, S. Fu, and Z. Ding, “Client Selection and Cost-Efficient Joint Optimization for NOMA-Enabled Hierarchical Federated Learning,” IEEE Transactions on Wireless Communications, 23(10), 14289–14303, 2024. DOI: 10.1109/TWC.2024.3411479.

[9] X. Chen, G. Zhu, Y. Deng, and Y. M. Fang, “Federated Learning Over Multihop Wireless Networks With In-Network Aggregation,” IEEE Transactions on Wireless Communications, 2022. DOI: 10.1109/TWC.2022.3168538.

[10] P. Pinyoanuntapong, P. Janakaraj, R. Balakrishnan, M. Lee, C. Chen, and P. Wang, “EdgeML: Towards Network-Accelerated Federated Learning over Wireless Edge,” Computer Networks, 218, 109396, 2022. DOI: 10.1016/j.comnet.2022.109396.

[11] T. V. Nguyen, N. D. Ho, H. T. Hoang, C. D. Do, and K.-S. Wong, “Toward Efficient Hierarchical Federated Learning Design Over Multi-Hop Wireless Communications Networks,” IEEE Access, 10, 111910–111922, 2022. DOI: 10.1109/ACCESS.2022.3215758.

[12] J. Wu, F. Dong, H. Leung, Z. Zhu, J. Zhou, and S. Drew, “Topology-Aware Federated Learning in Edge Computing: A Comprehensive Survey,” ACM Computing Surveys, 56(10), Article 262, 1–41, 2024. DOI: 10.1145/3659205.

[13] M. Alsofyani, I. Al-Turaiki, and H. Mathkour, “A Fairness Perspective on Client Selection and Aggregation Methods for Non-IID Mitigation in Federated Learning: A Survey,” Electronics, 2026. DOI: 10.3390/electronics15143178.

[14] M. J. Neely, Stochastic Network Optimization with Application to Communication and Queueing Systems, Morgan & Claypool, 2010. DOI: 10.2200/S00271ED1V01Y201006CNT007.

[15] Intel Berkeley Research Lab sensor dataset. Available: https://db.csail.mit.edu/labdata/labdata.html.

[16] UCI Machine Learning Repository, “Human Activity Recognition Using Smartphones.” DOI: 10.24432/C54S4K.
"""
    src = src[:src.index("## References")] + refs
    return front + src + "\n"

SOURCE = transform_source()
(OUT / "NEXUS_MANUSCRIPT_SOURCE.md").write_text(SOURCE)
def set_cell_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:fill"), fill); tcPr.append(shd)

def set_cell_text(cell, text, bold=False, color=None, size=8.5):
    cell.text = ""
    p = cell.paragraphs[0]
    r = p.add_run(text); r.bold = bold
    r.font.name = "Times New Roman"; r.font.size = Pt(size)
    if color: r.font.color.rgb = RGBColor.from_string(color)

def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    a = OxmlElement("w:fldChar"); a.set(qn("w:fldCharType"), "begin")
    b = OxmlElement("w:instrText"); b.set(qn("xml:space"), "preserve"); b.text = "PAGE"
    c = OxmlElement("w:fldChar"); c.set(qn("w:fldCharType"), "end")
    run._r.append(a); run._r.append(b); run._r.append(c)

def configure_doc(doc):
    sec = doc.sections[0]
    sec.top_margin=Inches(.75); sec.bottom_margin=Inches(.75); sec.left_margin=Inches(.85); sec.right_margin=Inches(.85)
    n=doc.styles["Normal"]; n.font.name="Times New Roman"; n.font.size=Pt(11); n.paragraph_format.space_after=Pt(5); n.paragraph_format.line_spacing=1.08
    for sname,size in [("Title",16),("Heading 1",13),("Heading 2",11.5),("Heading 3",11)]:
        st=doc.styles[sname]; st.font.name="Times New Roman"; st.font.size=Pt(size); st.font.bold=True
    add_page_number(sec.footer.paragraphs[0])

def parse_inline_runs(p, text):
    pos=0; pat=re.compile(r"(\*\*.*?\*\*|\*[^*]+\*)")
    for m in pat.finditer(text):
        if m.start()>pos:
            rr=p.add_run(text[pos:m.start()]); rr.font.name="Times New Roman"
        token=m.group(0); rr=p.add_run(token.strip("*")); rr.font.name="Times New Roman"
        if token.startswith("**"): rr.bold=True
        else: rr.italic=True
        pos=m.end()
    if pos<len(text):
        rr=p.add_run(text[pos:]); rr.font.name="Times New Roman"

def add_math_para(doc, text):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    t=text.replace("\\left","").replace("\\right","").replace("\\sum","Σ").replace("\\le","≤").replace("\\ge","≥")
    t=t.replace("\\rho","ρ").replace("\\pi","π").replace("\\eta","η").replace("\\lambda","λ").replace("\\mu","μ").replace("\\Gamma","Γ").replace("\\epsilon","ε")
    t=re.sub(r"\\operatorname\{([^}]*)\}",r"\1",t); t=re.sub(r"\\(?:mathcal|mathrm|widetilde|mathbf|bar)\s*\{([^}]*)\}",r"\1",t)
    t=re.sub(r"[{}]","",t)
    r=p.add_run(t.strip()); r.font.name="Cambria Math"; r.font.size=Pt(10.5)

def build_docx():
    doc=Document(); configure_doc(doc); lines=SOURCE.splitlines(); i=0
    while i<len(lines):
        line=lines[i].rstrip()
        if i==0 and line.startswith("# "):
            p=doc.add_paragraph(style="Title"); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run(line[2:]).bold=True; i+=1; continue
        if line.startswith("## "): doc.add_paragraph(line[3:],style="Heading 1"); i+=1; continue
        if line.startswith("### "): doc.add_paragraph(line[4:],style="Heading 2"); i+=1; continue
        if line.startswith("[[FIGURE:"):
            idx=int(re.search(r"(\d+)",line).group(1)); rel,cap=FIGURES[idx]
            p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(ROOT/rel),width=Inches(6.25))
            cp=doc.add_paragraph(); cp.alignment=WD_ALIGN_PARAGRAPH.CENTER; rr=cp.add_run(cap); rr.font.name="Times New Roman"; rr.font.size=Pt(9); rr.italic=True
            i+=1; continue
        if line.startswith("- "):
            p=doc.add_paragraph(style="List Bullet"); parse_inline_runs(p,line[2:]); i+=1; continue
        if line.startswith("|") and i+1<len(lines) and re.match(r"^\|?\s*:?-+",lines[i+1]):
            block=[line]; i+=1
            while i<len(lines) and lines[i].startswith("|"): block.append(lines[i].rstrip()); i+=1
            rows=[]
            for k,row in enumerate(block):
                if k==1: continue
                rows.append([v.strip() for v in row.strip("|").split("|")])
            cols=max(len(r) for r in rows); tbl=doc.add_table(rows=len(rows),cols=cols); tbl.alignment=WD_TABLE_ALIGNMENT.CENTER; tbl.style="Table Grid"
            for ri,row in enumerate(rows):
                for ci in range(cols):
                    txt=re.sub(r"\*\*","",row[ci] if ci<len(row) else "")
                    set_cell_text(tbl.cell(ri,ci),txt,bold=(ri==0),color="FFFFFF" if ri==0 else None)
                    tbl.cell(ri,ci).vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                    if ri==0: set_cell_shading(tbl.cell(ri,ci),"17365D")
            doc.add_paragraph(); continue
        if line=="\\[":
            eq=[]; i+=1
            while i<len(lines) and lines[i].strip()!="\\]": eq.append(lines[i]); i+=1
            i+=1; add_math_para(doc," ".join(eq)); continue
        if not line: i+=1; continue
        p=doc.add_paragraph(); parse_inline_runs(p,line)
        if i<16: p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        i+=1
    out=OUT/"NEXUS_FINAL_MANUSCRIPT.docx"; doc.save(out); return out
def esc_tex(s):
    for a,b in [("&",r"\&"),("%",r"\%"),("#",r"\#"),("_",r"\_")]: s=s.replace(a,b)
    return s

def markdown_to_tex():
    lines=SOURCE.splitlines(); out=[
        r"\documentclass[11pt]{article}",r"\usepackage[a4paper,margin=2.2cm]{geometry}",r"\usepackage{graphicx}",
        r"\usepackage{amsmath,amssymb}",r"\usepackage{booktabs,longtable,array}",r"\usepackage{hyperref}",
        r"\usepackage{caption}",r"\usepackage{microtype}",r"\usepackage{xcolor}",r"\usepackage{enumitem}",
        r"\setlist{nosep}",r"\hypersetup{colorlinks=true,linkcolor=black,urlcolor=blue,citecolor=black}",r"\begin{document}"
    ]; i=0
    while i<len(lines):
        line=lines[i].rstrip()
        if i==0 and line.startswith("# "):
            out += [r"\begin{center}",r"{\LARGE\bfseries "+esc_tex(line[2:])+r"}\par\vspace{0.8em}",
                    r"{\large Abhishek Kumar Pandey$^{1,*}$, Shivam Bhardwaj$^{2}$}\par",
                    r"$^{1}$School of Computer Science Engineering and Technology, Bennett University\par",
                    r"$^{2}$United Institute of Management, Prayagraj, India\par",
                    r"$^*$Corresponding author: \href{mailto:abhishek.pandey2@bennett.edu.in}{abhishek.pandey2@bennett.edu.in}\par",
                    r"ORCID: 0000-0003-3799-9754 (A.K.P.); 0009-0005-4554-7397 (S.B.)",r"\end{center}\vspace{0.8em}"]
            i+=1
            while i<len(lines) and not lines[i].startswith("## Highlights"): i+=1
            continue
        if line.startswith("## "):
            h=line[3:]
            out.append(r"\section*{"+esc_tex(h)+r"}" if h in ("Highlights","In brief","Broader context","Resource availability","References","Abstract") else r"\section{"+esc_tex(re.sub(r"^\d+\.\s*","",h))+r"}")
            i+=1; continue
        if line.startswith("### "): out.append(r"\subsection*{"+esc_tex(re.sub(r"^\d+\.\d+\s*","",line[4:]))+r"}"); i+=1; continue
        if line.startswith("[[FIGURE:"):
            idx=int(re.search(r"(\d+)",line).group(1)); rel,cap=FIGURES[idx]; fn=Path(rel).name
            out += [r"\begin{figure}[htbp]",r"\centering",r"\includegraphics[width=0.96\linewidth]{figures/"+fn+r"}",r"\caption{"+esc_tex(re.sub(r"^Figure \d+\.\s*","",cap))+r"}",r"\end{figure}"]; i+=1; continue
        if line.startswith("- "):
            out.append(r"\begin{itemize}"); 
            while i<len(lines) and lines[i].startswith("- "):
                out.append(r"\item "+esc_tex(lines[i][2:].replace("**",""))); i+=1
            out.append(r"\end{itemize}"); continue
        if line.startswith("|") and i+1<len(lines) and re.match(r"^\|?\s*:?-+",lines[i+1]):
            block=[line]; i+=1
            while i<len(lines) and lines[i].startswith("|"): block.append(lines[i].rstrip()); i+=1
            rows=[]
            for k,row in enumerate(block):
                if k==1: continue
                rows.append([re.sub(r"\*\*","",v.strip()) for v in row.strip("|").split("|")])
            n=len(rows[0]); out += [r"\begin{table}[htbp]\centering\scriptsize",r"\resizebox{\linewidth}{!}{%",r"\begin{tabular}{l"+"r"*(n-1)+r"}\toprule"]
            for ri,row in enumerate(rows):
                out.append(" & ".join(esc_tex(v.replace("↓","").replace("↑","")) for v in row)+r" \\")
                if ri==0: out.append(r"\midrule")
            out += [r"\bottomrule\end{tabular}}",r"\end{table}"]; continue
        if line=="\\[":
            eq=[]; i+=1
            while i<len(lines) and lines[i].strip()!="\\]": eq.append(lines[i]); i+=1
            i+=1; out += [r"\["," ".join(eq),r"\]"]; continue
        if not line: i+=1; continue
        text=line.replace("**","").replace("*","")
        if re.match(r"^\[\d+\]",text): out.append(r"\noindent "+text.replace("&",r"\&")+r"\par"); i+=1; continue
        out.append(esc_tex(text)+r"\par"); i+=1
    out.append(r"\end{document}")
    return "\n".join(out)

def build_latex():
    for rel,_ in FIGURES: shutil.copy2(ROOT/rel,LATEX/"figures"/Path(rel).name)
    tex=markdown_to_tex(); (LATEX/"main.tex").write_text(tex); shutil.copy2(OUT/"NEXUS_MANUSCRIPT_SOURCE.md",LATEX/"NEXUS_MANUSCRIPT_SOURCE.md")
    return LATEX/"main.tex"

for stale in ("main.aux","main.log","main.out","main.pdf"):
    (LATEX/stale).unlink(missing_ok=True)
docx=build_docx(); tex=build_latex()
extras=OUT/"submission_extras"; extras.mkdir(exist_ok=True)
(extras/"highlights.txt").write_text("\n".join("• "+x for x in HIGHLIGHTS)+"\n")
(extras/"in_brief.txt").write_text(IN_BRIEF+"\n")
(extras/"broader_context.txt").write_text(BROADER+"\n")
zip_path=OUT/"NEXUS_LATEX_PROJECT.zip"
with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
    for p in LATEX.rglob("*"):
        if p.is_file() and p.suffix.lower() not in {".aux",".log",".out",".pdf"}: z.write(p,p.relative_to(LATEX))
print("DOCX",docx); print("TEX",tex); print("ZIP",zip_path)
