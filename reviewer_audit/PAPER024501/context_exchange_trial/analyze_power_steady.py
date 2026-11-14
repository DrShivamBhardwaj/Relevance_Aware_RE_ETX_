"""Steady-state M3 board power under 0/13/25/50B context traffic.

The first 120s show a large nonstationary voltage/power transition.
Exclude entire first two cycles (0-239s) before calculating comparisons.
Extrapolate subsequent phase start epoch from observed 60..300s serial
phase markers with documented median timestamp alignment. The firmware
sets each phase to 30 x CLOCK_SECOND; serial capture ended before terminal.
Only two within-node cycles are retained. No causal per-frame energy
calibration or paper-equivalent deployment claim is permitted.
"""
from pathlib import Path
from statistics import median,mean,stdev
from collections import defaultdict
import re,csv,json
BASE=Path(__file__).resolve().parent
LOG=BASE/"active/serial_capture_retry.log"
state=json.loads((BASE/"iotlab_state.json").read_text())
lines=LOG.read_text(errors="replace").splitlines()
matches=defaultdict(list)
for row in lines:
 m=re.search(r"^([0-9.]+);m3-(\d+);CONTEXT_PHASE role=\d+ mode=\d+ second=(\d+) bytes=\d+",row)
 if m:
  timestamp,node,second=m.groups()
  matches[int(node)].append(float(timestamp)-int(second))
def parse_oml(path):
 arr=[]
 for line in path.read_text(errors="replace").splitlines():
  f=line.split()
  if len(f)<8 or f[1]!="1":continue
  try:
   sec=float(f[3])+float(f[4])/1e6
   power=float(f[5])
   if 0<power<5:arr.append((sec,power*1000))
  except ValueError:pass
 return arr
out=[]
for node in state["nodes"]:
 sync=median(matches[node])
 power=parse_oml(BASE/"active/consumption"/f"m3_{node}.oml")
 for start in range(240,480,30):
  mode=(start//30)%4
  t=sync+start
  sample=[p for epoch,p in power if t+4<=epoch<t+26]
  if len(sample)<5:continue
  out.append({"node":node,"phase_start_second":start,"cycle":start//120,
    "mode":mode,"context_bytes":(0,13,25,50)[mode],
    "n_power_samples":len(sample),"mean_board_power_mW":mean(sample)})
with (BASE/"iotlab_steady_power_windows.csv").open("w",newline="") as f:
 if out:
  w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
deltas=[]
for node in state["nodes"]:
 for cycle in (2,3):
  window={r["mode"]:r for r in out if r["node"]==node and r["cycle"]==cycle}
  if 0 not in window:continue
  for mode in (1,2,3):
   if mode in window:
    deltas.append({"node":node,"cycle":cycle,"mode":mode,"context_bytes":(0,13,25,50)[mode],
      "mean_board_power_delta_mW":window[mode]["mean_board_power_mW"]-window[0]["mean_board_power_mW"]})
with (BASE/"iotlab_steady_paired_deltas.csv").open("w",newline="") as f:
 if deltas:
  w=csv.DictWriter(f,fieldnames=list(deltas[0]));w.writeheader();w.writerows(deltas)
grouped={}
for mode in (1,2,3):
 x=[r["mean_board_power_delta_mW"] for r in deltas if r["mode"]==mode]
 if x:grouped[str(mode)]={"context_bytes":(0,13,25,50)[mode],
   "n_same_board_cycles":len(x),"mean_delta_mW":mean(x),
   "min_delta_mW":min(x),"max_delta_mW":max(x),"sd_across_board_cycles_mW":stdev(x) if len(x)>1 else None}
audit={"experiment_id":state["experiment_id"],
 "calibration_type":"within-board physical phases, extrapolated periodic phase schedule",
 "first_240_seconds_excluded_due_to_nonstationary_startup":True,
 "boards":state["nodes"],"phase_windows":len(out),
 "paired_deltas":len(deltas),"summary":grouped,
 "independent_hardware_repetitions":0,
 "full_network_energy_calibrated":False,
 "source_sensing_real":False,
 "constraint":"Only two within-board steady cycles per board. Phase inference after serial capture uses firmware 30-second schedule, measured serial epoch alignment. PHY/MAC retries and radio-on-time not instrumented. No causal per-event current decomposition."}
(BASE/"iotlab_steady_power_audit.json").write_text(json.dumps(audit,indent=2)+"\n")
print(json.dumps({"experiment":audit["experiment_id"],"windows":len(out),"pairs":len(deltas),"summary":grouped},indent=2))
if len(out)<18 or len(deltas)<12:raise SystemExit("STEADY_PHASE_EVIDENCE_INCOMPLETE")
