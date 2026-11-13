"""Render Word draft and machine-check page count and embedded-image DPI.
Never equate an automated rendering with expert visual inspection.
"""
from pathlib import Path
import json,subprocess,hashlib
from docx import Document
from docx.oxml.ns import qn
from PIL import Image
from io import BytesIO
BASE=Path(__file__).resolve().parent/"manuscript_working"
DOC=BASE/"PAPER024501_IJWMT_RED_MARKED_EVIDENCE_DRAFT.docx"
R=BASE/"rendered"
R.mkdir(exist_ok=True)
if not DOC.exists():raise SystemExit("Word draft absent")
PDF=R/(DOC.stem+".pdf")
digest=hashlib.sha256(DOC.read_bytes()).hexdigest()
fingerprint=R/"pdf_source.sha256"
if not PDF.exists() or not fingerprint.exists() or fingerprint.read_text().strip()!=digest:
 p=subprocess.run(["/opt/homebrew/bin/soffice",
   "-env:UserInstallation=file:///tmp/lo_paper024501_render2",
   "--headless","--convert-to","pdf","--outdir",str(R),str(DOC)],
   capture_output=True,text=True,timeout=120)
 (R/"render.log").write_text(p.stdout+p.stderr)
 if p.returncode or not PDF.exists():raise RuntimeError("PDF render failed")
 fingerprint.write_text(digest+"\n")
info=subprocess.run(["/opt/homebrew/bin/pdfinfo",str(PDF)],capture_output=True,text=True,timeout=25)
page=[x.split(":",1)[1].strip() for x in info.stdout.splitlines() if x.startswith("Pages:")]
doc=Document(DOC)
shapes=[]
for x in doc.inline_shapes:
 try:
  rid=x._inline.xpath(".//a:blip")[0].get(qn("r:embed"))
  blob=doc.part.related_parts[rid].blob
  with Image.open(BytesIO(blob)) as img:w,h=img.size
  dpi_x=w/(x.width/914400)
  dpi_y=h/(x.height/914400)
  shapes.append({"width_pixels":w,"height_pixels":h,"dpi_x":round(dpi_x,1),
   "dpi_y":round(dpi_y,1),"meets_300":dpi_x>=300 and dpi_y>=300})
 except Exception as e:
  shapes.append({"error":repr(e),"meets_300":False})
report={"pdf_rendered":bool(page),"page_count":int(page[0]) if page else None,
 "embedded_image_resolution_audit":shapes,
 "all_inline_images_300dpi":bool(shapes) and all(x.get("meets_300") for x in shapes),
 "visual_qa_complete":False,"journal_submission_ready":False,
 "explanation":"Automated preflight only; pages, equations and tables still need human visual inspection"}
(BASE/"render_preflight.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({k:v for k,v in report.items() if k!="embedded_image_resolution_audit"}))
