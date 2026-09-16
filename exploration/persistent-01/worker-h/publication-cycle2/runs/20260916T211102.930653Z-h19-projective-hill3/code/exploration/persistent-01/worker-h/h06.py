import json,pathlib,numpy as np,datetime
R=pathlib.Path(__file__).parent;rng=np.random.default_rng(2026091726);M=json.load(open(R.parent/'worker-f/F06-maps.json'));x=[np.array([{'hyphen':0,'period':1}.get(g['type'],-1) for g in m['gaps']]) for m in M]
starts=np.cumsum([0]+[len(z) for z in x]);a=np.concatenate(x);ii=np.concatenate([np.arange(starts[j],starts[j+1]-1) for j in range(len(x))]);ii=ii[(a[ii]>=0)&(a[ii+1]>=0)];slots=[np.arange(starts[j],starts[j+1])[z>=0] for j,z in enumerate(x)]
def g(v):
 t=np.bincount(v[ii]*2+v[ii+1],minlength=4).reshape(2,2);e=np.outer(t.sum(1),t.sum(0))/t.sum();mask=t>0;return float(2*np.sum(t[mask]*np.log(t[mask]/e[mask]))),t.tolist()
def sh(v):
 u=v.copy()
 for s in slots:u[s]=rng.permutation(v[s])
 return u
controls=[]
for rep in range(4):
 c=a.copy()
 for s in slots:
  if len(s):c[s]=np.roll(np.sort(c[s]),int(rng.integers(len(s))))
 score,table=g(c);null=[g(sh(c))[0] for _ in range(99)];controls.append(dict(score=score,null=null,tail=(1+sum(n>=score for n in null))/100))
assert any(c['tail']<=.05 for c in controls)
score,table=g(a);null=[]
for rep in range(1999):
 if rep%100==0:
  assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
 null.append(g(sh(a))[0])
r=dict(score=score,table=table,tail=(1+sum(n>=score for n in null))/2000,null=null,controls=controls,seed=2026091726,pairs=len(ii),eligible_slots=sum(len(s) for s in slots),null_searches=1999,control_null_searches=396);(R/'H06-result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['null','controls']}))
