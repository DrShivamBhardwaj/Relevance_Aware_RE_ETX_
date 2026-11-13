"""Physical M3 power/current/voltage integration for experiment 458482.

OML schema defines: timestamp_s, timestamp_us, power, voltage, current.
Scientific bounds: these are direct DC consumption profiles of a NullNet
fragmentation probe, NOT a calibrated sensing/CPU/idle/RE-ETX decomposition.
A single reservation is exploratory, not a repeated confirmatory campaign.
"""
from pathlib import Path
import csv,hashlib,json,math,statistics,sys
BASE=Path(__file__).resolve().parent
FILES=sorted((BASE/"active/consumption").glob("m3_*.oml"))
REPORT=BASE/"m3_power_measurement_audit.json"
DATA=BASE/"m3_power_node_summary.csv"
if len(FILES)!=3:
 print("WAITING_FOR_3_OML_FILES",len(FILES))
 raise SystemExit(1)
rows=[]
for f in FILES:
 lines=f.read_text(errors="replace").splitlines()
 schema=next((line for line in lines if line.startswith("schema: 1 control_node_measures_consumption")),None)
 if not schema or not all(x in schema for x in ("power:double","voltage:double","current:double")):
  raise RuntimeError("Unexpected OML schema in "+f.name)
 ts=[];power=[];voltage=[];current=[]
 for line in lines:
  x=line.strip().split()
  if len(x)<8 or x[1]!="1":continue
  try:
   t=float(x[3])+float(x[4])/1e6
   p=float(x[5]); v=float(x[6]); c=float(x[7])
  except ValueError:continue
  if not (0<p<5 and 2<v<5 and 0<c<2 and math.isfinite(t)):continue
  if ts and t<=ts[-1]:continue
  ts.append(t);power.append(p);voltage.append(v);current.append(c)
 if len(ts)<4:raise RuntimeError(f"{f.name}: fewer than 4 valid readings")
 err=[abs(p-v*c)/max(p,1e-9) for p,v,c in zip(power,voltage,current)]
 if max(err)>0.10:raise RuntimeError("Power-voltage-current mismatch >10% in "+f.name)
 span=ts[-1]-ts[0]
 energy=sum((power[k]+power[k-1])*(ts[k]-ts[k-1])/2 for k in range(1,len(ts)))
 if not (span>10 and energy>0):raise RuntimeError("Invalid energy integration")
 rows.append({"node":f.stem,"samples":len(ts),"duration_s":round(span,3),
              "mean_power_W":round(energy/span,8),
              "median_power_W":round(statistics.median(power),8),
              "mean_current_A":round(statistics.mean(current),8),
              "mean_voltage_V":round(statistics.mean(voltage),8),
              "integrated_energy_J":round(energy,6),
              "max_relative_vi_mismatch":round(max(err),8),
              "sha256":hashlib.sha256(f.read_bytes()).hexdigest()})
with DATA.open("w",newline="") as fp:
 w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
report={"experiment_id":458482,"profile":"array_active_power_20261110",
 "hardware":"FIT IoT-LAB Grenoble M3, DC consumption profile",
 "source_program":"PAPER024501 NullNet 3-node fragmentation probe",
 "nodes":rows,"n_independent_hardware_experiments":1,
 "timestamp_integration":"trapezoidal integral over measured W and seconds",
 "physical_power_trace_verified":True,
 "source_policy_RE_ETX_ported":False,
 "component_level_sensing_CPU_idle_ack_energy_calibrated":False,
 "calibrated_network_simulator":False,
 "duty_state_calibration":"not present: no hardware phase tags/sensing-only/CPU-only/idle-only controls",
 "interpretation":"Measured total M3 board power during a transport demonstration; does not directly quantify model-level per-activity energy or RE-ETX performance"}
REPORT.write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"verified_nodes":len(rows),"samples_total":sum(r["samples"] for r in rows),
 "avg_power_W":[r["mean_power_W"] for r in rows],
 "integrated_energy_J":[r["integrated_energy_J"] for r in rows],
 "per_component_calibrated":False},indent=2))
