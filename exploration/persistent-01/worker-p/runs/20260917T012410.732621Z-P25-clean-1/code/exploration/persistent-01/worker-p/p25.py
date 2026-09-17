import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,gzip,random,hashlib,datetime,time,sys,importlib.util,itertools
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'exploration/persistent-01';P=B/'worker-p/P25';Q=B/'coordinator/Q05-latin'
spec=importlib.util.spec_from_file_location('p03',B/'worker-c/p03_frozen.py');p03=importlib.util.module_from_spec(spec);spec.loader.exec_module(p03)
TRANS=[r['transliteration'] for r in json.loads((ROOT/'KNOWLEDGE.json').read_text())['gematria_primus']['table']]
def guard():
 assert not (B/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(n,x):
 b=json.dumps(x,separators=(',',':'),allow_nan=False).encode()
 if n.endswith('.gz'):
  with gzip.open(P/n,'wb') as f:f.write(b)
 else:(P/n).write_bytes(b+b'\n')
def load(n):
 with gzip.open(n,'rt') as f:return json.load(f)
class LM:
 def __init__(self):
  assert hashlib.sha256((Q/'model.npz').read_bytes()).hexdigest()=='16f491d53007cc4492d1bb94b42fed16aca136bca0f62ba7ebe1b8ba769c3b93'
  self.logp=np.load(Q/'model.npz')['logp'].tolist()
 def step(self,s,x):return (s[-1],x),self.logp[s[0]][s[1]][x]
 def extend(self,s,r,end):
  s,v=self.step(s,r)
  if end:s,z=self.step(s,29);v+=z
  return s,v
 def score(self,plain,ends):
  s=(29,29);score=0
  for i,v in enumerate(plain):s,z=self.extend(s,v,i in ends);score+=z
  return score/(len(plain)+len(ends))
def cells():return p03.cells(16,True)
def reencrypt(plain,literal,key,sign):
 literal=set(literal);c=[];u=0
 for i,v in enumerate(plain):
  if i in literal:assert v==0;c.append(0)
  else:c.append((v-sign*key[u%len(key)])%29);u+=1
 return c,u
def packet(ix):
 if ix<4:
  control=load(Q/'held-controls.json.gz')[ix];p=control['indices'];ends=set(control['ends']);ki=[0,5,10,15][ix];phase=ix;sign=[-1,1,-1,1][ix];id=f'clue:{ki:03}:{phase}:{sign}'
  cell=next(x for x in cells() if x['id']==id);literal=[i for i,v in enumerate(p) if v==0 and i%3!=1];c,u=reencrypt(p,literal,cell['key'],sign)
  return dict(packet=ix,name=control['id'],cipher=c,ends=sorted(ends),truth=p,truth_literal=literal,truth_id=id,truth_used=u,source=control)
 pageid=[0,17,55][ix-4];page=next(p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page']==pageid)
 return dict(packet=ix,name='original'+str(pageid),cipher=page['indices'],ends=[w['end']-1 for w in page['words']],source=page)
def null(c,seed):
 rng=random.Random(seed);s=[0 if c[0]==0 else rng.randrange(1,29)]
 for i in range(1,len(c)):
  if c[i]==0:s.append(0)
  elif c[i]==c[i-1]:s.append(s[-1])
  else:s.append(rng.choice([j for j in range(1,29) if j!=s[-1]]))
 assert [v==0 for v in s]==[v==0 for v in c] and [a==b for a,b in zip(s,s[1:])]==[a==b for a,b in zip(c,c[1:])]
 return s
def search(name,data,c=None,seed=None):
 guard();file=P/(name+'.json.gz')
 if file.exists():return load(file)
 lm=LM();cs=cells();cipher=data['cipher'] if c is None else c;ends=set(data['ends']);truth=data.get('truth_literal') if c is None else None;t=time.monotonic();rows=[];alts=[]
 for j,cell in enumerate(cs):
  if j%32==0:guard()
  r,d=p03.beam(cipher,ends,cell['key'],cell['sign'],lm,width=64,truth=truth if cell['id']==data.get('truth_id') else None)
  for z in r:
   assert reencrypt(z['plain'],z['literal_positions'],cell['key'],cell['sign'])==(cipher,z['used'])
   alts.append(dict(id=cell['id'],**z))
  rows.append(dict(id=cell['id'],top_score=r[0]['score'],alternatives=r,diagnostics=d))
 alts.sort(key=lambda x:x['score'],reverse=True);global16=[];seen={}
 for z in alts:
  k=(tuple(z['plain']),tuple(z['literal_positions']))
  if k not in seen:
   if len(global16)>=16:continue
   obj=dict(**z,aliases=[]);seen[k]=obj;global16.append(obj)
  if k in seen:seen[k]['aliases'].append(z['id'])
 result=dict(name=name,packet=data['packet'],cipher=cipher,ends=sorted(ends),null_seed=seed,cells=rows,global16=global16,maximum=alts[0]['score'],seconds=time.monotonic()-t)
 if truth is not None:
  tr=next(x for x in rows if x['id']==data['truth_id']);exact=[i+1 for i,z in enumerate(tr['alternatives']) if z['plain']==data['truth'] and list(z['literal_positions'])==truth]
  result['control']=dict(truth_id=data['truth_id'],truth_key_rank=1+sum(r['top_score']>tr['top_score'] for r in rows),truth_score=lm.score(data['truth'],ends),truth_path_rank_in_correct_cell=exact[0] if exact else None,first_truth_pruned=tr['diagnostics']['first_truth_pruned'],selected_rune_errors=sum(a!=b for a,b in zip(global16[0]['plain'],data['truth'])),correct_cell_errors=sum(a!=b for a,b in zip(tr['alternatives'][0]['plain'],data['truth'])),selected_id=global16[0]['id'],truth=data['truth'],truth_literal=truth)
 save(name+'.json.gz',result);print(name,result['maximum'],result['seconds'],flush=True);return result
def tiny():
 lm=LM();rng=random.Random(525100);out=[]
 for i in range(100):
  n=rng.randrange(1,7);c=[rng.choice([0,0,rng.randrange(29)]) for _ in range(n)];ends={j for j in range(n) if rng.random()<.3}|{n-1};key=[rng.randrange(29) for _ in range(rng.randrange(1,6))];sign=rng.choice([-1,1]);zpos=[j for j,v in enumerate(c) if v==0];truths=[]
  for bits in itertools.product([0,1],repeat=len(zpos)):
   literal={j for j,b in zip(zpos,bits) if b};u=0;p=[]
   for j,v in enumerate(c):
    if j in literal:p.append(0)
    else:p.append((v+sign*key[u%len(key)])%29);u+=1
   truths.append(lm.score(p,ends))
  r,d=p03.beam(c,ends,key,sign,lm,width=64);assert np.allclose([x['score'] for x in r],sorted(truths,reverse=True)[:16],atol=1e-12,rtol=0);out.append(dict(cipher=c,ends=sorted(ends),key=key,sign=sign,scores=[x['score'] for x in r]))
 save('tiny-controls.json',out)
def run(ix,count=19):
 data=packet(ix);save(f'packet-{ix}.json',data);main=search(f'packet-{ix}-main',data);ns=[]
 for j in range(count):
  seed=525200+100*ix+j;ns.append(search(f'packet-{ix}-null-{j:02}',data,null(data['cipher'],seed),seed))
 result=dict(packet=ix,name=data['name'],n=len(data['cipher']),boundaries=len(data['ends']),nulls=count,maximum=main['maximum'],tail=(1+sum(r['maximum']>=main['maximum'] for r in ns))/(count+1),control=main.get('control'),seconds=sum(r['seconds'] for r in ns)+main['seconds'])
 save(f'packet-{ix}-summary.json',result);print(json.dumps(result),flush=True)
if __name__=='__main__':
 guard();t=time.monotonic();mode=sys.argv[1]
 if mode=='pilot':tiny();d=packet(0);save('packet-0.json',d);search('packet-0-main',d);save('keys.json',cells())
 elif mode=='packet':run(int(sys.argv[2]))
 print('SECONDS',time.monotonic()-t)
