"""Independent variable-feature/composite review; no actual C07 score."""
import pathlib,sys,json,hashlib,random,math,numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];F=R/'exploration/persistent-02/feedback';sys.path.insert(0,str(F));import page_invariant as M
def dump(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
def decode(c,seed):
 p=[];k=len(seed)
 for i,v in enumerate(c):p.append((v-(seed[i] if i<k else sum(p[i-k:i])))%29)
 return p
def null(c,seed):
 rr=random.Random(seed);out=[c[0]]
 for i in range(1,len(c)):out.append(out[-1] if c[i]==c[i-1] else rr.choice([v for v in range(29) if v!=out[-1]]))
 return out
def independent_matrix(c,seedbase):
 ks=list(range(2,len(c)//20));num=np.zeros((200,len(ks)),dtype=np.int64);den=[]
 for j in range(200):
  cc=c if j==0 else null(c,seedbase+j-1)
  for col,k in enumerate(ks):
   q=decode(cc,[0]*k);counts=[np.bincount(q[t::k+1],minlength=29) for t in range(k+1)];num[j,col]=sum(int(v)*(int(v)-1) for row in counts for v in row)
   if j==0:den.append(sum(len(q[t::k+1])*(len(q[t::k+1])-1) for t in range(k+1)))
 frac=num/np.array(den);z=np.empty_like(frac)
 for col in range(len(ks)):
  v=frac[:,col].tolist();mu=math.fsum(v)/200;sd=math.sqrt(math.fsum((x-mu)**2 for x in v)/200);z[:,col]=[(x-mu)/sd for x in v]
 return ks,num,np.array(den),z
def main():
 d=json.loads((F/'C07/inputs.json').read_text());f=R/d['source'];assert hashlib.sha256(f.read_bytes()).hexdigest()==d['source_sha256'];src=json.loads(f.read_text());r=random.Random(2026092200);ix=0
 for author in ['guest','mill','shelley','blake']:
  full=next(x['truth'] for x in src['cases'] if x['id']==f'fresh-{author}-2')
  for n in [66,121,249]:
   for k in sorted(set([2,n//20-1])):
    x=d['controls'][ix];ix+=1;seed=[r.randrange(29) for _ in range(k)];assert x['plain']==full[:n] and x['seed']==seed and x['k']==k and decode(x['cipher'],seed)==x['plain']
 for n in [66,121,249]:
  for k in sorted(set([2,n//20-1])):
   p=[r.randrange(29) for _ in range(n)];seed=[r.randrange(29) for _ in range(k)];x=d['controls'][ix];ix+=1;assert x['plain']==p and x['seed']==seed and decode(x['cipher'],seed)==p
 assert ix==25;assert len(d['pages'])==45 and len({x['page'] for x in d['pages']})==45;assert sum(len(x['ks']) for x in d['pages'])==411
 cfg=json.loads((F.parent/'config.json').read_text());assert not set(cfg['reserved_originals'])&{x['page'] for x in d['pages']}
 original={x['page']:x for x in json.loads((R/'exploration/persistent-01/worker-f/F06-maps.json').read_text())}
 for page in d['pages']:
  assert page['cipher']==original[page['page']]['indices'];assert page['ks']==list(range(2,len(page['cipher'])//20));assert all(len(page['cipher'])//(k+1)>=20 for k in page['ks'])
 # Three varied lengths plus exact cutoff80 demonstrate feature count changes.
 checks=[];panels=[];r=random.Random(9170407)
 for n,base in [(66,817100),(80,817200),(121,817300),(249,817400)]:
  c=[r.randrange(29) for _ in range(n)];got=M.matrix(c,base);want=independent_matrix(c,base);assert got[0]==want[0] and np.array_equal(got[1],want[1]) and np.array_equal(got[2],want[2]);assert np.max(np.abs(got[3]-want[3]))<1e-12
  checks.append(dict(n=n,seedbase=base,cipher=c,ks=got[0],max_z_error=float(np.max(np.abs(got[3]-want[3])))));panels.append(want)
 # Exercise producer summarizer with redirected outputs on own numerical fixtures.
 M.O=O;features=[dict(unit=i,k=k) for i,p in enumerate(panels) for k in p[0]];z=np.concatenate([p[3] for p in panels],axis=1);mx=z.max(axis=1);rank=(1+sum(x>=mx[0] for x in mx[1:]))/200
 got=M.summarize('c07-variable-fixture',features,[p[1] for p in panels],[p[2] for p in panels],[p[3] for p in panels],dict(scope='reviewer synthetic fixture'))
 assert got['rank']==rank and got['selected']==features[int(z[0].argmax())]
 order=list(range(199,-1,-1));flip=M.summarize('c07-permuted-fixture',features,[p[1][order] for p in panels],[p[2] for p in panels],[p[3][order] for p in panels],{})
 assert flip['rank']==sum(x>=mx[-1] for x in mx)/200
 zeros=[np.zeros((200,1))];ties=M.summarize('c07-tie-fixture',[dict(k=2)],[np.zeros((200,1),dtype=np.int64)],[np.array([100])],zeros,{})
 assert ties['rank']==1.
 # Slice identity with fresh source seed/start, no physical reset assumed.
 for k in [2,5,11]:
  p=[r.randrange(29) for _ in range(360)];seed=[r.randrange(29) for _ in range(k)];c=[(p[i]+(seed[i] if i<k else sum(p[i-k:i])))%29 for i in range(len(p))];start=43;cc=c[start:start+121];pp=p[start:start+121];effective=[(a-b)%29 for a,b in zip(cc[:k],pp[:k])];assert decode(cc,effective)==pp
 # All prereg seed blocks are disjoint, including baseline versus comparator slots.
 seeds=[]
 for t in range(25):
  seeds.extend(range(2026300000+1000*t,2026300000+1000*t+199))
  for page in d['pages']:
   b=2026600000+100000*t+1000*page['page'];seeds.extend(range(b,b+199))
   if page['page']!=49:seeds.append(b+900)
 for page in d['pages']:b=2026400000+1000*page['page'];seeds.extend(range(b,b+199))
 assert len(seeds)==len(set(seeds))
 dump('c07-checks.json',dict(passed=True,frozen_plants=25,pages=45,actual_feature_count=411,matrix_checks=checks,variable_fixture_rank=rank,ties_rank=1.,seed_assignments=len(seeds),all_seed_assignments_unique=True,slice_identity_cases=3,scope='Algorithm/calibration/fixture review; no actual page statistic computed. Synthetic-book capability remains subject to observed short-control power.'))
 print('C07 tiny/composite checks PASS')
if __name__=='__main__':main()
