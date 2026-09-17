import emitted_feedback as e,numpy as np,itertools,random,json,pathlib
rng=random.Random(2026092307);rows=[]
for ix in range(90):
 N=[2,3,29][ix%3];k=2+ix%2;n=7;cut=1+ix%5;seed=[rng.randrange(N) for _ in range(k)];c=[0 if rng.random()<.6 else rng.randrange(N) for _ in range(n)];ends={i for i in range(n) if rng.random()<.3};L=np.array([rng.uniform(-8,0) for _ in range((N+1)**3)]).reshape((N+1,)*3);hist=[];phase=0;a=b=N
 for i,x in enumerate(c[:cut]):
  if x==0 and rng.random()<.5:p=0
  else:key=seed[phase] if phase<k else sum(hist[-k:]);p=(x-key)%N;phase+=1
  hist.append(p);a,b=b,p
  if i in ends:a,b=b,N
 best=-float('inf');paths=[]
 for mask in itertools.product([False,True],repeat=sum(x==0 for x in c[cut:])):
  h=hist.copy();j=phase;aa,bb=a,b;mi=0;s=0.;plain=[];literal=[]
  for pos in range(cut,n):
   lit=False
   if c[pos]==0:lit=mask[mi];mi+=1
   if lit:p=0;literal.append(pos-cut)
   else:key=seed[j] if j<k else sum(h[-k:]);p=(c[pos]-key)%N;j+=1
   h.append(p);plain.append(p);s+=L[aa,bb,p];aa,bb=bb,p
   if pos in ends:s+=L[aa,bb,N];aa,bb=bb,N
  best=max(best,s);paths.append((plain,literal,s))
 out=e.Engine(k,L,seed=seed).solve(c[cut:],{i-cut for i in ends if i>=cut},initial_history=hist[-k:],initial_phase=min(phase,k),initial_context=(a,b),block=1+ix%5);assert abs(out['maximum']-best)<1e-9
 for alt in out['alternatives']:assert any(p==alt['plain'] and l==alt['literal_positions'] and abs(s-alt['total'])<1e-9 for p,l,s in paths)
 rows.append(dict(index=ix,N=N,k=k,cut=cut,phase=phase,maximum=float(best),paths=len(paths)))
p=pathlib.Path('exploration/persistent-02/feedback/C11/continuation-check.json');p.write_text(json.dumps(rows,indent=2)+'\n');print('PASS',len(rows))
