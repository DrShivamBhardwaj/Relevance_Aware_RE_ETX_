"""Stage source-preserving IJWMT working copy if the submitted DOCX exists.

Does not alter equation objects or manipulate unknown authors/ORCIDs.
A draft is not camera-ready without separate inspection and author sign-off.
"""
from pathlib import Path
import json,re,shutil
from docx import Document
from docx.shared import RGBColor
BASE=Path(__file__).resolve().parent
source=BASE/"PAPER024501_submitted_source.docx"
template=BASE/"IJWMT_template.docx"
out=BASE/"PAPER024501_IJWMT_WORKING_DRAFT.docx"
report={
 "input_source":str(source),"template":str(template),
 "source_exists":source.is_file(),"template_exists":template.is_file(),
 "draft_generated":False,"submission_ready":False,
 "missing_author_confirmation":["ORCID iDs","biographical profiles","passport photographs","nine journal declarations"]
}
if source.exists():
 d=Document(source)
 edits={
 "Observations add a spatial Gaussian event":"Observations include a superimposed spatial Gaussian event",
 "Positive costs permit one sink-rooted Dijkstra search":"Positive costs ensure the validity of one sink-rooted Dijkstra search",
 "C1 and C2 are nearly the same across Table 4":"C1 and C2 exhibit negligible differences across the metrics in Table 4",
 "Stretching the topology makes the robustness result more useful":"Stretching the topology makes the robustness result more informative",
 "Most of the contribution is in how the method is specified and tested":"The primary contribution lies in a controlled experimental design that separates traffic-volume reduction from relevance-directed allocation"
 }
 applied=[]
 # Perform only run-local replacements to avoid deleting drawings, objects,
 # footnotes, equations or other formatting. Unmatched phrases stay pending.
 for para in d.paragraphs:
  for run in para.runs:
   for before,after in edits.items():
    if before in run.text:
     run.text=run.text.replace(before,after)
     run.font.color.rgb=RGBColor(190,0,0)
     applied.append(before)
 out.parent.mkdir(parents=True,exist_ok=True)
 d.save(out)
 text="\n".join(p.text for p in d.paragraphs)
 cites={int(z) for z in re.findall(r"(?<!\w)\[(\d+)\]",text)}
 report.update({"draft_generated":True,"draft_path":str(out),"applied_run_local_prose_changes":applied,"unmatched_proposed_prose_changes":[x for x in edits if x not in applied],
                "reference_citation_numbers_detected":sorted(cites),
                "requirements_not_verified":["editable equation numbering","image pixel density","bibliographic DOI verification","complete metadata","redline visual QA","journal typography","exact statistical claim consistency"]})
else:
 report["blocked_reason"]="Source attached to ChatGPT is not present on Mac or GitHub. Original formatting, equations and figures cannot be reconstructed faithfully."
(BASE/"manuscript_stage_status.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"draft_generated":report["draft_generated"],"submission_ready":False,"blocked_reason":report.get("blocked_reason"),"applied_count":len(report.get("applied_run_local_prose_changes",[]))}))
