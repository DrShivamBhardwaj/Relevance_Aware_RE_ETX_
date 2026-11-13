"""Unattended *evidence-gated* PAPER024501 manuscript and experiment workflow.

Never asserts that missing original codec, a calibrated current trace or
full RE-ETX Contiki firmware have been validated. Work from the journal-
submitted source and original template found on the authorized Mac.
Runs idempotently, safely during 20-minute local Git checkpoints.
"""
import csv
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import time
import zipfile
import sys
from datetime import datetime, timezone

from docx import Document
from docx.shared import Pt, RGBColor

BASE = pathlib.Path(__file__).resolve().parent
ROOT = BASE.parents[1]
sys.path.insert(0, str(ROOT))
DEST = BASE / "manuscript_working"
DEST.mkdir(exist_ok=True)
SOURCE = pathlib.Path.home() / "Downloads/PAPER024501-1.docx"
TEMPLATE = pathlib.Path.home() / "Downloads/Example_paper_template-IJWMT.docx"
GUIDE = pathlib.Path.home() / "Downloads/IJWMT_Preparation_Instruction.docx"
REVIEWS = BASE / "revision_response_matrix.csv"
MEMO = BASE / "PAPER024501_validation_memorandum.md"
OUT = DEST / "PAPER024501_IJWMT_RED_MARKED_EVIDENCE_DRAFT.docx"
RESPONSE = DEST / "PAPER024501_POINT_BY_POINT_EVIDENCE_DRAFT.docx"
STATE = BASE / "unattended_release_status.json"
NOW = datetime.now(timezone.utc).isoformat()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(state):
    prior = {}
    try:
        prior = json.loads(STATE.read_text())
    except (FileNotFoundError, ValueError):
        pass
    state["created_utc"] = prior.get("created_utc", state.get("created_utc", NOW))
    if {k:v for k,v in prior.items() if k != "updated_utc"} == {k:v for k,v in state.items() if k != "updated_utc"}:
        return
    state["updated_utc"] = datetime.now(timezone.utc).isoformat()
    temp = STATE.with_suffix(".json.tmp")
    temp.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")
    temp.replace(STATE)


def read_json(relative):
    p = BASE / relative
    return json.loads(p.read_text()) if p.is_file() else {}


def package_counts(p):
    with zipfile.ZipFile(p) as z:
        names = z.namelist()
        xml = z.read("word/document.xml")
        return {
            "media_files": sorted(x for x in names if x.startswith("word/media/")),
            "equation_elements": xml.count(b"<m:oMath>") + xml.count(b"<m:oMath "),
            "tables": len(Document(p).tables),
            "paragraphs": len(Document(p).paragraphs),
        }


def after(para, message):
    p = para.insert_paragraph_before("")
    para._p.addnext(p._p)
    run = p.add_run(message)
    run.font.color.rgb = RGBColor(180, 0, 0)
    run.font.name = "Times New Roman"
    run.font.size = Pt(9)
    return p


def create_manuscript(state):
    if not SOURCE.is_file():
        state["manuscript"] = {"status": "blocked", "reason": "Submitted source not found on Mac"}
        return
    if not TEMPLATE.is_file() or not GUIDE.is_file():
        state["manuscript"] = {"status": "blocked", "reason": "Required IJWMT template/instructions absent"}
        return

    data = {
        "receiver": read_json("new_validation_summary.json"),
        "receiver_100": read_json("receiver_campaign_100r/progress.json"),
        "energy": read_json("full_network_energy/progress.json"),
        "cooja": read_json("cooja_transport/campaign_progress.json"),
        "hardware": read_json("iotlab_m3/hardware_status.json"),
        "physical_power": read_json("hardware_power_calibration/m3_power_measurement_audit.json"),
    }
    fingerprint = hashlib.sha256(
        ("|".join(sha(p) for p in (SOURCE, TEMPLATE, GUIDE)) + sha(pathlib.Path(__file__)) + json.dumps(data, sort_keys=True)).encode()
    ).hexdigest()
    hash_file = DEST / "manuscript_inputs.sha256"
    if OUT.is_file() and hash_file.is_file() and hash_file.read_text().strip() == fingerprint:
        try:
            previous = json.loads(STATE.read_text()).get("manuscript", {})
        except (FileNotFoundError, ValueError):
            previous = {}
        state["manuscript"] = previous if previous.get("status") == "red_marked_evidence_draft_NOT_submission_ready" else {
            "status":"red_marked_evidence_draft_NOT_submission_ready",
            "document":str(OUT.relative_to(ROOT)), "source_found":True}
        return

    doc = Document(SOURCE)
    from docx.oxml.ns import qn
    formula = doc.paragraphs[50]._p.xpath(".//m:oMath")
    formula_text = "".join(e.text or "" for m in formula for e in m.iter() if e.tag == qn("m:t"))
    verified_eq6 = bool(formula and "0.50" in formula_text and "0.85" in formula_text and "0.75" in formula_text)
    from config import SimulationConfig
    from simulator.semantic_payload import SemanticPayloadController
    mapping = SemanticPayloadController(SimulationConfig())
    table_path = BASE / "payload_mapping_review.csv"
    with table_path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["relevance_v","payload_bits","submitted_equation6_branch"])
        for i in range(11):
            v = i / 10
            branch = "full" if v >= 0.85 else "3000-bit floor or proportional" if v >= 0.5 else "proportional"
            w.writerow([f"{v:.1f}",int(mapping.payload_bits([v])[0]),branch])
    if not verified_eq6 or int(mapping.payload_bits([0.5])[0]) != 3000:
        raise RuntimeError("Equation (6) safeguards or executable payload map not verified")
    groups = {
        "3.2. Channel, fragmentation and energy": [
            "REVISION EVIDENCE — The supplementary node-state energy study now debits modeled sensing, CPU, idle, neighbour-context/control, radio and approximate ACK costs. Moderate and high additional-cost profiles are assumptions, not hardware-calibrated current measurements. Therefore, any original radio-only reduction percentage must be identified as such and must not be generalized to deployment-wide energy."
        ],
        "4.2. Payload mapping and safeguards": [
            "EQUATION (6) CLARIFICATION — The original submitted Word equation already contains a three-branch safeguard: ρ(v)=0.25+0.75v for v<0.50; ρ(v)=max(0.75,0.25+0.75v) for 0.50≤v<0.85; and ρ(v)=1 for v≥0.85. The existing Word equation therefore gives L(0.50)=3000 bits, not 2500 bits. The reviewer appears to have evaluated only the unguarded linear branch. The executable source and a complete mapping table are available as verification evidence. Preserve the original editable Word equation; provide a clearer rendering/interpretation in the response."
        ],
        "6.5. What remains after matching the source bit budget": [
            "RECEIVER DIAGNOSTIC (new reference codec, NOT part of the submitted original): The 100-round matched-seed DCT experiment gave receiver RMSE 0.06534 for C3 and 0.06060 for C5. Paired C5 minus C3 RMSE was −0.004742 (95% CI −0.005711 to −0.003772; Holm-adjusted p = 0.000011; ten seeds). C3 did not establish a reliable event-F1 improvement over C5. These are codec-specific results and do not establish the application fidelity of the original length-only reporting scheme."
        ],
        "6.7. Sensitivity to multi-hop topology depth": [
            "INTERPRETATION LIMITATION — The archive supports depth-specific C3/C5 paired contrasts, but per-packet information age and event-to-receipt staleness were not recorded. Hop count alone is not sufficient to attribute the deep-topology reversal to stale relevance. No causal staleness mechanism is asserted."
        ],
        "7. Discussion and limitations": [
            "NEW CONTROLLED ENERGY SCENARIOS — In 10 paired seeds, C3 LND was 2636.4 rounds with no added cost, 1862.7 with the moderate assumed cost profile, and 1047.7 with the high-cost profile. Corresponding C1 LND values were 1268.6, 1042.9 and 725.9 rounds. The modeled advantage narrows as previously uncharged costs increase. Device-current calibration, context contention, ACK timing and chip duty-state measurements remain open.",
            "COOJA / FIT IoT-LAB SCOPE — Fifteen Cooja stress cases verified direct, fragmented NullNet/CSMA transport. FIT IoT-LAB Grenoble M3 experiment 458478 captured actual source transmissions and sink report reassembly. Neither study implemented the paper-equivalent distributed RE-ETX route-selection policy. Partial-window serial matching is not physical PHY PDR.",
            "SEPARATE PHYSICAL POWER PILOT — In the single Grenoble M3 consumption-profile experiment 458482, 694 raw OML samples across three nodes gave time-integrated mean device powers of 0.10480 W, 0.10231 W, and 0.10050 W and trace energies of 50.553 J, 49.301 J, and 48.349 J, respectively. This is total board power of a NullNet fragmentation probe, not a measurement of source sensing, CPU, idle, control or RE-ETX energy separately. The simulation overhead profiles remain uncalibrated."
        ],
        "8. Conclusions": [
            "EVIDENCE-CONSTRAINED CONCLUSION — The results establish a radio-only and scenario-based lifetime advantage over fixed full-payload reporting in the tested simulator, not universal semantic reconstruction superiority. A newly introduced reference codec exposed a C3 reconstruction disadvantage against equal-budget C5. Complete source encoding/decoding, independent task utility, hardware-calibrated energy and deployed RE-ETX firmware remain prerequisites for stronger claims."
        ],
    }
    inserted = []
    for heading, texts in groups.items():
        candidates = [p for p in doc.paragraphs if p.text.strip() == heading]
        if len(candidates) != 1:
            continue
        anchor = candidates[0]
        for line in texts:
            anchor = after(anchor, line)
            inserted.append(heading)
    doc.save(OUT)
    old, new = package_counts(SOURCE), package_counts(OUT)
    invariant = {
        "original_media": len(old["media_files"]),
        "revised_media": len(new["media_files"]),
        "original_equation_elements": old["equation_elements"],
        "revised_equation_elements": new["equation_elements"],
        "original_tables": old["tables"],
        "revised_tables": new["tables"],
        "media_names_preserved": old["media_files"] == new["media_files"],
        "equation_count_preserved": old["equation_elements"] == new["equation_elements"],
        "table_count_preserved": old["tables"] == new["tables"],
    }
    (DEST/"manuscript_structure_invariants.json").write_text(json.dumps(invariant, indent=2) + "\n")
    if not all((invariant["media_names_preserved"], invariant["equation_count_preserved"], invariant["table_count_preserved"])):
        OUT.unlink(missing_ok=True)
        raise RuntimeError("Manuscript source preservation invariant failed")
    hash_file.write_text(fingerprint+"\n")
    state["manuscript"] = {
        "status": "red_marked_evidence_draft_NOT_submission_ready",
        "document": str(OUT.relative_to(ROOT)),
        "source_found": True,
        "journal_templates_found": True,
        "sections_with_red_evidence": inserted,
        "remaining": ["Confirm Equation (6) branch alignment in Word rendering and explain reviewer reading",
                      "Author-confirmed ORCIDs, headshots and profiles",
                      "Journal's nine declarations",
                      "Verify references and updated figure/table layout",
                      "Full visual and editorial signoff"],
        "invariants": invariant,
        "equation_6_piecewise_verified": verified_eq6,
        "mapping_table": "reviewer_audit/PAPER024501/payload_mapping_review.csv",
    }


def make_response(state):
    if not REVIEWS.is_file():
        state["responses"] = {"status": "blocked", "reason": "Review matrix absent"}
        return
    rows = list(csv.DictReader(REVIEWS.open()))
    response_hash_file = DEST / "reviewer_response_inputs.sha256"
    power_file = BASE / "hardware_power_calibration/m3_power_measurement_audit.json"
    fingerprint = hashlib.sha256((sha(REVIEWS) + (sha(MEMO) if MEMO.exists() else "") + (sha(power_file) if power_file.exists() else "") + sha(pathlib.Path(__file__))).encode()).hexdigest()
    if RESPONSE.is_file() and response_hash_file.is_file() and response_hash_file.read_text().strip() == fingerprint:
        try:
            previous = json.loads(STATE.read_text()).get("responses", {})
        except (FileNotFoundError, ValueError):
            previous = {}
        state["responses"] = previous if previous.get("status") == "draft_not_submission_ready" else {
            "status":"draft_not_submission_ready","count":len(rows),
            "document":str(RESPONSE.relative_to(ROOT)),"missing_page_references":True}
        return
    d = Document()
    d.styles["Normal"].font.name = "Times New Roman"
    d.styles["Normal"].font.size = Pt(10)
    d.add_heading("PAPER024501 — Point-by-point evidence response", 0)
    d.add_paragraph("INTERNAL EVIDENCE DRAFT — NOT FOR SUBMISSION. Page references remain unverified.")
    d.add_paragraph("The supplementary diagnostic experiments have been executed and archived. They do not establish an original source codec, calibrated hardware-energy superiority or a deployed RE-ETX policy.")
    for kind in ("Major", "Minor", "Mandatory"):
        d.add_heading(kind + " concerns", 1)
        for row in rows:
            if row["type"] != kind:
                continue
            d.add_heading(row["id"] + ": " + row["concern"], 2)
            if row["id"] == "m1":
                d.add_paragraph("Technical response / verification target: Submitted source Equation (6) contains the piecewise 0.50 and 0.85 safeguards. Its existing editable OMML is retained. The expression 2500 bits at 0.50 follows only when the reviewer omits the max(0.75, ...) branch. Executable value is 3000 bits; see payload_mapping_review.csv.")
            elif row["id"] == "M4":
                d.add_paragraph("Technical response / verification target: 60 full network battery-state scenario runs now include explicit uncalibrated sensing/CPU/idle/control/ACK assumptions. A separate M3 power-profile experiment 458482 produced three raw timestamped current, voltage and power traces (694 samples total). The board-level power integral is measured, but no sensing/CPU/ACK phase-resolved calibration or RE-ETX firmware exists. Therefore this major issue remains partially addressed.")
            else:
                d.add_paragraph("Technical response / verification target: " + row["response_plan"])
            evidence = "PAPER024501_validation_memorandum.md and corresponding seed/hardware logs, where applicable; otherwise pending"
            d.add_paragraph("Evidence: " + evidence)
            d.add_paragraph("Manuscript section/page: pending final Word pagination and visual audit")
            d.add_paragraph("Disposition: PARTIAL / PENDING FINAL VERIFICATION")
    d.save(RESPONSE)
    response_hash_file.write_text(fingerprint + "\n")
    state["responses"] = {"status": "draft_not_submission_ready", "count": len(rows), "document": str(RESPONSE.relative_to(ROOT)), "missing_page_references": True}


def inspect_hardware(state):
    # Only verify proof of source-level feature implementation, never infer
    # full routing from an unrelated NullNet smoke-test ELF.
    c = BASE / "cooja_transport/paper024501-transport.c"
    src = c.read_text() if c.is_file() else ""
    physical = read_json("iotlab_m3/hardware_status.json")
    source_feature = {
        "source_payload_mapping": "bits_for_relevance" in src,
        "source_fragmentation": "PAPER024501_TX" in src,
        "sink_fragment_reassembly": "PAPER024501_RX_COMPLETE" in src,
        "RE_ETX_parent_select": bool(re.search(r"rpl_mrhof|etx_route_selection|parent_cost", src)),
        "distributed_spatial_relevance": bool(re.search(r"neighbor_observation|spatial_score", src)),
        "physical_energy_metered": bool(physical.get("hardware_energy_measured")),
    }
    state["protocol_hardware"] = {
        "status": "blocked_paper_equivalent_algorithm_not_ported",
        "source_features": source_feature,
        "experiment_458478": "physical transport demonstration only",
        "next_steps": ["Port relevance/context and RE-ETX with actual neighbour exchange",
                       "Add trace-identifiable routing decisions and total application bits",
                       "Compile on Cooja and M3 targets, then repeated paired trials",
                       "Use independent traffic/PHY captures and hardware-profile calibration"],
    }


def inspect_energy(state):
    e = read_json("full_network_energy/progress.json")
    installed = (pathlib.Path.home() / "Research/.iotlabcli-venv/bin/iotlab-profile").is_file()
    power = read_json("hardware_power_calibration/m3_power_measurement_audit.json")
    state["device_energy_calibration"] = {
        "status": "measured_total_board_power_COMPONENT_CALIBRATION_PENDING" if power.get("physical_power_trace_verified") else "not_calibrated",
        "observed_power_nodes": len(power.get("nodes", [])),
        "network_scenario_runs": e.get("completed", 0),
        "power_profile_cli_installed": bool(installed),
        "current_trace_files": len(power.get("nodes", [])),
        "next_steps": ["Define M3 consumption/voltage/period profile using testbed account",
                       "Reserve powered measurement nodes, flash isolated firmware roles",
                       "Capture and archive actual timestamped current/voltage samples",
                       "Integrate J = integral[V(t)*I(t)]dt and uncertainty",
                       "Calibrate sensing/CPU/idle/MAC energy values, rerun comparisons"],
        "auto_submit_hardware": False,
    }


def main():
    state = {"pipeline": "PAPER024501", "created_utc": NOW}
    try:
        create_manuscript(state)
    except Exception as e:
        state["manuscript"] = {"status": "failed", "error": repr(e)}
    try:
        make_response(state)
    except Exception as e:
        state["responses"] = {"status": "failed", "error": repr(e)}
    inspect_hardware(state)
    inspect_energy(state)
    (BASE/"manuscript_stage_status.json").write_text(json.dumps({
        "source_exists": bool(SOURCE.is_file()),
        "template_exists": bool(TEMPLATE.is_file() and GUIDE.is_file()),
        "draft_generated": OUT.is_file(),
        "draft_path": str(OUT.relative_to(ROOT)) if OUT.is_file() else None,
        "submission_ready": False,
        "unresolved": ["Full paper-equivalent receiver codec validation","M3 calibrated per-state energy",
                       "Cooja/M3 RE-ETX policy implementation","Authors' verified profiles/photos/declarations",
                       "Final equation, references and visual QA approval"]
    },indent=2)+"\n")
    state["scientific_release_allowed"] = False
    state["reason"] = "Original codec, hardware energy calibration and complete RE-ETX port are not established; editorial approval incomplete"
    save(state)
    print(json.dumps({k: v.get("status") for k, v in state.items() if isinstance(v, dict)}, indent=2))


if __name__ == "__main__":
    main()
