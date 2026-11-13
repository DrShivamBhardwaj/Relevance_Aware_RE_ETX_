"""Physical 3-M3 RE-ETX-proxy data: matched serial windows, not PHY PDR.

The prototype uses synthetic readings, beacon-reception PRR, and modeled
energy debit.  It is NOT a full paper-equivalent 100-node RE-ETX comparison.
"""
import csv,json,re,hashlib,statistics
from pathlib import Path
BASE=Path(__file__).resolve().parent
FILE=BASE/"active/serial_capture_2.log"
if not FILE.is_file():raise SystemExit("MISSING_SERIAL_CAPTURE")
raw=FILE.read_text(errors="replace")
TX=re.compile(r"^([\d.]+);m3-(\d+);PAPER_PARENT source=(\d+) seq=(\d+) mode=(\d+) parent=(\d+) relevance_x100=(\d+) payload_bits=(\d+)")
RX=re.compile(r"^([\d.]+);m3-(\d+);PAPER_RX_COMPLETE src=(\d+) seq=(\d+) bits=(\d+) frags=(\d+) trialmode=(\d+)")
tx={};rx={}
for line in raw.splitlines():
 m=TX.search(line)
 if m:
  t,mote,src,seq,fixed,parent,rel,bits=m.groups()
  key=(int(src),int(seq))
  tx[key]={"tx_time":float(t),"physical_mote":int(mote),"source":key[0],"sequence":key[1],
           "fixed_flag":int(fixed),"route_parent":int(parent),
           "relevance":int(rel)/100,"bits":int(bits),"trialmode":(key[1]//12)%4}
 m=RX.search(line)
 if m:
  t,mote,src,seq,bits,frags,mode=m.groups()
  rx[(int(src),int(seq))]={"rx_time":float(t),"sink_mote":int(mote),
      "bits":int(bits),"frags":int(frags),"trialmode":int(mode)}
rows=[]
for key,t in tx.items():
 r=rx.get(key)
 good=bool(r and r["rx_time"]>=t["tx_time"] and r["bits"]==t["bits"] and r["trialmode"]==t["trialmode"])
 rows.append({**t,"matched_sink_complete":int(good),"latency_ms":round(1000*(r["rx_time"]-t["tx_time"]),3) if good else "",
              "right_censored":int(t["tx_time"]>max([v["rx_time"] for v in rx.values()] or [0])-3)})
rows.sort(key=lambda r:(r["source"],r["sequence"]))
with (BASE/"matched_trace.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else ["source"]);w.writeheader();w.writerows(rows)
modes=["adaptive_RE_ETX_proxy","fixed_RE_ETX_proxy","adaptive_direct","fixed_direct"]
summary=[]
for mode in range(4):
 for src in (2,3):
  d=[x for x in rows if x["trialmode"]==mode and x["source"]==src and not x["right_censored"]]
  if not d:continue
  lat=[x["latency_ms"] for x in d if x["matched_sink_complete"]]
  summary.append({"trialmode":mode,"mode":modes[mode],"source":src,
    "observed_tx":len(d),"sink_matched_complete":sum(x["matched_sink_complete"] for x in d),
    "trace_window_match_ratio":sum(x["matched_sink_complete"] for x in d)/len(d),
    "relay_parent_count":sum(x["route_parent"]==2 for x in d),
    "mean_requested_bits":statistics.mean(x["bits"] for x in d),
    "median_report_latency_ms":statistics.median(lat) if lat else None})
with (BASE/"physical_mode_summary.csv").open("w",newline="") as f:
 w=csv.DictWriter(f,fieldnames=list(summary[0]) if summary else ["mode"]);w.writeheader();w.writerows(summary)
report={"experiment_id":458513,"hardware":"Grenoble M3 96 sink, 97 relay, 98 source",
 "tx_reports_in_partial_capture":len(tx),"rx_reports_in_partial_capture":len(rx),
 "paired_rows":len(rows),"mode_summary":summary,
 "serial_sha256":hashlib.sha256(FILE.read_bytes()).hexdigest(),
 "full_original_RE_ETX_validated":False,
 "original_hardware_semantic_relevance":False,
 "hardware_residual_energy_measurement_in_policy":False,
 "source_event_sensor":"deterministic synthetic source, not ISL29020 or original correlated process",
 "routing_metric":"APP beacon PRR surrogate + modeled energy-debit proxy, not full-report ETX calibrated against ACK",
 "caveats":"Single physical deployment, non-randomized alternating policy order, partial serial window, small 3-node topology. Ratios are not independently sniffer-calibrated packet delivery."}
(BASE/"hardware_ab_audit.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"tx":len(tx),"rx":len(rx),"modes":len(summary),"full_original_validated":False}))
