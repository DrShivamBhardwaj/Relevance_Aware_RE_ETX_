from pathlib import Path
import csv,json
BASE=Path(__file__).resolve().parents[1]/"reviewer_audit/PAPER024501"

def test_all_cooja_context_pilots_are_archived_with_matching_packets():
    p=BASE/"context_exchange_trial/cooja_results.csv"
    rows=list(csv.DictReader(p.open()))
    assert len(rows)==20
    assert len({x["seed"] for x in rows})==5
    assert all(int(x["context_tx"])==int(x["context_rx"]) for x in rows)
    assert all(int(x["context_tx"])>0 for x in rows if int(x["mode"])>0)

def test_iotlab_context_power_audit_never_claims_calibrated_network_energy():
    a=json.loads((BASE/"context_exchange_trial/iotlab_steady_power_audit.json").read_text())
    assert a["full_network_energy_calibrated"] is False
    assert a["source_sensing_real"] is False
    assert a["first_240_seconds_excluded_due_to_nonstationary_startup"] is True

def test_original_event_trace_inference_rejects_wallclock_staleness():
    a=json.loads((BASE/"event_timing_depth/event_timing_audit.json").read_text())
    assert a["completed_original_simulator_runs"]==60
    assert a["physical_event_staleness_measured"] is False
    assert a["all_10_matched_seeds_per_topology"] is True
    assert len(a["paired_seed_contrasts"])==9

def test_event_timing_contrasts_use_ten_independent_seed_values():
    a=json.loads((BASE/"event_timing_depth/event_timing_audit.json").read_text())
    assert all(x["n_paired_seeds"]==10 for x in a["paired_seed_contrasts"])
    assert all(x["matched_both_delivered_events"]>=100 for x in a["paired_seed_contrasts"])
