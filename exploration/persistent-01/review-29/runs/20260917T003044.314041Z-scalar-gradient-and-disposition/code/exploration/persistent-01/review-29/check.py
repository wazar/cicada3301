from pathlib import Path
import json,hashlib,math,bisect
import numpy as np
R=Path(__file__).parent;B=R.parent;P=B/'worker-p/P19';pages=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda x:x['page']);assert not {4,9,14,19,24,29,34,39,44,50,54}&{p['page'] for p in pages}
(R/'snapshots').mkdir(exist_ok=True);sources=list(P.glob('*.json'))+[P/'CARD.md',B/'worker-p/p19.py',P/'metric.npz',B/'worker-r/R04-bank.npz',B/'worker-i/route-mapping.json',B/'worker-f/F06-maps.json'];manifest={}
for p in sources:
 b=p.read_bytes();manifest[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 if p.suffix!='.npz':(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(manifest,indent=2))
bank=np.load(B/'worker-r/R04-bank.npz');mapping=json.loads((B/'worker-i/route-mapping.json').read_text());mp={int(k):v[0] for k,v in mapping['class_to_runes'].items()};assert len(mp)==29 and len(set(mp.values()))==29 and all(len(v)==1 for v in mapping['class_to_runes'].values())
features=np.zeros((29,2048));selected=[]
for ix,shape in enumerate(bank['shapes']):
 for ai,angle in enumerate(bank['angles']):
  for si,shift in enumerate(bank['shifts']):
   if angle==0 and list(shift)==[0,0]:
    idx=(ix*len(bank['angles'])+ai)*len(bank['shifts'])+si;features[mp[int(shape)]]=bank['features'][idx];selected.append({'shape':int(shape),'rune':mp[int(shape)],'index':idx})
assert len(selected)==29
raw=np.zeros((29,29))
for i in range(29):
 for j in range(29):raw[i,j]=math.sqrt(float(np.dot(features[i]-features[j],features[i]-features[j]))/2048)
values=[raw[i,j] for i in range(29) for j in range(29) if i!=j];mean=sum(values)/812;sd=math.sqrt(sum((v-mean)**2 for v in values)/812);D=(raw-mean)/sd;np.fill_diagonal(D,0);saved=np.load(P/'metric.npz');assert np.array_equal(features,saved['features']);assert np.max(abs(D-saved['D']))<1e-13

def law(a,beta):
 ans=[]
 for i in range(29):
  scores=[a[j]+beta*D[i,j] for j in range(29)];mx=max(scores[j] for j in range(29) if i!=j);weights=[math.exp(v-mx) if j!=i else 0 for j,v in enumerate(scores)];den=sum(weights);ans.append([w/den for w in weights])
 return np.array(ans)
def generate(a,beta,seed):
 rng=np.random.default_rng(seed);pr=law(a,beta);out=[]
 for p in pages:
  s=[p['indices'][0]]
  for x,y in zip(p['indices'],p['indices'][1:]):
   if x==y:s.append(s[-1])
   else:s.append(bisect.bisect_right(list(np.cumsum(pr[s[-1]])),float(rng.random())))
  out.append(s)
 return out
maxgraderr=0.;maxllerr=0.;unqualified=[];rows=[];rngcount=0
paths=[P/'actual.json']+sorted(P.glob('actual-null-*.json'))+sorted(P.glob('control-null-*.json'))+sorted(P.glob('control-moderate-*.json'))+sorted(P.glob('control-strong-*.json'))
for path in paths:
 z=json.loads(path.read_text());ss=z['sequences'];counts=np.zeros((45,29,29),int)
 for k,(s,p) in enumerate(zip(ss,pages)):
  assert s[0]==p['indices'][0] and len(s)==len(p['indices']);assert [x==y for x,y in zip(s,s[1:])]==[x==y for x,y in zip(p['indices'],p['indices'][1:])]
  for x,y in zip(s,s[1:]):
   if x!=y:counts[k,x,y]+=1
 if path.name=='actual.json':assert ss==[p['indices'] for p in pages]
 else:assert ss==generate(z['generating_a'],z['generating_beta'],z['seed']);rngcount+=1
 C=counts[:23].sum(0);n=C.sum();lls=[];quals=[]
 for visual,key in [(False,'baseline'),(True,'visual')]:
  f=z[key];a=np.r_[f['parameters'][:28],0];beta=f['beta'];pr=law(a,beta);E=C.sum(1)[:,None]*pr-C;g=list(E.sum(0)[:28]/n)
  if visual:g.append(float((E*D).sum()/n))
  maxgraderr=max(maxgraderr,float(np.max(abs(np.array(g)-f['gradient']))));pg=g[:]
  if visual and beta<=1e-12:pg[-1]=min(pg[-1],0)
  q=f['success'] and max(abs(t) for t in pg)<=2e-6;assert q==f['qualified'];quals.append(q)
  ll=[sum(int(ct[i,j])*math.log(pr[i,j]) for i in range(29) for j in range(29) if i!=j) for ct in counts];assert abs(-sum(ll[:23])/n-f['objective'])<1e-12;lls.append(ll)
 gain=[v-b for b,v in zip(*lls)];held=sum(gain[23:]);maxllerr=max(maxllerr,abs(held-z['held_gain']),float(np.max(abs(np.array(lls).T-z['per_page_loglik']))));assert maxllerr<1e-9
 qualified=all(quals) and z['visual']['objective']<=z['baseline']['objective']+1e-9;assert qualified==z['qualified']
 if not qualified:unqualified.append({'file':path.name,'baseline_gradient':z['baseline']['projected_gradient_inf'],'visual_gradient':z['visual']['projected_gradient_inf'],'gain':held})
 rows.append({'file':path.name,'gain':held,'qualified':qualified})
actual=rows[0]['gain'];null=[r for r in rows if r['file'].startswith('actual-null')];known=sum(r['gain']>=actual for r in null if r['qualified']);unknown=sum(not r['qualified'] for r in null);interval=[(1+known)/100,(1+known+unknown)/100];controlnull=[r['gain'] for r in rows if r['file'].startswith('control-null')];power={}
for kind in ['moderate','strong']:
 tails=[(1+sum(v>=r['gain'] for v in controlnull))/100 for r in rows if r['file'].startswith('control-'+kind)];power[kind]={'tails':tails,'power_at_05':sum(t<=.05 for t in tails)}
assert len(rows)==239 and rngcount==238
out={'status':'PASS_IMPLEMENTATION_WITH_UNQUALIFIED_NULLS','panels':len(rows),'regenerated':rngcount,'metric_mean':mean,'metric_sd':sd,'bank_selection':selected,'max_gradient_difference':maxgraderr,'max_loglik_difference':maxllerr,'unqualified':unqualified,'actual_gain':actual,'qualified_null_exceedances':known,'unknown_nulls':unknown,'conservative_rank_interval':interval,'controls':power};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='bank_selection'},indent=2))
