import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np, scipy, json,sys,time,datetime,hashlib
from scipy.optimize import minimize
from scipy.special import logsumexp
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'exploration/persistent-01';OUT=BASE/'worker-p/P26'
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';MASK=~np.eye(29,dtype=bool)
def guard():
 assert not (BASE/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(name,x):(OUT/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def pages():
 p=sorted(json.loads((BASE/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page'])
 assert len(p)==45 and not set(x['page'] for x in p)&{4,9,14,19,24,29,34,39,44,50,54};return p
def count(seqs):
 C=np.zeros((29,29),int)
 for s in seqs:np.add.at(C,(s[:-1],s[1:]),1)
 np.fill_diagonal(C,0);return C
def logprob(x):
 a=np.r_[x,0.];L=np.broadcast_to(a,(29,29)).copy();np.fill_diagonal(L,-np.inf)
 return L-logsumexp(L,axis=1)[:,None]
def objective(x,C):
 L=logprob(x);P=np.exp(L);L[~MASK]=0;N=C.sum()
 return -float(np.sum(C*L))/N,((C.sum(1)[:,None]*P-C).sum(0)/N)[:28]
def baseline(C):
 r=minimize(objective,np.zeros(28),args=(C,),jac=True,method='L-BFGS-B',options=dict(ftol=1e-12,gtol=1e-9,maxiter=2000,maxls=50))
 return dict(a=r.x.tolist(),objective=float(r.fun),gradient=r.jac.tolist(),gradient_inf=float(max(abs(r.jac))),success=bool(r.success),status=int(r.status),message=str(r.message),nit=int(r.nit),qualified=bool(r.success and max(abs(r.jac))<=2e-6))
def candidates(C):
 A=C.astype(float)+.5*MASK;A/=A.sum(1)[:,None];ev,V=np.linalg.eig(A);rows=[];orders={}
 for i,z in enumerate(ev):
  v=V[:,i];amp=np.abs(v);phase=np.angle(v)%(2*np.pi);ix=np.lexsort((np.arange(29),phase));gaps=np.diff(np.r_[phase[ix],phase[ix[0]]+2*np.pi])
  row=dict(index=i,eigenvalue=[float(z.real),float(z.imag)],real=v.real.tolist(),imag=v.imag.tolist(),min_amplitude=float(min(amp)),minimum_phase_gap=float(min(gaps)),near_ties=int(sum(gaps<=1e-10)),accepted=False)
  if z.imag>1e-8 and min(amp)>1e-10:
   cyc=np.roll(ix,-int(np.flatnonzero(ix==0)[0]));key=tuple(map(int,cyc));row['cycle']=list(key);row['accepted']=True
   orders.setdefault(key,[]).append(i)
  rows.append(row)
 return A,rows,orders
def evaluate(seqs):
 C=count(seqs[:23]);H=count(seqs[23:]);b=baseline(C);L=logprob(np.array(b['a']));L[~MASK]=0;bltrain=float((C*L).sum());blheld=float((H*L).sum())
 A,eig,orders=candidates(C);cand=[];decoded=[]
 for cyc,aliases in sorted(orders.items()):
  f=np.empty(29,dtype=int);f[list(cyc)]=np.arange(29);D=(f[None,:]-f[:,None])%29
  counts=np.bincount(D[MASK],weights=C[MASK],minlength=29);held=np.bincount(D[MASK],weights=H[MASK],minlength=29)
  q=np.r_[0.,(counts[1:]+.5)/(C.sum()+14)];lp=np.zeros(29);lp[1:]=np.log(q[1:]);tr=float(counts@lp);he=float(held@lp)
  cand.append(dict(cycle=list(cyc),f=f.tolist(),eigen_indices=aliases,q=q.tolist(),train_counts=counts.astype(int).tolist(),held_counts=held.astype(int).tolist(),train_ll=tr,held_ll=he,held_gain=he-blheld))
  decoded.append(np.concatenate([np.r_[255,(f[np.array(s[1:])]-f[np.array(s[:-1])])%29] for s in seqs]).astype(np.uint8))
 best=min(range(len(cand)),key=lambda i:(-cand[i]['train_ll'],cand[i]['cycle'])) if cand else None
 return dict(baseline=b,baseline_train_ll=bltrain,baseline_held_ll=blheld,eigenvectors=eig,candidates=cand,selected=best,held_gain=cand[best]['held_gain'] if best is not None else None,qualified=b['qualified'] and best is not None,train_counts=C.tolist(),held_counts=H.tolist(),train_events=int(C.sum()),held_events=int(H.sum())),np.array(decoded,dtype=np.uint8)
def simulate(template,seed,L=None,cycle=None,q=None):
 rng=np.random.default_rng(seed);seqs=[];draws=[];steps=[]
 if L is not None:
  cdf=np.cumsum(np.exp(L),axis=1);cdf[:,-1]=1
 else:
  inv=np.array(cycle);f=np.empty(29,int);f[inv]=np.arange(29);cdf=np.cumsum(q);cdf[-1]=1
 for orig in template:
  s=[int(orig[0])];p=[255]
  for i in range(1,len(orig)):
   if orig[i]==orig[i-1]:s.append(s[-1]);p.append(0);continue
   u=float(rng.random());draws.append(u)
   if L is not None:k=int(np.searchsorted(cdf[s[-1]],u,side='right'));p.append(255)
   else:
    step=int(np.searchsorted(cdf,u,side='right'));k=int(inv[(f[s[-1]]+step)%29]);p.append(step)
   assert k!=s[-1];s.append(k)
  assert np.array_equal(np.diff(s)==0,np.diff(orig)==0);seqs.append(s);steps.extend(p)
 return seqs,np.array(draws),np.array(steps,dtype=np.uint8)
def control(i):
 name=['0_welcome','jpg107-167','p56_an_end','p57_parable'][i];path=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');raw=path.read_text();pos=[j for j,c in enumerate(raw) if c in ABC];rs=[ABC.index(raw[j]) for j in pos];c=np.bincount(rs,minlength=29);q=np.r_[0.,(c[1:]+.5)/(sum(c[1:])+14)]
 rng=np.random.default_rng(526100+i);cycle=rng.permutation(29);cycle=np.roll(cycle,-int(np.flatnonzero(cycle==0)[0]));seq,draws,steps=simulate([p['indices'] for p in pages()],526110+i,cycle=cycle,q=q)
 return seq,dict(source=str(path.relative_to(ROOT)),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),source_runes=rs,source_char_positions=pos,source_counts=c.tolist(),q=q.tolist(),cycle=cycle.tolist(),cycle_seed=526100+i,draw_seed=526110+i),draws,steps
def affine(cycle,truth):
 f=np.empty(29,int);f[cycle]=np.arange(29);g=np.empty(29,int);g[truth]=np.arange(29)
 # f(0)=g(0)=0 fixes rotation. A general b follows from the equality at rune0.
 matches=[int(sum(f==(a*g)%29)) for a in range(1,29)];return dict(maximum_matches=max(matches),multipliers=[i+1 for i,x in enumerate(matches) if x==max(matches)],exact=max(matches)==29)
def panel(name,seqs,extra,draws=np.array([]),steps=np.array([],dtype=np.uint8)):
 guard();file=OUT/(name+'.json')
 if file.exists():return json.loads(file.read_text())
 t=time.monotonic();r,d=evaluate(seqs);r.update(name=name,seconds=time.monotonic()-t,**extra)
 if 'cycle' in extra:
  r['order_recovery']=[affine(c['cycle'],extra['cycle']) for c in r['candidates']]
  f=np.empty(29,int);f[extra['cycle']]=np.arange(29);re=np.concatenate([np.r_[255,(f[np.array(s[1:])]-f[np.array(s[:-1])])%29] for s in seqs]);assert np.array_equal(re,steps)
 np.savez_compressed(OUT/(name+'.npz'),cipher=np.concatenate(seqs).astype(np.uint8),lengths=np.array(list(map(len,seqs))),decoded=d,draws=draws,planted_steps=steps)
 save(name+'.json',r);return r
def comparison(name,main,ns):
 unknown=sum(not r['qualified'] for r in ns);ge=sum(r['qualified'] and r['held_gain']>=main['held_gain'] for r in ns) if main['qualified'] else None
 r=dict(main_qualified=main['qualified'],held_gain=main['held_gain'],unknown_nulls=unknown,nulls=len(ns),tail=(1+ge)/(len(ns)+1) if ge is not None and not unknown else None,tail_interval=[(1+ge)/(len(ns)+1),(1+ge+unknown)/(len(ns)+1)] if ge is not None else None,selected=main['selected'],candidate_count=len(main['candidates']),baseline_gradient=main['baseline']['gradient_inf'])
 if 'order_recovery' in main:r['selected_order_recovery']=main['order_recovery'][main['selected']] if main['selected'] is not None else None;r['any_exact_order']=any(x['exact'] for x in main['order_recovery'])
 save(name,r);return r
def ensemble(i,n):
 seqs,extra,draws,steps=control(i);r=panel(f'control-{i}',seqs,extra,draws,steps);assert r['baseline']['qualified'];L=logprob(np.array(r['baseline']['a']));ns=[]
 for j in range(n):
  seed=526200+100*i+j;s,u,p=simulate(seqs,seed,L=L);ns.append(panel(f'control-{i}-null-{j:03}',s,dict(seed=seed,generating_a=r['baseline']['a']),u,p))
 out=comparison(f'control-{i}-'+('pilot' if n<99 else 'summary')+'.json',r,ns);print(json.dumps(dict(control=i,**out)),flush=True)
def pilot():
 rng=np.random.default_rng(526000);C=rng.integers(1,20,(29,29));np.fill_diagonal(C,0);x=rng.normal(0,.2,28);v,g=objective(x,C);ng=[]
 for j in range(28):
  e=np.zeros(28);e[j]=1e-6;ng.append((objective(x+e,C)[0]-objective(x-e,C)[0])/2e-6)
 assert max(abs(g-ng))<1e-7
 # noiseless circulant all nonconstant eigenvectors must recover affine truth
 q=np.r_[0.,np.arange(1,29,dtype=float)**2];q/=sum(q);cycle=rng.permutation(29).tolist();f=np.empty(29,int);f[cycle]=np.arange(29);D=(f[None,:]-f[:,None])%29;A=q[D]*1e6;_,ev,orders=candidates(A);recover=[affine(list(k),cycle) for k in orders]
 # affine() rotation gauge requires canonicalized truth.
 truth=np.roll(cycle,-cycle.index(0)).tolist();recover=[affine(list(k),truth) for k in orders];assert recover and all(z['exact'] for z in recover)
 save('arithmetic-check.json',dict(gradient_max_error=float(max(abs(g-ng))),noiseless_affine=recover,versions=dict(numpy=np.__version__,scipy=scipy.__version__)))
 ensemble(0,3)
def controls():
 for i in range(4):ensemble(i,99)
def actual():
 assert all((OUT/f'control-{i}-summary.json').exists() for i in range(4))
 p=pages();seqs=[x['indices'] for x in p];r=panel('actual',seqs,dict(pages=[x['page'] for x in p],source_positions=[x['source_char_positions'] for x in p]));assert r['baseline']['qualified'];L=logprob(np.array(r['baseline']['a']));ns=[]
 for j in range(199):
  seed=527000+j;s,u,z=simulate(seqs,seed,L=L);ns.append(panel(f'actual-null-{j:03}',s,dict(seed=seed,generating_a=r['baseline']['a']),u,z))
 print(json.dumps(comparison('summary.json',r,ns)),flush=True)
if __name__=='__main__':
 guard();t=time.monotonic();{'pilot':pilot,'controls':controls,'actual':actual}[sys.argv[1]]();print('SECONDS',time.monotonic()-t)
