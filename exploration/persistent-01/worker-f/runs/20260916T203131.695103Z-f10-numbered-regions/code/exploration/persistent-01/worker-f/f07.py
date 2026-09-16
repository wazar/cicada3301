import pathlib,json,numpy as np,gzip,datetime
R=pathlib.Path(__file__).parent;M=json.load(open(R/'F06-maps.json'));rng=np.random.default_rng(2026091717);P=np.array([x for x in range(2,110) if all(x%d for d in range(2,int(x**.5)+1))]);maps=[np.arange(29),P];ps=[(np.array(m['indices']),np.array([w['end']-w['start'] for w in m['words']])) for m in M]
def decode(ps,m):return [np.add.reduceat(m[x],np.r_[0,np.cumsum(ls)[:-1]])%29 for x,ls in ps]
def stats(seq):
 x=np.concatenate(seq);f=np.bincount(x,minlength=29);chi=float(np.sum((f-len(x)/29)**2/(len(x)/29)));j=np.zeros((29,29))
 for s in seq:j+=np.bincount(s[:-1]*29+s[1:],minlength=841).reshape(29,29)
 j/=j.sum();e=j.sum(0)[None,:]*j.sum(1)[:,None];ok=j>0;return [chi,float(np.sum(j[ok]*np.log(j[ok]/e[ok])))]
def scan(ps):return np.array([v for m in maps for v in stats(decode(ps,m))])
def trial(ps,n):
 real=scan(ps);null=[];offsets=[]
 for rep in range(n):
  if rep%100==0:assert not (R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
  off=[int(rng.integers(len(x))) for x,l in ps];offsets.append(off);null.append(scan([(np.roll(x,-o),l) for (x,l),o in zip(ps,off)]))
 null=np.array(null);tails=(1+(null>=real).sum(0))/(n+1);return {'real':real.tolist(),'null':null.tolist(),'offsets':offsets,'tails':tails.tolist(),'bonferroni4':np.minimum(1,4*tails).tolist()}
real=trial(ps,999);controls=[]
for mi,m in enumerate(maps):
 for typ in ['biased','markov']:
  target=[];words=[];attempts=0
  for i in range(2000):
   t=int(rng.choice(29,p=np.arange(29,0,-1)/435)) if typ=='biased' else ((target[-1]+1)%29 if i and rng.random()<.7 else int(rng.integers(29)));target.append(t)
   while True:
    pre=rng.integers(29,size=3);need=(t-sum(m[pre]))%29;cand=np.flatnonzero(m%29==need);attempts+=1
    if len(cand):words.append([*pre,int(rng.choice(cand))]);break
  cp=[(np.array(words).ravel(),np.full(2000,4))];out=decode(cp,m)[0];assert np.array_equal(out,target);t=trial(cp,100);t.update(type=typ,map=mi,encoded=cp[0][0].tolist(),target=target,attempts=attempts);controls.append(t)
baseline=[]
for rep in range(8):
 cp=[]
 for x,l in ps:
  y=[int(rng.integers(29))]
  for i in range(1,len(x)):
   z=int(rng.integers(28));y.append(z+(z>=y[-1]))
  cp.append((np.array(y),l))
 t=trial(cp,199);t.update(streams=[x.tolist() for x,l in cp]);baseline.append(t)
def strip(t):return {k:v for k,v in t.items() if k not in ['null','offsets','encoded','target','streams']}
res={'real':strip(real),'controls':[strip(t) for t in controls],'baseline':[strip(t) for t in baseline],'baseline_detections':sum(min(t['bonferroni4'])<=.05 for t in baseline),'counts':{'real':1,'real_null':999,'strong_controls':4,'strong_control_null':400,'baseline':8,'baseline_null':1592},'seed':2026091717}
with gzip.open(R/'F07-evidence.json.gz','wt') as f:json.dump({'real':real,'controls':controls,'baseline':baseline,'real_outputs':[[s.tolist() for s in decode(ps,m)] for m in maps]},f)
(R/'F07-result.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
