import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,gzip,hashlib,sys,time,datetime
from scipy.optimize import minimize
from scipy.special import logsumexp
O=Path(__file__).resolve().parent;R=O.parents[3];B=R/'exploration/persistent-01';inv=np.array([0]+[pow(x,-1,29) for x in range(1,29)]);mask=~np.eye(29,dtype=bool);design=[np.broadcast_to(np.arange(29),(29,29)).copy(),(inv[None,:]-np.arange(29)[:,None])%29]
pages=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page']);template=[p['indices'] for p in pages];assert len(pages)==45 and not set(p['page'] for p in pages)&{4,9,14,19,24,29,34,39,44,50,54}
def guard():assert not (B/'STOP').exists() and datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def lp(x,m):
 a=np.r_[x,0.];v=a[design[m]].copy();np.fill_diagonal(v,-np.inf);return v-logsumexp(v,axis=1)[:,None]
def obj(x,C,m):
 L=lp(x,m);P=np.exp(L);z=L.copy();z[~mask]=0;N=C.sum();g=np.bincount(design[m].ravel(),weights=(C.sum(1)[:,None]*P-C).ravel(),minlength=29)/N
 return -float((C*z).sum())/N,g[:28]
def counts(seqs):
 c=np.zeros((29,29),int)
 for s in seqs:np.add.at(c,(s[:-1],s[1:]),1)
 np.fill_diagonal(c,0);return c
def fit(c,m):
 z=minimize(obj,np.zeros(28),args=(c,m),jac=True,method='L-BFGS-B',options=dict(ftol=1e-12,gtol=1e-9,maxiter=2000,maxls=50));L=lp(z.x,m)
 return dict(theta=z.x.tolist(),objective=float(z.fun),gradient=z.jac.tolist(),gradient_inf=float(max(abs(z.jac))),success=bool(z.success),message=str(z.message),iterations=int(z.nit),qualified=bool(z.success and max(abs(z.jac))<=2e-6),log_probabilities=np.where(mask,L,0).tolist())
def simulate(orig,seed,L):
 rng=np.random.default_rng(seed);cdf=np.cumsum(np.exp(L),axis=1);cdf[:,-1]=1.;seq=[];draw=[]
 for s in orig:
  out=[s[0]]
  for i in range(1,len(s)):
   if s[i]==s[i-1]:out.append(out[-1]);continue
   u=float(rng.random());draw.append(u);y=int(np.searchsorted(cdf[out[-1]],u,side='right'));assert y!=out[-1];out.append(y)
  seq.append(out);assert np.array_equal(np.diff(s)==0,np.diff(out)==0)
 return seq,draw
def panel(name,seq,seed=None,draws=None,extra=None):
 guard();path=O/(name+'.json.gz')
 if path.exists():return json.load(gzip.open(path,'rt'))
 C=counts(seq[:23]);H=counts(seq[23:]);fits=[fit(C,m) for m in range(2)];ll=[float((H*np.array(f['log_probabilities'])).sum()) for f in fits]
 decoded=[[255]+[int((inv[y]-x)%29) for x,y in zip(s,s[1:])] for s in seq]
 result=dict(name=name,seed=seed,draws=draws,extra=extra,cipher=seq,decoded=decoded,train_counts=C.tolist(),held_counts=H.tolist(),fits=fits,held_ll=ll,held_gain=ll[1]-ll[0],qualified=all(f['qualified'] for f in fits))
 with gzip.open(path,'wt') as f:json.dump(result,f,separators=(',',':'),allow_nan=False)
 return result
def source(i):
 names=['0_welcome','jpg107-167','p56_an_end','p57_parable'];p=R/'audit/parallel-01/reference/sources'/('solved_'+names[i]+'.txt');abc='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';raw=p.read_text();positions=[j for j,c in enumerate(raw) if c in abc];rs=[abc.index(raw[j]) for j in positions];q=np.bincount(rs,minlength=29)+.5;q=q/q.sum();theta=np.log(q[:28]/q[28]);return lp(theta,1),dict(path=str(p.relative_to(R)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),runes=rs,positions=positions,q=q.tolist())
def ensemble(i,n):
 if i>=0:
  L,src=source(i);s,u=simulate(template,609100+i,L);main=panel('control'+str(i),s,609100+i,u,src);stem='control'+str(i);base=610000+100*i
 else:s=template;main=panel('actual',s);stem='actual';base=611000
 ns=[];L=lp(np.array(main['fits'][0]['theta']),0)
 for j in range(n):
  t,u=simulate(s,base+j,L);ns.append(panel(stem+f'-null{j:03}',t,base+j,u))
 bad=sum(not r['qualified'] for r in ns);ge=sum(r['qualified'] and r['held_gain']>=main['held_gain'] for r in ns);valid=main['qualified'];res=dict(main=stem,held_gain=main['held_gain'],main_qualified=valid,nulls=n,unknown_nulls=bad,tail=(1+ge)/(n+1) if valid and not bad else None,tail_interval=[(1+ge)/(n+1),(1+ge+bad)/(n+1)] if valid else None)
 (O/(stem+('-pilot' if n==3 else '-summary')+'.json')).write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res),flush=True)
def pilot():
 for x in range(29):
  for p in range(29):y=inv[(p+x)%29];assert (inv[y]-x)%29==p
 rng=np.random.default_rng(609000);C=rng.integers(1,100,(29,29));np.fill_diagonal(C,0);x=rng.normal(0,.1,28);err=[]
 for m in range(2):
  _,g=obj(x,C,m);v=[]
  for j in range(28):
   e=np.zeros(28);e[j]=1e-6;v.append((obj(x+e,C,m)[0]-obj(x-e,C,m)[0])/2e-6)
  err.append(float(max(abs(g-np.array(v)))))
 assert max(err)<1e-7
 (O/'arithmetic.json').write_text(json.dumps(dict(inverse_cases=841,gradient_errors=err),indent=2)+'\n');ensemble(0,3)
if __name__=='__main__':
 t=time.monotonic();mode=sys.argv[1]
 if mode=='pilot':pilot()
 elif mode=='controls':
  for i in range(4):ensemble(i,99)
 elif mode=='actual':ensemble(-1,199)
 print('elapsed',time.monotonic()-t)
