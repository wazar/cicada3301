import json, pathlib, hashlib, time
import numpy as np
BASE=pathlib.Path('exploration/persistent-01/worker-s'); SOURCE=pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json')
SEED=1709202601; rng=np.random.default_rng(SEED)
pages=[x for x in json.loads(SOURCE.read_text()) if x['page'] in (0,1)]
assert [p['page'] for p in pages]==[0,1]
layouts=[]; matrices=[]
for p in pages:
 n=len(p['indices']); ids=np.full(n,-1,int)
 for wi,w in enumerate(p['words']):
  assert np.all(ids[w['start']:w['end']]==-1)
  ids[w['start']:w['end']]=wi
 assert np.all(ids>=0)
 layouts.append(ids)
 matrices.append([np.array([np.roll(ids,s)[:-d]==np.roll(ids,s)[d:] for s in range(n)]) for d in range(2,9)])
def table(xs):
 out=[]; details=[]
 for x,ms in zip(xs,matrices):
  cols=[]; detail=[]
  for d,m in zip(range(2,9),ms):
   eq=(x[:-d]==x[d:]); a=m.sum(1); b=(~m).sum(1)
   cols.append((m@eq.astype(float))/a-((~m)@eq.astype(float))/b)
   detail.append({'distance':d,'within_pairs':int(a[0]),'across_pairs':int(b[0]),'within_equal':int(eq[m[0]].sum()),'across_equal':int(eq[~m[0]].sum())})
  out.append(np.stack(cols,1)); details.append(detail)
 return out,details
def evaluate(xs,trials):
 ts,details=table(xs)
 offsets=np.column_stack([rng.integers(len(t),size=trials) for t in ts])
 samples=sum(t[offsets[:,i]] for i,t in enumerate(ts))/len(ts)
 obs=sum(t[0] for t in ts)/len(ts)
 center=sum(t.mean(0) for t in ts)/len(ts)
 sd=samples.std(0); sd=np.maximum(sd,1e-12)
 zs=(center-obs)/sd; nullmax=((center-samples)/sd).max(1)
 stat=float(zs.max()); pval=float((1+(nullmax>=stat).sum())/(1+trials))
 return {'p':pval,'max_z':stat,'distance_z':zs.tolist(),'contrast':obs.tolist(),'null_center':center.tolist(),'null_sd':sd.tolist(),'details':details},ts

def generate(kind):
 xs=[]
 for p in pages:
  n=len(p['indices']); x=np.zeros(n,int)
  if kind=='markov':
   x[0]=rng.integers(29)
   for i in range(1,n):
    x[i]=rng.integers(29)
    if x[i]==x[i-1] and rng.random()<.83:
     x[i]=(x[i-1]+rng.integers(1,29))%29
  else:
   for w in p['words']:
    k=w['end']-w['start']; assert k<=29
    x[w['start']:w['end']]=rng.choice(29,size=k,replace=False)
  xs.append(x)
 return xs
# Controls are executed before real evidence; no real-driven tuning.
start=time.monotonic(); controls={}; generated={}
for kind in ['markov','word_urn']:
 controls[kind]=[]
 for rep in range(100):
  xs=generate(kind)
  for p,x in zip(pages,xs): generated[f'{kind}_{rep}_page{p["page"]}']=x
  controls[kind].append(evaluate(xs,999)[0])
np.savez_compressed(BASE/'S01-generated-controls.npz',**generated)
real,tables=evaluate([np.array(p['indices']) for p in pages],9999)
np.savez_compressed(BASE/'S01-offset-tables.npz',**{f'page{p["page"]}':t for p,t in zip(pages,tables)})
result={'seed':SEED,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'pages':[{'page':p['page'],'runes':len(p['indices']),'words':len(p['words'])} for p in pages],'distances':list(range(2,9)),'real_null_draws':9999,'controls_each':100,'control_null_draws_each':999,'control_summary':{k:{'p_le_05':sum(r['p']<=.05 for r in v),'p_le_01':sum(r['p']<=.01 for r in v)} for k,v in controls.items()},'real':real,'controls':controls,'elapsed_seconds':time.monotonic()-start}
(BASE/'S01-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='controls'},indent=2))
