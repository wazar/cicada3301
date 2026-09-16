import json,pathlib,numpy as np,datetime
R=pathlib.Path(__file__).parent;rng=np.random.default_rng(2026091725);M=json.load(open(R.parent/'worker-f/F06-maps.json'));x=[np.array([w['end']-w['start'] for w in m['words']]) for m in M];starts=np.cumsum([0]+[len(z) for z in x]);ii=np.concatenate([np.arange(starts[j],starts[j+1]-1) for j in range(len(x))]);a=np.concatenate(x)
def g(v):
 z=np.minimum(v,8)-1;t=np.bincount(z[ii]*8+z[ii+1],minlength=64).reshape(8,8);e=np.outer(t.sum(1),t.sum(0))/t.sum();mask=t>0;return float(2*np.sum(t[mask]*np.log(t[mask]/e[mask])))
def sh(v):return np.concatenate([rng.permutation(v[starts[j]:starts[j+1]]) for j in range(len(x))])
controls=[]
for rep in range(4):
 c=np.concatenate([np.concatenate([rng.permutation(z[z%2==0]),rng.permutation(z[z%2==1])]) for z in x]);score=g(c);null=[g(sh(c)) for _ in range(99)];controls.append(dict(score=score,null=null,tail=(1+sum(n>=score for n in null))/100))
assert any(c['tail']<=.05 for c in controls)
score=g(a);null=[]
for rep in range(1999):
 if rep%100==0:
  assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
 null.append(g(sh(a)))
r=dict(score=score,tail=(1+sum(n>=score for n in null))/2000,null=null,controls=controls,seed=2026091725,real_searches=1,real_null_searches=1999,control_searches=4,control_null_searches=396);(R/'H05-result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['null','controls']}));print([(c['score'],c['tail']) for c in controls])
