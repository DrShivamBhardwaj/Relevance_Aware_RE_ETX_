"""Physical IoT-LAB context-packet and power-window audit.

Scope: three Grenoble M3 boards. 0/13/25/50-byte synthetic neighbour
context, 30-second modes, application-serial counters and whole-board DC power.
Cannot establish deployment-wide energy saving, actual 100-bit context,
link-layer reception, or original 100-node RE-ETX implementation.
"""
from pathlib import Path
import re,json,csv,statistics,hashlib
BASE=Path(__file__).resolve().parent
ACTIVE=BASE/"active"
STATE=BASE/"iotlab_state.json"
RUN=json.loads(STATE.read_text())
LOG=ACTIVE/"serial_capture_retry.log"
if not LOG.is_file():LOG=ACTIVE/"serial_aggregator.log"
if not LOG.is_file():raise SystemExit("NO_SERIAL_TRACE")
text=LOG.read_text(errors="replace")
CAPTURED=[]
pattern=re.compile(r"^([0-9.]+);m3-(\d+);(CONTEXT_PHASE|CONTEXT_TX|CONTEXT_RX|REPORT_TX|REPORT_RX) (.*)$")
for line in text.splitlines():
 m=pattern.match(line)
 if not m:continue
 at,node,typ,rest=m.groups()
 attrs={}
 for k,v in re.findall(r"([a-zA-Z_]+)=([0-9]+)",rest):
  attrs[k]=int(v)
 CAPTURED.append({"epoch":float(at),"node":int(node),"type":typ,**attrs})
def key(m,kind):
 return (m.get("mode"),m.get("second"),kind)
bytype={k:[x for x in CAPTURED if x["type"]==k] for k in
 ["CONTEXT_PHASE","CONTEXT_TX","CONTEXT_RX","REPORT_TX","REPORT_RX"]}
counts=[]
for mode,nb in enumerate((0,13,25,50)):
 ct=[x for x in bytype["CONTEXT_TX"] if x.get("mode")==mode]
 cr=[x for x in bytype["CONTEXT_RX"] if x.get("mode")==mode]
 dt=[x for x in bytype["REPORT_TX"] if x.get("mode")==mode]
 dr=[x for x in bytype["REPORT_RX"] if x.get("mode")==mode]
 ctkeys={x["second"] for x in ct}
 crkeys={x["second"] for x in cr}
 dtkeys={(x.get("source"),x["second"]) for x in dt}
 drkeys={(x.get("source"),x["second"]) for x in dr}
 counts.append({"mode":mode,"context_application_bytes":nb,
   "logged_context_sent":len(ctkeys),"logged_context_received":len(crkeys),
   "matched_context_rx_tx":len(ctkeys&crkeys),
   "logged_data_sent":len(dtkeys),"logged_data_received":len(drkeys),
   "matched_data_rx_tx":len(dtkeys&drkeys),
   "capture_covers_full_experiment":False})
with (BASE/"iotlab_packet_counts.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(counts[0]));w.writeheader();w.writerows(counts)
OML=ACTIVE/"consumption"
def read_oml(path):
 if not path.is_file():return []
 data=[]
 for line in path.read_text(errors="replace").splitlines():
  x=line.strip().split()
  if len(x)<8 or x[1]!="1":continue
  try:
   timestamp=float(x[3])+float(x[4])/1e6
   power,volt,amp=map(float,x[5:8])
   if 0<power<5 and 2<volt<5 and 0<amp<2:
    data.append((timestamp,power,volt,amp))
  except ValueError:pass
 return data
windows=[]
for node in RUN["nodes"]:
 phase=[x for x in bytype["CONTEXT_PHASE"] if x["node"]==node]
 phase.sort(key=lambda x:x["epoch"])
 series=read_oml(OML/f"m3_{node}.oml")
 for start,nextone in zip(phase,phase[1:]):
  span=nextone["epoch"]-start["epoch"]
  if not 27<=span<=34:continue
  selected=[p for p in series if start["epoch"]+3<=p[0]<=nextone["epoch"]-3]
  if len(selected)<5:continue
  windows.append({"node":node,"role":start["role"],
     "mode":start["mode"],"cycle":start["second"]//120,
     "context_application_bytes":start["bytes"],
     "start_second":start["second"],"n_current_samples":len(selected),
     "mean_board_power_mW":statistics.mean(p[1] for p in selected)*1000,
     "mean_board_current_mA":statistics.mean(p[3] for p in selected)*1000,
     "mean_board_voltage_V":statistics.mean(p[2] for p in selected)})
with (BASE/"iotlab_power_windows.csv").open("w",newline="") as f:
 if windows:
  w=csv.DictWriter(f,fieldnames=list(windows[0]));w.writeheader();w.writerows(windows)
diff=[]
for node in RUN["nodes"]:
 cycles=sorted({x["cycle"] for x in windows if x["node"]==node})
 for c in cycles:
  sets={x["mode"]:x for x in windows if x["node"]==node and x["cycle"]==c}
  if 0 not in sets:continue
  for m in (1,2,3):
   if m in sets:
    diff.append({"node":node,"cycle":c,"mode":m,
      "context_application_bytes":(0,13,25,50)[m],
      "board_power_delta_vs_mode0_mW":sets[m]["mean_board_power_mW"]-sets[0]["mean_board_power_mW"],
      "n_phase_samples":sets[m]["n_current_samples"]})
with (BASE/"iotlab_power_paired_deltas.csv").open("w",newline="") as f:
 if diff:
  w=csv.DictWriter(f,fieldnames=list(diff[0]));w.writeheader();w.writerows(diff)
record={"experiment_id":RUN["experiment_id"],"three_nodes":RUN["nodes"],
  "status":"COMPLETED" if RUN.get("completed") else "INCOMPLETE",
  "captured_context_packet_modes":counts,"serial_lines":len(text.splitlines()),
  "raw_power_board_count":sum(bool(read_oml(OML/f"m3_{n}.oml")) for n in RUN["nodes"]),
  "phase_windows_usable":len(windows),
  "paired_board_mode_comparisons":len(diff),
  "channel_or_physical_PDR_calibrated":False,
  "full_network_energy_savings_validated":False,
  "original_REETX_firmware_validated":False,
  "serial_sha256":hashlib.sha256(LOG.read_bytes()).hexdigest(),
  "limitations":"3-node prototype with synthetic source reports and isolated context frames. Whole-board power and serial reception are observational; mixed traffic and temporal drift preclude independently calibrated per-context joules. Full experiment serial coverage not independently sniffer-confirmed."}
(BASE/"iotlab_audit.json").write_text(json.dumps(record,indent=2)+"\n")
print(json.dumps({"experiment":RUN["experiment_id"],"raw_boards":record["raw_power_board_count"],
 "phase_windows":len(windows),"within_board_deltas":len(diff),
 "context_sent":[x["logged_context_sent"] for x in counts],
 "context_received":[x["logged_context_received"] for x in counts]}))
if record["raw_power_board_count"]<3 or len(windows)<6:
 raise SystemExit("PHYSICAL_POWER_EVIDENCE_INCOMPLETE")
