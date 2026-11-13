"""Restartable unattended reviewer-evidence pipeline.

All files under reviewer_audit/PAPER024501. Run modes:
  python run_revision_pipeline.py --archive-only
  python run_revision_pipeline.py --pilot
A pilot is executed in an isolated temporary directory and never overwrites
the archived original C1--C7 results. Testbed experiments require separate,
reviewed firmware/protocol setup and are explicitly excluded.
"""
import argparse,datetime,json,os,pathlib,subprocess,sys,tempfile,traceback
BASE=pathlib.Path(__file__).resolve().parent
ROOT=BASE.parents[1]
PY=sys.executable
STATUS=BASE/"pipeline_status.json"
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def load():
 try:return json.loads(STATUS.read_text())
 except (FileNotFoundError,ValueError):return {"created":now(),"stages":{}}
def save(state):STATUS.write_text(json.dumps(state,indent=2)+"\n")
def stage(state,name,args,timeout=600,env=None,cwd=None):
 rec=state["stages"].get(name,{})
 if rec.get("status")=="passed":return
 state["stages"][name]={"status":"running","started":now(),"command":args};save(state)
 try:
  p=subprocess.run(args,cwd=cwd or ROOT,env=env or os.environ.copy(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=timeout)
  log=BASE/(name+".log");log.write_text(p.stdout)
  state["stages"][name].update({"status":"passed" if p.returncode==0 else "failed","completed":now(),"exit_code":p.returncode,"log":str(log.relative_to(ROOT))})
 except subprocess.TimeoutExpired as e:
  (BASE/(name+".log")).write_text((e.stdout or b"").decode(errors="replace") if isinstance(e.stdout,bytes) else str(e.stdout or ""))
  state["stages"][name].update({"status":"timeout","completed":now(),"error":str(e)})
 except Exception as e:
  state["stages"][name].update({"status":"failed","completed":now(),"error":repr(e)})
 save(state)
def main():
 a=argparse.ArgumentParser();a.add_argument("--pilot",action="store_true");a.add_argument("--archive-only",action="store_true");args=a.parse_args()
 state=load();state["updated"]=now();state["scope"]="archive checks and analytical sweeps; pilot only when --pilot"
 stage(state,"archive_integrity",[PY,str(BASE/"audit_archived_results.py")])
 stage(state,"context_energy_illustration",[PY,str(BASE/"context_overhead_sensitivity.py")])
 stage(state,"payload_map_analytical_sweep",[PY,str(BASE/"parameter_mapping_audit.py")])
 if args.pilot and not args.archive_only:
  # Derived reproducibility test, never label this as source raw data
  for mode in ("C1","C3"):
   name="pilot_"+mode+"_seed42"
   rec=state["stages"].get(name,{})
   if rec.get("status")=="passed":continue
   wd=BASE/"pilot_workdirs"/name
   (wd/"results").mkdir(parents=True,exist_ok=True)
   env=os.environ.copy()
   env.update({"PYTHONPATH":str(ROOT),"EXPERIMENT_MODE":mode,"SEMANTIC_SEED":"42"})
   stage(state,name,[PY,str(ROOT/"run_semantic_re_etx.py")],timeout=1800,env=env,cwd=wd)
 state["pending_experiments"]=[
  "Reviewer full factorial network-level parameter sensitivity: require controlled rerun design and validated output",
  "Receiver-side reconstruction/error task: requires explicit encoding/decoding semantics, not just payload lengths",
  "Distributed context acquisition: requires realistic packet exchange scheduling and resulting relay-load/energy model",
  "Cooja implementation: existing Python simulator is not equivalent to embedded firmware",
  "FIT IoT-LAB: needs hardware firmware and reserved nodes; no physical validation is claimed",
  "Journal manuscript transformation and verified ORCID/profile/photograph/declarations"
 ]
 state["updated"]=now();save(state)
 print(json.dumps({"status":state["stages"],"pending":state["pending_experiments"]},indent=2))
if __name__=="__main__":main()
