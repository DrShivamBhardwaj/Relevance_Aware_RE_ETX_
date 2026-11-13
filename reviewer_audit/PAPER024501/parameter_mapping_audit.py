"""Analytical payload-map sweep, NOT a network-performance sensitivity experiment."""
from pathlib import Path
import csv,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from config import SimulationConfig
from simulator.semantic_payload import SemanticPayloadController

out=ROOT/"reviewer_audit/PAPER024501"
rows=[]
for t in (0.4,0.5,0.6):
 for h in (0.75,0.85,0.95):
  for floor in (0.65,0.75,0.85):
   for v in (0.0,0.4,0.5,0.6,0.75,0.85,0.95,1.0):
    cfg=SimulationConfig()
    cfg.semantic_high_recall_threshold=t
    cfg.semantic_high_confidence_threshold=h
    cfg.semantic_high_recall_min_ratio=floor
    p=SemanticPayloadController(cfg)
    rows.append({"threshold_low":t,"threshold_high":h,"protected_ratio":floor,"relevance":v,"payload_bits":int(p.payload_bits([v])[0])})
with (out/"parameter_mapping_sweep.csv").open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
weights=[]
for w in (0.2,0.4,0.6,0.8):
 for temporal,spatial in ((0,1),(0.25,0.75),(0.5,0.5),(0.75,0.25),(1,0)):
  score=w*temporal+(1-w)*spatial
  weights.append({"temporal_weight":w,"spatial_weight":1-w,"temporal_feature":temporal,"spatial_feature":spatial,"linear_combination":score})
with (out/"relevance_weight_analytical_sweep.csv").open("w",newline="") as f:
 writer=csv.DictWriter(f,fieldnames=list(weights[0]));writer.writeheader();writer.writerows(weights)
print(json.dumps({"payload_map_rows":len(rows),"relevance_weight_rows":len(weights),"network_performance_tested":False}))
