"""Within-board phase-aligned M3 power comparison.

Do not mistake periodic probes for measured standalone sensing/CPU/radio
currents. With a 20s protothread timer, the CPU and TX work occurs mainly
at a phase transition; segment averages may not distinguish these loads.
"""
from pathlib import Path
import re,csv,json,statistics,hashlib
BASE=Path(__file__).resolve().parent
SER=BASE/"active/serial_phase_capture.log"
OML=BASE/"active/consumption"
EVENT=re.compile(r"^([\d.]+);m3-(\d+);PHASE_START node=\d+ phase=(\d+) round=(\d+)")
starts={}
for line in SER.read_text(errors="replace").splitlines():
 m=EVENT.search(line)
 if m:
  t,node,phase,round_id=m.groups()
  starts.setdefault(int(node),[]).append((float(t),int(phase),int(round_id)))
names={0:"idle_window",1:"CPU_work_window",2:"radio_output_window"}
samples={}
for node in (96,97,98):
 f=OML/f"m3_{node}.oml"
 if not f.is_file():raise FileNotFoundError(f)
 rows=[]
 for line in f.read_text().splitlines():
  x=line.strip().split()
  if len(x)<8 or x[1]!="1":continue
  try:
   ts=float(x[3])+float(x[4])/1e6
   p,v,c=map(float,x[5:8])
  except ValueError:continue
  if 0<p<5 and 2<v<5 and 0<c<2:rows.append((ts,p,v,c))
 samples[node]=rows
segments=[]
for node in sorted(starts):
 evt=sorted(set(starts[node]))
 for (t,phase,r),(end,_,_) in zip(evt,evt[1:]):
  if end-t<17 or end-t>24:continue
  eligible=[x for x in samples[node] if t+2<=x[0]<=end-2]
  if len(eligible)<3:continue
  segments.append({"mote":node,"round":r,"phase":names[phase],"start_epoch":t,
                   "end_epoch":end,"samples":len(eligible),
                   "mean_W":statistics.mean(x[1] for x in eligible),
                   "median_W":statistics.median(x[1] for x in eligible),
                   "mean_A":statistics.mean(x[3] for x in eligible),
                   "mean_V":statistics.mean(x[2] for x in eligible)})
path=BASE/"phase_window_summary.csv"
with path.open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(segments[0]) if segments else ["mote"]);w.writeheader();w.writerows(segments)
aggregates=[]
for node in sorted(starts):
 for phase in names.values():
  group=[x for x in segments if x["mote"]==node and x["phase"]==phase]
  if not group:continue
  aggregates.append({"mote":node,"phase":phase,"windows":len(group),
    "mean_W":statistics.mean(x["mean_W"] for x in group),
    "mean_A":statistics.mean(x["mean_A"] for x in group),
    "n_samples":sum(x["samples"] for x in group)})
with (BASE/"phase_mote_aggregates.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(aggregates[0]) if aggregates else ["mote"]);w.writeheader();w.writerows(aggregates)
deltas=[]
for node in sorted(starts):
 m={x["phase"]:x["mean_W"] for x in aggregates if x["mote"]==node}
 if all(x in m for x in names.values()):
  deltas.append({"mote":node,"cpu_minus_idle_mW":(m["CPU_work_window"]-m["idle_window"])*1000,
   "radio_minus_idle_mW":(m["radio_output_window"]-m["idle_window"])*1000})
with (BASE/"within_mote_phase_differences.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(deltas[0]) if deltas else ["mote"]);w.writeheader();w.writerows(deltas)
report={"experiment_id":458510,"boards":sorted(starts),"firmware":"simple phase-timed CPU workload and NullNet radio output",
 "phase_windows_with_usable_current_samples":len(segments),"paired_board_differences":len(deltas),
 "raw_power_files_verified":len(samples)==3,
 "raw_serial_sha256":hashlib.sha256(SER.read_bytes()).hexdigest(),
 "observed_within_mote_differences":deltas,
 "hardware_phase_comparison_complete":len(deltas)==3,
 "individual_sensing_energy_calibrated":False,"real_CPU_active_current_calibrated":False,
 "real_MAC_TX_RX_current_calibrated":False,"original_RE_ETX_energy_calibrated":False,
 "warning":"Each phase contains one protocol scheduling burst around a 20s timer. These are whole-board window averages, not standalone per-component current. Single testbed allocation; no independent repetition."}
(BASE/"phase_power_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps(report,indent=2))
