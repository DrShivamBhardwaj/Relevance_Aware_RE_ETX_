"""Crossref DOI-title check only; no fabricated publication metadata.

Uses all DOI strings supplied in the 27-entry reviewer manuscript.
Reference [24] is a 1979 bibliographic record with a JSTOR stable link,
not a DOI. HTTP failures remain unresolved, not silently marked verified.
"""
from urllib.request import Request,urlopen
from urllib.parse import quote
from urllib.error import HTTPError
from pathlib import Path
import re,json,time,difflib
BASE=Path(__file__).resolve().parent
REFS=[
 (1,"10.1109/MCOM.2002.1024422","A survey on sensor networks"),
 (2,"10.1109/HICSS.2000.926982","Energy-efficient communication protocol for wireless microsensor networks"),
 (3,"10.1109/TWC.2002.804190","An application-specific protocol architecture for wireless microsensor networks"),
 (4,"10.1145/938985.939000","A high-throughput path metric for multi-hop wireless routing"),
 (5,"10.17487/RFC6550","RPL: IPv6 routing protocol for low-power and lossy networks"),
 (6,"10.17487/RFC6719","The minimum rank with hysteresis objective function"),
 (7,"10.1016/j.ins.2015.10.004","Data prediction, compression, and recovery in clustered wireless sensor networks for environmental monitoring applications"),
 (8,"10.1016/j.pmcj.2018.06.007","A distributed real-time data prediction and adaptive sensing approach for wireless sensor networks"),
 (9,"10.1109/JIOT.2018.2869986","Using correlated information to extend device lifetime"),
 (10,"10.1049/wss2.12070","ETXRE: Energy and delay efficient routing metric for RPL protocol and wireless sensor networks"),
 (11,"10.1016/j.vlsi.2023.102097","Energy and relevance-aware adaptive monitoring method for wireless sensor nodes with hard energy constraints"),
 (12,"10.1016/j.future.2023.11.007","Prediction-based data reduction with dynamic target node selection in IoT sensor networks"),
 (13,"10.1109/TNET.2020.3005549","The age of incorrect information: A new performance metric for status updates"),
 (14,"10.1109/JSAC.2021.3065072","Age of information: An introduction and survey"),
 (15,"10.1109/MCOM.001.2000604","Semantics-empowered communication for networked intelligent systems"),
 (16,"10.1109/TSP.2021.3071210","Deep learning enabled semantic communication systems"),
 (17,"10.1109/JIOT.2021.3114102","Energy-aware deep reinforcement learning scheduling for sensors correlated in time and space"),
 (18,"10.1109/MWC.101.2100269","Semantic communications: Overview, open issues, and future research directions"),
 (19,"10.1109/JSAC.2022.3223408","Beyond transmitting bits: Context, semantics, and task-oriented communications"),
 (20,"10.1109/ACCESS.2024.3381967","A survey on goal-oriented semantic communication: Techniques, challenges, and future directions"),
 (21,"10.1016/j.adhoc.2025.103972","Supervised machine learning-based ETX optimization for energy-efficient routing in IoT-enabled WSNs"),
 (22,"10.1016/j.icte.2026.08.005","An SDN-based adaptive payload structure and transmission management for reliable WSN data collection in extreme cold region environments"),
 (23,"10.1145/1464420.1464425","On the lifetime of wireless sensor networks"),
 (25,"10.2307/3001968","Individual comparisons by ranking methods"),
 (26,"10.3390/s25092823","Scalable semantic adaptive communication for task requirements in WSNs"),
 (27,"10.3390/s26196124","Prediction-aided adaptive semantic communication for IoT sensor streams under outdated channel state information"),
]
def norm(t):
 return re.sub(r"[^a-z0-9]+"," ",str(t).lower()).strip()
data=[]
for idx,doi,title in REFS:
 got=None;status="HTTP_FAILED";http=None;err=None
 for retry in range(4):
  try:
   req=Request("https://api.crossref.org/works/"+quote(doi,safe=""),headers={
    "User-Agent":"PAPER024501-Reference-Audit/1.0 (noncommercial research; human review)"})
   with urlopen(req,timeout=15) as r:
    m=json.load(r)["message"];http=r.status;got=m.get("title",[""])[0]
   status="DOI_TITLE_MATCH" if difflib.SequenceMatcher(None,norm(title),norm(got)).ratio()>=.75 else "TITLE_REQUIRES_CHECK"
   break
  except Exception as e:
   err=repr(e)
   time.sleep(2*(retry+1))
 data.append({"reference_no":idx,"DOI":doi,"expected_title":title,
              "Crossref_title":got,"http_status":http,"status":status,"failure":err if got is None else None})
 print(idx,status,flush=True)
 time.sleep(.3)
audit={"source":"PAPER024501 27-item reviewer manuscript; reviewer audit 14 Nov 2026",
 "total_entries":27,"doi_entries":len(data),
 "no_DOI_reference":{"reference_no":24,"title":"A simple sequentially rejective multiple test procedure",
                    "archive_url":"https://www.jstor.org/stable/4615733",
                    "Crossref_DOI_lookup":"not applicable; no DOI supplied"},
 "counts":{"verified_doi_title":sum(x["status"]=="DOI_TITLE_MATCH" for x in data),
   "requiring_manual_check":sum(x["status"]!="DOI_TITLE_MATCH" for x in data)},
 "note":"Titles only. Citation author order, volume, issue, pages and publication status are not certified by this automated title check.",
 "results":data}
(BASE/"reference_doi_title_audit.json").write_text(json.dumps(audit,indent=2)+"\n")
print("AUDIT",audit["counts"],flush=True)
