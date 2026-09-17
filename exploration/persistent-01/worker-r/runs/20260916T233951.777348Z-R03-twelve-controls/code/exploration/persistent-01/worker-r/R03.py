import pathlib,json,gzip,hashlib,time,datetime,argparse,warnings
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import csc_matrix
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).parent
raw=(OUT/'R01-input.json').read_bytes();D=sorted(json.loads(raw),key=lambda x:x['page']);assert len(D)==45
assert not ({4,9,14,19,24,29,34,39,44,50,54}&{x['page'] for x in D})
TR=list(range(0,45,2));HE=list(range(1,45,2));REAL=[x['indices'] for x in D]
MASKS=[np.array(a[1:])==np.array(a[:-1]) for a in REAL]
EDGES=[(a,b) for a in range(29) for b in range(a+1,29)]
A=np.zeros((30,len(EDGES)))
for k,(a,b) in enumerate(EDGES):A[a,k]=A[b,k]=A[29,k]=1
CON=LinearConstraint(csc_matrix(A),np.array([0]*29+[14]),np.array([1]*29+[14]))
BOUNDS=Bounds(np.zeros(len(EDGES)),np.ones(len(EDGES)))
warnings.filterwarnings('ignore',message='Unrecognized options detected')
def guard():
 if (ROOT/'exploration/persistent-01/STOP').exists():raise SystemExit('STOP')
def solve(cost):
 guard();t=time.monotonic();r=milp(np.array(cost,float),integrality=np.ones(len(EDGES)),bounds=BOUNDS,constraints=CON,options={'time_limit':5.0,'mip_rel_gap':0.0,'threads':1,'random_seed':0})
 if not r.success or r.status!=0 or r.mip_gap>1e-10:raise RuntimeError(str(r))
 ix=np.flatnonzero(r.x>.5);pairs=[EDGES[k] for k in ix];assert len(pairs)==14 and len(set(v for p in pairs for v in p))==28
 assert abs(sum(cost[k] for k in ix)-r.fun)<1e-7
 return pairs,dict(status=int(r.status),gap=float(r.mip_gap),nodes=int(r.mip_node_count),seconds=time.monotonic()-t,objective=float(r.fun))
def counter(vs,which):
 c=np.zeros((29,29),dtype=int)
 for i in which:
  a=vs[i];np.add.at(c,(a[:-1],a[1:]),1)
 np.fill_diagonal(c,0);return c
def weights(vs):return (np.bincount(np.concatenate([vs[i] for i in TR]),minlength=29)+.5)/(sum(len(vs[i]) for i in TR)+14.5)
def expect(c,w):
 e=c.sum(axis=1)[:,None]*w[None,:]/(1-w[:,None]);np.fill_diagonal(e,0);return e
def costs(c,e):return [(c[a,b]+c[b,a]-e[a,b]-e[b,a])/np.sqrt(e[a,b]+e[b,a]) for a,b in EDGES]
def fit(vs):
 w=weights(vs);ct=counter(vs,TR);ch=counter(vs,HE);et=expect(ct,w);eh=expect(ch,w);p,s=solve(costs(ct,et));heldcost=costs(ch,eh);lookup=dict(zip(EDGES,heldcost));stat=sum(lookup[x] for x in p)
 return dict(weights=w.tolist(),pairs=p,train_counts=ct.tolist(),held_counts=ch.tolist(),train_expected=et.tolist(),held_expected=eh.tolist(),solver=s,held_stat=float(stat),held_count=int(sum(ch[a,b]+ch[b,a] for a,b in p)),singleton=next(x for x in range(29) if all(x not in q for q in p)))
def generate(w,seed,inverse=None):
 r=np.random.default_rng(seed);ps=[]
 for a in range(29):
  p=np.array(w,float);p[a]=0
  if inverse is not None and inverse[a]!=a:p[inverse[a]]=0
  p/=p.sum();ps.append(np.cumsum(p))
 vs=[]
 for mask in MASKS:
  a=[int(r.choice(29,p=w))];u=r.random(len(mask))
  for i,loop in enumerate(mask):a.append(a[-1] if loop else min(28,int(np.searchsorted(ps[a[-1]],u[i],side='right'))))
  assert np.array_equal(np.array(a[1:])==np.array(a[:-1]),mask)
  if inverse is not None:assert all(x==y or inverse[x]!=y for x,y in zip(a,a[1:]))
  vs.append(a)
 return vs
def inversion(seed):
 r=np.random.default_rng(seed);ls=list(map(int,r.permutation(29)));iv=list(range(29))
 for a,b in zip(ls[:28:2],ls[1:28:2]):iv[a]=b;iv[b]=a
 return iv
def experiment(vs,seedbase,n,stream,tag,truth=None):
 z=fit(vs);stream.write(json.dumps(dict(tag=tag,kind='panel',streams=vs,fit=z,truth=truth))+'\n');null=[]
 for i in range(n):
  ns=generate(z['weights'],seedbase+i);rz=fit(ns);null.append(rz['held_stat']);stream.write(json.dumps(dict(tag=tag,kind='null',seed=seedbase+i,streams=ns,fit=rz))+'\n')
 z['p_lower']=(1+sum(x<=z['held_stat'] for x in null))/(n+1);z['null_stats']=null
 if truth is not None:z['true_pairs_recovered']=sum(truth[a]==b for a,b in z['pairs']);z['true_singleton_recovered']=truth[z['singleton']]==z['singleton']
 return z
# Exact solver fixture: unique matching of pairs(0,1),...(26,27);28singleton.
cost=[0 if a%2==0 and b==a+1 else 10 for a,b in EDGES];p,fixture=solve(cost);assert p==[(a,a+1) for a in range(0,28,2)]
a=argparse.ArgumentParser();a.add_argument('--mode',choices=['pilot','controls','real'],required=True);a.add_argument('--start',type=int,default=0);a.add_argument('--end',type=int,default=12);args=a.parse_args()
t=time.monotonic();w=np.geomspace(1,5,29);w/=w.sum();res=dict(mode=args.mode,fixture=fixture,input_sha256=hashlib.sha256(raw).hexdigest(),train_pages=[D[i]['page'] for i in TR],test_pages=[D[i]['page'] for i in HE],panels=[])
name='R03-'+args.mode+(f'-{args.start}-{args.end}' if args.mode=='controls' else '')
with gzip.open(OUT/(name+'-full.jsonl.gz'),'wt') as f:
 if args.mode=='real':
  z=experiment(REAL,430000,199,f,'real');res['panels'].append(z);print('REAL',z['held_stat'],z['held_count'],z['p_lower'],flush=True)
 else:
  choices=range(2) if args.mode=='pilot' else range(args.start,args.end)
  for c in choices:
   planted=(c%2==0);seed=460001+c if args.mode=='pilot' else 440000+1000*c;iv=inversion(seed+9) if planted else None;vs=generate(w,seed,iv);base=470000+1000*c if args.mode=='pilot' else 450000+1000*c
   z=experiment(vs,base,19 if args.mode=='pilot' else 49,f,str(c),iv);z.update(control=c,planted=planted,generation_seed=seed);res['panels'].append(z);print('CONTROL',c,planted,z['held_stat'],z['p_lower'],z.get('true_pairs_recovered'),flush=True)
res['seconds']=time.monotonic()-t;res['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(OUT/(name+'-results.json')).write_text(json.dumps(res,indent=2)+'\n');print('SECONDS',res['seconds'])
