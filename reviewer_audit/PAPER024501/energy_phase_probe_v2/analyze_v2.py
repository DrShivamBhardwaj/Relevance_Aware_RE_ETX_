"""Paired phase-resolved M3 power measurements for ISL29020 light, CPU and MAC output.

Each board cycles: baseline, ISL29020 light sensor continuously active and
sampled, CPU arithmetic, and periodic broadcast output, 20s each. Parses raw
IoT-LAB power/voltage/current OML with serial-aggregator phase markers.
Differences are within-node *whole-board phase powers*, not deconvolved
transistor-level components or the original RE-ETX implementation.
"""
from pathlib import Path
import json,csv,re,hashlib,statistics
from math import sqrt
BASE=Path(__file__).resolve().parent
RAW=BASE/"active/consumption"
LOG=BASE/"active/serial_capture_2.log"
if not LOG.is_file(): LOG=BASE/"active/serial_aggregator.log"
start_re=re.compile(r"^([\d.]+);m3-(\d+);PHASE_V2_START phase=(\d+) tick=(\d+)")
points={}
if not LOG.is_file():raise SystemExit("WAIT_FOR_SERIAL_LOG")
for line in LOG.read_text(errors="replace").splitlines():
 m=start_re.search(line)
 if m:
  t,node,phase,tick=m.groups()
  points.setdefault(int(node),[]).append((float(t),int(phase),int(tick)))
def read_oml(path):
 if not path.is_file():return []
 rows=[]
 for line in path.read_text(errors="replace").splitlines():
  x=line.strip().split()
  if len(x)<8 or x[1]!="1":continue
  try:
   t=float(x[3])+float(x[4])/1e6
   p,v,i=(float(x[5]),float(x[6]),float(x[7]))
   if 0<p<5 and 2<v<5 and 0<i<2:rows.append((t,p,v,i))
  except ValueError:pass
 return rows
labels=("radio_on_baseline","light_ISL29020","CPU_busy","radio_broadcast")
segments=[]
for mote,starts in points.items():
 starts=sorted(set(starts))
 power=read_oml(RAW/f"m3_{mote}.oml")
 for (t,phase,tick),(end,_,_) in zip(starts,starts[1:]):
  if end-t<17 or end-t>26:continue
  selection=[p for p in power if t+2.5<=p[0]<=end-2.0]
  if len(selection)<3:continue
  segments.append({"mote":mote,"phase":labels[phase],"phase_index":phase,
   "tick":tick,"cycle":tick//80,"samples":len(selection),
   "avg_power_W":statistics.mean(x[1] for x in selection),
   "avg_current_A":statistics.mean(x[3] for x in selection),
   "avg_voltage_V":statistics.mean(x[2] for x in selection)})
if len(segments)<12:
 print("NOT_ENOUGH_PHASE_SEGMENTS",len(segments))
 raise SystemExit(2)
with (BASE/"phase_segments.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(segments[0]));w.writeheader();w.writerows(segments)
paired=[]
for mote in sorted(points):
 cycles=sorted({x["cycle"] for x in segments if x["mote"]==mote})
 for cy in cycles:
  data={x["phase_index"]:x for x in segments if x["mote"]==mote and x["cycle"]==cy}
  if 0 not in data:continue
  for phase in (1,2,3):
   if phase not in data:continue
   paired.append({"mote":mote,"cycle":cy,"phase":labels[phase],
                  "phase_minus_baseline_mW":1000*(data[phase]["avg_power_W"]-data[0]["avg_power_W"]),
                  "phase_minus_baseline_20s_mJ":20000*(data[phase]["avg_power_W"]-data[0]["avg_power_W"])})
with (BASE/"within_board_paired_deltas.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(paired[0]) if paired else ["mote"]);w.writeheader();w.writerows(paired)
perboard=[]
for mote in sorted(points):
 for phase in labels[1:]:
  x=[v["phase_minus_baseline_mW"] for v in paired if v["mote"]==mote and v["phase"]==phase]
  if x:perboard.append({"mote":mote,"phase":phase,"n_cycle_pairs":len(x),
                        "mean_increment_mW":statistics.mean(x),
                        "sd_cycle_mW":statistics.stdev(x) if len(x)>1 else None})
with (BASE/"perboard_phase_deltas.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(perboard[0]) if perboard else ["mote"]);w.writeheader();w.writerows(perboard)
report={"experiment_id":None,"motes":sorted(points),"raw_serial_file":str(LOG.relative_to(BASE)),
        "phase_windows":len(segments),"within_board_cycle_pairs":len(paired),
        "perboard_results":perboard,
        "real_ISL29020_sensor_instrumented":True,
        "real_CPU_workload_instrumented":True,
        "real_radio_broadcast_workload_instrumented":True,
        "real_REETX_phy_energy_decomposition":False,
        "calibrated_paper_equivalent_sensing_CPU_MAC":False,
        "scope":"Whole-board measured power under 4 workloads. No independent RE-ETX protocol-current calibration, no sensing-per-sample uncertainty at MAC level.",
        "limitation":"Same session, 3 motes and cyclic phases; time drift, neighbor traffic and MAC retries can confound causal per-component power."}
state=BASE/"phase_v2_run_state.json"
if state.is_file():
 try:report["experiment_id"]=json.loads(state.read_text()).get("experiment_id")
 except ValueError:pass
(BASE/"phase_v2_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"experiment":report["experiment_id"],"motes":len(points),"windows":len(segments),"within_board_pairs":len(paired),"power_calibration_equivalent":False}))
