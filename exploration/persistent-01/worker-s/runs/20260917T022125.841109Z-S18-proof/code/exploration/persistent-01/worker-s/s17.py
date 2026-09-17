import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1';os.environ['MKL_NUM_THREADS']='1'
from pathlib import Path
import json,gzip,hashlib,subprocess,sys,time,datetime,random
import numpy as np
B=Path('exploration/persistent-01/worker-s');O=B/'S17';O.mkdir(exist_ok=True);M=Path('exploration/persistent-01/coordinator/Q05-latin-clean');SRC=Path('exploration/persistent-01/worker-f/F06-maps.json');DEAD=int(datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc).timestamp());STOP=Path('exploration/persistent-01/STOP')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def guard():assert not STOP.exists() and time.time()<DEAD
lm=np.load(M/'model.npz')['logp'];held=json.loads(gzip.decompress((M/'held-controls.json.gz').read_bytes()));counts=json.loads(gzip.decompress((M/'counts.json.gz').read_bytes()))[0];count={r['key'][0]:r['count'] for r in counts};plainrank=sorted(range(29),key=lambda r:(-count.get(r,0),r))
def setup():
 guard();(O/'model-table.bin').write_bytes(lm.astype('<f8').tobytes());cmd=['c++','-O3','-std=c++17',str(B/'s17_engine.cpp'),'-o',str(O/'engine')];p=subprocess.run(cmd,capture_output=True,timeout=120);(O/'build.stderr').write_bytes(p.stderr);assert p.returncode==0,p.stderr
 rng=random.Random(1709202617);packets=[]
 for i,h in enumerate(held):
  enc=list(range(29));rng.shuffle(enc);dec=[enc.index(r) for r in range(29)];packets.append({'id':i,'name':h['id'],'cipher':[enc[x] for x in h['indices']],'ends':h['ends'],'truth':h['indices'],'truth_map':dec,'encoder_map':enc,'source':h})
 pages={p['page']:p for p in json.loads(SRC.read_text())}
 for i,page in enumerate([0,17,55],4):
  p=pages[page];packets.append({'id':i,'name':f'original{page}','cipher':p['indices'],'ends':[w['end']-1 for w in p['words']],'source':p})
 (O/'packets.json').write_text(json.dumps(packets));inputs=[M/'model.npz',M/'held-controls.json.gz',M/'counts.json.gz',M/'model.json',SRC,B/'s17_engine.cpp',B/'S17-CARD.md'];meta={'hashes':{str(p):sha(p) for p in inputs},'compile':cmd,'binary_sha256':sha(O/'engine'),'model_table_sha256':sha(O/'model-table.bin'),'plain_frequency_rank':plainrank,'numpy_version':np.__version__,'null_rng':'numpy.default_rng PCG64'};(O/'manifest.json').write_text(json.dumps(meta,indent=2))
def checkfixed():
 meta=json.loads((O/'manifest.json').read_text());assert all(sha(Path(p))==h for p,h in meta['hashes'].items());assert sha(O/'engine')==meta['binary_sha256'];assert sha(O/'model-table.bin')==meta['model_table_sha256']
def null(ix,j):
 guard();path=O/f'packet{ix}-null{j:02}.input.json'
 if path.exists():return json.loads(path.read_text())
 p=json.loads((O/'packets.json').read_text())[ix];x=np.array(p['cipher']);target=int(np.sum(x[:-1]==x[1:]));seed=1709172617+100*ix+j;rng=np.random.default_rng(seed);start=time.monotonic();found=None
 for attempt in range(1,500001):
  if attempt%1000==0:guard()
  y=rng.permutation(x)
  if int(np.sum(y[:-1]==y[1:]))==target:found=y.tolist();break
 r={'packet':ix,'j':j,'seed':seed,'attempts':attempt,'seconds':time.monotonic()-start,'target_equal_count':target,'complete':found is not None,'cipher':found}
 path.write_text(json.dumps(r));return r

def tokens(xs,ends):
 es=set(ends);out=[]
 for i,x in enumerate(xs):out.append(x);out.extend([29] if i in es else [])
 return out

def py_score(ts,m):
 q=[29,29]+[29 if x==29 else m[x] for x in ts];return sum(float(lm[q[i-2],q[i-1],q[i]]) for i in range(2,len(q)))
def search(ix,j=None):
 guard();checkfixed();out=O/f'packet{ix}-'+Path('x') if False else O/(f'packet{ix}-main.json' if j is None else f'packet{ix}-null{j:02}.json')
 if out.exists():return json.loads(out.read_text())
 p=json.loads((O/'packets.json').read_text())[ix];xs=p['cipher'] if j is None else null(ix,j)['cipher'];assert xs is not None,'null generation UNKNOWN'
 ts=tokens(xs,p['ends']);freq=[xs.count(r) for r in range(29)];rank=sorted(range(29),key=lambda r:(-freq[r],r));init=[0]*29
 for a,b in zip(rank,plainrank):init[a]=b
 seed=1709182617+100*ix+(0 if j is None else j+1);inp=out.with_suffix('.txt');inp.write_text(' '.join(map(str,[len(ts),seed,DEAD]+init+ts))+'\n');cmd=[str((O/'engine').resolve()),str((O/'model-table.bin').resolve()),str(inp.resolve()),str(STOP.resolve())];start=time.monotonic();r=subprocess.run(cmd,capture_output=True,timeout=min(850,max(1,int(DEAD-time.time()))));seconds=time.monotonic()-start;out.with_suffix('.stderr').write_bytes(r.stderr);out.with_suffix('.stdout').write_bytes(r.stdout);assert r.returncode==0,('engine exit',r.returncode)
 data=json.loads(r.stdout);assert len(data['restarts'])==24
 for probe in data['probes']:
  m=probe['map'];before=py_score(ts,m);sw=m.copy();sw[probe['a']],sw[probe['b']]=sw[probe['b']],sw[probe['a']];after=py_score(ts,sw);assert abs(before-probe['before'])<1e-8 and abs(after-probe['after'])<1e-8 and abs(after-before-probe['delta'])<1e-8
 for row in data['restarts']:
  assert sorted(row['map'])==list(range(29));assert abs(py_score(ts,row['map'])-row['score'])<1e-8;row['plain']=[row['map'][x] for x in xs]
 best=max(data['restarts'],key=lambda r:r['score']);data.update({'packet':ix,'j':j,'cipher':xs,'ends':p['ends'],'tokens':ts,'seconds':seconds,'command':cmd,'exit':r.returncode,'best_restart':best['restart'],'maximum':best['score'],'mean_token_score':best['score']/len(ts),'complete':True})
 if ix<4:
  truth=p['truth'];used=sorted(set(xs));tmap=p['truth_map'];truthscore=py_score(ts,tmap)
  data['control']={'truth_score':truthscore,'truth_rank':1+sum(a['score']>truthscore+1e-9 for a in data['restarts']),'plaintext_accuracy':sum(a==b for a,b in zip(truth,best['plain']))/len(truth),'rune_errors':[i for i,(a,b) in enumerate(zip(truth,best['plain'])) if a!=b],'used_labels':used,'observed_map_accuracy':sum(best['map'][r]==tmap[r] for r in used)/len(used),'full_map_accuracy':sum(a==b for a,b in zip(best['map'],tmap))/29,'equivalent_on_observed':all(best['map'][r]==tmap[r] for r in used),'unused_labels':[r for r in range(29) if r not in used],'best_alternative_accuracy':max(sum(a==b for a,b in zip(truth,row['plain']))/len(truth) for row in data['restarts'])}
 out.write_text(json.dumps(data));print(json.dumps({'packet':ix,'null':j,'seconds':seconds,'maximum':data['maximum'],'control':data.get('control')}),flush=True);return data
mode=sys.argv[1]
if mode=='pilot':
 setup();r=search(0);samp=[null(i,0) for i in [4,5,6]];print(json.dumps({'pilot_search_seconds':r['seconds'],'null_generation':[ {k:v for k,v in a.items() if k!='cipher'} for a in samp],'forecast_64_search_seconds':64*r['seconds']}))
elif mode=='controls':
 checkfixed();rs=[search(i) for i in range(4)];gate=sum(r['control']['plaintext_accuracy']>=.8 for r in rs)>=2;(O/'controls-summary.json').write_text(json.dumps({'gate_at_least_two_80percent':gate,'controls':[r['control'] for r in rs]},indent=2));print('gate',gate)
elif mode=='actual':
 checkfixed();assert json.loads((O/'controls-summary.json').read_text())['gate_at_least_two_80percent'];ix=int(sys.argv[2]);assert ix in [4,5,6];search(ix)
 for j in range(19):search(ix,j)
