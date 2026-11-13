"""Conservative machine-checkable completion gates for PAPER024501."""
from pathlib import Path
import json,csv
BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
sweep=BASE/"network_parameter_sweep"
stage={
 "archive_integrity":{"complete":(BASE/"archive_check.json").exists()},
 "parameter_network_sweep":{"complete":len(list(sweep.glob("*_seed*.json")))==90 and (sweep/"paired_sensitivity_analysis.csv").exists()},
 "context_energy_analytic":{"complete":(BASE/"context_overhead_sensitivity.csv").exists(),"scope":"no per-node control frames; no lifetime counterfactual"},
 "receiver_side":{"complete":False,"reason":"A source codec, decoder and timed delivery trace are not specified"},
 "full_energy_model":{"complete":False,"reason":"Missing validated sensing, idle, CPU and control-traffic profiles"},
 "deep_topology_staleness":{"complete":False,"reason":"No timestamped per-packet destination trace in archive"},
 "cooja":{"complete":False,"reason":"No paper-equivalent Contiki firmware or Cooja scenarios"},
 "iotlab":{"complete":False,"reason":"No paper-equivalent hardware firmware, calibration and reserved nodes"},
 "IJWMT_docx":{"complete":False,"reason":"Submitted DOCX and template must be staged on Mac and visually audited; author metadata/photos/declarations need author confirmation"},
 "pointwise_response":{"complete":False,"reason":"Final page/line references need revised DOCX, validated experiments"}
}
report={"paper_id":"PAPER024501","scientific_gates":stage,"all_release_gates_pass":all(x["complete"] for x in stage.values()),"notice":"A draft manuscript is not camera-ready until all editorial gates and author data are confirmed"}
(BASE/"revision_gate_status.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"all_release_gates_pass":report["all_release_gates_pass"],"completed":[x for x,d in stage.items() if d["complete"]],"blocked":[x for x,d in stage.items() if not d["complete"]]},indent=2))
