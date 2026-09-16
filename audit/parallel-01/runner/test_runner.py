"""Run the real wrapper body in temporary repositories with substituted child commands.
Only fixture ROOT, child-command list and timeout are changed through AST.
No inherited scientific command runs. Invoke --source PATH --label NAME.
"""
import argparse, ast, hashlib, json, os, pathlib, subprocess, sys, tempfile, time
HERE=pathlib.Path(__file__).resolve().parent
ENV=os.environ.copy()
ENV.update(PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1')
CASES={'all_success':('print("child success")',0,'PASS'),
 'exit_1':('print("child failure 1"); raise SystemExit(1)',1,'NONZERO_REQUIRES_REVIEW'),
 'exit_2':('import sys; print("child failure 2",file=sys.stderr); raise SystemExit(2)',2,'NONZERO_REQUIRES_REVIEW'),
 'signal':('import os,signal; os.kill(os.getpid(),signal.SIGTERM)',-15,'NONZERO_REQUIRES_REVIEW'),
 'timeout':('import time; print("before timeout",flush=True); time.sleep(30)',-9,'TIMEOUT'),
 'launch_error':(None,None,'ERROR')}
class Substitute(ast.NodeTransformer):
 def __init__(self, root, commands): self.root,self.commands=root,commands
 def visit_Assign(self,node):
  if any(isinstance(t,ast.Name) and t.id=='ROOT' for t in node.targets):
   node.value=ast.parse('Path('+repr(str(self.root))+')',mode='eval').body
  elif any(isinstance(t,ast.Name) and t.id=='commands' for t in node.targets):
   node.value=ast.parse(repr(self.commands),mode='eval').body
  return self.generic_visit(node)
 def visit_Constant(self,node):
  return ast.copy_location(ast.Constant(.2),node) if type(node.value)==int and node.value==300 else node

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--label',required=True);ap.add_argument('--expect-fixed',action='store_true');args=ap.parse_args()
 source=pathlib.Path(args.source).read_text(); dest=HERE/args.label;dest.mkdir(exist_ok=False)
 results=[]
 for name,(code,expected_child,outcome) in CASES.items():
  with tempfile.TemporaryDirectory(prefix='lp-runner-fixture-') as tmp:
   root=pathlib.Path(tmp);(root/'audit/tools').mkdir(parents=True)
   subprocess.run(['git','init','-q',tmp],check=True,env=ENV)
   subprocess.run(['git','-C',tmp,'-c','user.name=Fixture','-c','user.email=fixture@example.invalid','commit','-q','--allow-empty','-m','fixture'],check=True,env=ENV)
   child=[sys.executable,'-c',code] if code is not None else [str(root/'missing-executable')]
   commands=[('01-fixture',child),('02-after',[''+sys.executable,'-c','print("continued after first child")'])]
   tree=Substitute(root,commands).visit(ast.parse(source));ast.fix_missing_locations(tree)
   fixture=root/'audit/tools/run_t0.py';fixture.write_text(ast.unparse(tree)+'\n')
   started=time.time();p=subprocess.run([sys.executable,'-B',str(fixture)],capture_output=True,text=True,env=ENV,timeout=30)
   def redact(s): return s.replace(str(root),'<FIXTURE_ROOT>').replace(str(pathlib.Path.cwd()),'<REPO_ROOT>')
   (dest/(name+'.stdout.txt')).write_text(redact(p.stdout));(dest/(name+'.stderr.txt')).write_text(redact(p.stderr))
   runs=list((root/'audit/runs/T0').iterdir());assert len(runs)==1
   manifest=json.loads((runs[0]/'manifest.json').read_text())
   assert manifest[0]['exit_code']==expected_child and manifest[0]['outcome']==outcome,manifest
   assert manifest[1]['outcome']=='PASS',manifest
   for entry in manifest:
    for stream in ['stdout','stderr']:
     (dest/(name+'.'+entry[stream])).write_text(redact((runs[0]/entry[stream]).read_text()))
   (dest/(name+'.manifest.json')).write_text(redact(json.dumps(manifest,indent=2))+'\n')
   expected_parent=0 if name=='all_success' else 1
   if args.expect_fixed: assert p.returncode==expected_parent,(name,p.returncode)
   else: assert p.returncode==0,(name,p.returncode)
   results.append({'case':name,'parent_exit':p.returncode,'child_exit':expected_child,'child_outcome':outcome,'continued':True,'seconds':round(time.time()-started,3)})
  print(json.dumps(results[-1]),flush=True)
 metadata={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'command':['.venv/bin/python','-B','audit/parallel-01/runner/test_runner.py','--source',args.source,'--label',args.label]+(['--expect-fixed'] if args.expect_fixed else []),'started_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'fixture_timeout_seconds':.2,'parent_timeout_seconds':30,'cases':results,'missing_inputs':[],'skipped_tests':[]}
 (dest/'results.json').write_text(json.dumps(metadata,indent=2)+'\n')
if __name__=='__main__': main()
