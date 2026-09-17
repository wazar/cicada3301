import pathlib,json,gzip,hashlib,time,sys,datetime
import numpy as np
import scipy
from scipy.optimize import minimize
B=pathlib.Path('exploration/persistent-01/worker-s');SRC=pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json');CARD=pathlib.Path('exploration/persistent-01/worker-n/N10/READY-CARD.md');assert hashlib.sha256(CARD.read_bytes()).hexdigest()=='59196e337f302e8a7faec20ce3d37ed3112b85c1372415b7ab63a730f2af3110'
pages={p['page']:p for p in json.loads(SRC.read_text()) if p['page'] in [0,1,2,3,5,6]};ORDER=[0,1,2,3,5,6];GROUP={p:('cross' if p in [0,1,2] else 'scroll') for p in ORDER};prior=(np.ones((29,29))-np.eye(29))*(.5/28)
def probs(theta):
 a=np.exp(theta-np.max(theta));m=np.tile(a,(29,1));np.fill_diagonal(m,0);return m/m.sum(1)[:,None]
def objective(t,c,hessian=False):
 theta=np.r_[t,0.];P=probs(theta);rows=c.sum(1);dest=c.sum(0);total=c.sum();den=np.log(np.exp(theta-np.max(theta)).sum()-np.exp(theta-np.max(theta)))+np.max(theta);value=(rows@den-dest@theta)/total;g=(rows@P-dest)/total
 if hessian:H=(np.diag(rows@P)-P.T@(rows[:,None]*P))/total;return float(value),g[:28],H[:28,:28]
 return float(value),g[:28]
def fit(c):
 aug=c+prior;dest=aug.sum(0);initial=np.log(dest[:28]/dest[28]);result=minimize(lambda t:objective(t,aug),initial,jac=True,method='L-BFGS-B',options={'maxiter':300,'gtol':1e-9,'ftol':1e-14,'maxls':40});before,g,H=objective(result.x,aug,True);after_theta=result.x-np.linalg.solve(H,g);after,finalg=objective(after_theta,aug);theta=np.r_[after_theta,0.];ok=bool(result.success and np.isfinite(theta).all() and np.isfinite(after) and after<=before+1e-12 and np.max(np.abs(finalg))<=1e-7)
 return {'theta':theta.tolist(),'P':probs(theta).tolist(),'counts':c.astype(int).tolist(),'initial':initial.tolist(),'optimizer_theta':result.x.tolist(),'optimizer_success':bool(result.success),'optimizer_message':str(result.message),'nit':int(result.nit),'nfev':int(result.nfev),'objective_before_Newton':before,'objective_after_Newton':after,'gradient_inf':float(np.max(np.abs(finalg))),'ok':ok}
def counts(xs):
 c=np.zeros((29,29))
 for a,b in zip(xs[:-1],xs[1:]):
  if a!=b:c[a,b]+=1
 return c
def panel(seqs):
 cs={p:counts(seqs[p]) for p in ORDER};models={'pooled':fit(sum(cs[p] for p in [0,1,3,5])),'cross':fit(cs[0]+cs[1]),'scroll':fit(cs[3]+cs[5])};scores={};details={}
 for p in [2,6]:
  group=GROUP[p];pg=np.array(models[group]['P']);pp=np.array(models['pooled']['P']);terms=[]
  for i,(a,b) in enumerate(zip(seqs[p][:-1],seqs[p][1:]),1):
   if a!=b:terms.append({'position':i,'log_group':float(np.log(pg[a,b])),'log_pooled':float(np.log(pp[a,b])),'difference':float(np.log(pg[a,b])-np.log(pp[a,b]))})
  scores[str(p)]=sum(t['difference'] for t in terms);details[str(p)]=terms
 return {'models':models,'page_scores':scores,'held_details':details,'statistic':sum(scores.values()),'ok':all(m['ok'] for m in models.values())}
def generate(logits,seed=None,rng=None):
 rng=np.random.default_rng(seed) if rng is None else rng;Ps={k:probs(v) for k,v in logits.items()};seqs={};uniforms={}
 for p in ORDER:
  original=pages[p]['indices'];xs=[original[0]];draws=[]
  for i in range(1,len(original)):
   if original[i]==original[i-1]:xs.append(xs[-1]);draws.append(None)
   else:
    u=float(rng.random());row=Ps[GROUP[p]][xs[-1]];v=int(np.searchsorted(np.cumsum(row),u,side='right'));assert v<29 and v!=xs[-1];xs.append(v);draws.append(u)
  assert [a==b for a,b in zip(xs[:-1],xs[1:])]==[a==b for a,b in zip(original[:-1],original[1:])];seqs[p]=xs;uniforms[p]=draws
 return seqs,uniforms

def control(i):
 beta=[0,.25,.75][i//4];rng=np.random.default_rng(722610+i);base=rng.normal(0,.35,29);raw=rng.normal(0,1,29);contrast=raw-raw.mean();contrast/=np.sqrt(np.mean(contrast**2));logits={'cross':base+beta*contrast,'scroll':base-beta*contrast};seqs,us=generate(logits,rng=rng)
 return {'i':i,'beta':beta,'base':base.tolist(),'raw_contrast':raw.tolist(),'normalized_contrast':contrast.tolist(),'truth_logits':{k:v.tolist() for k,v in logits.items()},'truth_P':{k:probs(v).tolist() for k,v in logits.items()},'runes':seqs,'uniforms':us,'fit':panel(seqs),'nulls':[]}
def nullpanel(parent,seed):
 theta=np.array(parent['fit']['models']['pooled']['theta']);seqs,us=generate({'cross':theta,'scroll':theta},seed);return {'seed':seed,'runes':seqs,'uniforms':us,'fit':panel(seqs)}
def save(path,x):(B/path).write_bytes(gzip.compress(json.dumps(x,separators=(',',':')).encode(),mtime=0))
def load(path):return json.loads(gzip.decompress((B/path).read_bytes()))
def stopcheck():
 if pathlib.Path('exploration/persistent-01/STOP').exists() or datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc):raise RuntimeError('STOP/deadline reached')
def summarize(record):
 vals=[x['fit']['statistic'] for x in record['nulls']];obs=record['fit']['statistic'];okay=record['fit']['ok'] and all(n['fit']['ok'] for n in record['nulls'])
 return {'statistic':obs,'page_scores':record['fit']['page_scores'],'null_count':len(vals),'null_min':min(vals),'null_max':max(vals),'upper_add_one_rank':(1+sum(x>=obs for x in vals))/(1+len(vals)),'all_numeric_ok':okay,'both_page_scores_positive':all(x>0 for x in record['fit']['page_scores'].values()),'inference':'NUMERICALLY_VALID' if okay else 'UNKNOWN'}
def checks():
 rng=np.random.default_rng(722600);c=rng.integers(0,5,(29,29)).astype(float);np.fill_diagonal(c,0);c+=prior;t=rng.normal(0,.3,28);f,g,H=objective(t,c,True);eps=1e-5;ng=np.empty(28);nh=np.empty((28,28))
 for j in range(28):
  d=np.zeros(28);d[j]=eps;f1,g1=objective(t+d,c);f0,g0=objective(t-d,c);ng[j]=(f1-f0)/(2*eps);nh[:,j]=(g1-g0)/(2*eps)
 assert np.max(np.abs(g-ng))<=1e-7 and np.max(np.abs(H-nh))<=1e-7;P=probs(np.zeros(29));assert np.max(np.abs(P.sum(1)-1))<=1e-14 and np.all(np.diag(P)==0) and np.max(np.abs(P[~np.eye(29,dtype=bool)]-1/28))<=1e-14
 direct=-sum(c[a,b]*np.log(probs(np.r_[t,0.])[a,b]) for a in range(29) for b in range(29) if a!=b)/c.sum();assert abs(direct-f)<1e-12
 result={'gradient_error':float(np.max(np.abs(g-ng))),'Hessian_error':float(np.max(np.abs(H-nh))),'objective_direct_error':float(abs(direct-f)),'fixture_counts':c.tolist(),'fixture_theta':t.tolist(),'numpy':np.__version__,'scipy':scipy.__version__};(B/'S12-arithmetic-check.json').write_text(json.dumps(result,indent=2)+'\n')
def main():
 start=time.monotonic();mode=sys.argv[1]
 if mode=='pilot':
  checks();c=control(0)
  for j in range(3):c['nulls'].append(nullpanel(c,723000+j))
  save('S12-control0.json.gz',c);r={'mode':mode,'seconds':time.monotonic()-start,'panels':4,'all_numeric_ok':c['fit']['ok'] and all(n['fit']['ok'] for n in c['nulls']),'statistic':c['fit']['statistic'],'null_statistics':[n['fit']['statistic'] for n in c['nulls']]};r['projected_1600_panel_seconds']=r['seconds']/4*1600;(B/'S12-pilot.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
 elif mode=='controls':
  summary=[]
  for i in range(12):
   stopcheck();name=f'S12-control{i}.json.gz';c=load(name) if (B/name).exists() else control(i)
   for j in range(len(c['nulls']),99):
    if j%10==0:stopcheck()
    c['nulls'].append(nullpanel(c,723000+100*i+j))
   save(name,c);s={'i':i,'beta':c['beta'],**summarize(c)};summary.append(s);print(json.dumps(s),flush=True)
  report={'controls':summary,'seconds':time.monotonic()-start,'all_numeric_ok':all(c['all_numeric_ok'] for c in summary),'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ready_card_sha256':hashlib.sha256(CARD.read_bytes()).hexdigest()};(B/'S12-controls-summary.json').write_text(json.dumps(report,indent=2)+'\n')
 elif mode=='actual':
  report=json.loads((B/'S12-controls-summary.json').read_text());assert report['all_numeric_ok'];stopcheck();name='S12-real.json.gz'
  c=load(name) if (B/name).exists() else {'runes':{p:pages[p]['indices'] for p in ORDER},'fit':panel({p:pages[p]['indices'] for p in ORDER}),'nulls':[]}
  for j in range(len(c['nulls']),399):
   if j%10==0:stopcheck()
   c['nulls'].append(nullpanel(c,725000+j))
  save(name,c);r={**summarize(c),'seconds':time.monotonic()-start,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'ready_card_sha256':hashlib.sha256(CARD.read_bytes()).hexdigest(),'pages':ORDER,'source_maps':{p:pages[p]['source_char_positions'] for p in ORDER}};(B/'S12-real-summary.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='source_maps'},indent=2))
if __name__=='__main__':main()
