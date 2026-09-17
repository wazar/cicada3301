from pathlib import Path
import sys,random,itertools,json,numpy as np
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'exploration/persistent-02/feedback'));from fixed_reset import Engine,Refused
rng=random.Random(9174107);records=[];paths=0
for t in range(140):
 N=[2,3,29][t%3];k=[1,2,8,13][t%4];seed=[rng.randrange(N) for _ in range(k)];h0=[rng.randrange(N) for _ in range(rng.randrange(k+1))];ctx=(rng.randrange(N+1),rng.randrange(N+1));n=rng.randrange(11);c=[0 if rng.random()<.7 else rng.randrange(N) for _ in range(n)];ends={i for i in range(n) if rng.random()<.4};resets={i for i in range(n) if rng.random()<.3};L=np.array([rng.uniform(-3,1) if t%2 else rng.randrange(-3,2) for _ in range((N+1)**3)],dtype=float).reshape((N+1,)*3);rows={};F=[i for i,v in enumerate(c) if v==0]
 for bits in itertools.product([False,True],repeat=len(F)):
  lit=tuple(i for i,v in zip(F,bits) if v);h=h0.copy();a,b=ctx;score=0.;p=[]
  for i,v in enumerate(c):
   if i in resets:h=[]
   if i in lit:z=0
   else:z=(v-(seed[len(h)] if len(h)<k else sum(h[-k:])))%N;h.append(z)
   p.append(z);score+=L[a,b,z];a,b=b,z
   if i in ends:score+=L[a,b,N];a,b=b,N
  rows[lit]=(p,score);paths+=1
 a=Engine(seed,L).solve(c,ends,resets,block=1,initial_history=h0,initial_context=ctx);b=Engine(seed,L).solve(c,ends,resets,block=4,initial_history=h0,initial_context=ctx);assert a['alternatives']==b['alternatives'];assert abs(a['maximum']-max(v for p,v in rows.values()))<1e-10
 for alt in a['alternatives']:
  p,v=rows[tuple(alt['literal_positions'])];assert p==alt['plain'] and abs(v-alt['total'])<1e-10
 records.append(dict(t=t,N=N,k=k,n=n,cipher=c,history=h0,context=ctx,ends=sorted(ends),resets=sorted(resets)))
for reason,engine in [('state',Engine([1,2],np.zeros((4,4,4)),max_states=1)),('time',Engine([1,2],np.zeros((4,4,4)),seconds=-1))]:
 try:engine.solve([0,0],[],[])
 except Refused:pass
 else:raise AssertionError(reason+' refusal missing')
out=dict(passed=True,cases=records,exhaustive_paths=paths,refusals=['state','time'],blocks=[1,4]);(Path(__file__).parent/'fixed-reset-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(records),paths=paths)))
