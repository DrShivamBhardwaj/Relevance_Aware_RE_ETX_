"""Generate a reproducible pointwise review matrix, never invent completion."""
from pathlib import Path
import json,csv
BASE=Path(__file__).resolve().parent
MAJOR=[
 ("M1","Uncharged central neighbour context exchange","Analytical per-exchange and report-normalized energy bounds; full distributed energy/network evaluation pending"),
 ("M2","Insufficient weight/threshold sensitivity","90 executed network runs with 10 paired seeds and Holm-corrected output; no global optimum claim"),
 ("M3","Missing receiver reconstruction or event F1","Blocked until documented source codec, receiver decoder and timestamped packet records exist"),
 ("M4","Missing sensing, computation, routing-control and idle energy","Analytical per-generated-report sensitivity; full node-level ledger and lifetime reruns pending"),
 ("M5","Ambiguous deep-topology mechanisms","Paired 3-profile contrasts generated; packet-level information age/staleness not measured")]
MINOR=[
 ("m1","Equation (6) versus 3000 bits at v=0.50","Code confirms 3000 bits: guarded threshold; verify and correct editable equation"),
 ("m2","Statistical novelty versus semantic information distinction","Draft comparison required; no semantic decoding claim"),
 ("m3","Expand C3 versus C5 deep topology discussion","Add verified topology contrasts, avoid causal staleness attribution"),
 ("m4","Contributions too vague","Describe causal attribution controls rather than novelty of simple components"),
 ("m5","Section 3.1 'Observations add'","Change to 'Observations include a superimposed...'"),
 ("m6","Section 4.3 Dijkstra wording","State non-negative weights ensure applicability of Dijkstra's algorithm"),
 ("m7","Section 6.2 imprecise C1/C2 wording","State small observed differences across listed metrics"),
 ("m8","Section 7 'useful' wording","Replace with 'informative'"),
 ("m9","Section 8 long sentence","Split with preserved caveats"),
 ("m10","Title lacks attribution contribution","Proposed title emphasizes traffic-volume versus relevance effects; author approval needed"),
 ("m11","Abstract limitations and numerical precision","Report 54.0% delay, 54.2% energy per delivered report and context/energy caveats"),
 ("m12","Arnaiz et al. comparison","Add verified methodological comparison; no fabricated first-use claim"),
 ("m13","Algorithm pseudocode and complexity","Write auditable C3 steps with dense graph memory and route cost assumptions"),
 ("m14","Hardware and simulation environment","Record actual system/commit/version, no testbed inference"),
 ("m15","Conclusion parameter-selection limitation","Integrate observed sensitivity and ten reused-seed caveat"),
 ("m16","Recent semantic communication references","Independently verify 2025-2026 DOI and methodology before citing")]
MANDATORY=[
 ("R1","Editable consecutively numbered equations"),("R2","Three-line primary tables, bordered raw tables"),("R3","Figures >=300 dpi"),
 ("R4","Consolidated bracketed citations"),("R5","Reference existence, uniqueness and citation cross-audit"),
 ("R6","ORCID iDs after names/emails"),("R7","Remove author job titles below title"),
 ("R8","Verified biographies and photographs"),("R9","Exact IJWMT template/declarations"),
 ("R10","Nine complete journal statements or N/A"),("R11","Red changes and detailed response")]
sections=[("Major",MAJOR),("Minor",MINOR),("Mandatory",MANDATORY)]
rows=[]
for cls,items in sections:
 for item in items:
  id,concern,action = item if len(item)==3 else (item[0],item[1],"Verify and apply formatting requirement in camera-ready manuscript")
  rows.append({"id":id,"type":cls,"concern":concern,"response_plan":action,"status":"planned / partial, evidence required","manuscript_page":"TBD after final layout","verification_file":"TBD"})
with (BASE/"revision_response_matrix.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
lines=["# PAPER024501 — Draft point-by-point revision response","", "**NOT FOR SUBMISSION: scientific gates and author confirmation incomplete.**","",
       "The responses below are an evidence-indexed plan. Do not state an action was implemented without checking the final DOCX.",""]
for cls,items in sections:
 lines.append("## "+cls+" comments")
 for item in items:
  id,concern,action = item if len(item)==3 else (item[0],item[1],"Verify and apply formatting requirement in camera-ready manuscript")
  lines += ["",f"### {id}. {concern}","**Proposed response:** "+action+".",
            "**Revised location:** Pending final manuscript page and paragraph check.",
            "**Evidence/verification:** Pending release-gate confirmation."]
(BASE/"REVISION_RESPONSE_DRAFT.md").write_text("\n".join(lines)+"\n")
print(json.dumps({"entries":len(rows),"draft_is_final":False}))
