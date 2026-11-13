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
from datetime import datetime, timezone

from docx import Document
from docx.shared import Pt, RGBColor

BASE = pathlib.Path(__file__).resolve().parent
ROOT = BASE.parents[1]
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
    }
    fingerprint = hashlib.sha256(
        ("|".join(sha(p) for p in (SOURCE, TEMPLATE, GUIDE)) + json.dumps(data, sort_keys=True)).encode()
    ).hexdigest()
    hash_file = DEST / "manuscript_inputs.sha256"
    if OUT.is_file() and hash_file.is_file() and hash_file.read_text().strip() == fingerprint:
        state["manuscript"] = {"status": "working_draft_cached", "document": str(OUT.relative_to(ROOT)), "source_found": True}
        return

    doc = Document(SOURCE)
    groups = {
        "3.2. Channel, fragmentation and energy": [
            "REVISION EVIDENCE — The supplementary node-state energy study now debits modeled sensing, CPU, idle, neighbour-context/control, radio and approximate ACK costs. Moderate and high additional-cost profiles are assumptions, not hardware-calibrated current measurements. Therefore, any original radio-only reduction percentage must be identified as such and must not be generalized to deployment-wide energy."
        ],
        "4.2. Payload mapping and safeguards": [
            "MATHEMATICAL CORRECTION REQUIRED — The executable payload controller uses ρ_base(v) = 0.25 + 0.75v. If v ≥ 0.85, the safeguarded payload is 4000 bits; if 0.50 ≤ v < 0.85, the proportional payload is floored at 3000 bits; otherwise it follows 8·ceil[4000·ρ_base(v)/8]. Thus L(0.50) = 3000 bits, whereas the unguarded expression gives 2500 bits. Equation (6) must be replaced by an editable, consecutively numbered piecewise Word equation before submission."
        ],
        "6.5. What remains after matching the source bit budget": [
            "RECEIVER DIAGNOSTIC (new reference codec, NOT part of the submitted original): The 100-round matched-seed DCT experiment gave receiver RMSE 0.06534 for C3 and 0.06060 for C5. Paired C5 minus C3 RMSE was −0.004742 (95% CI −0.005711 to −0.003772; Holm-adjusted p = 0.000011; ten seeds). C3 did not establish a reliable event-F1 improvement over C5. These are codec-specific results and do not establish the application fidelity of the original length-only reporting scheme."
        ],
        "6.7. Sensitivity to multi-hop topology depth": [
            "INTERPRETATION LIMITATION — The archive supports depth-specific C3/C5 paired contrasts, but per-packet information age and event-to-receipt staleness were not recorded. Hop count alone is not sufficient to attribute the deep-topology reversal to stale relevance. No causal staleness mechanism is asserted."
        ],
        "7. Discussion and limitations": [
            "NEW CONTROLLED ENERGY SCENARIOS — In 10 paired seeds, C3 LND was 2636.4 rounds with no added cost, 1862.7 with the moderate assumed cost profile, and 1047.7 with the high-cost profile. Corresponding C1 LND values were 1268.6, 1042.9 and 725.9 rounds. The modeled advantage narrows as previously uncharged costs increase. Device-current calibration, context contention, ACK timing and chip duty-state measurements remain open.",
            "COOJA / FIT IoT-LAB SCOPE — Fifteen Cooja stress cases verified direct, fragmented NullNet/CSMA transport. FIT IoT-LAB Grenoble M3 experiment 458478 captured actual source transmissions and sink report reassembly. Neither study implemented the paper-equivalent distributed RE-ETX route-selection policy, and no hardware power profile was measured. Partial-window serial matching is not physical PHY PDR."
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
        "remaining": ["Replace original equation (6) with editable piecewise OMML",
                      "Author-confirmed ORCIDs, headshots and profiles",
                      "Journal's nine declarations",
                      "Verify references and updated figure/table layout",
                      "Full visual and editorial signoff"],
        "invariants": invariant,
    }


def make_response(state):
    if not REVIEWS.is_file():
        state["responses"] = {"status": "blocked", "reason": "Review matrix absent"}
        return
    rows = list(csv.DictReader(REVIEWS.open()))
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
            d.add_paragraph("Technical response / verification target: " + row["response_plan"])
            evidence = "PAPER024501_validation_memorandum.md and corresponding seed/hardware logs, where applicable; otherwise pending"
            d.add_paragraph("Evidence: " + evidence)
            d.add_paragraph("Manuscript section/page: pending final Word pagination and visual audit")
            d.add_paragraph("Disposition: PARTIAL / PENDING FINAL VERIFICATION")
    d.save(RESPONSE)
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
    installed = shutil.which("iotlab-profile")
    state["device_energy_calibration"] = {
        "status": "not_calibrated",
        "network_scenario_runs": e.get("completed", 0),
        "power_profile_cli_in_path": bool(installed),
        "current_trace_files": 0,
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
    state["scientific_release_allowed"] = False
    state["reason"] = "Original codec, hardware energy calibration and complete RE-ETX port are not established; editorial approval incomplete"
    save(state)
    print(json.dumps({k: v.get("status") for k, v in state.items() if isinstance(v, dict)}, indent=2))


if __name__ == "__main__":
    main()
