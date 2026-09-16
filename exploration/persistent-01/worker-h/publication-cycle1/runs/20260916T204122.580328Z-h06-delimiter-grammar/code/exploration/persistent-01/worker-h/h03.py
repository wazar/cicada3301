import pathlib,json,numpy as np,gzip,datetime
R=pathlib.Path(__file__).parent;rng=np.random.default_rng(2026091723)
M=json.load(open(R.parent/'worker-f/F06-maps.json'));x=[np.array([w['end']-w['start'] for w in m['words']],dtype=float) for m in M]
def gate():
 assert not(R.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
# Flatten while retaining per-page centered values and legal withinpage pairs.
a=np.concatenate([v-v.mean() for v in x]);starts=np.cumsum([0]+[len(v) for v in x]);pairs=[]
for k in range(1,9):
 ii=np.concatenate([np.arange(starts[j],starts[j+1]-k) for j in range(len(x)) if len(x[j])>k]);pairs.append((ii,ii+k))
def stat(v):
 c=[float(np.dot(v[i],v[j])/np.sqrt(np.dot(v[i],v[i])*np.dot(v[j],v[j]))) for i,j in pairs];return max(map(abs,c)),c
def perm(v):
 p=np.concatenate([rng.permutation(np.arange(starts[j],starts[j+1])) for j in range(len(x))]);return v[p],p
controls=[]
for mode in range(4):
 parts=[]
 for v in x:
  s=np.sort(v-v.mean());n=len(s)
  if mode==1:s=s[::-1]
  if mode==2:
   order=[];lo=0;hi=n-1
   while lo<=hi:
    order.append(lo);lo+=1
    if lo<=hi:order.append(hi);hi-=1
   s=s[order]
  if mode==3:
   z=np.empty_like(s);cursor=0
   for phase in range(4):count=len(z[phase::4]);z[phase::4]=s[cursor:cursor+count];cursor+=count
   s=z
  parts.append(s)
 v=np.concatenate(parts);score,corr=stat(v);ns=[stat(perm(v)[0])[0] for _ in range(99)];controls.append(dict(mode=mode,score=score,correlations=corr,null=ns,tail=(1+sum(n>=score for n in ns))/100))
assert any(c['tail']<=.05 for c in controls)
score,corr=stat(a);null=[];pp=[]
for rep in range(9999):
 if rep%200==0:gate()
 v,p=perm(a);null.append(stat(v)[0]);pp.append(p.tolist())
r=dict(score=score,correlations=corr,tail=(1+sum(n>=score for n in null))/10000,controls=controls,pages=len(x),units=len(a),pairs_per_lag=[len(i) for i,j in pairs],null_searches=9999,control_null_searches=396,seed=2026091723)
with gzip.open(R/'H03-evidence.json.gz','wt') as f:json.dump(dict(null=null,permutations=pp,lengths=[v.tolist() for v in x]),f)
(R/'H03-result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='controls'}))
