#!/usr/bin/env python3
"""Resume an unchanged design, retaining failed attempts outside the analysis root.

Only infrastructure/incomplete-log failures may be retried. Completed outcomes,
including zero delivery, are reused without replacement.
"""
import csv,json,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'validation/cooja'))
import run_suite as rs
original=rs.execute

def resume(contiki,out,case,policy,replay,dry_run=False):
 folder=(out/f'{case["name"]}_s{case["seed"]}_{policy}').resolve()
 manifest=folder/'manifest.json'
 if manifest.exists():
  data=json.loads(manifest.read_text())
  if data['status']=='executed and accounting checks passed':
   rows=[{k:int(v) for k,v in row.items()} for row in csv.DictReader((folder/'offered_trace.csv').open())]
   print('REUSE',folder.name,flush=True);return rows,data['summary']
  archive=out.parent.parent/'cooja_failed_attempts'/out.parent.name/out.name/(folder.name+'_'+str(time.time_ns()))
  archive.parent.mkdir(parents=True,exist_ok=True)
  folder.rename(archive)
  (archive/'retry_reason.json').write_text(json.dumps({'reason':'incomplete or failed execution; completed outcomes were not replaced','original_status':data['status']},indent=2))
  print('ARCHIVE FAILED ATTEMPT',archive,flush=True)
 return original(contiki,out,case,policy,replay,dry_run)

if __name__=='__main__':
 rs.execute=resume
 rs.main()
