"""Draft IJWMT point-by-point response from an evidence matrix.

This is NOT a submission-ready document. Every response carries a pending
verification and the final manuscript page remains unknown until camera-ready
QA; never report items as addressed based solely on this generator.
"""
from pathlib import Path
import csv
import hashlib
from docx import Document
from docx.shared import Inches,Pt,RGBColor
BASE=Path(__file__).resolve().parent
rows=list(csv.DictReader((BASE/"revision_response_matrix.csv").open()))
out=BASE/"PAPER024501_Revision_Response_DRAFT.docx"
fingerprint=BASE/".response_matrix_sha256"
digest=hashlib.sha256((BASE/"revision_response_matrix.csv").read_bytes()).hexdigest()
if out.exists() and fingerprint.exists() and fingerprint.read_text().strip()==digest:
 print("Reusing unchanged response draft",out)
 raise SystemExit(0)
d=Document()
sec=d.sections[0]
sec.top_margin=Inches(.8);sec.bottom_margin=Inches(.8)
sec.left_margin=Inches(.85);sec.right_margin=Inches(.85)
styles=d.styles
styles["Normal"].font.name="Times New Roman"
styles["Normal"].font.size=Pt(10)
d.add_heading("Revision Response — PAPER024501",0)
d.add_paragraph("Relevance-aware payload adaptation with residual-energy ETX routing for wireless sensor networks")
p=d.add_paragraph("DRAFT FOR INTERNAL REVIEW — DO NOT SUBMIT");p.runs[0].bold=True;p.runs[0].font.color.rgb=RGBColor(180,0,0)
d.add_paragraph("The responses below identify supporting work and open verification tasks. They do not assert that manuscript changes, complete receiver reconstruction or hardware validation have been performed.")
for section in ("Major","Minor","Mandatory"):
 d.add_heading(section+" Review Comments",level=1)
 for r in rows:
  if r["type"]!=section:continue
  d.add_heading(r["id"]+" — "+r["concern"],level=2)
  p=d.add_paragraph();p.add_run("Response plan: ").bold=True;p.add_run(r["response_plan"])
  p=d.add_paragraph();p.add_run("Evidence status: ").bold=True;p.add_run(r["status"])
  p=d.add_paragraph();p.add_run("Revised manuscript section/page: ").bold=True;p.add_run("TBD after complete manuscript audit")
d.add_heading("Release criteria",level=1)
d.add_paragraph("Required before submission: original IJWMT manuscript and source-accurate edits; verified references, author ORCIDs, biographies, photographs and declarations; editable equations; figure-quality check; statistical result audit; separate clean and marked versions; exact section/page references for every response.")
d.save(out)
fingerprint.write_text(digest+"\n")
print("Generated",out,"entries",len(rows))
