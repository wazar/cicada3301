import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,collections,hashlib,itertools,random,time,datetime,sys
B=Path('exploration/persistent-01');O=B/'review-63';Q=B/'coordinator/Q12-sum-autokey';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def guard():assert not (B/'STOP').exists() and datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def parse(raw):
 p=[];ends=[];inside=False
 for char in raw:
  if char in ABC:p.append(ABC.index(char));inside=True
  elif inside:ends.append(len(p)-1);inside=False
 if inside:ends.append(len(p)-1)
 return p,ends
meta=json.loads((Q/'model.json').read_text());counts=[collections.Counter() for _ in range(3)];totals=[collections.Counter() for _ in range(3)]
for row in meta['sources']:
 f=Path(row['path']);assert sha(f)==row['sha256'];p,ends=parse(f.read_text());es=set(ends);tokens=[29,29]+[x for i,r in enumerate(p) for x in ([r,29] if i in es else [r])]
 for i in range(2,len(tokens)):
  for n in range(3):key=tuple(tokens[i-n:i+1]);counts[n][key]+=1;totals[n][key[:-1]]+=1
L=np.empty((30,30,30))
for a,b,x in itertools.product(range(30),repeat=3):
 v=(counts[0][(x,)]+.5)/(totals[0][()]+15)
 for n,alpha in [(1,8),(2,5)]:ctx=(a,b)[-n:];v=(counts[n][ctx+(x,)]+alpha*v)/(totals[n][ctx]+alpha)
 L[a,b,x]=np.log(v)
assert np.max(np.abs(L-np.load(Q/'model.npz')['logprob']))<1e-14

def direct(c,seed):
 p=[]
 for i,x in enumerate(c):
  total=seed[i] if i<len(seed) else sum(p[i-len(seed):i]);p.append((x-total)%29)
 return p

def score(p,ends):
 a=b=29;s=0.;es=set(ends)
 for i,x in enumerate(p):
  s+=L[a,b,x];a,b=b,x
  if i in es:s+=L[a,b,29];a,b=b,29
 return s/(len(p)+len(ends))

def batch_scores(c,ends,k,lo,hi):
 # Independent full forward recurrence. No periodic offsets used to decode.
 ids=np.arange(lo,hi,dtype=np.int64);seed=[(-((ids//29**(k-1-j))%29))%29 for j in range(k)];hist=[None]*k;rolling=np.zeros(hi-lo,dtype=np.int64);sc=np.zeros(hi-lo);a=b=29;es=set(ends)
 for i,x in enumerate(c):
  now=(x-(seed[i] if i<k else rolling))%29
  if i>=k:rolling-=hist[i%k]
  rolling+=now;hist[i%k]=now
  sc+=L[a,b,now];a,b=b,now
  if i in es:sc+=L[a,b,29];a,b=b,29
 return sc/(len(c)+len(ends))

def factors(q,ends,k):
 # Expanded token/reference stream, then assign each token's LM term to its owner rune.
 refs=[None,None];owners=[None,None];es=set(ends)
 for i in range(len(q)):
  refs.append(i);owners.append(i)
  if i in es:refs.append(None);owners.append(i)
 grid=np.indices((29,29,29),dtype=np.int16);W=np.zeros((k+1,29,29,29))
 for j in range(2,len(refs)):
  owner=owners[j];ix=[]
  for r in refs[j-2:j+1]:ix.append(29 if r is None else (q[r]+grid[r-owner+2])%29)
  W[owner%(k+1)]+=L[tuple(ix)]
 return W

def seed_from_index(idx,k):return [-(idx//29**(k-1-j)%29)%29 for j in range(k)]
def panel(name):
 guard();start=time.monotonic();d=json.loads((Q/(name+'.json')).read_text());arr=np.load(Q/(name+'.npz'));c=d['cipher'];ends=d['ends'];out={'name':name,'inputs':[{'path':str(Q/(name+ext)),'sha256':sha(Q/(name+ext))} for ext in ['.json','.npz']],'rune_count':len(c),'checks':[]};tops=[]
 for row in d['rows']:
  k=row['k'];q=direct(c,[0]*k);assert q==arr[f'k{k}_zero_plain'].tolist();wf=factors(q,ends,k);ferr=float(np.max(np.abs(wf-arr[f'k{k}_factors'])));assert ferr<1e-10
  saved=arr[f'k{k}_scores'];own=np.empty(29**k);err=0
  for lo in range(0,len(own),32768):
   guard();hi=min(lo+32768,len(own));v=batch_scores(c,ends,k,lo,hi);own[lo:hi]=v;err=max(err,float(np.max(np.abs(v-saved[lo:hi]))))
  assert err<1e-10;assert len(saved)==29**k;order=np.lexsort((np.arange(len(saved)),-saved))[:16];assert [r['index'] for r in row['top16']]==order.tolist()
  for r in row['top16']:
   seed=seed_from_index(r['index'],k);p=direct(c,seed);assert seed==r['seed'] and p==r['plain'];assert r['offset_period']==[(-a)%29 for a in seed]+[sum(seed)%29];assert abs(score(p,ends)-r['score'])<1e-10;assert [ (x+(seed[i] if i<k else sum(p[i-k:i])))%29 for i,x in enumerate(p)]==c;tops.append(r)
  # Maximum independently attained; ties checked within floating tolerance.
  assert abs(float(own.max())-row['top16'][0]['score'])<1e-10
  if 'control' in row:
   t=row['control'];truth=d['control']['truth'];assert direct(c,d['control']['seed'])==truth;assert t['truth_index']==sum((-a)%29*29**(k-1-j) for j,a in enumerate(d['control']['seed']));assert abs(score(truth,ends)-t['truth_score'])<1e-10;assert t['rank_in_correct_k']==1+int(np.sum(saved>saved[t['truth_index']]+1e-12))
   for eq in t['equal_seed_diagnostics']:
    p=direct(c,eq['seed']);assert abs(score(p,ends)-eq['score'])<1e-10 and sum(a!=b for a,b in zip(p,truth))==eq['errors']
  out['checks'].append({'k':k,'all_seed_scores':len(own),'maximum':float(own.max()),'max_score_error':err,'max_factor_error':ferr,'score_sha256':hashlib.sha256(own.tobytes()).hexdigest()})
 tops.sort(key=lambda r:(-r['score'],r['k'],r['index']));unique=[];seen=set()
 for r in tops:
  key=tuple(r['plain'])
  if key not in seen:unique.append(r);seen.add(key)
  if len(unique)==16:break
 assert unique==d['global16'] and d['maximum']==unique[0]['score'] and d['seeds']==732511
 if 'control' in d:
  ctl=d['control'];source=Path(d['source']['path']);assert sha(source)==d['source']['sha256'];p,e=parse(source.read_text());assert p==ctl['truth'] and e==ends;ix=int(name[-1]);rng=random.Random(612100+ix);assert ctl['seed']==[rng.randrange(29) for _ in range([2,3,4,4][ix])];assert ctl['selected_errors']==sum(a!=b for a,b in zip(unique[0]['plain'],p));assert ctl['global_seed_rank']==1+sum(int(np.sum(arr[f'k{k}_scores']>score(p,ends)+1e-12)) for k in [2,3,4]);out['control']=ctl
 else:
  pg=int(name.split('-')[0].replace('actual',''));source=next(p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page']==pg);assert source==d['source'];assert ends==[w['end']-1 for w in source['words']]
  if '-null' not in name:assert c==source['indices']
  else:
   j=int(name[-2:]);seed=612200+100*[0,17,55].index(pg)+j;assert d['null_seed']==seed;orig=source['indices'];rng=random.Random(seed);expected=[orig[0]]
   for i in range(1,len(orig)):expected.append(expected[-1] if orig[i]==orig[i-1] else rng.choice([r for r in range(29) if r!=expected[-1]]))
   assert c==expected and c[0]==orig[0];assert [a==b for a,b in zip(c,c[1:])]==[a==b for a,b in zip(orig,orig[1:])]
 out['maximum']=d['maximum'];out['seconds']=time.monotonic()-start;(O/(name+'-review.json')).write_text(json.dumps(out,indent=2));print(json.dumps({'name':name,'seconds':out['seconds'],'maximum':out['maximum'],'score_max_error':max(r['max_score_error'] for r in out['checks'])}),flush=True)

def tiny():
 raw=json.loads((Q/'pilot-checks.json').read_text());count=0
 for case in raw['random']:
  k=case['k'];assert direct(case['cipher'],case['seed'])==case['plain'];q=direct(case['cipher'],[0]*k);e=[(p-r)%29 for p,r in zip(case['plain'],q)];assert e==[case['offset'][i%(k+1)] for i in range(len(e))] and sum(case['offset'])%29==0
 case=raw['tiny'];c=case['cipher'];ends=case['ends'];v=batch_scores(c,ends,2,0,841)
 for idx in range(841):assert abs(score(direct(c,seed_from_index(idx,2)),ends)-v[idx])<1e-12;count+=1
 # Fresh finite fixtures: every 29^2 seed, random ciphertext and all/no/irregular boundary patterns.
 rng=random.Random(632000)
 for n in [2,3,8,13]:
  c=[rng.randrange(29) for _ in range(n)]
  for ends in [[],list(range(n)),[i for i in range(n) if i%3==1]]:
   v=batch_scores(c,ends,2,0,841)
   for idx in range(841):assert abs(score(direct(c,seed_from_index(idx,2)),ends)-v[idx])<1e-12;count+=1
 # Fresh arbitrary-seed periodic identities, including short lengths and k3/4.
 for k in [2,3,4]:
  for n in [k,k+1,2*k+5]:
   for rep in range(20):
    c=[rng.randrange(29) for _ in range(n)];seed=[rng.randrange(29) for _ in range(k)];p=direct(c,seed);q=direct(c,[0]*k);e=[(-a)%29 for a in seed]+[sum(seed)%29];assert p==[(v+e[i%(k+1)])%29 for i,v in enumerate(q)]
 result={'scalar_seed_score_checks':count,'fresh_periodic_fixtures':180,'root_random_fixtures':len(raw['random']),'lm_cells':27000,'model_max_error':float(np.max(np.abs(L-np.load(Q/'model.npz')['logprob'])))};(O/'tiny.json').write_text(json.dumps(result,indent=2));print(result)
if sys.argv[1]=='pilot':tiny();panel('control0')
elif sys.argv[1]=='panel':panel(sys.argv[2])
elif sys.argv[1]=='all':
 for name in ['control'+str(i) for i in range(4)]+[s for pg in [0,17,55] for s in ['actual'+str(pg)]+['actual'+str(pg)+f'-null{j:02}' for j in range(19)]]:
  if (O/(name+'-review.json')).exists():continue
  panel(name)
