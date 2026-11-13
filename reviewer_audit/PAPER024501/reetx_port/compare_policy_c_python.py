"""Full grid parity of the C hardware payload rule with simulator Python."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
import json,subprocess,tempfile
import numpy as np
from config import SimulationConfig
from simulator.semantic_payload import SemanticPayloadController
BASE=Path(__file__).resolve().parent
source='''#include <stdio.h>
#include "paper024501_policy_core.h"
int main(void) {
 for(int i=0;i<=1000;i++)printf("%d %u\\n",i,paper_payload_bits((double)i/1000.0));
 return 0;
}
'''
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)/"compare.c";p.write_text(source)
 binary=Path(tmp)/"compare"
 run=subprocess.run(["cc","-std=c99","-O2","-I",str(BASE),str(p),"-lm","-o",str(binary)],capture_output=True,text=True)
 if run.returncode:raise RuntimeError(run.stderr)
 out=subprocess.run([str(binary)],capture_output=True,text=True,check=True)
 c={int(i):int(bits) for i,bits in (line.split() for line in out.stdout.splitlines())}
py=SemanticPayloadController(SimulationConfig())
expected=py.payload_bits(np.arange(1001,dtype=float)/1000.0)
mismatch=[(i,c[i],int(expected[i])) for i in range(1001) if c[i]!=int(expected[i])]
report={"n_relevance_points":1001,"matching":1001-len(mismatch),"mismatches":mismatch[:60],
        "same_rule_on_full_grid":not bool(mismatch),
        "scope":"formula parity only, not radio/energy or receiver validation"}
(BASE/"c_python_policy_parity.json").write_text(json.dumps(report,indent=2)+"\n")
print(json.dumps({"n":len(expected),"mismatches":len(mismatch),"examples":mismatch[:12]}))
if mismatch:raise SystemExit(1)
