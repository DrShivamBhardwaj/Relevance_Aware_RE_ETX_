import csv,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]/"reviewer_audit/PAPER024501"

def test_received_cache_campaign_has_all_twenty_completed_pairs():
    p=json.loads((BASE/"distributed_context_100node/progress.json").read_text())
    assert (p["completed"],p["planned"]) == (20,20)
    rows=list(csv.DictReader((BASE/"distributed_context_100node/completed.csv").open()))
    assert len(rows)==20
    assert len({(r["variant"],r["seed"]) for r in rows})==20
    assert all(0<=float(r["context_rx_fraction"])<=1 for r in rows)
    assert all(float(r["context_battery_energy_j"])>=0 for r in rows)

def test_cooja_radio_loss_sweep_all_cases_and_three_udgm_settings():
    p=json.loads((BASE/"context_exchange_trial/cooja_rx_sweep/progress.json").read_text())
    assert (p["passed"],p["planned"]) == (15,15)
    rows=list(csv.DictReader((BASE/"context_exchange_trial/cooja_rx_sweep/results.csv").open()))
    assert len(rows)==60
    assert {float(r["udgm_rx_success"]) for r in rows}=={0.6,0.8,1.0}
    assert all(int(r["context_rx"])<=int(r["context_tx"]) for r in rows)

def test_failed_physical_serial_capture_never_called_verified_replication():
    r=json.loads((BASE/"context_exchange_replication/iotlab_state.json").read_text())
    assert r["experiment_id"]==458597
    assert r["serial_captured"] is False
    assert r["repeat_validation_successful"] is False
