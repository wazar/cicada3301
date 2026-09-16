import pathlib,json,random,itertools,collections,math,gzip,datetime
import numpy as np
O=pathlib.Path(__file__).resolve().parent;rng=np.random.default_rng(33010202)
def check():
 assert not (O.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
def cost(n,k):
 q,r=divmod(int(n),k);return (k-r)*q*(q-1)//2+r*q*(q+1)//2
def bound(counts,slots=29,allocation=False):
 counts=[int(n) for n in counts if n];extra=slots-len(counts);assert extra>=0
 dp=[0]+[10**15]*extra;paths=[[] for _ in dp]
 for n in counts:
  nd=[];npth=[]
  for e in range(extra+1):
   z,t=min((dp[e-t]+cost(n,1+t),t) for t in range(e+1));nd.append(z);npth.append(paths[e-t]+[1+t])
  dp,paths=nd,npth
 return (dp[-1],paths[-1]) if allocation else dp[-1]
def pairs(c):return sum(n*(n-1)//2 for n in collections.Counter(c).values())
check();controls=[]
for _ in range(100):
 m=int(rng.integers(1,6));slots=int(rng.integers(m,m+5));c=rng.integers(1,16,m).tolist();brute=min(sum(cost(n,k) for n,k in zip(c,ks)) for ks in itertools.product(range(1,slots+1),repeat=m) if sum(ks)==slots);v,ks=bound(c,slots,True);assert v==brute
 cipher=[];truth=[];codebook={};offset=0
 for i,(n,k) in enumerate(zip(c,ks)):
  codebook.update({offset+j:i for j in range(k)});cipher.extend(offset+j%k for j in range(n));truth.extend([i]*n);offset+=k
 assert pairs(cipher)==v and [codebook[x] for x in cipher]==truth
 controls.append({'counts':c,'slots':slots,'allocation':ks,'bound':v,'brute':brute,'cipher':cipher,'truth':truth})
D=json.loads((O/'j01-results.json').read_text());texts=[c for c in D['controls'] if c['mode']=='original'];pages=D['real'];lens=[len(p['cipher']) for p in pages];actual=[pairs(p['cipher']) for p in pages];total=sum(actual)
profiles=[]
for name,sub in [('train5',texts[:5]),('held4',texts[5:])]:
 counts=np.bincount(sum([c['source'] for c in sub],[]),minlength=29);profiles.append({'name':name,'counts':counts.tolist(),'probabilities':(counts/counts.sum()).tolist(),'groups':[c['name'] for c in sub]})
windows=[]
for n in lens:
 row=[]
 for text in texts:
  if len(text['source'])<max(lens):continue
  s=text['source']
  for start in range(len(s)-n+1):
   c=np.bincount(s[start:start+n],minlength=29).tolist();row.append({'group':text['name'],'start':start,'counts':c,'bound':bound(c)})
 windows.append(row)
with gzip.open(O/'j02-windows.json.gz','wt') as f:json.dump({'lengths':lens,'windows':windows},f)
records=[];summaries=[]
with gzip.open(O/'j02-sampling.jsonl.gz','wt') as f:
 for profile in profiles+[{'name':'contiguous_windows'}]:
  vals=[];pagevals=[[] for _ in lens]
  for i in range(9999):
   if i%200==0:check()
   cts=[];bs=[];refs=[]
   for j,n in enumerate(lens):
    if profile['name']=='contiguous_windows':
     idx=int(rng.integers(len(windows[j])));w=windows[j][idx];c=w['counts'];b=w['bound'];refs.append(idx)
    else:c=rng.multinomial(n,profile['probabilities']).tolist();b=bound(c)
    cts.append(c);bs.append(b);pagevals[j].append(b)
   v=sum(bs);vals.append(v);f.write(json.dumps({'model':profile['name'],'replicate':i,'counts':cts,'bounds':bs,'total':v,'window_indices':refs})+'\n')
  hits=sum(v<=total for v in vals);summaries.append({'model':profile['name'],'n':9999,'compatible_bound_count':hits,'compatibility_fraction':hits/9999,'total_bound_quantiles':np.quantile(vals,[0,.01,.05,.5,.95,.99,1]).tolist(),'actual_total':total,'page_compatibility_fractions':[sum(v<=a for v in vs)/9999 for a,vs in zip(actual,pagevals)]})
result={'seed':33010202,'controls':controls,'profiles':profiles,'actual':[{'page':p['page'],'n':len(p['cipher']),'pairs':a,'sorted_counts':sorted(collections.Counter(p['cipher']).values(),reverse=True)} for p,a in zip(pages,actual)],'summaries':summaries,'n_dp_controls':100,'draws':3*9999,'page_draws':3*9999*5}
(O/'j02-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['controls','profiles']}))
