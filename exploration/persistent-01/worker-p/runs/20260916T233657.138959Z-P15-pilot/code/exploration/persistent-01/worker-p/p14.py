import ast,collections,datetime,gzip,hashlib,json,math,pathlib,random,sys,time
R=pathlib.Path(__file__).resolve().parent;ROOT=R.parents[2];O=R/'P14';S=.83;CAP=2048;CUTS=[262,528,729]
sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'))
from p03_frozen import LM,parse
lm=LM()
old=ROOT/'exploration/persistent-01/worker-m/M25/m25.py';tree=ast.parse(old.read_text());env=dict(random=random,S=S)
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['encoder','transitions']],type_ignores=[]),str(old),'exec'),env)
encoder=env['encoder'];transitions=env['transitions']
def gate():
 assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(name,x):
 with gzip.open(O/(name+'.json.gz'),'wt') as f:json.dump(x,f)
def keys():
 primes=[];n=2
 while len(primes)<CAP:
  if all(n%p for p in primes if p*p<=n):primes.append(n)
  n+=1
 phi=list(range(CAP+1))
 for p in range(2,CAP+1):
  if phi[p]==p:
   for n in range(p,CAP+1,p):phi[n]-=phi[n]//p
 arrays={'prime_minus_one':[(p-1)%29 for p in primes],'integer_phi':[p%29 for p in phi[1:]]}
 cells=[dict(id=f+':'+str(s),family=f,sign=s,key=arrays[f]) for f in arrays for s in [-1,1]]
 inherited=json.loads((old.parent/'keys.json').read_text())
 assert all(c['key'][:1024]==next(x['key'] for x in inherited if x['id']==c['id']) for c in cells)
 return cells
CELLS=keys()
def decode(c,ends,cuts,cell,reset=False,retain=1):
 states={(0,(29,29)):[(0.,b'',())]};history=[];excluded=0;maxqueried=-1
 for i,v in enumerate(c):
  nxt=collections.defaultdict(list);cache={};atcut=i in cuts;prev=None if i==0 or(reset and atcut) else c[i-1]
  for (u,ctx),paths in states.items():
   if atcut:ctx=(29,29)
   if reset and atcut:u=0
   if u not in cache:
    cache[u]=transitions(v,prev,u,cell['key'],cell['sign'],2)
    if u>=CAP:excluded+=1
    else:
     maxqueried=max(maxqueried,u)
     if prev is not None:
      p=(prev+cell['sign']*cell['key'][u])%29;q=u+2
      while q<CAP:
       maxqueried=max(maxqueried,q)
       if (p-cell['sign']*cell['key'][q])%29!=prev:break
       q+=2
      if q>=CAP:excluded+=1
   for p,uu,t in cache[u]:
    ss,w=lm.extend(ctx,p,i in ends);w+=t*math.log(S)+(math.log(1-S) if prev is not None and v==prev else 0)
    for score,plain,skips in paths:nxt[(uu,ss)].append((score+w,plain+bytes([p]),skips+(t,)))
  states={}
  for state,paths in nxt.items():paths.sort(key=lambda x:x[0],reverse=True);states[state]=paths[:retain]
  history.append([i,len(states),sum(map(len,states.values()))])
  if not states:return dict(feasible=False,alternatives=[],history=history,cap_excluded=excluded,max_queried=maxqueried)
 ordered=sorted([(sc,u,p,t,ctx) for (u,ctx),ps in states.items() for sc,p,t in ps],key=lambda x:x[0],reverse=True)
 alts=[dict(score=sc/(len(c)+len(ends)),total=sc,used=u,plain=list(p),reject_counts=list(t)) for sc,u,p,t,ctx in ordered[:retain]]
 return dict(feasible=True,alternatives=alts,history=history,cap_excluded=excluded,max_queried=maxqueried,max_terminal_used=max(x[1] for x in ordered))
def walk(c,a,cuts,cell,reset=False):
 j=0;rows=[]
 for i,(v,p,t) in enumerate(zip(c,a['plain'],a['reject_counts'])):
  if reset and i in cuts:j=0
  prev=None if i==0 or(reset and i in cuts) else c[i-1];accept=j+2*t
  assert not t or prev is not None
  assert all((p-cell['sign']*cell['key'][k])%29==prev for k in range(j,accept,2))
  assert (p-cell['sign']*cell['key'][accept])%29==v
  rows.append(dict(i=i,start=j,accepted=accept,after=accept+1,rejected=list(range(j,accept,2)),burned=list(range(j+1,accept,2))))
  j=accept+1
 assert j==a['used'];return rows

def search(name,c,ends,cuts,diagnostic=True):
 gate();start=time.monotonic();rows=[]
 for cell in CELLS:
  d=decode(c,ends,cuts,cell);a=d['alternatives'][0];a['walk']=walk(c,a,cuts,cell);rows.append(dict(id=cell['id'],decode=d,score=a['score']))
 rows.sort(key=lambda r:r['score'],reverse=True);cell=next(x for x in CELLS if x['id']==rows[0]['id']);top=decode(c,ends,cuts,cell,retain=16)
 assert abs(top['alternatives'][0]['score']-rows[0]['score'])<1e-12
 for a in top['alternatives']:a['walk']=walk(c,a,cuts,cell)
 diag=[]
 if diagnostic:
  for cell in CELLS:
   d=decode(c,ends,cuts,cell,reset=True)
   for a in d['alternatives']:a['walk']=walk(c,a,cuts,cell,True)
   diag.append(dict(id=cell['id'],decode=d))
 result=dict(name=name,cipher=c,ends=sorted(ends),cuts=cuts,rows=rows,top16=top,reset=diag,seconds=time.monotonic()-start);dump(name,result);return result

def fixture(ix):
 p=[];ends=set();maps=[]
 for name in ['0_welcome','jpg107-167','p56_an_end','p57_parable']:
  path=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');q,e=parse(path.read_text());offset=len(p);p+=q;ends.update(offset+i for i in e);maps.append(dict(path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),start=offset,length=len(q)))
 cell=CELLS[ix];seed=331400+ix;c,events,u=encoder(p,cell['key'],cell['sign'],seed)
 # Independently written scalar encoder, explicit 1+1 burned draw increments.
 rng=random.Random(seed);cc=[];j=0;accepts=[]
 for x in p:
  while True:
   y=(x-cell['sign']*cell['key'][j])%29
   if cc and cc[-1]==y and rng.random()<.83:j+=1;j+=1;continue
   cc.append(y);accepts.append(j);j+=1;break
 assert cc==c and j==u and accepts==[e['accepted'] for e in events]
 return dict(plain=p,ends=sorted(ends),maps=maps,cipher=c,events=events,used=u,cell_id=cell['id'],seed=seed,cuts=CUTS)
def control(ix):
 f=fixture(ix);dump('fixture-'+str(ix),f);r=search('control-'+str(ix),f['cipher'],set(f['ends']),CUTS);a=r['top16']['alternatives'][0];truth=next(x for x in r['rows'] if x['id']==f['cell_id'])['decode']['alternatives'][0]
 ts=[len(e['rejected']) for e in f['events']];ta=dict(plain=f['plain'],reject_counts=ts,used=f['used']);w=walk(f['cipher'],ta,CUTS,CELLS[ix]);assert [x['accepted'] for x in w]==[e['accepted'] for e in f['events']]
 reset=next(x for x in r['reset'] if x['id']==f['cell_id'])['decode']['alternatives'][0]
 out=dict(ix=ix,length=len(f['plain']),key_recovered=r['rows'][0]['id']==f['cell_id'],errors=sum(x!=y for x,y in zip(a['plain'],f['plain'])),truth_key_errors=sum(x!=y for x,y in zip(truth['plain'],f['plain'])),path_recovered=a['reject_counts']==ts,reset_errors=sum(x!=y for x,y in zip(reset['plain'],f['plain'])),boundaries=[w[k-1:k+1] for k in CUTS],seconds=r['seconds'],max_queried=max(x['decode']['max_queried'] for x in r['rows']),cap_excluded=sum(x['decode']['cap_excluded'] for x in r['rows']))
 dump('control-summary-'+str(ix),out);print(json.dumps(out),flush=True);return out

def brute():
 results=[]
 for case in range(32):
  rng=random.Random(331440+case);cell=dict(key=[rng.randrange(4) for _ in range(12)],sign=[-1,1][case%2]);c=[rng.randrange(4) for _ in range(4)];ends={1,3};cuts=[2]
  # Short keys padded only for production cap accounting; enumeration uses real length.
  global CAP
  saved=CAP;CAP=len(cell['key'])
  for reset in [False,True]:
   paths=[]
   def rec(i,j,ctx,score,p,ts):
    if i==len(c):paths.append((score,p,ts));return
    if i in cuts:ctx=(29,29)
    if reset and i in cuts:j=0
    prev=None if i==0 or(reset and i in cuts) else c[i-1]
    for accept in range(j,len(cell['key']),2):
     t=(accept-j)//2;x=(c[i]+cell['sign']*cell['key'][accept])%29
     if t and(prev is None or any((x-cell['sign']*cell['key'][k])%29!=prev for k in range(j,accept,2))):continue
     ss,w=lm.extend(ctx,x,i in ends);w+=t*math.log(S)+(math.log(1-S) if prev is not None and c[i]==prev else 0);rec(i+1,accept+1,ss,score+w,p+[x],ts+[t])
   rec(0,0,(29,29),0.,[],[]);paths.sort(reverse=True,key=lambda x:x[0]);d=decode(c,ends,cuts,cell,reset,16)
   assert len(d['alternatives'])==min(16,len(paths))
   assert all(abs(a['total']-p[0])<1e-11 for a,p in zip(d['alternatives'],paths));results.append(dict(case=case,reset=reset,paths=len(paths),scores=[x[0] for x in paths[:16]]))
  CAP=saved
 dump('brute',results)
def actual():
 maps=json.loads((ROOT/'exploration/persistent-01/worker-f/F06-maps.json').read_text());p=[];ends=set();selected=[];cuts=[]
 for pid in [0,1,2,3]:
  m=next(x for x in maps if x['page']==pid);q,e=parse(m['raw_joined']);assert q==m['indices'];offset=len(p)
  if offset:cuts.append(offset)
  p+=q;ends.update(offset+i for i in e);selected.append(m)
 assert cuts==CUTS and len(p)==946;dump('real-maps',selected);r=search('real',p,ends,cuts);rng=random.Random(331419);null=[]
 for rep in range(19):
  gate();c=[rng.randrange(29)]
  for i in range(1,len(p)):
   if p[i]==p[i-1]:c.append(c[-1])
   else:v=rng.randrange(28);c.append(v+(v>=c[-1]))
  assert [a==b for a,b in zip(c,c[1:])]==[a==b for a,b in zip(p,p[1:])]
  nr=search('null-'+str(rep),c,ends,cuts,False);null.append(dict(rep=rep,score=nr['rows'][0]['score'],best=nr['rows'][0]['id'],seconds=nr['seconds']));print(json.dumps(null[-1]),flush=True)
 summary=dict(real_score=r['rows'][0]['score'],best=r['rows'][0]['id'],null=null,tail=(1+sum(x['score']>=r['rows'][0]['score'] for x in null))/20,seed=331419)
 dump('summary',summary);print(json.dumps(summary),flush=True)
if __name__=='__main__':
 gate();mode=sys.argv[1]
 if mode=='pilot':dump('keys',CELLS);dump('model',lm.files);brute();control(0)
 elif mode=='controls':
  for ix in range(1,4):control(ix)
 elif mode=='actual':actual()
