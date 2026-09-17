"""Independent C04 algebra, plants, matched panels and family-statistic review."""
import pathlib,sys,importlib.util,json,random,hashlib,math,collections
import numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2]
sys.path.insert(0,str(R/'exploration/persistent-02/feedback'))
import invariant as I
def dump(name,x):(O/name).write_text(json.dumps(x,indent=2)+'\n')
def baseline(c,k):
 p=list(c[:k])
 if len(c)>k:p.append((c[k]-sum(p))%29)
 for i in range(k+1,len(c)):p.append((p[i-k-1]+c[i]-c[i-1])%29)
 return p
def direct(c,seed):
 p=[];k=len(seed)
 for i,x in enumerate(c):p.append((x-(seed[i] if i<k else sum(p[i-k:i])))%29)
 return p
def null(c,seed):
 r=random.Random(seed);out=[c[0]]
 for i in range(1,len(c)):
  out.append(out[-1] if c[i]==c[i-1] else r.choice([v for v in range(29) if v!=out[-1]]))
 return out
def main():
 r=random.Random(260917902);records=[]
 for k in [2,3,5,8,17,34]:
  for n in [1,k,k+1,k+2,2*k+7,716]:
   p=[r.randrange(29) for _ in range(n)];seed=[r.randrange(29) for _ in range(k)];c=[(p[i]+(seed[i] if i<k else sum(p[i-k:i])))%29 for i in range(n)]
   q=baseline(c,k);assert q==I.simple_baseline(c,k)==direct(c,[0]*k);assert direct(c,seed)==p
   aa,bb,hh=I.collisions(p,k+1);a,b,h=I.collisions(q,k+1);assert (a,b)==(aa,bb)
   for phase in range(k+1):
    offsets={(q[i]-p[i])%29 for i in range(phase,n,k+1)};assert len(offsets)<=1
   if n<100:
    assert a==sum(q[i]==q[j] for i in range(n) for j in range(n) if i!=j and (i-j)%(k+1)==0)
    assert b==sum(1 for i in range(n) for j in range(n) if i!=j and (i-j)%(k+1)==0)
   records.append(dict(k=k,n=n,seed=seed,cipher=c,plain=p,numerator=a,denominator=b))
 frozen=json.loads((I.O/'inputs.json').read_text());src=json.loads((R/frozen['source']).read_text());assert hashlib.sha256((R/frozen['source']).read_bytes()).hexdigest()==frozen['source_sha256']
 r=random.Random(2026092000);ix=0
 for source in ['guest','mill','shelley','blake']:
  p=next(x['truth'] for x in src['cases'] if x['id']==f'fresh-{source}-2')
  for k in [3,8,17,34]:
   x=frozen['controls'][ix];ix+=1;seed=[r.randrange(29) for _ in range(k)];assert x['plain']==p and x['seed']==seed and x['k']==k;assert direct(x['cipher'],seed)==p
 for k in [3,8,17,34]:
  p=[r.randrange(29) for _ in range(716)];seed=[r.randrange(29) for _ in range(k)];x=frozen['controls'][ix];ix+=1;assert x['plain']==p and x['seed']==seed and direct(x['cipher'],seed)==p
 matrices=[]
 for ix in [0,15,16]:
  x=frozen['controls'][ix];name=f'control{ix:02}';meta=json.loads((I.O/(name+'.json')).read_text());a=np.load(I.O/(name+'.npz'));nums=np.zeros((200,33),dtype=np.int64);dens=[]
  for j in range(200):
   c=x['cipher'] if j==0 else null(x['cipher'],2026100000+1000*ix+j-1);assert c==a['cipher'][j].tolist()
   for col,k in enumerate(range(2,35)):
    q=baseline(c,k);h=np.array([[q[t::k+1].count(v) for v in range(29)] for t in range(k+1)],dtype=np.int64)
    num=int(sum(int(v)*(int(v)-1) for v in h.flat));den=sum(len(q[t::k+1])*(len(q[t::k+1])-1) for t in range(k+1));nums[j,col]=num
    assert np.array_equal(h,a['histograms'][j,col,:k+1]);assert not a['histograms'][j,col,k+1:].any();assert den==a['denominators'][col]
   if j==0:dens=a['denominators'].tolist()
  assert np.array_equal(nums,a['numerators']);fractions=nums/np.array(dens);z=np.zeros_like(fractions)
  for col in range(33):
   v=fractions[:,col].tolist();mu=math.fsum(v)/200;sd=math.sqrt(math.fsum((s-mu)**2 for s in v)/200);z[:,col]=[(s-mu)/sd for s in v]
  maxima=z.max(axis=1);rank=(1+sum(s>=maxima[0] for s in maxima[1:]))/200
  assert np.max(np.abs(z-a['z']))<1e-12 and rank==meta['rank'];assert int(z[0].argmax())+2==meta['selected_k']
  # Label relabelling preserves maxima: standardization uses all200 panels.
  rev=fractions[::-1];rz=(rev-rev.mean(axis=0))/rev.std(axis=0);assert np.max(np.abs(rz.max(axis=1)-maxima[::-1]))<1e-12
  matrices.append(dict(control=ix,rank=rank,selected_k=meta['selected_k'],cipher_panels=200,periods=33,source_meta_sha256=hashlib.sha256((I.O/(name+'.json')).read_bytes()).hexdigest()))
  print('C04 matrix passed',name,rank,flush=True)
 dump('invariant-checks.json',dict(passed=True,algebra_cases=records,frozen_plants_reconstructed=20,matrices=matrices,scope='No actual results scored/read; only frozen language/uniform controls. Conditional composite family rank, no global discovery probability.'))
 print('C04 CLEAR: invariant, plants, and3complete control-panel matrices passed')
if __name__=='__main__':main()
