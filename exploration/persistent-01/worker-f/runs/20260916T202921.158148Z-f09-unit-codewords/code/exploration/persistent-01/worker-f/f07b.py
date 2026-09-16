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

controls=[]
for mi,m in enumerate(maps):
 for typ in ['biased','markov']:
  cp=[];targets=[];attempts=0;resets=0;last=None
  for x,ls in ps:
   words=[];page_targets=[]
   for length in ls:
    target=int(rng.choice(29,p=np.arange(29,0,-1)/435)) if typ=='biased' else ((last+1)%29 if last is not None and rng.random()<.7 else int(rng.integers(29)))
    if length==1 and target not in set(m%29):
     source=int(rng.choice(29,p=np.arange(29,0,-1)/435)) if typ=='biased' else int(rng.integers(29));target=int(m[source]%29);resets+=1
    for attempt in range(1000):
     pre=rng.integers(29,size=int(length)-1);need=(target-sum(m[pre]))%29;cand=np.flatnonzero(m%29==need);attempts+=1
     if len(cand):words.extend([*pre,int(rng.choice(cand))]);break
    else:raise RuntimeError('bounded rejection failed')
    page_targets.append(target);last=target
   cp.append((np.array(words),ls));targets.append(page_targets)
  decoded=decode(cp,m)
  assert all(np.array_equal(a,b) for a,b in zip(decoded,targets))
  t=trial(cp,199);t.update(map=mi,type=typ,encoded=[x.tolist() for x,l in cp],target=targets,attempts=attempts,forced_target_resets=resets);controls.append(t)
symmetry=[]
for mm,(x,ls) in zip(M,ps):
 mask=np.zeros(len(x),bool);mask[np.r_[0,np.cumsum(ls)[:-1]]]=True;preserved=[i for i in range(len(x)) if np.array_equal(mask,np.roll(mask,i))];symmetry.append({'page':mm['page'],'runes':len(x),'stabilizer_offsets':preserved,'distinct_phases':len(x)//len(preserved)})
result={'controls':[{k:v for k,v in t.items() if k not in ['null','offsets','encoded','target']} for t in controls],'symmetry':symmetry,'constant4_fixture_distinct_phases':4,'counts':{'controls':4,'control_null':796,'real':0}}
with gzip.open(R/'F07b-evidence.json.gz','wt') as f:json.dump({'controls':controls},f)
(R/'F07b-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
