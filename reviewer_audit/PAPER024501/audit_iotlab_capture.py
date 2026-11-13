"""Parse complete and partial Grenoble M3 PAPER024501 diagnostic traces.

Records explicitly pair application TX requests to sink RX_COMPLETE reassembly.
Capture edges are censored; a missing sink log is NOT automatically a channel
failure because no independent PHY sniffer was configured.
"""
from pathlib import Path
import re,sys,json,csv,statistics
BASE=Path(__file__).resolve().parent/"iotlab_m3/experiment_458478"
filename=sys.argv[1] if len(sys.argv)>1 else "serial_capture2.log"
src=BASE/filename
rows=src.read_text(errors="replace").splitlines()
pattern=re.compile(r"^([\d.]+);m3-(\d+);PAPER024501_(TX|RX_COMPLETE) source=(\d+) seq=(\d+) .*?bits=(\d+) frags=(\d+)")
tx={};rx={}
for line in rows:
 m=pattern.search(line)
 if not m:continue
 tm,mote,kind,source,seq,bits,frags=m.groups()
 e={"timestamp":float(tm),"mote":int(mote),"source":int(source),
    "seq":int(seq),"bits":int(bits),"fragments":int(frags)}
 if kind=="TX":tx[(e["source"],e["seq"])]=e
 else:rx[(e["source"],e["seq"])]=e
last=max([float(line.split(";")[0]) for line in rows if re.match(r"^\d{10}\.",line)] or [0])
paired=[];unpaired=[];censored=[]
for key,sent in sorted(tx.items()):
 received=rx.get(key)
 if received and received["timestamp"]>=sent["timestamp"] and received["bits"]==sent["bits"] and received["fragments"]==sent["fragments"]:
  paired.append({"source":key[0],"sequence":key[1],"bits":sent["bits"],
                 "fragments":sent["fragments"],"tx_epoch_s":sent["timestamp"],
                 "rx_epoch_s":received["timestamp"],
                 "latency_ms":round(1000*(received["timestamp"]-sent["timestamp"]),3)})
 elif sent["timestamp"]>last-2.0:
  censored.append(key)
 else:
  unpaired.append(key)
report={
 "experiment_id":458478,"source_log":filename,
 "physical_link":"IoT-LAB M3 direct NullNet/CSMA broadcast, fragmented application reports",
 "source_reports_observed":len(tx),"sink_complete_reports_observed":len(rx),
 "matched_completed":len(paired),"eligible":len(paired)+len(unpaired),
 "unmatched_eligible":len(unpaired),"right_censored":len(censored),
 "sink_without_corresponding_source_log":len(set(rx)-set(tx)),
 "trace_window_matched_ratio":len(paired)/(len(paired)+len(unpaired)) if paired or unpaired else None,
 "median_matched_latency_ms":statistics.median(p["latency_ms"] for p in paired) if paired else None,
 "first_source_epoch":min([s["timestamp"] for s in tx.values()] or [None]),
 "last_event_epoch":last,
 "hardware_RE_ETX_algorithm_tested":False,
 "hardware_energy_metered":False,
 "warning":"Trace-window matched ratio is not calibrated PHY PDR; incomplete logs, radio collisions and missed aggregator output are not distinguishable"
}
stem=Path(filename).stem
(BASE/(stem+"_audit.json")).write_text(json.dumps(report,indent=2)+"\n")
if paired:
 with (BASE/(stem+"_matched.csv")).open("w",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(paired[0]));w.writeheader();w.writerows(paired)
print(json.dumps(report,indent=2))
