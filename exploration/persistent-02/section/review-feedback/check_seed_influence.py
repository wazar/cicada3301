from pathlib import Path
import importlib.util,itertools,random,json
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/coordinator/emitted-seed-influence';sp=importlib.util.spec_from_file_location('influence',D/'check.py');M=importlib.util.module_from_spec(sp);sp.loader.exec_module(M)
def det(a,q):
 n=len(a);value=0
 for p in itertools.permutations(range(n)):
  inv=sum(p[i]>p[j] for i in range(n) for j in range(i+1,n));z=(-1)**inv
  for i,j in enumerate(p):z*=a[i][j]
  value+=z
 return value%q
def rank(a,q,k):
 for r in range(min(len(a),k),0,-1):
  for rr in itertools.combinations(range(len(a)),r):
   for cc in itertools.combinations(range(k),r):
    if det([[a[i][j] for j in cc] for i in rr],q):return r
 return 0
def decode(c,seed,lit,q,emitted):
 p=[];h=[];normal=0
 for i,v in enumerate(c):
  if i in lit:z=0
  else:z=(v-(seed[normal] if normal<len(seed) else sum(h[-len(seed):])))%q;normal+=1
  p.append(z)
  if emitted or i not in lit:h.append(z)
 return p
rng=random.Random(9171010);records=[];evaluations=0
for t in range(120):
 q=[2,3,5,29][t%4];k=1+(t//4)%4;n=rng.randrange(18);c=[0 if rng.random()<.5 else rng.randrange(q) for _ in range(n)];lit={i for i,v in enumerate(c) if v==0 and rng.random()<.7}
 for emitted in [False,True]:
  got=M.trace(c,k,lit,q,emitted);zero=decode(c,[0]*k,lit,q,emitted);basis=[]
  for j in range(k):seed=[0]*k;seed[j]=1;basis.append(decode(c,seed,lit,q,emitted))
  coeff=[[ (basis[j][i]-zero[i])%q for j in range(k)] for i in range(n)];assert got['forms']==[[zero[i]]+coeff[i] for i in range(n)]
  hist=[];phase=0;prev=None
  for i,row in enumerate(coeff):
   if i not in lit:phase=min(k,phase+1)
   if emitted or i not in lit:hist=(hist+[row])[-k:]
   rk=rank(hist,q,k);assert got['ranks'][i]==rk and got['phases'][i]==phase
   if phase==k:
    if prev is not None:assert rk<=prev
    if not emitted:assert rk==k
    prev=rk
  seeds=list(itertools.product(range(q),repeat=k)) if q**k<=125 else [tuple(rng.randrange(q) for _ in range(k)) for _ in range(12)]
  zpos=got['first_mature_zero'];suffix=None
  for seed in seeds:
   p=decode(c,seed,lit,q,emitted);expected=[(zero[i]+sum(v*s for v,s in zip(coeff[i],seed)))%q for i in range(n)];assert p==expected;evaluations+=1
   if zpos is not None:
    if suffix is None:suffix=p[zpos+1:]
    assert p[zpos+1:]==suffix
  records.append(dict(t=t,q=q,k=k,cipher=c,literal=sorted(lit),emitted=emitted,first_mature_zero=zpos,final_rank=got['ranks'][-1] if n else 0))
out=dict(passed=True,cases=len(records),seed_evaluations=evaluations,fixtures=records,independent_rank='all minors via permutation determinants',real_leaders_not_read=True);(Path(__file__).parent/'seed-influence-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='fixtures'}))
