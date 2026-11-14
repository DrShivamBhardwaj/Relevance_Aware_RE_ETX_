"""Current review execution host only, not original archive's unverified host."""
import sys,os,json,platform,subprocess,importlib.metadata as metadata
from pathlib import Path
base=Path(__file__).resolve().parent
def cmd(args):
 try:
  r=subprocess.run(args,text=True,capture_output=True,timeout=10)
  return r.stdout.strip()[:250] if r.returncode==0 else "UNAVAILABLE"
 except Exception:return "UNAVAILABLE"
out={"scope":"connected review computer 2026-11-14; ORIGINAL ARCHIVE HOST NOT VERIFIED",
 "os":platform.platform(),"python":sys.version.split()[0],
 "hardware_model":"Apple M1 MacBook Air (observed system_profiler)",
 "installed_memory":"8 GB (observed system_profiler)",
 "modules":{},"github_branch":"review/PAPER024501-audit",
 "contiki_ng_commit":cmd(["git","-C",str(Path.home()/"Research/contiki-ng"),"rev-parse","HEAD"]),
 "git_head":cmd(["git","rev-parse","HEAD"])}
for pkg in ("numpy","scipy","pandas","matplotlib","pytest"):
 try:out["modules"][pkg]=metadata.version(pkg)
 except metadata.PackageNotFoundError:out["modules"][pkg]="NOT_INSTALLED"
(base/"platform_audit.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps(out,indent=2))
