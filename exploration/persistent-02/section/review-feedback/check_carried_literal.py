from pathlib import Path
import sys,random,itertools,json,numpy as np
R=Path(__file__).resolve().parents[4];sys.path.insert(0,str(R/'exploration/persistent-02/feedback'));from reset_literal import Engine
rng=random.Random(9173206);rows=[];paths=0
for t in range(100):
 N=[2,3,29][t%3];k=1+t%3;seed=[rng.randrange(N) for _ in range(k)];history=[rng.randrange(N) for _ in range(rng.randrange(k+1))];ctx=(rng.randrange(N+1),rng.randrange(N+1));n=rng.randrange(7);c=[0 if rng.random()<.6 else rng.randrange(N) for _ in range(n)];ends={i for i in range(n) if rng.random()<.4};resets={i for i in range(n) if rng.random()<.3};L=np.array([rng.uniform(-3,1) for _ in range((N+1)**3)]).reshape((N+1,)*3);known={}
 F=[i for i,v in enumerate(c) if v==0]
 for bits in itertools.product([False,True],repeat=len(F)):
  lit=tuple(i for i,b in zip(F,bits) if b);h=history.copy();a,b=ctx;score=0.;plain=[]
  for i,v in enumerate(c):
   if i in resets:h=[]
   if i in lit:p=0
   else:p=(v-(seed[len(h)] if len(h)<k else sum(h[-k:])))%N;h.append(p)
   plain.append(p);score+=L[a,b,p];a,b=b,p
   if i in ends:score+=L[a,b,N];a,b=b,N
  known[lit]=(plain,score);paths+=1
 got=Engine([seed],L).solve(c,ends,resets,block=2,initial_history=history,initial_context=ctx)
 assert abs(got['maximum']-max(v for p,v in known.values()))<1e-10
 for a in got['alternatives']:
  p,v=known[tuple(a['literal_positions'])];assert p==a['plain'] and abs(v-a['total'])<1e-10
 rows.append(dict(t=t,N=N,k=k,history=history,context=ctx,cipher=c,resets=sorted(resets),ends=sorted(ends)))
out=dict(passed=True,cases=rows,paths=paths);(Path(__file__).parent/'literal-carried-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows),paths=paths)))
