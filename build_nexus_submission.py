from pathlib import Path
import re, shutil, zipfile, os, json
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "submission" / "nexus"
LATEX = OUT / "latex"
OUT.mkdir(parents=True, exist_ok=True)
LATEX.mkdir(parents=True, exist_ok=True)
(LATEX / "figures").mkdir(parents=True, exist_ok=True)

TITLE = "Cross-Layer Utility-Aware Hierarchical Federated Learning for Multi-Hop IoT Sensor Networks"
HIGHLIGHTS = [
    "Two-level cloud influence is tracked after edge and cloud normalization",
    "Held-out evaluation separates parameter tuning from final inference",
    "Matched controls isolate adaptive compression from client scheduling",
    "Utility-target alignment improves at an explicit network-cost trade-off",
]
IN_BRIEF = ("Pandey and Bhardwaj study how hierarchical federated-learning decisions change when "
            "model updates traverse multi-hop sensor routes. Their controller coordinates utility-target "
            "participation, update fidelity, relay pressure, and staleness, and is evaluated with "
            "held-out seeds, compression-matched controls, real sensing data, and low-power wireless replay.")
BROADER = (
    "Edge intelligence increasingly supports environmental monitoring, infrastructure observation, "
    "industrial sensing, and personal activity recognition, often where communication capacity and "
    "battery energy are limited. In these deployments, selecting a learning client also selects the "
    "route and relays that must transport its model update. The resulting design problem is not simply "
    "to minimize traffic: inexpensive clients can dominate training while remote or difficult-to-reach "
    "clients contribute less often. This study develops and audits a cross-layer controller that makes "
    "that trade-off explicit. Importantly, the revised experiments separate parameter tuning from "
    "held-out evaluation and compare selection policies under matched compression. The evidence therefore "
    "supports a Pareto interpretation rather than a claim of universal network or statistical superiority. "
    "Such transparent trade-offs are relevant when distributed intelligence must operate over low-power "
    "sensing infrastructure without overstating sustainability or population-representativeness claims."
)


FIGURES = [
    ("figures/final/02_system_architecture.png", "Figure 1. Cross-layer hierarchical architecture. Learning-capable sensor clients send model updates through multi-hop relay paths to edge gateways and then to the cloud."),
    ("figures/final/01_network_topology.png", "Figure 2. Intel Berkeley Lab WSN topology abstraction. Gateway motes form the edge layer and measured directed connectivity defines route feasibility and ETX burden."),
    ("figures/final/07_intel_berkeley_results.png", "Figure 3. Intel held-out evaluation at strong resource-data correlation. Main values and 95% confidence intervals are reported in Table 2."),
    ("figures/final/06_uci_har_results.png", "Figure 4. UCI HAR held-out evaluation using the blocked overlap-safe within-client split. Main values and 95% confidence intervals are reported in Table 3."),
    ("figures/final/04_ablation.png", "Figure 5. Component ablations on Intel and UCI HAR. Adaptive fidelity provides the largest traffic reduction, whereas the participation-deficit and relay-pressure terms affect different trade-off dimensions."),
    ("figures/final/03_ns3_validation.png", "Figure 6. ns-3.47 IEEE 802.15.4/LR-WPAN replay of held-out synthetic traffic profiles. The replay validates communication consequences of offered load; the HFL controller itself is not executed inside ns-3."),
    ("figures/final/05_learning_communication_tradeoff.png", "Figure 7. Held-out learning-communication trade-offs for compression-matched controls, the FedCG-adapted comparator, and the proposed controller."),
]

def transform_source():
    src = (ROOT / "MANUSCRIPT_RECONSTRUCTION.md").read_text().strip()
    front = "# " + TITLE + "\n\n"
    front += "**Abhishek Kumar Pandey***  \nAssistant Professor, School of Computer Science Engineering and Technology, Bennett University  \nORCID: 0000-0003-3799-9754\n\n"
    front += "**Shivam Bhardwaj**  \nAssistant Professor, United Institute of Management, Prayagraj, India  \nORCID: 0009-0005-4554-7397\n\n"
    front += "*Corresponding author: abhishek.pandey2@bennett.edu.in  \nShivam Bhardwaj: shivambhardwaj@gmail.com\n\n"
    front += "## Highlights\n\n" + "\n".join("- " + h for h in HIGHLIGHTS) + "\n\n"
    front += "## In brief\n\n" + IN_BRIEF + "\n\n## Broader context\n\n" + BROADER + "\n\n"
    return front + src + "\n"

SOURCE = transform_source()
(OUT / "NEXUS_MANUSCRIPT_SOURCE.md").write_text(SOURCE)
OMML_MAP = json.loads((OUT / "omml_math_map.json").read_text())
OMML_INLINE = OMML_MAP["inline"]
OMML_BLOCK = OMML_MAP["block"]

def _append_omml(parent, xml_text):
    parent.append(parse_xml(xml_text))

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
    pos=0
    pat=re.compile(r"(\*\*.*?\*\*|\*[^*]+\*|\\\(.*?\\\))")
    for m in pat.finditer(text):
        if m.start()>pos:
            rr=p.add_run(text[pos:m.start()]); rr.font.name="Times New Roman"
        token=m.group(0)
        if token.startswith("\\("):
            key=token[2:-2].strip()
            if key not in OMML_INLINE:
                raise KeyError(f"Missing inline OMML mapping: {key}")
            _append_omml(p._p, OMML_INLINE[key])
        else:
            rr=p.add_run(token.strip("*")); rr.font.name="Times New Roman"
            if token.startswith("**"): rr.bold=True
            else: rr.italic=True
        pos=m.end()
    if pos<len(text):
        rr=p.add_run(text[pos:]); rr.font.name="Times New Roman"

def add_math_para(doc, text):
    key=" ".join(text.split())
    if key not in OMML_BLOCK:
        raise KeyError(f"Missing block OMML mapping: {key}")
    p=doc.add_paragraph()
    _append_omml(p._p, OMML_BLOCK[key])
    return p

def add_table_caption(doc, text):
    clean=re.sub(r"^\*\*|\*\*$", "", text).strip()
    p=doc.add_paragraph()
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before=Pt(6)
    p.paragraph_format.space_after=Pt(3)
    r=p.add_run(clean)
    r.bold=True
    r.font.name="Times New Roman"
    r.font.size=Pt(9)
    return p

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
        if re.match(r"^\*\*Table \d+\.", line):
            add_table_caption(doc, line); i+=1; continue
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
