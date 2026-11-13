"""Conservative machine-checkable completion gates for PAPER024501."""
from pathlib import Path
import json,csv
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
sweep=BASE/"network_parameter_sweep"
stage={
 "reference_DCT_receiver_200round":{"complete":len(list((BASE/"receiver_campaign").glob("*_seed*.json")))==40,
  "scope":"NEW diagnostic reference codec, not submitted manuscript's codec"},
 "reference_DCT_receiver_100round":{"complete":len(list((BASE/"receiver_campaign_100r").glob("*_seed*.json")))==40,
  "scope":"NEW matched pre-mortality diagnostic"},
 "energy_node_state_scenarios":{"complete":len(list((BASE/"full_network_energy").glob("*_seed*.json")))==60,
  "scope":"C1/C3 x 10 seeds x 3 UNCALIBRATED cost assumptions"},
 "cooja_transport_diagnostic":{"complete":(BASE/"cooja_transport/campaign_results.json").exists() and len(json.loads((BASE/"cooja_transport/campaign_results.json").read_text()))==15,
  "scope":"15 NullNet/CSMA fragmentation simulations, not RE-ETX"},
 "iotlab_M3_transport_diagnostic":{"complete":(BASE/"iotlab_m3/experiment_458478/serial_capture2_audit.json").exists() and json.loads((BASE/"iotlab_m3/experiment_458478/serial_capture2_audit.json").read_text())["matched_completed"]>0,
  "scope":"Physical M3 application reassembly, not algorithm/energy validation"},
 "archive_integrity":{"complete":(BASE/"archive_check.json").exists()},
 "parameter_network_sweep":{"complete":len(list(sweep.glob("*_seed*.json")))==90 and (sweep/"paired_sensitivity_analysis.csv").exists()},
 "context_energy_analytic":{"complete":(BASE/"context_overhead_sensitivity.csv").exists(),"scope":"no per-node control frames; no lifetime counterfactual"},
 "receiver_side":{"complete":False,"reason":"Submitted codec absent; new reference DCT reconstruction is diagnostic only"},
 "full_energy_model":{"complete":False,"reason":"Full node-state reruns complete for 3 uncalibrated scenarios; no calibrated device currents or control airtime"},
 "deep_topology_staleness":{"complete":False,"reason":"No timestamped per-packet destination trace in archive"},
 "cooja":{"complete":False,"reason":"NullNet fragmentation/reference transport proved; actual RE-ETX firmware not implemented"},
 "iotlab":{"complete":False,"reason":"Grenoble M3 NullNet fragmentation validated physically; RE-ETX routing and energy meter not tested"},
 "IJWMT_docx":{"complete":False,"reason":"Submitted DOCX and template must be staged on Mac and visually audited; author metadata/photos/declarations need author confirmation"},
 "pointwise_response":{"complete":False,"reason":"Final page/line references need revised DOCX, validated experiments"}
}
report={"paper_id":"PAPER024501","scientific_gates":stage,"all_release_gates_pass":all(x["complete"] for x in stage.values()),"notice":"A draft manuscript is not camera-ready until all editorial gates and author data are confirmed"}
(BASE/"revision_gate_status.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"all_release_gates_pass":report["all_release_gates_pass"],"completed":[x for x,d in stage.items() if d["complete"]],"blocked":[x for x,d in stage.items() if not d["complete"]]},indent=2))
