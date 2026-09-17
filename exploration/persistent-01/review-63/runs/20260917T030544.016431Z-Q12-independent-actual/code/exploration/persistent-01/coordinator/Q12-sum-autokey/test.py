import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import importlib.util,json,gzip,numpy as np,random,itertools,time,sys,datetime,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3];B=R/'exploration/persistent-01';sp=importlib.util.spec_from_file_location('p03',B/'worker-c/p03_frozen.py');p03=importlib.util.module_from_spec(sp);sp.loader.exec_module(p03);lm=p03.LM();L=np.array([lm.step((a,b),c)[1] for a,b,c in itertools.product(range(30),repeat=3)]).reshape(30,30,30);G=[np.arange(29).reshape(29,1,1),np.arange(29).reshape(1,29,1),np.arange(29).reshape(1,1,29)];OFF={}
for k in [2,3,4]:
 a=np.indices((29,)*k,dtype=np.int16).reshape(k,-1).T;OFF[k]=np.column_stack((a,(-a.sum(1))%29)).astype(np.int16)
def guard():assert not (B/'STOP').exists() and datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def decode(c,seed):
 k=len(seed);p=[]
 for i,v in enumerate(c):p.append((v-(seed[i] if i<k else sum(p[i-k:i])))%29)
 return p
def enc(p,seed):
 k=len(seed);return [(v+(seed[i] if i<k else sum(p[i-k:i])))%29 for i,v in enumerate(p)]
def table(q,ends,k):
 W=np.zeros((k+1,29,29,29));context=[-1,-1]
 for i in range(len(q)):
  for v in ([i,-1] if i in ends else [i]):
   refs=context+[v];inds=[29 if j<0 else (q[j]+G[j-i+2])%29 for j in refs];W[i%(k+1)]+=L[tuple(inds)];context=[context[-1],v]
 return W
def scores(W,k):
 e=OFF[k];v=np.zeros(len(e))
 for j in range(k+1):v+=W[j,e[:,(j-2)%(k+1)],e[:,(j-1)%(k+1)],e[:,j]]
 return v
def packet(ix):
 if ix<4:
  path=R/'audit/parallel-01/reference/sources'/('solved_'+p03.CHECK[ix]+'.txt');raw=path.read_text();p,ends=p03.parse(raw);k=[2,3,4,4][ix];rng=random.Random(612100+ix);seed=[rng.randrange(29) for _ in range(k)];attempts=[seed.copy()]
  while len(set(seed))==1:seed=[rng.randrange(29) for _ in range(k)];attempts.append(seed.copy())
  return dict(name='control'+str(ix),cipher=enc(p,seed),ends=sorted(ends),truth=p,k=k,seed=seed,seed_draws=attempts,source=dict(path=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),raw=raw))
 page=next(p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page']==[0,17,55][ix-4]);return dict(name='actual'+str(page['page']),cipher=page['indices'],ends=[w['end']-1 for w in page['words']],source=page)
def null(c,seed):
 rng=random.Random(seed);out=[c[0]]
 for i,v in enumerate(c[1:],1):out.append(out[-1] if v==c[i-1] else rng.choice([a for a in range(29) if a!=out[-1]]))
 return out
def search(data,name=None,cipher=None,null_seed=None):
 guard();name=name or data['name'];path=O/(name+'.json');
 if path.exists():return json.loads(path.read_text())
 c=data['cipher'] if cipher is None else cipher;ends=set(data['ends']);norm=len(c)+len(ends);rows=[];arrays={};alltops=[];t=time.monotonic()
 for k in [2,3,4]:
  q=decode(c,[0]*k);W=table(q,ends,k);v=scores(W,k)/norm;e=OFF[k];order=np.lexsort((np.arange(len(v)),-v))[:16];tops=[]
  for idx in order:
   seed=((-e[idx,:k])%29).tolist();p=decode(c,seed);assert p==[(q[i]+int(e[idx,i%(k+1)]))%29 for i in range(len(c))];sc=lm.score(p,ends);assert abs(sc-float(v[idx]))<1e-11;tops.append(dict(k=k,index=int(idx),seed=seed,offset_period=e[idx].tolist(),score=float(v[idx]),plain=p))
  arrays[f'k{k}_scores']=v;arrays[f'k{k}_factors']=W;arrays[f'k{k}_zero_plain']=np.array(q,dtype=np.uint8);row=dict(k=k,seeds=len(v),top16=tops)
  if cipher is None and 'truth' in data and k==data['k']:
   free=[(-a)%29 for a in data['seed']];idx=int(np.ravel_multi_index(tuple(free),(29,)*k));truthsc=lm.score(data['truth'],ends);assert abs(v[idx]-truthsc)<1e-11
   equal=[dict(seed=[a]*k,score=lm.score(decode(c,[a]*k),ends),errors=sum(x!=y for x,y in zip(decode(c,[a]*k),data['truth']))) for a in range(29)];row['control']=dict(truth_index=idx,truth_score=truthsc,rank_in_correct_k=1+int(np.sum(v>v[idx]+1e-12)),equal_seed_diagnostics=equal)
  rows.append(row);alltops+=tops
 alltops.sort(key=lambda r:(-r['score'],r['k'],r['index']));top=[];seen=set()
 for r in alltops:
  key=tuple(r['plain'])
  if key not in seen:top.append(r);seen.add(key)
  if len(top)==16:break
 out=dict(name=name,cipher=c,ends=sorted(ends),null_seed=null_seed,source=data['source'],rows=rows,global16=top,maximum=top[0]['score'],seeds=732511,seconds=time.monotonic()-t)
 if cipher is None and 'truth' in data:
  out['control']=dict(truth=data['truth'],k=data['k'],seed=data['seed'],seed_draws=data.get('seed_draws'),selected_errors=sum(x!=y for x,y in zip(top[0]['plain'],data['truth'])),truth_score=lm.score(data['truth'],ends),global_seed_rank=1+sum(int(np.sum(arrays[f'k{k}_scores']>lm.score(data['truth'],ends)+1e-12)) for k in [2,3,4]))
 np.savez_compressed(O/(name+'.npz'),**arrays);path.write_text(json.dumps(out,separators=(',',':'))+'\n');print(name,out['maximum'],out['seconds'],flush=True);return out
def pilot():
 rng=random.Random(612000);checks=[]
 for k in [2,3,4]:
  for t in range(20):
   p=[rng.randrange(29) for _ in range(50)];seed=[rng.randrange(29) for _ in range(k)];c=enc(p,seed);q=decode(c,[0]*k);e=[(-s)%29 for s in seed];e+=[-sum(e)%29];assert p==[(q[i]+e[i%(k+1)])%29 for i in range(len(p))];ends={i for i in range(len(p)) if rng.random()<.2};W=table(q,ends,k)
   for z in range(20):
    idx=rng.randrange(29**k);off=OFF[k][idx];v=sum(W[j,off[(j-2)%(k+1)],off[(j-1)%(k+1)],off[j]] for j in range(k+1))/(len(p)+len(ends));d=decode(c,((-off[:k])%29).tolist());assert abs(v-lm.score(d,ends))<1e-11
   checks.append(dict(k=k,plain=p,seed=seed,cipher=c,offset=e,ends=sorted(ends)))
 # Complete 841-seed scalar comparison on one independent tiny packet.
 p=[rng.randrange(29) for _ in range(12)];c=enc(p,[2,7]);ends={3,8,11};q=decode(c,[0,0]);v=scores(table(q,ends,2),2)/15
 for idx,off in enumerate(OFF[2]):assert abs(v[idx]-lm.score(decode(c,((-off[:2])%29).tolist()),ends))<1e-11
 (O/'pilot-checks.json').write_text(json.dumps(dict(random=checks,tiny=dict(cipher=c,ends=sorted(ends)),complete_seed_checks=841),indent=2)+'\n');np.savez_compressed(O/'model.npz',logprob=L);(O/'model.json').write_text(json.dumps(dict(sources=lm.files,train=p03.TRAIN,check=p03.CHECK),indent=2)+'\n');search(packet(0))
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='pilot':pilot()
 elif mode=='controls':
  for i in range(4):search(packet(i))
 elif mode=='actual':
  for i in range(4,7):
   d=packet(i);main=search(d);ns=[]
   for j in range(19):
    seed=612200+100*(i-4)+j;ns.append(search(d,d['name']+f'-null{j:02}',null(d['cipher'],seed),seed))
   (O/(d['name']+'-summary.json')).write_text(json.dumps(dict(main=d['name'],maximum=main['maximum'],nulls=19,tail=(1+sum(r['maximum']>=main['maximum'] for r in ns))/20),indent=2)+'\n')
