"""Fresh algorithm review; own exhaustive enumeration, no author selftest reuse."""
import pathlib,sys,importlib.util,random,itertools,json,hashlib,time
import numpy as np
O=pathlib.Path(__file__).resolve().parent; R=O.parents[2]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,R/path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
exact=load('review_exact','exploration/persistent-02/decoder/exact.py')
st=load('review_structured','exploration/persistent-02/feedback/structured.py')
rng=random.Random(9170835); nr=np.random.default_rng(9170835)
def dump(name,x): (O/name).write_text(json.dumps(x,indent=2)+'\n')
def decoder():
 records=[]
 for z in range(900):
  n=rng.randrange(13);c=[rng.choice([0,0,0,1,7,28]) for _ in range(n)];key=[rng.randrange(29) for _ in range(rng.randrange(1,7))]
  sign=rng.choice([-1,1]);periodic=rng.choice([True,False]);start=rng.randrange(len(key)+1);ends={i for i in range(n) if rng.random()<.3};retain=rng.choice([1,2,7,16,35]);ctx=tuple(rng.randrange(30) for _ in range(2))
  weights=nr.integers(-8,9,size=(30,30,30)).astype(float)
  if z%3==0:weights/=7.
  if z%5==0:weights[:]=0.
  def extend(s,r,end):
   w=weights[s+(r,)];s=(s[1],r)
   if end:w+=weights[s+(29,)];s=(s[1],29)
   return s,w
  fs=[i for i,v in enumerate(c) if v==0];full=[]
  for bits in itertools.product([0,1],repeat=len(fs)):
   literals=set(i for i,b in zip(fs,bits) if b);pos=start;ss=ctx;score=0.;p=[];mask=0
   for i,v in enumerate(c):
    if i not in literals and not periodic and pos>=len(key):break
    r=0 if i in literals else (v+sign*key[pos%len(key)])%29
    # Full history reconstruction rather than using supplied extend callback.
    w=float(weights[ss+(r,)]);ss=(ss[1],r)
    if i in ends:w+=float(weights[ss+(29,)]);ss=(ss[1],29)
    score+=w;p.append(r);pos+=i not in literals;mask=mask*2+(i in literals)
   else:full.append((score,mask,p,sorted(literals),pos-start))
  full.sort(key=lambda x:(-x[0],x[1]))
  try:got,diag=exact.decode(c,key,extend,sign=sign,periodic=periodic,start=start,ends=ends,retain=retain,context=ctx)
  except ValueError:
   assert not full;records.append(dict(case=z,exhausted=True));continue
  assert len(got)==min(retain,len(full))
  assert [x['total'] for x in got]==[x[0] for x in full[:retain]],(z,got,full)
  bymask={x[1]:x for x in full}
  for x in got:
   f=bymask[int(x['mask'])];assert (x['total'],x['plain'],x['literal_positions'],x['used'])==(f[0],f[2],f[3],f[4])
  count=sum(x[0]==full[0][0] for x in full);assert int(diag['optimal_path_ties_lower_bound'])<=count
  records.append(dict(case=z,paths=len(full),ties=count,reported_ties=diag['optimal_path_ties_lower_bound']))
 dump('decoder-checks.json',dict(seed=9170835,passed=True,records=records))
 print('decoder passed',len(records),flush=True)
def exhaustive(W):
 m=len(W);free=np.indices((29,)*(m-1),dtype=np.int16).reshape(m-1,-1).T;e=np.column_stack([free,(-free.sum(axis=1))%29]);v=np.zeros(len(e))
 for j in range(m):v+=W[j,e[:,(j-2)%m],e[:,(j-1)%m],e[:,j]]
 ix=int(v.argmax());return float(v[ix]),e[ix].tolist()
def structured():
 records=[]
 for m in [3,4,5]:
  for kind in ['integer','normal','tiny','constant']:
   W=nr.integers(-5,6,size=(m,29,29,29)).astype(float)
   if kind=='normal':W=nr.normal(size=W.shape)
   if kind=='tiny':W*=1e-12
   if kind=='constant':W[:]=-.25
   expected,arg=exhaustive(W)
   name=f'factors-m{m}-{kind}.npz';np.savez_compressed(O/name,W=W)
   for nodes,seconds in [(100000,30.),(0,30.),(1,30.),(3,30.),(100000,0.)]:
    got=st.solve(W,max_nodes=nodes,max_seconds=seconds)
    assert got['maximum']<=expected+1e-10 and got['upper_bound']>=expected-1e-10,(m,kind,expected,got)
    if nodes==100000 and seconds>0:assert abs(got['maximum']-expected)<=1e-10
    for alt in got['alternatives']:
     e=alt['offset'];assert sum(e)%29==0
     score=sum(float(W[j,e[j-2],e[j-1],e[j]]) for j in range(m));assert abs(score-alt['score'])<1e-12
    records.append(dict(m=m,kind=kind,factors=name,expected=expected,argmax=arg,result=got))
   print('structured',m,kind,'passed',flush=True)
 dump('structured-checks.json',dict(seed=9170835,passed=True,records=records))
if __name__=='__main__':
 t=time.monotonic();decoder();structured();print('all passed seconds',time.monotonic()-t)
