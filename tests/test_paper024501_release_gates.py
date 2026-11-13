"""Machine-verifiable safeguards preventing premature journal claims."""
import json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/"reviewer_audit/PAPER024501"

def test_draft_is_never_claimed_submission_ready():
    state=json.loads((BASE/"unattended_release_status.json").read_text())
    assert state["scientific_release_allowed"] is False
    assert state["manuscript"]["status"] in ("red_marked_evidence_draft_NOT_submission_ready","blocked")
    # A CI runner has no local ~/Downloads journal source. Both statuses
    # correctly block journal release; source presence is Mac-specific.
    assert state["protocol_hardware"]["source_features"]["RE_ETX_parent_select"] is False

def test_scientific_gate_rejects_missing_original_codec_and_calibration():
    gate=json.loads((BASE/"revision_gate_status.json").read_text())
    assert not gate["all_release_gates_pass"]
    assert not gate["scientific_gates"]["receiver_side"]["complete"]
    assert not gate["scientific_gates"]["full_energy_model"]["complete"]
    assert not gate["scientific_gates"]["iotlab"]["complete"]

def test_payload_controller_branch_is_explicitly_correct():
    import csv
    rows=list(csv.DictReader((BASE/"payload_mapping_review.csv").open()))
    table={float(x["relevance_v"]):int(x["payload_bits"]) for x in rows}
    assert len(rows)==11
    assert table[0.0]==1000
    assert table[0.5]==3000
    assert table[0.9]==4000
