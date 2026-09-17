import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
import json,math,hashlib,datetime
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'exploration/persistent-01';P=BASE/'worker-p/P19'
assert not (BASE/'STOP').exists()
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
pages=sorted(json.loads((BASE/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page'])
bank=np.load(BASE/'worker-r/R04-bank.npz');mapping=json.loads((BASE/'worker-i/route-mapping.json').read_text())['class_to_runes']
features={}
for i,c in enumerate(bank['shapes']):
 candidates=[]
 for ai,a in enumerate(bank['angles']):
  for si,s in enumerate(bank['shifts']):
   if a==0 and all(s==0):candidates.append(bank['features'][(i*13+ai)*9+si])
 assert len(candidates)==1
 features[mapping[str(c)][0]]=candidates[0]
raw=np.zeros((29,29))
for i in range(29):
 for j in range(29):raw[i,j]=math.sqrt(sum(float(x-y)**2 for x,y in zip(features[i],features[j]))/2048)
off=[raw[i,j] for i in range(29) for j in range(29) if i!=j];mu=sum(off)/812;sd=math.sqrt(sum((x-mu)**2 for x in off)/812)
D=(raw-mu)/sd;np.fill_diagonal(D,0)
stored=np.load(P/'metric.npz');assert np.max(abs(D-stored['D']))<1e-12
def prob(a,b):
 z=[]
 for i in range(29):
  w=[0 if j==i else math.exp(a[j]+b*D[i,j]) for j in range(29)];den=sum(w);z.append([v/den for v in w])
 return z
def loglik(s,T):
 return sum(math.log(T[i][j]) for i,j in zip(s,s[1:]) if i!=j)
rows=[];maxerr=0;draws=0
files=sorted(P.glob('control-*.json'))+sorted(P.glob('actual-null-*.json'))+[P/'actual.json']
for f in files:
 r=json.loads(f.read_text());seqs=r['sequences']
 assert len(seqs)==45
 if 'seed' in r:
  rng=np.random.default_rng(r['seed']);T=prob(r['generating_a'],r['generating_beta'])
  for page,s in zip(pages,seqs):
   orig=page['indices'];expected=[orig[0]]
   for k in range(1,len(orig)):
    if orig[k]==orig[k-1]:expected.append(expected[-1])
    else:
     u=float(rng.random());cum=0;j=28
     for j,w in enumerate(T[expected[-1]]):
      cum+=w
      if u<cum:break
     expected.append(j);draws+=1
   assert expected==s,f.name
 else:assert seqs==[x['indices'] for x in pages]
 for page,s in zip(pages,seqs):
  assert len(page['indices'])==len(s)
  assert [a==b for a,b in zip(s,s[1:])]==[a==b for a,b in zip(page['indices'],page['indices'][1:])]
 Ts=[]
 for model in ['baseline','visual']:
  q=r[model];a=q['parameters'][:28]+[0];T=prob(a,q['beta']);Ts.append(T)
  train=-sum(loglik(s,T) for s in seqs[:23])/r['train_events']
  maxerr=max(maxerr,abs(train-q['objective']));assert abs(train-q['objective'])<1e-11
 gains=[]
 for i,s in enumerate(seqs):
  ll=[loglik(s,T) for T in Ts];gains.append(ll[1]-ll[0]);maxerr=max(maxerr,max(abs(ll[k]-r['per_page_loglik'][i][k]) for k in range(2)))
  assert max(abs(ll[k]-r['per_page_loglik'][i][k]) for k in range(2))<1e-8
 assert abs(sum(gains[23:])-r['held_gain'])<1e-8
 rows.append(dict(file=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),qualified=r['qualified']))
actual=json.loads((P/'actual.json').read_text());null=[json.loads(f.read_text()) for f in sorted(P.glob('actual-null-*.json'))]
unknown=[r['name'] for r in null if not r['qualified']]
known_ge=sum(r['qualified'] and r['held_gain']>=actual['held_gain'] for r in null)
result=dict(pass_all=True,panels=len(rows),random_draws=draws,max_scalar_score_error=maxerr,metric_max_error=float(np.max(abs(D-stored['D']))),actual_beta=actual['visual']['beta'],unknown_nulls=unknown,raw_rank_tail=(1+sum(r['held_gain']>=actual['held_gain'] for r in null))/100,rank_interval_if_only_unqualified_scores_unknown=[(1+known_ge)/100,(1+known_ge+len(unknown))/100],rows=rows)
(P/'independent-check.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
