import pathlib,json,gzip,time,datetime,argparse,hashlib
import numpy as np
from scipy.special import logsumexp,softmax
from scipy.optimize import minimize,linear_sum_assignment
P=pathlib.Path(__file__).resolve().parent;SRC=P/'R01-input.json';raw=SRC.read_bytes();D=sorted(json.loads(raw),key=lambda p:p['page']);REAL=[p['indices'] for p in D];MASKS=[np.array(a[1:])==np.array(a[:-1]) for a in REAL];HEAD=[]
for p in D:
 h=np.zeros(len(p['indices'])-1,dtype=bool)
 for g in p['gaps']:
  assert g['next']==g['previous']+1
  if g['type']=='hyphen':h[g['previous']]=True
 HEAD.append(h)
assert len(D)==45 and not ({4,9,14,19,24,29,34,39,44,50,54}&{p['page'] for p in D})
def guard():
 assert not (P.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def obj(z,A):
 theta=np.r_[z,0.];choice=np.broadcast_to(theta,(29,29)).copy();np.fill_diagonal(choice,-np.inf);lp=choice-logsumexp(choice,axis=1)[:,None];pr=np.exp(lp);lp[np.diag_indices(29)]=0;total=A.sum();return -np.sum(A*lp)/total,((A.sum(1)@pr-A.sum(0))/total)[:-1]
def fitweights(C):
 prior=np.full((29,29),.5/28);np.fill_diagonal(prior,0);A=C+prior;initial=np.log(A.sum(0));initial-=initial[-1];r=minimize(obj,initial[:-1],args=(A,),jac=True,method='L-BFGS-B',options=dict(maxiter=300,gtol=1e-9,ftol=1e-14,maxls=40));val,g=obj(r.x,A);theta=np.r_[r.x,0.];lp=np.broadcast_to(theta,(29,29)).copy();np.fill_diagonal(lp,-np.inf);lp-=logsumexp(lp,axis=1)[:,None];pr=np.exp(lp);ok=bool(r.success and max(abs(g))<=1e-7 and np.isfinite(val));assert ok,(r.message,max(abs(g)));assert np.allclose(pr.sum(1),1,atol=1e-12) and np.all(np.diag(pr)==0)
 return dict(weights=softmax(theta).tolist(),theta=theta.tolist(),qualified=ok,gradient_max=float(max(abs(g))),iterations=int(r.nit),evaluations=int(r.nfev),objective=float(val),status=int(r.status)),pr

def counts(vs):
 tr=np.zeros((2,29,29),int);he=np.zeros((2,29,29),int)
 for i,a in enumerate(vs):
  x=np.array(a[:-1]);y=np.array(a[1:]);keep=x!=y;dst=tr if i%2==0 else he;np.add.at(dst,(HEAD[i][keep].astype(int),x[keep],y[keep]),1)
 return tr,he

def fit(vs):
 guard();tr,he=counts(vs);fits=[];probs=[]
 for s in [0,1]:f,pr=fitweights(tr[s]);fits.append(f);probs.append(pr)
 E=tr[1].sum(1)[:,None]*probs[1];gain=tr[1]-E;cost=-gain;np.fill_diagonal(cost,np.inf);r,c=linear_sum_assignment(cost);assert np.array_equal(r,np.arange(29));assert len(set(c))==29 and np.all(c!=r);observed=int(he[1][r,c].sum());expected=float(np.sum(he[1].sum(1)*probs[1][r,c]));n=int(he[1].sum());score=(observed-expected)/n
 return dict(baseline_fits=fits,pi=c.tolist(),train_counts=tr.tolist(),held_counts=he.tolist(),train_objective=float(gain[r,c].sum()),train_matches=int(tr[1][r,c].sum()),train_eligible=int(tr[1].sum()),held_matches=observed,held_expected=expected,held_eligible=n,score=float(score),held_match_rate=observed/n),probs

def conditional(w):
 pr=np.broadcast_to(w,(29,29)).copy();np.fill_diagonal(pr,0);pr/=pr.sum(1)[:,None];return pr

def generate(probs,seed,pi=None,rate=0):
 rng=np.random.default_rng(seed);cdf=np.cumsum(probs,axis=2);vs=[];choices=[]
 for mask,head in zip(MASKS,HEAD):
  a=[int(rng.integers(29))];u=rng.random(len(mask));coin=rng.random(len(mask));echo=[]
  for j,loop in enumerate(mask):
   x=a[-1]
   if loop:y=x
   elif head[j] and pi is not None and coin[j]<rate:y=int(pi[x]);echo.append(j)
   else:y=min(28,int(np.searchsorted(cdf[int(head[j]),x],u[j],side='right')))
   a.append(y)
  assert np.array_equal(np.array(a[1:])==np.array(a[:-1]),mask)
  if pi is not None:assert all(a[j+1]==pi[a[j]] for j in echo)
  vs.append(a);choices.append(echo)
 return vs,choices

def plant(seed,rate):
 rng=np.random.default_rng(seed);pi=rng.permutation(29)
 while np.any(pi==np.arange(29)):pi=rng.permutation(29)
 w=np.geomspace(1,5,29);w/=w.sum();weights=[rng.permutation(w),rng.permutation(w)];probs=np.array([conditional(x) for x in weights]);vs,echo=generate(probs,seed+1,pi,rate);return vs,dict(pi=pi.tolist(),rate=rate,weights=[x.tolist() for x in weights],echo_positions=echo,generation_seed=seed+1)

def experiment(vs,base,n,f,tag,truth=None):
 z,probs=fit(vs);f.write(json.dumps(dict(kind='panel',tag=tag,streams=vs,fit=z,truth=truth))+'\n');null=[]
 for i in range(n):
  ns,_=generate(np.array(probs),base+i);q,_=fit(ns);null.append(q['score']);f.write(json.dumps(dict(kind='null',tag=tag,seed=base+i,streams=ns,fit=q))+'\n')
 z['p_upper']=(1+sum(t>=z['score'] for t in null))/(n+1);z['null_scores']=null
 if truth is not None:z.update(true_pi_recovered=int(sum(a==b for a,b in zip(z['pi'],truth['pi']))),echo_rate=truth['rate'])
 return z

args=argparse.ArgumentParser();args.add_argument('--mode',choices=['pilot','controls','real'],required=True);args=args.parse_args();guard();t=time.monotonic();out=dict(mode=args.mode,input_sha256=hashlib.sha256(raw).hexdigest(),train_pages=[p['page'] for p in D[::2]],test_pages=[p['page'] for p in D[1::2]],panels=[]);name='R07-'+args.mode
with gzip.open(P/(name+'-full.jsonl.gz'),'wt') as f:
 if args.mode=='real':
  ctl=json.loads((P/'R07-controls-results.json').read_text());assert all(x['held_match_rate']>=.95 and x['p_upper']<=.01 for x in ctl['panels'] if x['echo_rate']==1);z=experiment(REAL,520000,399,f,'real');out['panels'].append(z);print('REAL',z['score'],z['held_matches'],z['held_expected'],z['p_upper'],flush=True)
 else:
  for c in range(3 if args.mode=='pilot' else 12):
   rate=[1,.25,0][c if args.mode=='pilot' else c//4];seed=479100+c if args.mode=='pilot' else 480000+1000*c;base=479500+100*c if args.mode=='pilot' else 500000+1000*c;vs,truth=plant(seed,rate);z=experiment(vs,base,19 if args.mode=='pilot' else 99,f,str(c),truth);z['control']=c;out['panels'].append(z);print('CONTROL',c,rate,z['true_pi_recovered'],z['held_match_rate'],z['p_upper'],flush=True)
out['seconds']=time.monotonic()-t;(P/(name+'-results.json')).write_text(json.dumps(out,indent=2)+'\n');print('SECONDS',out['seconds'])
