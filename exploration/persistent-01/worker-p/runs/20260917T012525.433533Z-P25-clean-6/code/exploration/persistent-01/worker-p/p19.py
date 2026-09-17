import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,hashlib,time,sys,datetime
import numpy as np
import scipy
from scipy.optimize import minimize
from scipy.special import logsumexp
ROOT=Path(__file__).resolve().parents[3]; BASE=ROOT/'exploration/persistent-01'; OUT=BASE/'worker-p/P19'
def guard():
 assert not (BASE/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(name,x): (OUT/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def inputs():
 bank=np.load(BASE/'worker-r/R04-bank.npz'); m=json.loads((BASE/'worker-i/route-mapping.json').read_text())
 assert not m['conflicts']
 mapping={int(k):v[0] for k,v in m['class_to_runes'].items()}
 assert all(len(v)==1 for v in m['class_to_runes'].values()) and sorted(mapping.values())==list(range(29))
 ai=list(bank['angles']).index(0); si=np.flatnonzero(np.all(bank['shifts']==0,axis=1)).item()
 f=np.empty((29,2048))
 for ix,c in enumerate(bank['shapes']):f[mapping[int(c)]]=bank['features'][ix*len(bank['angles'])*len(bank['shifts'])+ai*len(bank['shifts'])+si]
 raw=np.sqrt(np.mean((f[:,None,:]-f[None,:,:])**2,axis=2)); mask=~np.eye(29,dtype=bool)
 D=(raw-raw[mask].mean())/raw[mask].std();np.fill_diagonal(D,0)
 pages=sorted(json.loads((BASE/'worker-f/F06-maps.json').read_text()),key=lambda x:x['page'])
 assert len(pages)==45 and not set(p['page'] for p in pages)&{4,9,14,19,24,29,34,39,44,50,54}
 return D,pages,raw,f,mapping
def counts(seqs):
 C=np.zeros((29,29),int)
 for s in seqs:
  a=np.array(s[:-1]);b=np.array(s[1:]);q=a!=b;np.add.at(C,(a[q],b[q]),1)
 return C
def logits(a,beta,D):
 L=a[None,:]+beta*D;np.fill_diagonal(L,-np.inf);return L-logsumexp(L,axis=1)[:,None]
def objective(x,C,D,visual):
 a=np.r_[x[:28],0.];beta=x[28] if visual else 0.
 L=logits(a,beta,D);P=np.exp(L);L[np.eye(29,dtype=bool)]=0
 E=C.sum(1)[:,None]*P-C;n=C.sum()
 grad=E.sum(0)[:28]/n
 if visual:grad=np.r_[grad,np.sum(E*D)/n]
 return -float(np.sum(C*L))/n,grad
def fit(C,D,visual,base=None):
 x=np.zeros(29 if visual else 28) if base is None else np.r_[base['parameters'][:28],0.]
 r=minimize(objective,x,args=(C,D,visual),jac=True,method='L-BFGS-B',bounds=([(None,None)]*28+[(0,None)]) if visual else None,options=dict(ftol=1e-12,gtol=1e-8,maxiter=2000,maxls=50))
 pg=r.jac.copy()
 if visual and r.x[-1]<=1e-12:pg[-1]=min(pg[-1],0.)
 return dict(parameters=r.x.tolist(),beta=float(r.x[-1]) if visual else 0.,objective=float(r.fun),gradient=r.jac.tolist(),projected_gradient_inf=float(np.max(abs(pg))),success=bool(r.success),status=int(r.status),message=str(r.message),nit=int(r.nit),nfev=int(r.nfev),qualified=bool(r.success and np.max(abs(pg))<=2e-6))
def evaluate(seqs,D):
 C=counts(seqs[:23]);b=fit(C,D,False);v=fit(C,D,True,b)
 bL=logits(np.r_[b['parameters'],0],0,D);vL=logits(np.r_[v['parameters'][:28],0],v['beta'],D)
 gains=[];ll=[]
 for s in seqs:
  a=np.array(s[:-1]);z=np.array(s[1:]);q=a!=z
  bb=float(bL[a[q],z[q]].sum());vv=float(vL[a[q],z[q]].sum());gains.append(vv-bb);ll.append([bb,vv])
 return dict(baseline=b,visual=v,qualified=b['qualified'] and v['qualified'] and v['objective']<=b['objective']+1e-9,held_gain=sum(gains[23:]),per_page_gain=gains,per_page_loglik=ll,train_events=int(C.sum()),held_events=int(counts(seqs[23:]).sum()))
def simulate(pages,D,a,beta,seed):
 rng=np.random.default_rng(seed);P=np.exp(logits(a,beta,D));cdf=np.cumsum(P,axis=1);cdf[:,-1]=1
 out=[]
 for p in pages:
  orig=p['indices'];s=[orig[0]]
  for j in range(1,len(orig)):
   if orig[j]==orig[j-1]:s.append(s[-1])
   else:
    k=int(np.searchsorted(cdf[s[-1]],rng.random(),side='right'));assert k!=s[-1];s.append(k)
  assert np.array_equal(np.diff(s)==0,np.diff(orig)==0);out.append(s)
 return out
def panel(name,seed,beta,a,D,pages):
 guard();path=OUT/(name+'.json')
 if path.exists():return json.loads(path.read_text())
 t=time.monotonic();seqs=simulate(pages,D,a,beta,seed);r=evaluate(seqs,D)
 r.update(name=name,seed=seed,generating_beta=beta,generating_a=a.tolist(),sequences=seqs,seconds=time.monotonic()-t);save(name+'.json',r);return r
def prepare():
 guard();D,pages,raw,f,m=inputs();np.savez_compressed(OUT/'metric.npz',D=D,raw=raw,features=f)
 sources=[BASE/'worker-r/R04-bank.npz',BASE/'worker-i/route-mapping.json',BASE/'worker-f/F06-maps.json']
 save('inputs.json',dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources],mapping=m,train=[p['page'] for p in pages[:23]],held=[p['page'] for p in pages[23:]],versions=dict(numpy=np.__version__,scipy=scipy.__version__),metric_mean=float(raw[~np.eye(29,dtype=bool)].mean()),metric_sd=float(raw[~np.eye(29,dtype=bool)].std())))
 # Synthetic gradient check, independent of actual transitions.
 rng=np.random.default_rng(519900);C=rng.integers(1,10,(29,29));np.fill_diagonal(C,0);x=np.r_[rng.normal(0,.2,28),.3]
 val,g=objective(x,C,D,True);num=[]
 for i in range(29):
  dx=np.zeros(29);dx[i]=1e-6;num.append((objective(x+dx,C,D,True)[0]-objective(x-dx,C,D,True)[0])/2e-6)
 err=float(np.max(abs(g-num)));assert err<1e-7
 # Scalar probability normalization and objective independent loops.
 a=np.r_[x[:28],0];scalar=0
 for i in range(29):
  den=sum(np.exp(a[k]+x[28]*D[i,k]) for k in range(29) if k!=i)
  for j in range(29):
   if j!=i:scalar-=C[i,j]*np.log(np.exp(a[j]+x[28]*D[i,j])/den)
 assert abs(scalar/C.sum()-val)<1e-12
 save('arithmetic-check.json',dict(gradient_max_error=err,scalar_objective=scalar/C.sum(),vector_objective=val))
def controls(pilot=False):
 D,pages,*_=inputs();a=np.sin(np.arange(29))/4;a-=a[-1];rows=[]
 for kind,beta,seed,n in [('null',0,519000,99),('moderate',.25,519100,20),('strong',1.,519200,20)]:
  for i in range(2 if pilot else n):
   r=panel(f'control-{kind}-{i:03}',seed+i,beta,a,D,pages);rows.append({k:r[k] for k in ['name','qualified','held_gain','seconds']})
 save('pilot.json' if pilot else 'controls-complete.json',dict(rows=rows,seconds=sum(r['seconds'] for r in rows)))
 print(json.dumps(dict(pilot=pilot,count=len(rows),qualified=all(r['qualified'] for r in rows),seconds=sum(r['seconds'] for r in rows))))
def actual():
 D,pages,*_=inputs();seqs=[p['indices'] for p in pages]
 r=evaluate(seqs,D);r['sequences']=seqs;save('actual.json',r)
 assert r['qualified'],'Actual optimizer UNKNOWN'
 a=np.r_[r['baseline']['parameters'],0.]
 for i in range(99):panel(f'actual-null-{i:03}',519300+i,0,a,D,pages)
def summary():
 cs=json.loads((OUT/'controls-complete.json').read_text());null=[r['held_gain'] for r in cs['rows'] if r['name'].startswith('control-null')]
 rows=[]
 for kind in ['moderate','strong']:
  z=[r for r in cs['rows'] if r['name'].startswith('control-'+kind)]
  tails=[(1+sum(v>=r['held_gain'] for v in null))/100 for r in z]
  rows.append(dict(kind=kind,tails=tails,power_at_05=sum(t<=.05 for t in tails),n=len(tails)))
 a=json.loads((OUT/'actual.json').read_text());ns=[json.loads((OUT/f'actual-null-{i:03}.json').read_text()) for i in range(99)]
 qualified=all(r['qualified'] for r in cs['rows']) and a['qualified'] and all(r['qualified'] for r in ns)
 save('summary.json',dict(qualified=qualified,controls=rows,actual_beta=a['visual']['beta'],actual_gain=a['held_gain'],actual_events=a['held_events'],null_gains=[r['held_gain'] for r in ns],tail=(1+sum(r['held_gain']>=a['held_gain'] for r in ns))/100 if qualified else None))
 print((OUT/'summary.json').read_text())
if __name__=='__main__':
 guard();t=time.monotonic();mode=sys.argv[1]
 {'prepare':prepare,'pilot':lambda:controls(True),'controls':controls,'actual':actual,'summary':summary}[mode]()
 print('SECONDS',time.monotonic()-t)
