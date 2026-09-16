import pathlib,json,numpy as np,datetime,gzip
R=pathlib.Path(__file__).parent;rng=np.random.default_rng(2026091732);M=json.load(open(R.parent/'worker-f/F06-maps.json'));W=[[m['indices'][w['start']:w['end']] for w in m['words']] for m in M]
def prime(n):return n>=2 and all(n%d for d in range(2,int(n**.5)+1))
masks=[np.array([prime(i+1) for i in range(len(ws))]) for ws in W]
def orders(shifts):
 out=[]
 for m,k in zip(masks,shifts):
  mask=np.roll(m,k);p=np.r_[np.flatnonzero(mask),np.flatnonzero(~mask)];out.append((p,np.argsort(p)))
 return out
def stat(words,shift):
 oo=orders(shift);gg=[]
 for direction in [0,1]:
  pairs=[]
  for ws,pp in zip(words,oo):
   p=pp[direction];pairs.extend(ws[a][-1]*29+ws[b][0] for a,b in zip(p,p[1:]))
  t=np.bincount(pairs,minlength=841).reshape(29,29);e=np.outer(t.sum(1),t.sum(0))/t.sum();valid=t>0;gg.append(float(2*np.sum(t[valid]*np.log(t[valid]/e[valid]))))
 return max(gg),gg
def shifts():return [int(rng.integers(len(w))) for w in W]
def gate():
 assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
OO=orders([0]*len(W));controls=[]
for direction in [0,1]:
 for rep in range(2):
  raw=[];truth=[]
  for ws,oo in zip(W,OO):
   p=oo[direction];ordered=[];previous=None
   for i in p:
    n=len(ws[i]);first=int((previous+1)%29 if previous is not None and rng.random()<.85 else rng.integers(29));w=[first]
    for j in range(1,n):
     nxt=int(rng.integers(28));w.append(nxt+(nxt>=w[-1]))
    previous=w[-1];ordered.append(w)
   rr=[None]*len(ws)
   for i,w in zip(p,ordered):rr[i]=w
   assert [rr[i] for i in p]==ordered;raw.append(rr);truth.append(ordered)
  best,gg=stat(raw,[0]*len(W));null=[];ss=[]
  for k in range(99):s=shifts();ss.append(s);null.append(stat(raw,s)[0])
  controls.append(dict(direction=direction,score=best,scores=gg,tail=(1+sum(x>=best for x in null))/100,null=null,shifts=ss,raw=raw,truth=truth))
assert any(c['tail']<=.05 for c in controls)
gate();best,gg=stat(W,[0]*len(W));null=[];rawstats=[];ss=[]
for rep in range(999):
 if rep%100==0:gate()
 s=shifts();ss.append(s);b,g=stat(W,s);null.append(b);rawstats.append(g)
r=dict(scores=gg,score=best,tail=(1+sum(x>=best for x in null))/1000,controls=[{k:v for k,v in c.items() if k not in ['raw','truth','null','shifts']} for c in controls],pages=len(W),units=sum(map(len,W)),operators=2,real_null_searches=999,control_null_searches=396,seed=2026091732)
with gzip.open(R/'H12-evidence.json.gz','wt') as f:json.dump(dict(null=null,rawstats=rawstats,shifts=ss,controls=controls,real_words=W,orders=[[p.tolist() for p in oo] for oo in OO]),f)
(R/'H12-result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))
