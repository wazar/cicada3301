from pathlib import Path
import sys,json,random,math,hashlib,collections,importlib.util
import numpy as np
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/coordinator/shared-period';spec=importlib.util.spec_from_file_location('shared_test',D/'test.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
rng=random.Random(9172705);checks=0
for t in range(20):
 fs=[dict(page=p,k=k) for p in range(7) for k in range(2,2+p%4)];z=np.array([[rng.randrange(-3,5) for f in fs] for r in range(23)],dtype=float)
 if t==0:z[:]=1
 d=M.aggregate(fs,z);ks=sorted(k for k,n in collections.Counter(f['k'] for f in fs).items() if n>=2);raw=[[sum(float(z[r,j]) for j,f in enumerate(fs) if f['k']==k)/math.sqrt(sum(f['k']==k for f in fs)) for k in ks] for r in range(len(z))];scores=[]
 for j in range(len(ks)):
  col=[row[j] for row in raw];mu=sum(col)/len(col);sd=math.sqrt(sum((v-mu)**2 for v in col)/len(col));scores.append([0. if max(col)==min(col) else (v-mu)/sd for v in col])
 mx=[max(row) for row in zip(*scores)];assert np.allclose(mx,d['maximum'],atol=1e-13);assert d['rank']==sum(v>=mx[0] for v in mx)/len(mx)
 perm=list(range(len(z)));rng.shuffle(perm);e=M.aggregate(fs,z[perm]);assert np.allclose(e['maximum'],np.array(mx)[perm],atol=1e-13);checks+=1
x=json.loads((D/'inputs.json').read_text());inv=json.loads((R/x['inventory']).read_text());fresh=json.loads((R/x['source']).read_text());assert hashlib.sha256((R/x['inventory']).read_bytes()).hexdigest()==x['inventory_sha256'];assert hashlib.sha256((R/x['source']).read_bytes()).hexdigest()==x['source_sha256'];rng=random.Random(2026092300);seeds=[];plants=0

def null(c,seed):
 rr=random.Random(seed);out=[c[0]]
 for i in range(1,len(c)):out.append(out[-1] if c[i]==c[i-1] else rr.choice([v for v in range(29) if v!=out[-1]]))
 return out
for ix,case in enumerate(x['cases']):
 assert case['author']==['guest','mill','shelley','blake','uniform'][ix//3] and case['k']==[2,5,8][ix%3]
 for u,p in zip(case['units'],inv['pages']):
  k=case['k'];n=len(p['cipher']);base=2026700000+100000*ix+1000*p['page'];assert u['seedbase']==base and u['ks']==p['ks'];seeds.extend(range(base,base+199));seeds.append(base+900)
  if k in p['ks']:
   if case['author']=='uniform':plain=[rng.randrange(29) for _ in range(n)];start=None
   else:
    src=next(a['truth'] for a in fresh['cases'] if a['id']==f'fresh-{case["author"]}-2');start=rng.randrange(len(src)-n+1);plain=src[start:start+n]
   seed=[rng.randrange(29) for _ in range(k)];cipher=[(p+(seed[i] if i<k else sum(plain[i-k:i])))%29 for i,p in enumerate(plain)];assert u['plain']==plain and u['seed']==seed and u['source_start']==start and u['cipher']==cipher;plants+=1
  else:assert u['cipher']==null(p['cipher'],base+900)
assert len(seeds)==len(set(seeds))
# Recompute only three representative feature columns of control00, all 200 panels.
meta=json.loads((D/'control00.json').read_text());a=np.load(D/'control00.npz');fs=meta['features'];cols=[0,len(fs)//2,len(fs)-1]
for j in cols:
 f=fs[j];u=next(u for u in x['cases'][0]['units'] if u['page']==f['page']);k=f['k'];nums=[]
 for panel in range(200):
  c=u['cipher'] if panel==0 else null(u['cipher'],u['seedbase']+panel-1);p=[]
  for i,v in enumerate(c):p.append((v-(sum(p[-k:]) if i>=k else 0))%29)
  groups=[p[r::k+1] for r in range(k+1)];den=sum(len(g)*(len(g)-1) for g in groups);num=sum(sum(v*(v-1) for v in collections.Counter(g).values()) for g in groups);assert a['numerators'][panel,j]==num and a['denominators'][j]==den;nums.append(num)
 nums=np.array(nums,dtype=float)/den;assert np.allclose((nums-nums.mean())/nums.std(),a['feature_z'][:,j])
d=M.aggregate(fs,a['feature_z']);assert np.allclose(d['standardized'],a['aggregate_z']) and d['rank']==meta['rank']
out=dict(passed=True,scalar_permutation_cases=checks,books=15,units=675,plants=plants,unique_seeds=len(seeds),representative_columns=cols,representative_cells=600,source_sha256=hashlib.sha256((D/'test.py').read_bytes()).hexdigest(),actual_not_read=True)
(Path(__file__).parent/'shared-period-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
