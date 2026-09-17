"""Small command logger for PERSISTENT-01; unique evidence directories, no scientific imports."""
import argparse,datetime,hashlib,json,os,pathlib,signal,subprocess,sys,time
ROOT=pathlib.Path(__file__).resolve().parents[2]
def main():
 p=argparse.ArgumentParser();p.add_argument('--owner',required=True);p.add_argument('--label',required=True);p.add_argument('--seconds',type=int,default=900);p.add_argument('--input',action='append',default=[]);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args();cmd=a.command[1:] if a.command[:1]==['--'] else a.command
 assert cmd and 0<a.seconds<=3600
 owner=ROOT/a.owner;assert owner.is_relative_to(ROOT/'exploration/persistent-01');now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
 run=owner/'runs'/(datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')+'-'+a.label);run.mkdir(parents=True,exist_ok=False)
 files=sorted(set([str(x.relative_to(ROOT)) for x in owner.glob('*.py')]+a.input+['exploration/persistent-01/run_logged.py']))
 hashes=[];(run/'code').mkdir()
 for name in files:
  q=ROOT/name;r={'path':name,'exists':q.is_file()}
  if q.is_file():
   b=q.read_bytes();r.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
   if q.suffix=='.py':d=run/'code'/name;d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(b)
  hashes.append(r)
 env=os.environ.copy();overrides={'PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1','PYTHONUNBUFFERED':'1','PYTHONUTF8':'1','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1','VECLIB_MAXIMUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1'};env.update(overrides)
 for k in ['PYTHONPATH','PYTHONHOME']:env.pop(k,None)
 record={'command':cmd,'cwd':'<REPO_ROOT>','working_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'started_utc':now(),'timeout_seconds':a.seconds,'environment_overrides':overrides,'sources_inputs':hashes,'outcome':'RUNNING','exit_code':None}
 save=lambda:(run/'command.json').write_text(json.dumps(record,indent=2)+'\n');save();start=time.monotonic()
 with (run/'stdout.txt').open('wb') as out,(run/'stderr.txt').open('wb') as err:
  try:
   child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdout=out,stderr=err,start_new_session=True)
   record['pid']=child.pid;save()
   awake=subprocess.Popen(['/usr/bin/caffeinate','-i','-w',str(child.pid)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   try:code=child.wait(timeout=a.seconds);record.update(exit_code=code,outcome='PASS' if code==0 else 'NONZERO')
   except subprocess.TimeoutExpired:
    os.killpg(child.pid,signal.SIGKILL);record.update(exit_code=child.wait(),outcome='TIMEOUT')
  except OSError as e:record.update(outcome='ERROR',error=str(e))
 record.update(finished_utc=now(),duration_seconds=time.monotonic()-start);save();print(json.dumps({'run':str(run.relative_to(ROOT)),'outcome':record['outcome'],'exit_code':record['exit_code'],'seconds':record['duration_seconds']}));return 0 if record['outcome']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
