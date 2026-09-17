import fixed_reset as r,random,numpy as np,itertools,json,pathlib
rng=random.Random(2026092302);rows=[]
for case in range(100):
 N=[2,3,29][case%3];k=[1,2,3,8,13][case%5];n=case%9;seed=[rng.randrange(N) for _ in range(k)];c=[0 if rng.random()<.5 else rng.randrange(N) for _ in range(n)];ends={i for i in range(n) if rng.random()<.3};resets={i for i in range(n) if rng.random()<.3};L=np.array([rng.uniform(-8,1) for _ in range((N+1)**3)]).reshape((N+1,)*3);hist=[rng.randrange(N) for _ in range(rng.randrange(k+1))];ctx=[rng.randrange(N+1) for _ in range(2)];best=-float('inf');paths=[]
 for mask in itertools.product([False,True],repeat=sum(x==0 for x in c)):
  h=hist.copy();a,b=ctx;score=0.;mi=0;plain=[];lit=[]
  for i,x in enumerate(c):
   if i in resets:h=[]
   literal=False
   if x==0:literal=mask[mi];mi+=1
   p=0 if literal else (x-(seed[len(h)] if len(h)<k else sum(h[-k:])))%N
   if literal:lit.append(i)
   else:h.append(p)
   plain.append(p);score+=float(L[a,b,p]);a,b=b,p
   if i in ends:score+=float(L[a,b,N]);a,b=b,N
  paths.append((score,plain,lit));best=max(best,score)
 out=r.Engine(seed,L).solve(c,ends,resets,initial_history=hist,initial_context=ctx,block=1+case%5);assert abs(best-out['maximum'])<1e-9
 for a in out['alternatives']:assert any(p==a['plain'] and l==a['literal_positions'] and abs(s-a['total'])<1e-9 for s,p,l in paths)
 rows.append(dict(case=case,N=N,k=k,n=n,paths=len(paths),maximum=best))
O=pathlib.Path('exploration/persistent-02/feedback/C10');O.mkdir(exist_ok=True);(O/'tiny-tests.json').write_text(json.dumps(rows,indent=2)+'\n');print('PASS',len(rows))
