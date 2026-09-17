import os
for v in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[v]='1'
from pathlib import Path
import json,gzip,hashlib,math,collections,random,subprocess
import numpy as np
O=Path('exploration/persistent-01/review-57');S=Path('exploration/persistent-01/worker-s');D=S/'S17';M=Path('exploration/persistent-01/coordinator/Q05-latin-clean')
def read(p):return json.loads(p.read_text())
def gz(p):return json.loads(gzip.decompress(p.read_bytes()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[p for p in D.iterdir() if p.is_file()]+[S/'s17_engine.cpp',S/'s17.py',S/'S17-CARD.md',M/'counts.json.gz',M/'held-controls.json.gz',M/'model.npz',Path('exploration/persistent-01/worker-f/F06-maps.json')]
hashes={str(p):sha(p) for p in inputs};(O/'inputs.json').write_text(json.dumps(hashes,indent=2))
counts=[{tuple(x['key']):x['count'] for x in rows} for rows in gz(M/'counts.json.gz')]
tot=[]
for rows in counts:
 d=collections.Counter()
 for k,v in rows.items():d[k[:-1]]+=v
 tot.append(d)
logp=np.empty((30,30,30))
for a in range(30):
 for b in range(30):
  for c in range(30):
   p=(counts[0].get((c,),0)+.5)/(tot[0][()]+15)
   p=(counts[1].get((b,c),0)+8*p)/(tot[1][(b,)]+8)
   p=(counts[2].get((a,b,c),0)+5*p)/(tot[2][(a,b)]+5)
   logp[a,b,c]=math.log(p)
assert np.max(abs(logp-np.load(M/'model.npz')['logp']))<1e-12
assert np.array_equal(np.fromfile(D/'model-table.bin',dtype='<f8').reshape(30,30,30),np.load(M/'model.npz')['logp'])
def token(xs,ends):
 out=[]
 for i,x in enumerate(xs):
  out.append(x)
  if i in ends:out.append(29)
 return out
def score(ts,mp):
 a=b=29;v=0
 for x in ts:
  c=29 if x==29 else mp[x];v+=float(logp[a,b,c]);a,b=b,c
 return v
packets=read(D/'packets.json');held=gz(M/'held-controls.json.gz');f06={p['page']:p for p in read(Path('exploration/persistent-01/worker-f/F06-maps.json'))}
rng=random.Random(1709202617)
for i in range(4):
 enc=list(range(29));rng.shuffle(enc);p=packets[i]
 assert p['source']==held[i] and p['truth']==held[i]['indices'] and p['ends']==held[i]['ends']
 assert enc==p['encoder_map'] and p['truth_map']==[enc.index(x) for x in range(29)]
 assert p['cipher']==[enc[x] for x in p['truth']]
for i,page in enumerate([0,17,55],4):
 assert packets[i]['source']==f06[page] and packets[i]['cipher']==f06[page]['indices']
 assert packets[i]['ends']==[w['end']-1 for w in f06[page]['words']]
plainrank=sorted(range(29),key=lambda x:(-counts[0].get((x,),0),x))
worst=0;nr=0;probes=0;evals=0;accepted=0;ctrl=[];actual=[];attempts=[]
for i,p in enumerate(packets):
 results=[]
 for j in ([None] if i<4 else [None]+list(range(19))):
  label=f'packet{i}-main' if j is None else f'packet{i}-null{j:02}'
  r=read(D/(label+'.json'));x=p['cipher']
  if j is not None:
   q=read(D/(label+'.input.json'));seed=1709172617+100*i+j;assert seed==q['seed']
   g=np.random.default_rng(seed);target=sum(a==b for a,b in zip(x,x[1:]))
   for n in range(1,q['attempts']+1):
    y=g.permutation(x).tolist();okay=sum(a==b for a,b in zip(y,y[1:]))==target
    assert okay==(n==q['attempts'])
   assert y==q['cipher'] and q['complete'] and n<=500000 and q['target_equal_count']==target
   x=y;attempts.append(n)
  assert r['cipher']==x and r['ends']==p['ends'] and r['exit']==0 and r['complete']
  ts=token(x,set(p['ends']));assert ts==r['tokens']
  assert r['seed']==1709182617+100*i+(0 if j is None else j+1)
  rank=sorted(range(29),key=lambda v:(-x.count(v),v));init=[0]*29
  for a,b in zip(rank,plainrank):init[a]=b
  assert r['restarts'][0]['initial']==init
  for row in r['restarts']:
   assert sorted(row['map'])==sorted(row['initial'])==list(range(29))
   got=[row['map'][v] for v in x];assert got==row['plain']
   inv={v:k for k,v in enumerate(row['map'])};assert [inv[v] for v in got]==x
   err=abs(score(ts,row['map'])-row['score']);worst=max(worst,err);assert err<1e-8
   assert row['evaluations']==30000+406*row['hill_sweeps'] and 1<=row['hill_sweeps']<=10
   assert 0<=row['accepted_sa']<=30000
   if row['local_optimum']:
    # Complete end-state local optimality, not a replay of optimization history.
    base=score(ts,row['map'])
    # Sample each packet main first restart only; kernel covers all swaps independently.
    if j is None and row['restart']==0:
     for a in range(29):
      for b in range(a+1,29):
       mp=row['map'].copy();mp[a],mp[b]=mp[b],mp[a]
       assert score(ts,mp)<=base+1e-8
   evals+=row['evaluations'];accepted+=row['accepted_sa'];nr+=1
  for probe in r['probes']:
   mp=probe['map'];before=score(ts,mp);cp=mp.copy();a,b=probe['a'],probe['b'];cp[a],cp[b]=cp[b],cp[a];after=score(ts,cp)
   assert max(abs(before-probe['before']),abs(after-probe['after']),abs(after-before-probe['delta']))<1e-8;probes+=1
  best=max(r['restarts'],key=lambda z:z['score']);assert best['restart']==r['best_restart'] and best['score']==r['maximum']
  assert abs(r['mean_token_score']-best['score']/len(ts))<1e-12
  results.append(r)
  if i<4:
   errors=[n for n,(a,b) in enumerate(zip(best['plain'],p['truth'])) if a!=b];truthscore=score(ts,p['truth_map']);truthrank=1+sum(z['score']>truthscore+1e-9 for z in r['restarts']);used=set(x)
   c=r['control'];assert errors==c['rune_errors'] and truthrank==c['truth_rank'] and abs(truthscore-c['truth_score'])<1e-8
   assert c['plaintext_accuracy']==1-len(errors)/len(x)
   assert c['observed_map_accuracy']==sum(best['map'][u]==p['truth_map'][u] for u in used)/len(used)
   assert c['full_map_accuracy']==sum(a==b for a,b in zip(best['map'],p['truth_map']))/29
   ctrl.append({'errors':len(errors),'truth_rank':truthrank,'unused':29-len(used)})
 if i>=4:
  exceed=sum(r['maximum']>=results[0]['maximum'] for r in results[1:]);actual.append({'packet':i,'exceed':exceed,'tail':(1+exceed)/20})
summary=read(D/'summary.json');assert nr==summary['restarts']==1536 and evals==summary['total_swap_evaluations_including_hill'] and accepted==summary['accepted_sa']
assert [r['tail'] for r in actual]==[r['tail'] for r in summary['actual']]
cmd=['c++','-O2','-std=c++17',str(O/'kernel.cpp'),'-o',str(O/'kernel')]
b=subprocess.run(cmd,capture_output=True);(O/'compile.stderr').write_bytes(b.stderr);assert b.returncode==0
r=subprocess.run([str(O/'kernel')],capture_output=True,timeout=60);(O/'kernel.stdout').write_bytes(r.stdout);(O/'kernel.stderr').write_bytes(r.stderr);assert r.returncode==0
assert all(sha(Path(p))==h for p,h in hashes.items())
result={'pass':True,'retained_paths':nr,'score_max_error':worst,'score_probes':probes,'controls':ctrl,'actual':actual,'nulls':len(attempts),'null_attempt_minmax':[min(attempts),max(attempts)],'evaluations_recorded_not_reexecuted':evals,'accepted_recorded':accepted,'kernel':json.loads(r.stdout),'compile':cmd,'compile_exit':b.returncode,'kernel_exit':r.returncode,'limits':'No global optimality or full annealing RNG replay; final scores and retained maxima only. No fresh corpus audit.'}
(O/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
