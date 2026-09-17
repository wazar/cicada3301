import emitted_feedback as e,numpy as np,itertools,random,json,pathlib
rng=random.Random(2026092306);results=[]
for ix in range(64):
 N=2 if ix<24 else 3 if ix<48 else 29;k=2+ix%2;n=ix%7 if N<29 else 3+(ix%2);c=[0 if rng.random()<.5 else rng.randrange(N) for _ in range(n)];ends={i for i in range(n) if rng.random()<.25};L=np.array([rng.randrange(-9,2) for _ in range((N+1)**3)],dtype=float).reshape((N+1,)*3);best=-float('inf');paths=0
 for seed in itertools.product(range(N),repeat=k):
  for mask in itertools.product([False,True],repeat=sum(x==0 for x in c)):
   h=[];phase=0;a=b=N;score=0.;mi=0
   for i,x in enumerate(c):
    lit=False
    if x==0:lit=mask[mi];mi+=1
    if lit:p=0
    else:key=seed[phase] if phase<k else sum(h[-k:]);p=(x-key)%N;phase+=1
    h.append(p);score+=L[a,b,p];a,b=b,p
    if i in ends:score+=L[a,b,N];a,b=b,N
   best=max(best,score);paths+=1
 out=e.Engine(k,L).solve(c,ends,block=1+ix%5);assert out['maximum']==best
 for alt in out['alternatives']:
  seed=[0 if v is None else v for v in alt['seed']];assert e.encode(alt['plain'],seed,alt['literal_positions'],N)==c
 results.append(dict(index=ix,N=N,k=k,length=n,full_seed_mask_paths=paths,maximum=float(best)))
# Old/new construction scalar witness: k2 seed[1,2], P[3,4,0,5], literal at2.
# New final key last2 emitted=4+0=4 => C9; old normal-only key3+4=7=>C12.
assert e.encode([3,4,0,5],[1,2],[2])==[4,6,0,9]
O=pathlib.Path('exploration/persistent-02/feedback/C11');O.mkdir(exist_ok=True);(O/'tiny-tests.json').write_text(json.dumps(dict(cases=results,witness=dict(seed=[1,2],plain=[3,4,0,5],literal=[2],new_cipher=[4,6,0,9],old_cipher=[4,6,0,12])),indent=2)+'\n');print('PASS',len(results),sum(r['full_seed_mask_paths'] for r in results))
