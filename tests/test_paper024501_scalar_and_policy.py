"""Positive and negative scientific invariants for new diagnostics."""
from pathlib import Path
import json
from reviewer_audit.PAPER024501.receiver_scalar_source import ScalarSourceReceiver
BASE=Path(__file__).resolve().parents[1]/"reviewer_audit/PAPER024501"

def test_new_scalar_diagnostic_does_not_use_padding_as_information():
    a=ScalarSourceReceiver(1)
    b=ScalarSourceReceiver(1)
    a.record(0,1,0.625,True,1000,True)
    b.record(0,1,0.625,True,4000,True)
    assert a.results()==b.results()

def test_sink_holds_prior_source_value_on_packet_loss():
    a=ScalarSourceReceiver(1)
    a.record(0,1,0.625,True,1000,True)
    last=a.last[0]
    a.record(0,2,-0.5,False,1000,False)
    assert a.last[0]==last
    assert a.results()["received"]==1

def test_cpp_payload_parity_fully_exact_in_1001_point_grid():
    x=json.loads((BASE/"reetx_port/c_python_policy_parity.json").read_text())
    assert x["n_relevance_points"]==1001
    assert x["matching"]==1001
    assert x["mismatches"]==[]

def test_closure_gate_never_fabricates_original_receiver_validation():
    x=json.loads((BASE/"gap_closure_status.json").read_text())
    assert x["all_three_closed"] is False
    assert x["reviewer_fidelity"]["state"]=="NOT_ESTABLISHED_FOR_ORIGINAL_MANUSCRIPT"
    assert x["full_REETX_hardware"]["state"]=="PARTIAL_DIAGNOSTIC_PORT_NOT_PAPER_EQUIVALENT"
