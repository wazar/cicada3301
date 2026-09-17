from pathlib import Path
import sys,itertools,random,json,numpy as np
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'exploration/persistent-02/feedback'));from emitted_feedback import Engine,Refused
rng=random.Random(9170609);records=[];paths=0
for t in range(170):
 known=t>=100;N=29 if known and t%3==0 else [2,3,5][t%3];k=1+t%3;n=rng.randrange(8);c=[0 if rng.random()<.65 else rng.randrange(N) for _ in range(n)];ends={i for i in range(n) if rng.random()<.35};L=np.array([rng.uniform(-3,1) if t%2 else rng.randrange(-2,2) for _ in range((N+1)**3)],dtype=float).reshape((N+1,)*3);hist=[rng.randrange(N) for _ in range(rng.randrange(k+1))] if known else [];phase=rng.randrange(min(k,len(hist))+1) if known else 0;ctx=(rng.randrange(N+1),rng.randrange(N+1)) if known else (N,N);seed=[rng.randrange(N) for _ in range(k)] if known else None;seeds=[seed] if known else itertools.product(range(N),repeat=k);F=[i for i,v in enumerate(c) if v==0];rows={};maximum=-float('inf')
 for ss in seeds:
  ss=tuple(ss)
  for bits in itertools.product([False,True],repeat=len(F)):
   lit=tuple(i for i,b in zip(F,bits) if b);h=hist.copy();ph=phase;a,b=ctx;p=[];total=0.
   for i,v in enumerate(c):
    if i in lit:z=0
    else:z=(v-(ss[ph] if ph<k else sum(h[-k:])))%N;ph=min(ph+1,k)
    h.append(z);p.append(z);total+=L[a,b,z];a,b=b,z
    if i in ends:total+=L[a,b,N];a,b=b,N
   rows[(ss,lit)]=(p,total);maximum=max(maximum,total);paths+=1
 a=Engine(k,L,seed=seed).solve(c,ends,block=1,initial_history=hist,initial_phase=phase,initial_context=ctx);b=Engine(k,L,seed=seed).solve(c,ends,block=4,initial_history=hist,initial_phase=phase,initial_context=ctx);assert a['alternatives']==b['alternatives'];assert abs(a['maximum']-maximum)<1e-10
 for alt in a['alternatives']:
  ss=tuple(0 if v is None else v for v in alt['seed']);p,total=rows[(ss,tuple(alt['literal_positions']))];assert p==alt['plain'] and abs(total-alt['total'])<1e-10
 records.append(dict(t=t,known_seed=known,N=N,k=k,cipher=c,history=hist,phase=phase,context=ctx,ends=sorted(ends)))
for why,e in [('state',Engine(2,np.zeros((4,4,4)),max_states=1)),('time',Engine(2,np.zeros((4,4,4)),seconds=-1))]:
 try:e.solve([0],[])
 except Refused:pass
 else:raise AssertionError(why)
out=dict(passed=True,cases=records,exhaustive_paths=paths,blocks=[1,4],resource_refusals=True);(Path(__file__).parent/'emitted-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(records),paths=paths)))
