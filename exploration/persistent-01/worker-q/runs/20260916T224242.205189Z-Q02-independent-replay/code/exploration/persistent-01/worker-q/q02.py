import pathlib,json,gzip,itertools,datetime,hashlib
import numpy as np
R=pathlib.Path(__file__).parent;src=pathlib.Path('exploration/persistent-01/worker-f/F10-evidence.json.gz');regions=json.load(gzip.open(src,'rt'))['regions'];units=[[v for w in r['units'] for v in w] for r in regions];assert list(map(len,units))==[139,91,98,96,129]
bodies=np.zeros((28,5),dtype=np.int64)
for a in range(1,29):
 for j,u in enumerate(units):
  s=0
  for x in u[:-1]:s=(a*s+x)%29
  bodies[a-1,j]=a*s%29
  assert bodies[a-1,j]==sum(x*pow(a,len(u)-i-1,29) for i,x in enumerate(u[:-1]))%29
perms=list(itertools.permutations(range(5)))
def fit(t):
 v=(bodies+t)%29
 tr=np.array([np.bincount(x[:3],minlength=29) for x in v]);he=np.array([np.bincount(x[3:],minlength=29) for x in v]);ai,b=np.unravel_index(np.argmax(tr),tr.shape)
 return {'a':int(ai+1),'b':int(b),'train_hits':int(tr[ai,b]),'held_hits':int(he[ai,b]),'predictions':((b-bodies[ai,3:])%29).tolist(),'truth':list(map(int,t[3:])),'training_matrix':tr.tolist(),'held_matrix':he.tolist()}
def run(t):
 out=[]
 for perm in perms:
  assert not (R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
  out.append(fit(t[list(perm)]))
 scores=[x['held_hits'] for x in out];return {'terminals':t.tolist(),'fits':out,'observed':out[0],'tail':sum(x>=scores[0] for x in scores)/120,'score_histogram':[scores.count(x) for x in range(3)],'minimum_attainable_tail':sum(x>=max(scores) for x in scores)/120,'permutation_tails':[sum(x>=s for x in scores)/120 for s in scores]}
controls=[]
for a in [1,2,7,28]:
 b=(a+3)%29;t=(b-bodies[a-1])%29;assert np.all((bodies[a-1]+t)%29==b)
 z=run(t);z['plant']={'a':a,'b':b};controls.append(z)
real=run(np.array([u[-1] for u in units]));e={'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'regions':regions,'bodies':bodies.tolist(),'permutations':perms,'controls':controls,'real':real,'fits':600}
with gzip.open(R/'Q02-evidence.json.gz','wt') as f:json.dump(e,f)
def summary(z):return {k:({a:b for a,b in v.items() if not a.endswith('_matrix')} if k=='observed' else v) for k,v in z.items() if k not in ['fits','permutation_tails']}
s={'controls':[summary(z) for z in controls],'real':summary(real),'fits':600};(R/'Q02-result.json').write_text(json.dumps(s,indent=2));print(json.dumps(s))
