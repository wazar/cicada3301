import itertools,random,json,sys,hashlib
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/decoder/reset-feedback';sys.path.insert(0,str(D))
import model,solver
rng=random.Random(9172405);tests=[];maxerr=0;checks=0
for t in range(36):
 k=2+t%7;n=rng.randrange(1,90);c=[rng.randrange(29) for _ in range(n)];ends={i for i in range(n) if rng.random()<.3};resets={i+1 for i in ends if i+1<n and rng.random()<.7}
 if t%3==0:resets.add(0)
 L=np.array([rng.uniform(-4,1) for _ in range(30**3)]).reshape((30,)*3);W,B,q,info=model.factors(c,ends,k,resets,L)
 for rep in range(40):
  seed=[rng.randrange(29) for _ in range(k)];x=[(-z)%29 for z in seed];x.append((-sum(x))%29);hist=[];p=[]
  for i,v in enumerate(c):
   if i in resets:hist=[]
   key=seed[len(hist)] if len(hist)<k else sum(hist[-k:]);p.append((v-key)%29);hist.append(p[-1])
  assert model.decode(c,seed,resets)==p
  assert [int((v+x[j])%29) for v,j in zip(q,info['phases'])]==p
  a=b=29;direct=0.
  for i,z in enumerate(p):
   direct+=L[a,b,z];a,b=b,z
   if i in ends:direct+=L[a,b,29];a,b=b,29
  err=abs(direct-model.value(W,B,x));maxerr=max(maxerr,err);assert err<1e-10;checks+=1
 tests.append(dict(t=t,k=k,n=n,resets=sorted(resets),ends=sorted(ends)))
# Independent exhaustive constrained-offset maxima; arbitrary B exercises all cross-reset terms.
solves=[]
for t in range(6):
 k=2 if t<4 else 3;m=k+1
 W=np.array([rng.uniform(-2,2) for _ in range(m*29**3)]).reshape(m,29,29,29);B=np.array([rng.uniform(-2,2) for _ in range(m*29**2)]).reshape(m,29,29)
 best=-float('inf')
 for prefix in itertools.product(range(29),repeat=k):
  x=prefix+((-sum(prefix))%29,);s=sum(float(W[j,x[j-2],x[j-1],x[j]])+float(B[j,x[0],x[j]]) for j in range(m));best=max(best,s)
 for cap in [0,100000]:
  got=solver.solve(W,B,max_nodes=cap,max_seconds=30)
  assert got['maximum']<=best+1e-10 and got['upper_bound']>=best-1e-10
  if cap:assert abs(got['maximum']-best)<1e-10 and got['certified_within_1e_10']
  for a in got['alternatives']:
   x=a['offset'];assert sum(x)%29==0 and abs(a['score']-sum(float(W[j,x[j-2],x[j-1],x[j]])+float(B[j,x[0],x[j]]) for j in range(m)))<1e-10
  solves.append(dict(t=t,k=k,cap=cap,best=best,maximum=got['maximum'],upper=got['upper_bound'],termination=got['termination']))
try:model.factors([1,2,3],set(),2,{1},np.zeros((30,30,30)))
except ValueError:rejected=True
else:raise AssertionError('nonboundary reset accepted')
out=dict(passed=True,factor_checks=checks,max_error=maxerr,tests=tests,solver_checks=solves,nonboundary_reset_rejected=rejected,hashes={p:hashlib.sha256((D/p).read_bytes()).hexdigest() for p in ['model.py','solver.py']})
(Path(__file__).parent/'factor-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,factor_checks=checks,solver_checks=len(solves),max_error=maxerr)))
