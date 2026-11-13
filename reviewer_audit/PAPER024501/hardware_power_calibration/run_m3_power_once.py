"""Idempotent, one-experiment Grenoble M3 power-profile campaign.

Uses an existing user-owned DC-current/voltage/power measurement profile.
The source binary is PAPER024501's simple fragmentation probe, NOT RE-ETX.
The experiment number is persisted immediately after submit, preventing
duplicate reservations on restarts. No hardware-calibrated RE-ETX claim.
"""
from pathlib import Path
import json,os,re,subprocess,sys,time
BASE=Path(__file__).resolve().parent
PAPER=BASE.parent
M3=PAPER/"iotlab_m3/firmware"
STATE=BASE/"m3_power_run_state.json"
CLI=Path.home()/"Research/.iotlabcli-venv/bin/iotlab-experiment"
KEY=Path.home()/".ssh/id_ed25519_iotlab"
HOST="sbhardwa@grenoble.iot-lab.info"
PROFILE="array_active_power_20261110"
NAME="PAPER024501_M3_POWER_DIAGNOSTIC_20261113"
WD=BASE/"active"
WD.mkdir(exist_ok=True)
def run(cmd,timeout=120,cwd=None):
 p=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,timeout=timeout,cwd=cwd)
 if p.returncode:raise RuntimeError("COMMAND "+str(cmd[:3])+" RC="+str(p.returncode)+" "+p.stderr[-700:])
 return p.stdout
def readstate():
 try:return json.loads(STATE.read_text())
 except (FileNotFoundError,ValueError):return {"campaign":NAME,"profile":PROFILE,"scope":"M3 NullNet reference diagnostic; not RE-ETX current calibration"}
def save(s):STATE.write_text(json.dumps(s,indent=2)+"\n")
def ssh(cmd,timeout=120):
 return run(["ssh","-o","BatchMode=yes","-o","ConnectTimeout=10","-i",KEY,HOST,cmd],timeout)
def experiment(s):
 expid=s.get("experiment_id")
 if expid is None:
  # One shot and single 3-node 8-minute allocation, never resubmit.
  active=json.loads(run([CLI,"get","-e"],timeout=25) or "{}")
  if active and active not in ({},{"items":[]}):
   raise RuntimeError("Other experiment active; would not reserve duplicate resources")
  raw=run([CLI,"submit","-n",NAME,"-d","8","-l",
           f"3,archi=m3:at86rf231+site=grenoble,,{PROFILE}"],timeout=50)
  expid=int(json.loads(raw)["id"])
  s["experiment_id"]=expid;s["reservation_submitted"]=True;save(s)
 return int(expid)
def apply_firmware(expid,s):
 if s.get("flashed") is True:return
 run([CLI,"wait","-i",str(expid),"--state","Running","--timeout","180","--step","5"],timeout=220)
 info=json.loads(run([CLI,"get","-i",str(expid),"-p"],timeout=35))
 nodes=sorted(int(x) for x in re.findall(r"m3-(\d+)\.grenoble", " ".join(info.get("nodes",[]))))
 if len(nodes)!=3:raise RuntimeError("Unexpected allocation "+str(nodes))
 s["nodes"]=nodes;save(s)
 files=["role1_sink.iotlab","role2_source.iotlab","role3_source.iotlab"]
 for fname in files:
  if not (M3/fname).is_file():raise FileNotFoundError(fname)
 scp=run(["scp","-o","BatchMode=yes","-o","ConnectTimeout=10","-i",KEY,
         *map(str,[M3/x for x in files]),f"{HOST}:/senslab/users/sbhardwa/"],timeout=160)
 for node,fname in zip(nodes,files):
  text=ssh(f"iotlab-node -i {expid} --flash /senslab/users/sbhardwa/{fname} -l grenoble,m3,{node}",timeout=65)
  (WD/f"flash_{node}.txt").write_text(text)
  obj=json.loads(text)
  if "0" not in obj:raise RuntimeError("Firmware flash failed for node "+str(node))
 text=ssh(f"iotlab-node -i {expid} --reset -l grenoble,m3,"+"+".join(map(str,nodes)),timeout=65)
 (WD/"reset.txt").write_text(text)
 if "0" not in json.loads(text):raise RuntimeError("Reset failed")
 s["flashed"]=True;save(s)
def capture(expid,s):
 if s.get("serial_captured"):return
 ns="+".join(map(str,s["nodes"]))
 cmd=f"timeout 105 serial_aggregator -i {expid} -l grenoble,m3,{ns}"
 p=subprocess.run(["ssh","-o","BatchMode=yes","-i",str(KEY),HOST,cmd],
                  capture_output=True,text=True,timeout=125)
 (WD/"serial_aggregator.log").write_text(p.stdout+"\n"+p.stderr)
 s["serial_captured"]=True;s["serial_returncode"]=p.returncode;save(s)
def archive(expid,s):
 if s.get("archive_retrieved"):return
 # Archive cannot be read until experiment reaches terminal state.
 run([CLI,"wait","-i",str(expid),"--state","Terminated,Stopped,Error","--timeout","650","--step","15"],timeout=685)
 p=subprocess.run([str(CLI),"get","-i",str(expid),"-a"],cwd=WD,capture_output=True,text=True,timeout=120)
 (WD/"archive_fetch.log").write_text(p.stdout+"\n"+p.stderr)
 target=WD/(str(expid)+".tar.gz")
 if p.returncode or not target.is_file() or target.stat().st_size==0:
  raise RuntimeError("IOT-LAB archive not downloaded")
 s["archive_retrieved"]=True;s["archive_path"]=str(target);save(s)
def main():
 s=readstate()
 try:
  expid=experiment(s)
  apply_firmware(expid,s)
  capture(expid,s)
  archive(expid,s)
  s["completed"]=True
  s.pop("last_error", None)
  s["conclusion"]="Measurement archive downloaded; power calibration and classification pending validated data parse"
  save(s)
  print(json.dumps(s,indent=2))
 except Exception as e:
  s["last_error"]=repr(e);save(s)
  print("POWER_CAMPAIGN_PAUSED",repr(e),file=sys.stderr)
  sys.exit(1)
if __name__=="__main__":main()
