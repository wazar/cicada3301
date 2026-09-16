import pathlib,json,numpy as np,gzip,datetime
R=pathlib.Path(__file__).parent;M=json.load(open(R.parent/'worker-f/F06-maps.json'));rng=np.random.default_rng(2026091734);W=[[w['end']-w['start'] for w in m['words']] for m in M];raw=[np.array(m['indices']) for m in M];ends=[np.cumsum(w)-1 for w in W];starts=[np.r_[0,e[:-1]+1] for e in ends];masks=[np.array(w)>=3 for w in W];total=sum(int(v.sum()) for v in masks)
def stat(vs):return sum(int(np.sum(v[s[mask]]==v[e[mask]])) for v,s,e,mask in zip(vs,starts,ends,masks))
def shifts(vs):
 k=[int(rng.integers(len(v))) for v in vs];return [np.roll(v,j) for v,j in zip(vs,k)],k
def gate():
 assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
controls=[]
for cyclic in [True,False]:
 for rep in range(4):
  vs=[]
  for ww in W:
   flat=[]
   for n in ww:
    word=[]
    for j in range(n):
     banned=set()
     if word:banned.add(word[-1])
     elif flat:banned.add(flat[-1])
     if cyclic and n>=3 and j==n-1:banned.add(word[0])
     allowed=[a for a in range(29) if a not in banned];word.append(int(rng.choice(allowed)))
    flat.extend(word)
   vs.append(np.array(flat))
  score=stat(vs);ns=[stat(shifts(vs)[0]) for _ in range(99)];controls.append(dict(cyclic=cyclic,equal_closures=score,tail=(1+sum(n<=score for n in ns))/100,null=ns,raw=[v.tolist() for v in vs],linear_repeatcount=sum(int(np.sum(v[1:]==v[:-1])) for v in vs)))
assert any(c['tail']<=.05 for c in controls if c['cyclic'])
gate();score=stat(raw);null=[];ss=[]
for rep in range(999):
 if rep%100==0:gate()
 v,k=shifts(raw);null.append(stat(v));ss.append(k)
bylength={}
for vs,ww,s,e in zip(raw,W,starts,ends):
 for n,a,b in zip(ww,s,e):
  if n>=3:
   row=bylength.setdefault(n,dict(units=0,equal=0));row['units']+=1;row['equal']+=int(vs[a]==vs[b])
r=dict(eligible_units=total,equal_closures=score,rate=score/total,tail=(1+sum(n<=score for n in null))/1000,bylength=bylength,null=null,shifts=ss,controls=[{k:v for k,v in c.items() if k!='raw'} for c in controls],real_null_searches=999,control_null_searches=792,seed=2026091734)
with gzip.open(R/'H14-evidence.json.gz','wt') as f:json.dump(dict(controls=controls,raw=[v.tolist() for v in raw]),f)
(R/'H14-result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['null','shifts','controls','bylength']},indent=2));print([(c['cyclic'],c['equal_closures'],c['tail']) for c in controls])
