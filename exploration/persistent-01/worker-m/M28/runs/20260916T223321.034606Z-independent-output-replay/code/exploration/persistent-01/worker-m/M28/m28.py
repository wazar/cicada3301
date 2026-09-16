import pathlib,sys,json,gzip,ast,random,math,hashlib,time,datetime,collections,itertools
R=pathlib.Path(__file__).parent;ROOT=R.parents[3];sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'));from p03_frozen import LM,parse
sys.path.insert(0,str(ROOT/'liber-primus/src'));from lp import gematria as gp
S=.83;lm=LM();SOURCE=ROOT/'liber-primus/data/keys/armada18/mabinogion_vol1_guest_edwards_ed.txt';oldpath=ROOT/'liber-primus/analysis/campaign18_skip/armada2/selfref_skip.py';oldnode=next(n for n in ast.parse(oldpath.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='encipher_ctfeedback');ns=dict(random=random,N=29);exec(compile(ast.Module(body=[oldnode],type_ignores=[]),str(oldpath),'exec'),ns)
def dump(n,x):(R/(n+'.json')).write_text(json.dumps(x,indent=2))
def gate():
 assert not(R.parent.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def loadkey():
 raw=SOURCE.read_text();s=raw.upper();out=[];spans=[];i=0
 while i<len(s):
  for t,x in gp._TRANS_SORTED:
   if s.startswith(t,i):out.append(x);spans.append([i,i+len(t)]);i+=len(t);break
  else:
   x={'V':1,'K':5,'Z':15,'Q':5}.get(s[i]);
   if x is not None:out.append(x);spans.append([i,i+1])
   i+=1
 # Uppercase character offsets explicitly; no claim these are raw offsets under Unicode expansion.
 assert len(s)==len(raw), 'requires explicit Unicode map';return out,spans
K,SPANS=loadkey();CELLS=[dict(a=a,sign=s,id=f'{a}:{s}') for a in range(1,29) for s in [-1,1]]
def encoder(P,key,a,sign,seed):
 rng=random.Random(seed);C=[];events=[]
 for i,p in enumerate(P):
  if i>=len(key):raise ValueError('unsupported output')
  f=a*C[-1]%29 if C else 0;j=i;rr=[]
  while True:
   c=(p-sign*(key[j]+f))%29
   if C and c==C[-1]:
    u=rng.random();rr.append([j,u])
    if u<S:
     j+=1
     if j>=len(key):break
     continue
   break
  C.append(c);events.append(dict(start=i,accepted=min(j,len(key)-1),forced_eof=j>=len(key),decisions=rr))
 return C,events

def options(c,prev,i,key,a,sign):
 if i>=len(key):return []
 f=0 if prev is None else a*prev%29;p=(c+sign*(key[i]+f))%29
 if prev is None:return [(p,1.,[dict(accepted=i,rejected=0,probability=1.,forced=False)])]
 j=i
 while j<len(key) and key[j]==key[i]:j+=1
 if c==prev:
  traces=[dict(accepted=z,rejected=z-i,probability=(S**(z-i))*(1 if z==len(key)-1 else 1-S),forced=z==len(key)-1) for z in range(i,j)]
  return [(p,sum(t['probability'] for t in traces),traces)]
 ans=[(p,1.,[dict(accepted=i,rejected=0,probability=1.,forced=False)])]
 if j<len(key):
  alt=(prev+sign*(key[i]+f))%29
  if (alt-sign*(key[j]+f))%29==c:ans.append((alt,S**(j-i),[dict(accepted=j,rejected=j-i,probability=S**(j-i),forced=False)]))
 return ans

def decode(c,ends,cell,retain=1):
 states={(29,29):[(0.,b'')]};history=[]
 for i,v in enumerate(c):
  nxt=collections.defaultdict(list);opts=options(v,c[i-1] if i else None,i,K,cell['a'],cell['sign'])
  for ctx,paths in states.items():
   for p,prob,traces in opts:
    ss,w=lm.extend(ctx,p,i in ends);w+=math.log(prob)
    for score,plain in paths:nxt[ss].append((score+w,plain+bytes([p])))
  states={ss:sorted(paths,reverse=True)[:retain] for ss,paths in nxt.items()};history.append(len(states))
  if not states:return dict(feasible=False,unsupported_position=i,alternatives=[])
 ranked=sorted([z for paths in states.values() for z in paths],reverse=True)[:retain];out=[]
 for score,p in ranked:out.append(dict(score=score/(len(c)+len(ends)),joint_total=score,plain=list(p),language_score=lm.score(p,ends)))
 return dict(feasible=True,alternatives=out,state_counts=history)
def replay(c,p,cell):
 out=[]
 for i,(v,x) in enumerate(zip(c,p)):
  opt=next(z for z in options(v,c[i-1] if i else None,i,K,cell['a'],cell['sign']) if z[0]==x);out.append(dict(output=i,key_start=i,plaintext=x,probability=opt[1],traces=opt[2],source_spans=[SPANS[t['accepted']] for t in opt[2]]))
 return out

def search(name,c,ends):
 path=R/'evidence'/(name+'.json.gz')
 if path.exists():
  with gzip.open(path,'rt') as f:return json.load(f)
 gate();t=time.monotonic();rows=[]
 for cell in CELLS:
  d=decode(c,ends,cell);rows.append(dict(cell=cell,score=d['alternatives'][0]['score'] if d['feasible'] else None,decode=d))
 rows.sort(key=lambda x:x['score'] if x['score'] is not None else -1e100,reverse=True);cell=rows[0]['cell'];top=decode(c,ends,cell,16)
 assert top['alternatives'][0]['score']==rows[0]['score']
 for p in top['alternatives']:p['key_walk']=replay(c,p['plain'],cell)
 out=dict(name=name,cipher=c,ends=sorted(ends),rows=rows,top16=top,score=rows[0]['score'],seconds=time.monotonic()-t)
 with gzip.open(path,'wt') as f:json.dump(out,f)
 return out

def cumulative_reachable(c,p,cell):
 states={0};history=[]
 for i,(v,x) in enumerate(zip(c,p)):
  f=cell['a']*c[i-1]%29 if i else 0;nxt=set()
  for j in states:
   while j<len(K):
    z=(x-cell['sign']*(K[j]+f))%29
    if z==v:nxt.add(j+1)
    if i==0 or z!=c[i-1]:break
    j+=1
  states=nxt;history.append(sorted(states))
 return dict(reachable=bool(states),first_dead=next((i for i,s in enumerate(history) if not s),None),history=history)
def fixture(ix):
 name=['0_welcome','jpg107-167','p56_an_end','p57_parable'][ix];source=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');p,ends=parse(source.read_text());cell=dict(a=[7,13,22,28][ix],sign=[-1,1,-1,1][ix]);cell['id']=f"{cell['a']}:{cell['sign']}";c,events=encoder(p,K,cell['a'],cell['sign'],330828+ix);old=ns['encipher_ctfeedback'](p,K,k=1,coeffs=[0,cell['a']],sign=cell['sign'],supp=S,seed=330828+ix);assert c==old
 return dict(name='control-'+name,source=str(source.relative_to(ROOT)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),plain=p,ends=sorted(ends),cell=cell,cipher=c,events=events,reset_reachable=all(any(z[0]==x for z in options(v,c[i-1] if i else None,i,K,cell['a'],cell['sign'])) for i,(v,x) in enumerate(zip(c,p))),cumulative=cumulative_reachable(c,p,cell))
def masknull(c,rng):
 out=[rng.randrange(29)]
 for x,y in zip(c,c[1:]):
  if x==y:out.append(out[-1])
  else:z=rng.randrange(28);out.append(z+(z>=out[-1]))
 assert [x==y for x,y in zip(out,out[1:])]==[x==y for x,y in zip(c,c[1:])];return out

def setup():
 (R/'evidence').mkdir(exist_ok=True);dump('source',dict(source=str(SOURCE.relative_to(ROOT)),sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),values_sha256=hashlib.sha256(bytes(K)).hexdigest(),values=K,uppercase_spans=SPANS,missing_historical_path='liber-primus/data/keys/mabinogion.txt',historical_present=(ROOT/'liber-primus/data/keys/mabinogion.txt').exists(),old_encoder_source=str(oldpath.relative_to(ROOT)),old_sha256=hashlib.sha256(oldpath.read_bytes()).hexdigest(),ast_source=ast.get_source_segment(oldpath.read_text(),oldnode)));dump('model',dict(cells=CELLS,suppression=S,lm_files=lm.files,key_length=len(K)))

def pilot():
 setup();f=fixture(0);dump('pilot-control',f);r=search(f['name'],f['cipher'],set(f['ends']));dump('pilot',dict(seconds=r['seconds'],forecast=r['seconds']*280,winning_cell=r['rows'][0]['cell'],reset_reachable=f['reset_reachable'],cumulative_reachable=f['cumulative']['reachable']));print('PILOT',r['seconds'],r['rows'][0]['cell'],flush=True)
def run():
 setup();rng=random.Random(338028);controls=[]
 for ix in range(4):
  f=fixture(ix);dump(f['name']+'-fixture',f);r=search(f['name'],f['cipher'],set(f['ends']));null=[]
  for j in range(19):
   z=search(f['name']+'-null'+str(j),masknull(f['cipher'],rng),set(f['ends']));null.append(dict(name=z['name'],score=z['score']))
  tr=next(x for x in r['rows'] if x['cell']==f['cell']);out=dict(name=f['name'],reset_reachable=f['reset_reachable'],cumulative_reachable=f['cumulative']['reachable'],cumulative_first_dead=f['cumulative']['first_dead'],truth_rank=1+sum(x['score']>tr['score'] for x in r['rows']),true_cell_errors=sum(x!=y for x,y in zip(tr['decode']['alternatives'][0]['plain'],f['plain'])),winning_errors=sum(x!=y for x,y in zip(r['top16']['alternatives'][0]['plain'],f['plain'])),score=r['score'],tail=(1+sum(z['score']>=r['score'] for z in null))/20,null=null);controls.append(out);dump('controls',controls);print('CONTROL',out['name'],out['truth_rank'],out['winning_errors'],out['cumulative_first_dead'],flush=True)
 maps=json.load(open(ROOT/'exploration/persistent-01/worker-f/F06-maps.json'));real=[]
 for pid in [0,17]:
  m=next(z for z in maps if z['page']==pid);c=m['indices'];ends={w['end']-1 for w in m['words']};dump('real-'+str(pid)+'-map',m);r=search('real-'+str(pid),c,ends);null=[]
  for j in range(99):
   z=search(f'real-{pid}-null{j}',masknull(c,rng),ends);null.append(dict(name=z['name'],score=z['score']))
  real.append(dict(page=pid,score=r['score'],tail=(1+sum(z['score']>=r['score'] for z in null))/100,winner=r['rows'][0]['cell'],null=null));dump('real',real);print('REAL',pid,r['score'],real[-1]['tail'],flush=True)
 dump('result',dict(controls=controls,real=real,searches=280,cells=15680,extra_top16_calls=280,rng_after=rng.getstate(),no_expansion=True))
if __name__=='__main__':pilot() if sys.argv[1]=='pilot' else run()
