import reset_literal as r,random,numpy as np,itertools,json
from pathlib import Path
rng=random.Random(2026092301);checks=[]
for case in range(60):
 N=2 if case<30 else 3;k=1+case%3;n=6;seed=[rng.randrange(N) for _ in range(k)];c=[rng.randrange(N) for _ in range(n)];ends={i for i in range(n) if rng.random()<.3};resets={i for i in range(n) if rng.random()<.3};L=np.array([rng.randrange(-8,2) for _ in range((N+1)**3)]).reshape((N+1,)*3);split=1+case%5
 # Independently choose a legal prefix mask, then enumerate every suffix mask.
 history=[];a=b=N;prefix=[]
 for i,x in enumerate(c[:split]):
  if i in resets:history=[]
  literal=x==0 and rng.random()<.5
  p=0 if literal else (x-(seed[len(history)] if len(history)<k else sum(history[-k:])))%N
  if not literal:history.append(p)
  prefix.append(p);a,b=b,p
  if i in ends:a,b=b,N
 initial=history[-k:];ctx=(a,b);best=-float('inf')
 for mask in itertools.product([False,True],repeat=sum(x==0 for x in c[split:])):
  hist=history.copy();aa,bb=ctx;s=0;mi=0
  for i in range(split,n):
   if i in resets:hist=[]
   literal=False
   if c[i]==0:literal=mask[mi];mi+=1
   p=0 if literal else (c[i]-(seed[len(hist)] if len(hist)<k else sum(hist[-k:])))%N
   if not literal:hist.append(p)
   s+=L[aa,bb,p];aa,bb=bb,p
   if i in ends:s+=L[aa,bb,N];aa,bb=bb,N
  best=max(best,s)
 out=r.Engine([seed],L).solve(c[split:],{i-split for i in ends if i>=split},{i-split for i in resets if i>=split},initial_history=initial,initial_context=ctx)
 assert out['maximum']==best
 checks.append(dict(case=case,N=N,k=k,split=split,maximum=float(best),initial_history=initial,initial_context=ctx))
Path('exploration/persistent-02/feedback/C08/continuation-check.json').write_text(json.dumps(checks,indent=2)+'\n');print('PASS',len(checks))
