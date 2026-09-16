import json,pathlib,numpy as np,datetime
R=pathlib.Path(__file__).parent;rng=np.random.default_rng(2026091727);M=json.load(open(R.parent/'worker-f/F06-maps.json'));assert all(g['type'] in ['hyphen','period'] for m in M for g in m['gaps']);x=[np.array([g['type']=='period' for g in m['gaps']],dtype=int) for m in M];attempts=0
def adjacent(v):return int(np.sum(v[:-1]*v[1:]))
def stat(vs):
 d=np.concatenate([np.diff(np.flatnonzero(v)) for v in vs]);return -float(d.var()/d.mean()**2)
def draw(vs):
 global attempts
 out=[]
 for v in vs:
  target=adjacent(v)
  for j in range(100000):
   attempts+=1;u=rng.permutation(v)
   if adjacent(u)==target:out.append(u);break
  else:raise RuntimeError('conditional rejection limit')
 return out
controls=[]
for phase in [.1,.3,.5,.7]:
 cc=[]
 for v in x:
  n=len(v);k=int(v.sum());u=np.zeros(n,dtype=int)
  if k:u[np.floor((np.arange(k)+phase)*n/k).astype(int)]=1
  assert u.sum()==k;cc.append(u)
 s=stat(cc);ns=[stat(draw(cc)) for _ in range(99)];controls.append(dict(phase=phase,score=s,null=ns,tail=(1+sum(n>=s for n in ns))/100))
assert any(c['tail']<=.05 for c in controls)
s=stat(x);null=[]
for rep in range(999):
 if rep%50==0:
  assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
 null.append(stat(draw(x)))
r=dict(score=s,tail=(1+sum(n>=s for n in null))/1000,null=null,controls=controls,seed=2026091727,proposal_attempts=attempts,real_null_searches=999,control_null_searches=396);(R/'H07-result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['null','controls']}));print([(c['phase'],c['tail']) for c in controls])
