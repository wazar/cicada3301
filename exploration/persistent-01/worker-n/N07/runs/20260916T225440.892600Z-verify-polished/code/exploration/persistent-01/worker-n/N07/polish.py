import n07 as m
import numpy as np,json,gzip,math,hashlib
from scipy.special import logsumexp,softmax
from collections import defaultdict
O=m.O/'polished';O.mkdir(exist_ok=True)
def load(path):
 with gzip.open(path,'rt') as f:return json.load(f)
def geometry(z,A):
 theta=np.r_[z,0.];v=np.tile(theta,(len(A),1));np.fill_diagonal(v,-np.inf);v-=logsumexp(v,axis=1)[:,None];p=np.exp(v);row=A.sum(1);col=A.sum(0);total=A.sum();g=(row@p-col)/total;H=(np.diag(row@p)-p.T@(row[:,None]*p))/total
 return g[:-1],H[:-1,:-1],p,row,col,total
def improve(saved,C):
 A=m.augmented(C);z=np.array(saved['theta'][:-1]);trace=[];success=False;reason='iteration cap'
 for iteration in range(11):
  g,H,p,row,col,total=geometry(z,A);norm=float(max(abs(g)))
  if norm<=1e-9:success=True;reason='gradient target';break
  if iteration==10:break
  try:step=np.linalg.solve(H,g)
  except np.linalg.LinAlgError:reason='singular Hessian';break
  if not np.all(np.isfinite(step)):reason='nonfinite Newton step';break
  trials=[];accepted=False
  for ls in range(33):
   alpha=2.**(-ls);delta=np.r_[-alpha*step,0.];change=float((row@np.log1p(p@np.expm1(delta))-col@delta)/total);bound=float(1e-4*g@delta[:-1]);trials.append(dict(alpha=alpha,objective_change=change,armijo_bound=bound))
   if np.isfinite(change) and change<=bound:
    z+=delta[:-1];accepted=True;break
  trace.append(dict(iteration=iteration,gradient_before=norm,min_hessian_eigenvalue=float(np.linalg.eigvalsh(H)[0]),trials=trials,accepted=accepted))
  if not accepted:reason='line search failed';break
 value,g=m.objective(z,A);theta=np.r_[z,0.];final=dict(theta=theta.tolist(),weights=softmax(theta).tolist(),objective=float(value),gradient_max=float(max(abs(g))),success=success,qualified=bool(success and max(abs(g))<=1e-7 and np.isfinite(value) and np.all(np.isfinite(theta))),status=0 if success else 1,message=reason,iterations=len(trace),evaluations=sum(len(t['trials']) for t in trace),method='single Newton numerical polish')
 assert value<=saved['objective']+1e-12
 return dict(original=saved,replacement=final,trace=trace)
def counts(panel):
 out=np.zeros((59,29,29));records=[]
 for page,c in enumerate(panel):
  a=np.array(c);prev=a[:-1];cur=a[1:];ok=prev!=cur;state=np.cumsum(prev[None,:]==np.arange(29)[:,None],axis=1)%2;prev=prev[ok];cur=cur[ok];state=state[:,ok];records.append((prev,cur,state))
  if page%2==0:
   np.add.at(out[0],(prev,cur),1)
   for marker in range(29):np.add.at(out,(1+2*marker+state[marker],prev,cur),1)
 return out,records
def check_hessian():
 rng=np.random.default_rng(1707085);checks=[]
 for n in [3,5,29]:
  for rep in range(3):
   C=rng.integers(1,30,(n,n)).astype(float);np.fill_diagonal(C,0);A=m.augmented(C);z=rng.normal(size=n-1);g,H,*_=geometry(z,A);direction=rng.normal(size=n-1);eps=1e-5
   fd=(m.objective(z+eps*direction,A)[1]-m.objective(z-eps*direction,A)[1])/(2*eps);error=float(max(abs(fd-H@direction)));mineig=float(np.linalg.eigvalsh(H)[0]);assert error<2e-9 and mineig>0 and np.max(abs(H-H.T))<1e-14
   checks.append(dict(n=n,rep=rep,fd_error=error,min_eigenvalue=mineig))
 (O/'hessian-check.json').write_text(json.dumps(checks,indent=2))
check_hessian();diagnostics=load(m.O/'optimizer-diagnostics.json.gz');flagged=defaultdict(list)
for d in diagnostics:
 if not d['qualified']:flagged[d['panel']].append(d['fit'])
assert sum(map(len,flagged.values()))==85 and len(flagged)==58
patches=[]
for name,indices in flagged.items():
 m.guard();original=load(m.O/'panels'/(name+'.json.gz'));C,_=counts(m.load(name)['cipher']);fits=[original['baseline_fit']]+[f for pair in original['state_fits'] for f in pair]
 for idx in indices:
  change=improve(fits[idx],C[idx]);patches.append(dict(panel=name,fit=idx,original_panel_sha256=hashlib.sha256((m.O/'panels'/(name+'.json.gz')).read_bytes()).hexdigest(),**change))
with gzip.open(O/'fit-patches.json.gz','wt') as f:json.dump(patches,f)
# All numeric polishing above finishes before any new held predictions below.
byname=defaultdict(dict)
for p in patches:byname[p['panel']][p['fit']]=p['replacement']
(O/'panels').mkdir(exist_ok=True);panels={}
for comparison in json.loads((m.O/'comparisons.json').read_text()):
 name=comparison['name'];old=load(m.O/'panels'/(name+'.json.gz'));ref=dict(path=str((m.O/'panels'/(name+'.json.gz')).relative_to(m.O)),sha256=hashlib.sha256((m.O/'panels'/(name+'.json.gz')).read_bytes()).hexdigest())
 if name not in byname:
  panels[name]={k:old[k] for k in ['name','score','selected_marker','qualified']};panels[name]['unchanged_original_reference']=ref;continue
 fits=[old['baseline_fit']]+[f for pair in old['state_fits'] for f in pair];references=[]
 for idx in range(59):
  if idx in byname[name]:fits[idx]=byname[name][idx];references.append(dict(fit=idx,replacement='fit-patches.json.gz'))
  else:references.append(dict(fit=idx,unchanged_original=True))
 _,records=counts(m.load(name)['cipher']);lps=[]
 for f in fits:
  lp=np.tile(f['theta'],(29,1));np.fill_diagonal(lp,-np.inf);lp-=logsumexp(lp,axis=1)[:,None];lps.append(lp)
 gains=np.zeros((29,45))
 for page,(prev,cur,state) in enumerate(records):
  for marker in range(29):
   model=np.asarray([lps[1+2*marker],lps[2+2*marker]]);gains[marker,page]=np.sum(model[state[marker],prev,cur]-lps[0][prev,cur])
 training=gains[:,::2].sum(1);held=gains[:,1::2].sum(1);choice=int(np.argmax(training));r=dict(name=name,original_reference=ref,fit_references=references,train_total=training.tolist(),held_total=held.tolist(),perpage_gain=gains.tolist(),selected_marker=choice,score=float(held[choice]/old['held_nonrepeat_count']),held_nonrepeat_count=old['held_nonrepeat_count'],qualified=all(f['qualified'] for f in fits),initial_score=old['score'],initial_marker=old['selected_marker'])
 with gzip.open(O/'panels'/(name+'.json.gz'),'wt') as f:json.dump(r,f)
 panels[name]=r
initial=json.loads((m.O/'result.json').read_text());groups=[]
for group in initial['controls']+[initial['real']]:
 name=group['name'];real=panels[name];null=[panels[name+'-null-'+str(i)]['score'] for i in range(len(group['null']))];out={k:v for k,v in group.items() if k not in ['null','score','tail','selected_marker','all_qualified']};out.update(score=real['score'],selected_marker=real['selected_marker'],null=null,tail=(1+sum(v>=real['score'] for v in null))/(len(null)+1),all_qualified=all(panels[n]['qualified'] for n in [name]+[name+'-null-'+str(i) for i in range(len(null))]));groups.append(out)
remaining=[dict(panel=p['panel'],fit=p['fit'],status=p['replacement']) for p in patches if not p['replacement']['qualified']]
out=dict(status='PASS' if not remaining else 'INCOMPLETE',patched_fits=len(patches),affected_panels=len(flagged),remaining_failures=remaining,max_gradient=max(p['replacement']['gradient_max'] for p in patches),max_newton_steps=max(len(p['trace']) for p in patches),max_score_change=max(abs(panels[name]['score']-load(m.O/'panels'/(name+'.json.gz'))['score']) for name in flagged),changed_selections=[name for name in flagged if panels[name]['selected_marker']!=load(m.O/'panels'/(name+'.json.gz'))['selected_marker']],controls=groups[:-1],real=groups[-1])
(O/'references.json').write_text(json.dumps({name:r.get('unchanged_original_reference',r.get('original_reference')) for name,r in panels.items()},indent=2));(O/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['controls','real']},indent=2));print(json.dumps({k:v for k,v in out['real'].items() if k!='null'},indent=2));assert not remaining
