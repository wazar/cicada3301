import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,gzip,numpy as np
R=Path(__file__).parent;B=R.parent;S=B/'worker-s';pages={p['page']:p for p in json.loads((B/'worker-f/F06-maps.json').read_text())};order=[0,1,2,3,5,6];read=lambda p:json.load(gzip.open(p,'rt'));prior=(1-np.eye(29))*.5/28;count=0;maxgrad=0.;maxerr=0.;rows=[]
def prob(t):
 w=np.exp(np.array(t)-max(t));P=np.zeros((29,29))
 for x in range(29):
  ids=[i for i in range(29) if i!=x];P[x,ids]=w[ids]/sum(w[ids])
 return P

def generate(record,ts,rng):
 for p in order:
  src=pages[p]['indices'];xs=record['runes'][str(p)];us=record['uniforms'][str(p)];assert xs[0]==src[0];P=prob(ts[0 if p in [0,1,2] else 1])
  for i in range(1,len(src)):
   if src[i]==src[i-1]:assert xs[i]==xs[i-1] and us[i-1] is None
   else:
    u=float(rng.random());assert u==us[i-1];cum=0;chosen=None
    for v,q in enumerate(P[xs[i-1]]):
     cum+=q
     if u<cum:chosen=v;break
    assert chosen==xs[i]
def audit(record):
 global count,maxgrad,maxerr
 count+=1;cs={}
 for p in order:
  xs=record['runes'][str(p)];c=np.zeros((29,29),int)
  for a,b in zip(xs,xs[1:]):
   if a!=b:c[a,b]+=1
  cs[p]=c
 models=record['fit']['models'];Ps={}
 for name,ids in [('pooled',[0,1,3,5]),('cross',[0,1]),('scroll',[3,5])]:
  m=models[name];c=sum(cs[p] for p in ids);assert c.tolist()==m['counts'];aug=c+prior;t=np.array(m['theta']);P=prob(t);Ps[name]=P;assert np.max(abs(P-np.array(m['P'])))<1e-14
  g=np.zeros(29);objective=0
  for a in range(29):
   for b in range(29):
    if a!=b:objective-=aug[a,b]*np.log(P[a,b]);g+=aug[a,b]*P[a];g[b]-=aug[a,b]
  g/=aug.sum();objective/=aug.sum();maxgrad=max(maxgrad,float(abs(g[:28]).max()));assert abs(g[:28]).max()<=1e-7 and abs(objective-m['objective_after_Newton'])<1e-12 and m['ok'] and m['optimizer_success'];assert m['objective_after_Newton']<=m['objective_before_Newton']+1e-12
  assert abs(t[-1])==0
 total=0
 for p in [2,6]:
  xs=record['runes'][str(p)];group='cross' if p==2 else 'scroll';terms=[]
  for i,(a,b) in enumerate(zip(xs,xs[1:]),1):
   if a!=b:terms.append(dict(position=i,log_group=float(np.log(Ps[group][a,b])),log_pooled=float(np.log(Ps['pooled'][a,b])),difference=float(np.log(Ps[group][a,b])-np.log(Ps['pooled'][a,b]))))
  saved=record['fit']['held_details'][str(p)];assert len(terms)==len(saved)
  for a,b in zip(terms,saved):
   assert a['position']==b['position'];e=max(abs(a[k]-b[k]) for k in ['log_group','log_pooled','difference']);maxerr=max(maxerr,e);assert e<1e-12
  score=sum(x['difference'] for x in terms);assert abs(score-record['fit']['page_scores'][str(p)])<1e-10;total+=score
 assert abs(total-record['fit']['statistic'])<1e-10
 return total
for ix in range(13):
 rec=read(S/(f'S12-control{ix}.json.gz' if ix<12 else 'S12-real.json.gz'))
 if ix<12:
  rng=np.random.default_rng(722610+ix);base=rng.normal(0,.35,29);raw=rng.normal(0,1,29);v=raw-raw.mean();v/=np.sqrt(np.mean(v*v));beta=[0,.25,.75][ix//4];ts=[base+beta*v,base-beta*v];assert np.array_equal(base,rec['base']) and np.array_equal(raw,rec['raw_contrast']);generate(rec,ts,rng)
 else:
  assert all(rec['runes'][str(p)]==pages[p]['indices'] for p in order)
 obs=audit(rec);values=[]
 for j,n in enumerate(rec['nulls']):
  seed=(723000+100*ix+j) if ix<12 else (725000+j);assert seed==n['seed'];theta=rec['fit']['models']['pooled']['theta'];generate(n,[theta,theta],np.random.default_rng(seed));values.append(audit(n))
 tail=(1+sum(x>=obs for x in values))/(len(values)+1);rows.append(dict(panel=ix,statistic=obs,tail=tail));print(ix,tail,flush=True)
assert count==1600
(R/'panels-result.json').write_text(json.dumps(dict(status='PASS',panels=count,fits=3*count,max_gradient=maxgrad,max_term_error=maxerr,rows=rows),indent=2))
