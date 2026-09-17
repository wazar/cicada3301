import pathlib,json,gzip,hashlib,sys,random,time,itertools,datetime,collections
R=pathlib.Path(__file__).resolve().parent;ROOT=R.parents[2];O=R/'P18';sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'))
from frozen_finite import finite
from p03_frozen import LM,parse
lm=LM()
def gate():
 assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(name,x):
 with gzip.open(O/(name+'.json.gz'),'wt') as f:json.dump(x,f)
def load(name):
 with gzip.open(O/(name+'.json.gz'),'rt') as f:return json.load(f)
with gzip.open(R/'P17/source.json.gz','rt') as f:SOURCE=json.load(f)
KEY=[r for w in SOURCE['words'] for r in w['runes']]
assert len(KEY)==18584
def fixture(ix):
 name=['0_welcome','jpg107-167','p56_an_end','p57_parable'][ix];path=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');raw=path.read_text();plain,ends=parse(raw);offset=[0,4096,8192,12288][ix];sign=[-1,1,-1,1][ix];c=[];literal=[];u=0
 for i,p in enumerate(plain):
  if p==0 and i%3!=1:c.append(0);literal.append(i)
  else:c.append((p-sign*KEY[offset+u])%29);u+=1
 return dict(name='control-'+str(ix),cipher=c,ends=sorted(ends),truth=dict(offset=offset,sign=sign,plain=plain,literal_positions=literal,used=u),source=dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),character_offsets=[j for j,ch in enumerate(raw) if ch in parse.__globals__['ABC']]))
def packet(name):
 if name.startswith('control'):return fixture(int(name.split('-')[1]))
 typ,pid=name.split('-');pid=int(pid);assert pid in [0,17];maps=json.loads((ROOT/'exploration/persistent-01/worker-f/F06-maps.json').read_text());m=next(x for x in maps if x['page']==pid);c,ends=parse(m['raw_joined']);assert c==m['indices']
 if typ=='null':
  rng=random.Random(331819+pid);out=[rng.randrange(29)]
  for i in range(1,len(c)):
   if c[i]==c[i-1]:out.append(out[-1])
   else:v=rng.randrange(28);out.append(v+(v>=out[-1]))
  c=out
 return dict(name=name,cipher=c,ends=sorted(ends),page=pid,map=m)
def grid(f):return [dict(offset=o,sign=s) for o in range(len(KEY)-sum(x!=0 for x in f['cipher'])+1) for s in [-1,1]]
def cell(f,job,retain=1):
 a,d=finite(f['cipher'],set(f['ends']),KEY[job['offset']:],job['sign'],lm,retain);return dict(job=job,score=a[0]['score'] if a else None,alternatives=a,diagnostics=d)
def replay(f,job,a):
 u=0;lit=set(a['literal_positions']);key=KEY[job['offset']:];p=[]
 for i,v in enumerate(f['cipher']):
  if i in lit:assert v==0;p.append(0)
  else:assert u<len(key);p.append((v+job['sign']*key[u])%29);u+=1
 assert p==a['plain'] and u==a['used'];assert abs(lm.score(p,set(f['ends']))-a['score'])<1e-11
def exhaustive():
 rng=random.Random(331800);rows=[]
 for case in range(100):
  n=rng.randrange(1,14);c=[0 if rng.random()<.4 else rng.randrange(29) for _ in range(n)];key=[rng.randrange(29) for _ in range(rng.randrange(n+2))];ends={i for i in range(n) if rng.random()<.25}|{n-1};sign=rng.choice([-1,1]);sites=[i for i,v in enumerate(c) if v==0];ex=[]
  for bits in itertools.product([False,True],repeat=len(sites)):
   lit={i for i,b in zip(sites,bits) if b};p=[];u=0
   for i,v in enumerate(c):
    if i in lit:p.append(0)
    elif u<len(key):p.append((v+sign*key[u])%29);u+=1
    else:break
   if len(p)==n:ex.append(lm.score(p,ends))
  ex.sort(reverse=True);a,d=finite(c,ends,key,sign,lm,16);assert len(a)==min(16,len(ex));assert all(abs(x['score']-s)<1e-12 for x,s in zip(a,ex));rows.append(dict(case=case,cipher=c,key=key,ends=sorted(ends),sign=sign,validpaths=len(ex),top16=a,diag=d))
 dump('exhaustive',rows)
def pilot():
 gate();exhaustive();records=[];sizes=[]
 for ix in range(4):
  f=fixture(ix);jobs=grid(f);ids=[i*len(jobs)//64 for i in range(64)];start=time.monotonic();rows=[]
  for i in ids:r=cell(f,jobs[i]);[replay(f,r['job'],a) for a in r['alternatives']];rows.append(dict(id=i,**r))
  dt=time.monotonic()-start;records.append(dict(name=f['name'],grid=len(jobs),seconds=dt,ids=ids,rows=rows));sizes.append(dict(name=f['name'],cells=len(jobs),pilot_seconds=dt,estimated_seconds=dt*len(jobs)/64));dump('fixture-'+str(ix),f);print(json.dumps(sizes[-1]),flush=True)
 dump('pilot',records);dump('forecast',dict(controls=sizes,actual_cells=[dict(name=n,cells=len(grid(packet(n)))) for n in ['real-0','null-0','real-17','null-17']],key_length=len(KEY),model_sources=lm.files))
 dump('key-map',dict(key=KEY,map=[dict(word=wi,rune_in_word=ri,char_span=w['span']) for wi,w in enumerate(SOURCE['words']) for ri,_ in enumerate(w['runes'])],source_sha256=hashlib.sha256((R/'P17/pg45315.txt').read_bytes()).hexdigest()))
def batch(name,start,end):
 gate();f=packet(name);jobs=grid(f);assert 0<=start<end<=len(jobs);t=time.monotonic();path=O/(name+'-'+str(start)+'-'+str(end)+'.jsonl.gz');assert not path.exists()
 with gzip.open(path,'wt') as g:
  for i in range(start,end):
   if i%256==0:gate()
   row=cell(f,jobs[i]);g.write(json.dumps(dict(id=i,**row),separators=(',',':'))+'\n')
 assert path.stat().st_size<90_000_000
 dump(name+'-batch-'+str(start),dict(name=name,start=start,end=end,total=len(jobs),seconds=time.monotonic()-t,bytes=path.stat().st_size));print(name,start,end,time.monotonic()-t,flush=True)
def aggregate(name):
 gate();f=packet(name);jobs=grid(f);rows=[];paths=sorted(O.glob(name+'-*.jsonl.gz'),key=lambda p:int(p.name.split('-')[-2]))
 for path in paths:
  with gzip.open(path,'rt') as g:rows.extend(json.loads(line) for line in g)
 assert [r['id'] for r in rows]==list(range(len(jobs)));good=[r for r in rows if r['score'] is not None];good.sort(key=lambda r:r['score'],reverse=True)
 distinct=[];seen=set()
 for r in good:
  a=r['alternatives'][0];k=(tuple(a['plain']),tuple(a['literal_positions']))
  if k not in seen:seen.add(k);distinct.append(r)
  if len(distinct)==16:break
 threshold=distinct[-1]['score'] if len(distinct)==16 else float('-inf');eligible=[r for r in good if r['score']>=threshold];candidates={}
 for row in eligible:
  rr=cell(f,row['job'],16)
  for a in rr['alternatives']:
   replay(f,row['job'],a);k=(tuple(a['plain']),tuple(a['literal_positions']))
   if k not in candidates:candidates[k]=dict(**a,aliases=[])
   candidates[k]['aliases'].append(row['job'])
 best=sorted(candidates.values(),key=lambda a:a['score'],reverse=True)[:16]
 # Exhaustive aliases, including sourcewindows hidden by tied localtop16 paths.
 for a in best:
  a['retained_grid_aliases']=a['aliases'];a['aliases']=[];lit=set(a['literal_positions'])
  for sign in [-1,1]:
   required=bytes((sign*(p-v))%29 for i,(p,v) in enumerate(zip(a['plain'],f['cipher'])) if i not in lit)
   if required:
    start=0
    while True:
     offset=bytes(KEY).find(required,start)
     if offset<0:break
     a['aliases'].append(dict(offset=offset,sign=sign));start=offset+1
   else:a['aliases'].extend(dict(offset=o,sign=sign) for o in range(len(KEY)+1))
  assert all(x in a['aliases'] for x in a['retained_grid_aliases'])
 result=dict(name=name,cells=len(rows),feasible=len(good),infeasible=len(rows)-len(good),threshold=threshold,rerun_cells=len(eligible),top16=best,best_score=best[0]['score'] if best else None,packet=f)
 if 'truth' in f:
  truth=f['truth'];tr=next(r for r in rows if r['job']==dict(offset=truth['offset'],sign=truth['sign']));ta=cell(f,tr['job'],16);truthscore=lm.score(truth['plain'],set(f['ends']))
  result.update(truth_job_top1_score=tr['score'],truth_plain_score=truthscore,truth_job_score_rank=1+sum(r['score'] is not None and r['score']>tr['score'] for r in rows),best_errors=sum(x!=y for x,y in zip(best[0]['plain'],truth['plain'])),key_recovered=dict(offset=truth['offset'],sign=truth['sign']) in best[0]['aliases'],literal_path_recovered=best[0]['literal_positions']==truth['literal_positions'],truth_global_ranks=[i+1 for i,a in enumerate(best) if a['plain']==truth['plain'] and a['literal_positions']==truth['literal_positions']],truth_cell_top16=ta)
 dump(name+'-aggregate',result);print(json.dumps({k:v for k,v in result.items() if k not in ['packet','top16','truth_cell_top16']}),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='pilot':pilot()
 elif sys.argv[1]=='batch':batch(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]))
 elif sys.argv[1]=='aggregate':aggregate(sys.argv[2])
