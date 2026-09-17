"""Independent explicit seeds x legal literal masks; no state merges."""
import itertools,random,json,pathlib,time
import numpy as np
from literal_feedback import Engine
O=pathlib.Path(__file__).resolve().parent/'C05';O.mkdir(exist_ok=True)
def exhaustive(c,k,L,ends):
 N=len(L)-1;rows=[]
 for seed in itertools.product(range(N),repeat=k):
  f=[i for i,x in enumerate(c) if x==0]
  for bits in itertools.product([0,1],repeat=len(f)):
   literal={i for i,b in zip(f,bits) if b};history=[];p=[];score=0.;a=b=N
   for i,v in enumerate(c):
    if i in literal:r=0
    else:r=(v-(seed[len(history)] if len(history)<k else sum(history[-k:])))%N;history.append(r)
    score+=L[a,b,r];a,b=b,r
    if i in ends:score+=L[a,b,N];a,b=b,N
    p.append(r)
   rows.append((float(score),seed,tuple(p),tuple(sorted(literal))))
 return rows
if __name__=='__main__':
 rng=random.Random(2026092100);results=[]
 for rep in range(60):
  N=[2,3,5,29][rep%4];k=[1,2,3][rep%3];length=0 if rep==0 else rng.randrange(1,7)
  if N==29 and k==3:length=min(length,3)
  c=[rng.randrange(N) if rng.random()<.6 else 0 for _ in range(length)];ends={i for i in range(length) if rng.random()<.3};L=np.array([rng.randrange(-4,3) if rep%3 else 0 for _ in range((N+1)**3)],dtype=float).reshape((N+1,)*3)
  rows=exhaustive(c,k,L,ends);want=max(r[0] for r in rows);got=Engine(k,L).solve(c,ends,retain=16,block=2);assert got['maximum']==want
  valid={(r[2],r[3]):r[0] for r in rows}
  for alt in got['alternatives']:assert valid[(tuple(alt['plain']),tuple(alt['literal_positions']))]==alt['total']
  results.append(dict(rep=rep,N=N,k=k,cipher=c,ends=sorted(ends),paths=len(rows),maximum=want,result=got));print(rep,N,k,length,len(rows),got['seconds'],flush=True)
 (O/'tiny-tests.json').write_text(json.dumps(results,separators=(',',':'))+'\n');print('PASS',len(results),sum(r['paths'] for r in results))
