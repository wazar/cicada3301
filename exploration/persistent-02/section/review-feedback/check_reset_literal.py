import itertools,random,json,sys,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'exploration/persistent-02/feedback'))
from reset_literal import Engine
rng=random.Random(9172304);records=[];paths=0
for t in range(120):
 n=rng.randrange(9);N=[2,3,5,29][t%4];k=1+t%3
 seeds=list(itertools.product(range(N),repeat=k)) if N<6 else [tuple(rng.randrange(N) for _ in range(k)) for _ in range(7)]
 c=[0 if rng.random()<.6 else rng.randrange(N) for _ in range(n)];ends={i for i in range(n) if rng.random()<.4};resets={i for i in range(n) if rng.random()<.5}
 L=np.array([rng.uniform(-3,2) if t%3 else rng.randrange(-2,2) for _ in range((N+1)**3)]).reshape((N+1,)*3)
 rows={};maxi=-float('inf');F=[i for i,x in enumerate(c) if x==0]
 for seed in seeds:
  for mask in itertools.product([False,True],repeat=len(F)):
   lit=frozenset(i for i,x in zip(F,mask) if x);hist=[];p=[];a=b=N;v=0
   for i,x in enumerate(c):
    if i in resets:hist=[]
    if i in lit:y=0
    else:
     z=seed[len(hist)] if len(hist)<k else sum(hist[-k:]);y=(x-z)%N;hist.append(y)
    p.append(y);v+=L[a,b,y];a,b=b,y
    if i in ends:v+=L[a,b,N];a,b=b,N
   rows[(seed,lit)]=(p,v);maxi=max(maxi,v);paths+=1
 maxima=[]
 for start in range(0,len(seeds),7):
  subset=seeds[start:start+7];a=Engine(subset,L).solve(c,ends,resets,retain=19,block=1);b=Engine(subset,L).solve(c,ends,resets,retain=19,block=5)
  assert a['alternatives']==b['alternatives']
  maxima.append(a['maximum'])
  for alt in a['alternatives']:
   p,v=rows[(tuple(alt['seed']),frozenset(alt['literal_positions']))];assert alt['plain']==p and abs(alt['total']-v)<1e-10
 assert abs(max(maxima)-maxi)<1e-10
 records.append(dict(test=t,N=N,k=k,n=n,seeds=len(seeds),cipher=c,ends=sorted(ends),resets=sorted(resets),maximum=float(maxi)))
# Resource refusal must be explicit, never return a silently pruned maximum.
try:Engine([[0],[1]],np.zeros((3,3,3)),max_states=1).solve([0],[],[])
except MemoryError:refusal=True
else:raise AssertionError('state guard failed')
result=dict(passed=True,cases=records,exhaustive_paths=paths,block_invariance=[1,5],state_refusal=refusal,source_sha256=hashlib.sha256((R/'exploration/persistent-02/feedback/reset_literal.py').read_bytes()).hexdigest())
(Path(__file__).parent/'literal-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(records),paths=paths,state_refusal=refusal)))
