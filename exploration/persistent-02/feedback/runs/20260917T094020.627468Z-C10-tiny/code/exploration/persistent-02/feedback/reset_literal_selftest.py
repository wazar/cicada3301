"""Independent direct seed x Fmask enumeration with shared-seed resets."""
import itertools,random,json,pathlib,numpy as np
from reset_literal import Engine,encode
O=pathlib.Path(__file__).resolve().parent/'C08';O.mkdir(exist_ok=True)
def enumerate_direct(c,k,L,ends,resets):
 N=len(L)-1;rows=[];F=[i for i,v in enumerate(c) if v==0]
 for seed in itertools.product(range(N),repeat=k):
  for bits in itertools.product([0,1],repeat=len(F)):
   lit={i for i,v in zip(F,bits) if v};history=[];out=[];a=b=N;score=0.
   for i,v in enumerate(c):
    if i in resets:history=[]
    if i in lit:p=0
    else:
     key=seed[len(history)] if len(history)<k else sum(history[-k:]);p=(v-key)%N;history.append(p)
    out.append(p);score+=L[a,b,p];a,b=b,p
    if i in ends:score+=L[a,b,N];a,b=b,N
   rows.append(dict(seed=list(seed),plain=out,literal_positions=sorted(lit),total=float(score)))
 return rows
if __name__=='__main__':
 rng=random.Random(2026092301);records=[]
 for rep in range(40):
  N=[2,3,5,29][rep%4];k=[1,2,3][rep%3];n=0 if rep==0 else rng.randrange(1,7)
  if N==29 and k==3:n=min(n,4)
  c=[rng.randrange(N) if rng.random()<.6 else 0 for _ in range(n)];ends={i for i in range(n) if rng.random()<.4};resets={i for i in range(n) if rng.random()<.4};L=np.array([rng.randrange(-4,3) if rep%3 else 0 for _ in range((N+1)**3)],dtype=float).reshape((N+1,)*3);rows=enumerate_direct(c,k,L,ends,resets);maximum=max(r['total'] for r in rows);seeds=np.array(list(itertools.product(range(N),repeat=k)),dtype=np.int64);chunk=min(29,len(seeds));results=[]
  for lo in range(0,len(seeds),chunk):
   got=Engine(seeds[lo:lo+chunk],L).solve(c,ends,resets,block=2);results.append(got)
   for alt in got['alternatives']:
    assert encode(alt['plain'],alt['seed'],alt['literal_positions'],resets,N)==c
    same=next(r for r in rows if r['seed']==alt['seed'] and r['literal_positions']==alt['literal_positions']);assert same['plain']==alt['plain'] and same['total']==alt['total']
  assert max(r['maximum'] for r in results)==maximum;records.append(dict(rep=rep,N=N,k=k,cipher=c,ends=sorted(ends),resets=sorted(resets),paths=len(rows),maximum=maximum,partitions=len(results)));print(rep,N,k,n,len(rows),len(results),flush=True)
 # Explicit immutable-seed witness: same old history/context, different next P.
 for seed,mask,want in [([0,1],{0},1),([1,0],set(),0)]:
  rows=enumerate_direct([0,0,0,1],2,np.zeros((3,3,3)),{2},{3});r=next(r for r in rows if r['seed']==seed and set(r['literal_positions'])==mask);assert r['plain'][-1]==want
 (O/'tiny-tests.json').write_text(json.dumps(dict(passed=True,cases=records,seed_witness_passed=True),separators=(',',':'))+'\n');print('PASS',len(records))
