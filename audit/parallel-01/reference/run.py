"""Bounded command logger; writes only owned directory."""
import pathlib,subprocess,os,json,datetime,time,sys,hashlib
D=pathlib.Path(__file__).parent;ROOT=D.parents[2];env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
commands=[('reference',[sys.executable,str(D/'check.py')]),('compare',[sys.executable,str(D/'compare.py')]),('inherited',[sys.executable,'analysis/reproduce/run_all.py','-v']),('inherited-comparison',[sys.executable,str(D/'inherited_comparison.py')])]
records=[]
for name,command in commands:
    start=time.monotonic();r=dict(name=name,argv=[str(pathlib.Path(x).relative_to(ROOT)) if str(x).startswith(str(ROOT)) else x for x in command],timeout_seconds=300,started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        p=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,timeout=300);r.update(exit=p.returncode,timed_out=False)
        (D/'logs'/(name+'.stdout.txt')).write_bytes(p.stdout);(D/'logs'/(name+'.stderr.txt')).write_bytes(p.stderr)
    except subprocess.TimeoutExpired as e:
        r.update(exit=None,timed_out=True);(D/'logs'/(name+'.stdout.txt')).write_bytes(e.stdout or b'');(D/'logs'/(name+'.stderr.txt')).write_bytes(e.stderr or b'')
    r['elapsed_seconds']=time.monotonic()-start;records.append(r)
(D/'logs'/'runs.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2))

sys.exit(0 if all(r.get("exit")==0 and not r["timed_out"] for r in records) else 1)
