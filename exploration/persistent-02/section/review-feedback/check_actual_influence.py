from pathlib import Path
import json,hashlib,itertools
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/coordinator/emitted-seed-influence';x=json.loads((D/'actual.json').read_text());sources={}
for p,h in x['source_pins'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h;sources[p]=json.loads((R/p).read_text())
def decode(c,seed,lit):
 out=[];normal=0;k=len(seed)
 for i,v in enumerate(c):
  if i in lit:z=0
  else:z=(v-(seed[normal] if normal<k else sum(out[-k:])))%29;normal+=1
  out.append(z)
 return out
def det(a):
 total=0
 for p in itertools.permutations(range(len(a))):
  term=(-1)**sum(p[i]>p[j] for i in range(len(p)) for j in range(i+1,len(p)))
  for i,j in enumerate(p):term*=a[i][j]
  total+=term
 return total%29
def rank(a,k):
 for r in range(min(len(a),k),0,-1):
  for rr in itertools.combinations(range(len(a)),r):
   for cc in itertools.combinations(range(k),r):
    if det([[a[i][j] for j in cc] for i in rr]):return r
 return 0
collapsed=0;leaders=[]
for record in x['records']:
 d=sources[f'exploration/persistent-02/feedback/C11-actual/{record["model"]}-panel00.json'];r=next(r for r in d['rows'] if r['k']==record['k']);alts=r[record['kind']] if record['kind']=='continuation' else r[record['kind']]['alternatives'];a=alts[record['alternative']];k=record['k'];c=d['cipher'][:len(a['plain'])];lit=set(a['literal_positions']);assert decode(c,a['seed'],lit)==a['plain'];zero=decode(c,[0]*k,lit);basis=[]
 for j in range(k):seed=[0]*k;seed[j]=1;basis.append(decode(c,seed,lit))
 coeff=[[(basis[j][i]-zero[i])%29 for j in range(k)] for i in range(len(c))];phase=0;ranks=[];phases=[]
 for i in range(len(c)):
  if i not in lit:phase=min(k,phase+1)
  ranks.append(rank(coeff[max(0,i-k+1):i+1],k));phases.append(phase)
 assert ranks==record['rank_path'] and phases==record['seed_phase_path'];first=next((i for i,(rr,ph) in enumerate(zip(ranks,phases)) if rr==0 and ph==k),None);assert first==record['first_mature_zero'] and ranks[-1]==record['final_rank'];normal=[i for i in range(len(c)) if i not in lit][:k];assert len(normal)==k;assert det([coeff[i] for i in normal])!=0 and record['fixed_mask_full_plaintext_seed_rank']==k
 collapsed+=first is not None
 if record['alternative']==0:leaders.append({key:record[key] for key in ['model','k','kind','first_mature_zero','final_rank','fixed_mask_full_plaintext_seed_rank']})
out=dict(passed=True,records=len(x['records']),mature_collapsed=collapsed,full_plaintext_rank_k=len(x['records']),leaders=leaders);(Path(__file__).parent/'actual-influence-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='leaders'}))
