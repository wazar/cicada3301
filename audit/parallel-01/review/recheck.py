"""Fresh reviewer reruns; all output goes in review, no worker artifacts touched."""
import pathlib,sys,json,hashlib,importlib.util,random,ast,tempfile,subprocess,os,time
ROOT=pathlib.Path(__file__).resolve().parents[3]; OUT=pathlib.Path(__file__).resolve().parent
ALPH='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
raw=(ROOT/'liber-primus/data/krisyotam_runes.txt').read_text()
segments=[[ALPH.index(c) for c in s if c in ALPH] for s in raw.split('%')];segments=[s for s in segments if s]
a=json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())
assert segments==[p['indices'] for p in a['pages']]
unsolved=segments[:-2];flat=sum(unsolved,[])
within=sum(x==y for s in unsolved for x,y in zip(s,s[1:]));combined=sum(x==y for x,y in zip(flat,flat[1:]))
results={'input':{'runes':len(flat),'hash':hashlib.sha256(','.join(map(str,flat)).encode()).hexdigest(),'within_page_pairs':within,'within_page_denominator':sum(len(s)-1 for s in unsolved),'combined_pairs':combined,'combined_denominator':len(flat)-1,'page_join_equalities':[i for i in range(len(unsolved)-1) if unsolved[i][-1]==unsolved[i+1][0]]}}
ref=load('fresh_ref','audit/parallel-01/reference/reference.py');fixture=load('fresh_fixture','audit/parallel-01/reference/fixtures.py')
rows=[]
for name,method,key,interrupt,pages in fixture.CASES:
 d=ROOT/'audit/parallel-01/reference/sources';cipher=ref.indices((d/(name+'.txt')).read_text());want=ref.indices((d/('solved_'+name+'.txt')).read_text());got=ref.decode(cipher,method,key,interrupt)
 assert got==want
 rows.append({'case':name,'runes':len(want),'complete_equal':got==want})
results['complete_reference_reruns']=rows
# A separately written totient decoder checks the complete 85-rune solved page.
cipher=ref.indices((d/'p56_an_end.txt').read_text()); primes=[];v=2
while len(primes)<len(cipher):
 if all(v%q for q in range(2,v)):primes.append(v)
 v+=1
out=[];fcount=0;ki=0
for c in cipher:
 fcount+=(c==0)
 if c==0 and fcount==4:out.append(0)
 else:out.append((c-(primes[ki]-1))%29);ki+=1
assert out==ref.indices((d/'solved_p56_an_end.txt').read_text())
results['independent_totient']={'runes':len(out),'complete_equal':True,'key_symbols_consumed':ki}
cs=load('fresh_checks','audit/parallel-01/detectors/checks.py')
wrong=[random.Random(4242).randrange(29) for i in range(4096)];rng=random.Random(4242);varied=[rng.randrange(29) for i in range(4096)]
results['constant_wrong_key']={'legacy_unique':len(set(wrong)),'legacy_symbol':wrong[0],'varied_unique':len(set(varied))}
# Fresh deterministic seed: unsupported skip2 and supported standard skip comparison.
results['detector_probes']=[]
for construction in ['reset','skip2','continuous']:
 ps,k,ct,u=cs.plant(120,52001,construction);result=cs.select(ct,k,ps)
 results['detector_probes'].append({'construction':construction,'seed':52001,'result':result})
# Run actual runner body with inert git answers in a disposable fixture. No git writes.
source=(ROOT/'audit/tools/run_t0.py').read_text()
class Adapt(ast.NodeTransformer):
 def __init__(self,root,cmd):self.root=root;self.cmd=cmd
 def visit_Assign(self,n):
  names=[t.id for t in n.targets if isinstance(t,ast.Name)]
  if 'ROOT' in names:n.value=ast.parse('Path('+repr(str(self.root))+')',mode='eval').body
  if 'commands' in names:n.value=ast.parse(repr([('fixture',self.cmd),('after',[sys.executable,'-c','print("after")'])]),mode='eval').body
  return self.generic_visit(n)
 def visit_FunctionDef(self,n):
  if n.name=='git':n.body=ast.parse('return "fixture-head" if args[0] == "rev-parse" else ""').body;return n
  return self.generic_visit(n)
 def visit_Constant(self,n):return ast.copy_location(ast.Constant(.2),n) if type(n.value)==int and n.value==300 else n
results['runner']=[]
for name,code,wanted,child in [('success','print("ok")',0,0),('exit1','raise SystemExit(1)',1,1),('exit2','raise SystemExit(2)',1,2),('signal','import os,signal;os.kill(os.getpid(),signal.SIGTERM)',1,-15),('timeout','import time;time.sleep(5)',1,-9),('launch',None,1,None)]:
 with tempfile.TemporaryDirectory(dir=OUT) as tmp:
  root=pathlib.Path(tmp);(root/'audit').mkdir();cmd=[sys.executable,'-B','-c',code] if code else [str(root/'does-not-exist')]
  tree=Adapt(root,cmd).visit(ast.parse(source));ast.fix_missing_locations(tree);p=root/'runner.py';p.write_text(ast.unparse(tree));r=subprocess.run([sys.executable,'-B',str(p)],capture_output=True,text=True,timeout=30)
  manifest=json.loads(next((root/'audit/runs/T0').glob('*/manifest.json')).read_text());assert r.returncode==wanted and manifest[0]['exit_code']==child and manifest[1]['outcome']=='PASS'
  results['runner'].append({'case':name,'parent_exit':r.returncode,'child_exit':child,'outcome':manifest[0]['outcome'],'continued':True})
  (OUT/(name+'.stdout.txt')).write_text(r.stdout);(OUT/(name+'.stderr.txt')).write_text(r.stderr)
(OUT/'results.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(results,indent=2))
