import pathlib,sys,importlib.util,json,gzip,math,random,time,datetime,ast,collections,zlib,hashlib
R=pathlib.Path(__file__).parent;ROOT=R.parents[3];sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'));from p03_frozen import LM,parse
spec=importlib.util.spec_from_file_location('oldseq',ROOT/'exploration/overnight-01/worker-b/search.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);lm=LM();S=.83
seqs=old.seqs(1024);CELLS=[dict(id=family+':'+str(sign),family=family,sign=sign,key=seqs[family].tolist()) for family in ['prime_minus_one','integer_phi'] for sign in [-1,1]]
def gate():
 assert not(R.parent.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(name,x):(R/(name+'.json')).write_text(json.dumps(x,indent=2))
def save(name,x):
 with gzip.open(R/'evidence'/(name+'.json.gz'),'wt') as f:json.dump(x,f)
def encoder(p,key,sign,seed):
 rng=random.Random(seed);c=[];events=[];j=0;draws=[]
 for i,x in enumerate(p):
  tested=[];burn=[];decisions=[]
  while True:
   if j>=len(key):raise ValueError('key exhausted')
   v=(x-sign*key[j])%29
   if c and v==c[-1]:
    q=rng.random();decisions.append(q)
    if q<S:tested.append(j);burn.append(j+1);j+=2;continue
   break
  c.append(v);events.append(dict(rejected=tested,burned=burn,accepted=j,random_decisions=decisions));j+=1
 return c,events,j

def transitions(c,prev,j,key,sign,stride):
 if j>=len(key):return []
 out=[((c+sign*key[j])%29,j+1,0)]
 if prev is None:return out
 p=(prev+sign*key[j])%29;t=1
 while j+stride*t<len(key):
  v=(p-sign*key[j+stride*t])%29
  if v==c:out.append((p,j+stride*t+1,t))
  if v!=prev:break
  t+=1
 return out

def decode(c,ends,cell,stride=2,retain=1):
 key=cell['key'];sign=cell['sign'];states={(0,(29,29)):[(0.,b'',())]};expanded=0;dominated=0;history=[]
 for i,v in enumerate(c):
  nxt=collections.defaultdict(list);cache={};prev=c[i-1] if i else None
  for (u,ctx),paths in states.items():
   if u not in cache:cache[u]=transitions(v,prev,u,key,sign,stride)
   for p,uu,t in cache[u]:
    ss,w=lm.extend(ctx,p,i in ends);w+=t*math.log(S)+(math.log(1-S) if prev is not None and v==prev else 0.)
    for score,plain,skips in paths:nxt[(uu,ss)].append((score+w,plain+bytes([p]),skips+(t,)));expanded+=1
  states={}
  for state,paths in nxt.items():paths.sort(key=lambda x:x[0],reverse=True);dominated+=max(0,len(paths)-retain);states[state]=paths[:retain]
  history.append(dict(index=i,states=len(states),paths=sum(map(len,states.values()))))
  if not states:return dict(feasible=False,expanded=expanded,history=history,alternatives=[])
 ordered=sorted([(score,u,plain,skips,ctx) for (u,ctx),paths in states.items() for score,plain,skips in paths],key=lambda x:x[0],reverse=True);den=len(c)+len(ends);alts=[]
 for score,u,plain,skips,ctx in ordered[:max(16,retain) if retain>1 else 1]:
  alts.append(dict(score=score/den,joint_total=score,plain=list(plain),reject_counts=list(skips),used=u,context=list(ctx),language_score=lm.score(plain,ends)))
 return dict(feasible=True,alternatives=alts,expanded=expanded,dominated=dominated,history=history,terminal_states=[dict(used=u,context=list(ctx),best_joint_score=paths[0][0],retained=len(paths)) for (u,ctx),paths in states.items()])

def replay(c,plain,events,key,sign,stride):
 j=0;w=[]
 for i,(v,p,t) in enumerate(zip(c,plain,events)):
  rejected=[j+stride*q for q in range(t)];accepted=j+stride*t;assert accepted<len(key)
  assert not t or i>0
  assert all((p-sign*key[k])%29==c[i-1] for k in rejected)
  assert (p-sign*key[accepted])%29==v
  burned=[k for k in range(j,accepted) if k not in rejected];w.append(dict(input_index=i,key_start=j,rejected=rejected,burned=burned,accepted=accepted,key_after=accepted+1));j=accepted+1
 return j,w

def search(name,c,ends):
 path=R/'evidence'/(name+'.json.gz')
 if path.exists():
  with gzip.open(path,'rt') as f:return json.load(f)
 gate();start=time.monotonic();rows=[]
 for cell in CELLS:
  d=decode(c,ends,cell);a=d['alternatives'][0];used,walk=replay(c,a['plain'],a['reject_counts'],cell['key'],cell['sign'],2);assert used==a['used'];a['key_walk']=walk;a['statistics']=stats(a['plain']);rows.append(dict(id=cell['id'],score=a['score'],decode=d))
 rows.sort(key=lambda x:x['score'],reverse=True);cell=next(x for x in CELLS if x['id']==rows[0]['id']);top=decode(c,ends,cell,retain=16);assert abs(top['alternatives'][0]['score']-rows[0]['score'])<1e-12
 for a in top['alternatives']:
  u,w=replay(c,a['plain'],a['reject_counts'],cell['key'],cell['sign'],2);assert u==a['used'];a['key_walk']=w;a['statistics']=stats(a['plain'])
 r=dict(name=name,cipher=c,ends=sorted(ends),rows=rows,top16=top,score=rows[0]['score'],seconds=time.monotonic()-start);save(name,r);return r

def stats(p):
 cnt=collections.Counter(p);return dict(ioc_times_n=sum(n*(n-1) for n in cnt.values())/max(1,len(p)-1),min32distinct=min(len(set(p[i:i+32])) for i in range(max(1,len(p)-31))),zlib_bytes=len(zlib.compress(bytes(p))),non_english_lm='N/A sameEnglishreference register')
def fixture(ix):
 name=['0_welcome','jpg107-167','p56_an_end','p57_parable'][ix];f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');plain,ends=parse(f.read_text());cell=CELLS[ix];seed=330825+ix;c,events,used=encoder(plain,cell['key'],cell['sign'],seed);return dict(name='control-'+name,plain=plain,ends=sorted(ends),cell=cell,cipher=c,events=events,used=used,seed=seed,source=str(f.relative_to(ROOT)),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest())

def pilot():
 gate();(R/'evidence').mkdir(exist_ok=True);dump('keys',CELLS);dump('model',dict(suppression=S,objective='LM total + rejectioncount*ln(.83)+observedrepeatcount*ln(.17), normalized rune+boundary tokens',sources=lm.files))
 source=ROOT/'liber-primus/analysis/round18/L7-redteam/b1_power_envelope.py';tree=ast.parse(source.read_text());node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='enc_skip_by_two');ns=dict(random=random,N=29);exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'),ns);checks=[]
 for ix in range(40):
  rng=random.Random(33825+ix);plain=[rng.randrange(29) for _ in range(40)];key=[rng.randrange(29) for _ in range(256)];ours,events,u=encoder(plain,key,-1,3301+ix);up,info=ns['enc_skip_by_two'](plain,key,seed=3301+ix);assert up==ours and info['n_skips']==sum(len(x['rejected']) for x in events);checks.append(dict(case=ix,cipher=ours,plain=plain,key=key,seed=3301+ix,events=events,used=u))
 dump('upstream-controls',dict(path=str(source.relative_to(ROOT)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),controls=checks))
 # Independent acceptance-index enumeration, not transition helper, for finite shortcases.
 brute=[]
 for ix in range(50):
  rng=random.Random(33925+ix);key=[rng.randrange(4) for _ in range(16)];c=[rng.randrange(4) for _ in range(4)];ends={1,3};cell=dict(key=key,sign=-1);paths=[]
  def rec(i,j,ctx,score,plain,ts):
   if i==len(c):paths.append((score,plain,ts));return
   for a in range(j,len(key),2):
    p=(c[i]-key[a])%29;t=(a-j)//2
    if i==0 and t:continue
    if t and any((p+key[z])%29!=c[i-1] for z in range(j,a,2)):continue
    ss,w=lm.extend(ctx,p,i in ends);w+=t*math.log(S)+(math.log(1-S) if i and c[i]==c[i-1] else 0);rec(i+1,a+1,ss,score+w,plain+[p],ts+[t])
  rec(0,0,(29,29),0.,[],[]);paths.sort(key=lambda x:x[0],reverse=True);d=decode(c,ends,cell,retain=16);assert len(d['alternatives'])==min(16,len(paths));assert all(abs(a['joint_total']-p[0])<1e-12 for a,p in zip(d['alternatives'],paths));brute.append(dict(cipher=c,key=key,paths=len(paths),top16=[p[0] for p in paths[:16]]))
 dump('brute-controls',brute);f=fixture(0);r=search(f['name'],f['cipher'],set(f['ends']));dump('pilot',dict(fixture=f,result=r,seconds=r['seconds'],projected_280_searches=r['seconds']*280));print('PILOT',r['seconds'],r['rows'][0]['id'],flush=True)

def run():
 decision=json.load(open(R/'decision.json'));nc=decision['control_nulls'];nr=decision['real_nulls'];rng=random.Random(330826);controls=[]
 for ix in range(4):
  f=fixture(ix);c=f['cipher'];ends=set(f['ends']);r=search(f['name'],c,ends);truthrow=next(x for x in r['rows'] if x['id']==f['cell']['id']);old=decode(c,ends,f['cell'],stride=1);truthskips=[len(x['rejected']) for x in f['events']];u,walk=replay(c,f['plain'],truthskips,f['cell']['key'],f['cell']['sign'],2);assert u==f['used'];violations=[]
  for i,e in enumerate(f['events']):
   for burned in e['burned']:
    if (f['plain'][i]-f['cell']['sign']*f['cell']['key'][burned])%29!=c[i-1]:violations.append(dict(position=i,burned=burned))
  null=[]
  for rep in range(nc):
   sh=c.copy();rng.shuffle(sh);a=search(f['name']+'-null'+str(rep),sh,ends);null.append(dict(name=a['name'],score=a['score'],repeats=sum(x==y for x,y in zip(sh,sh[1:]))))
  row=dict(fixture=f,truth_key_rank=1+sum(x['score']>truthrow['score'] for x in r['rows']),key_recovered=r['rows'][0]['id']==f['cell']['id'],best_errors=sum(x!=y for x,y in zip(r['top16']['alternatives'][0]['plain'],f['plain'])),correctkey_errors=sum(x!=y for x,y in zip(truthrow['decode']['alternatives'][0]['plain'],f['plain'])),old_stride1_errors=sum(x!=y for x,y in zip(old['alternatives'][0]['plain'],f['plain'])),old_stride1=old,truth_path_admissible_stride2=True,truth_fixed_trace_violations_stride1=violations,score=r['score'],null=null,tail=(1+sum(x['score']>=r['score'] for x in null))/(nc+1));controls.append(row);dump('controls',controls);print(f['name'],row['truth_key_rank'],row['best_errors'],row['old_stride1_errors'],row['tail'],flush=True)
 maps=json.load(open(ROOT/'exploration/persistent-01/worker-f/F06-maps.json'));reals=[]
 for m in maps:
  if m['page'] not in [0,17]:continue
  c,ends=parse(m['raw_joined']);assert c==m['indices'];name='real-'+str(m['page']);r=search(name,c,ends);null=[]
  for rep in range(nr):
   sh=c.copy();rng.shuffle(sh);a=search(name+'-null'+str(rep),sh,ends);null.append(dict(name=a['name'],score=a['score'],repeats=sum(x==y for x,y in zip(sh,sh[1:]))))
  row=dict(page=m['page'],map=m,score=r['score'],best_id=r['rows'][0]['id'],null=null,tail=(1+sum(x['score']>=r['score'] for x in null))/(nr+1));reals.append(row);dump('real',reals);print(name,r['score'],row['tail'],flush=True)
 dump('summary',dict(controls=[{k:v for k,v in r.items() if k in ['truth_key_rank','key_recovered','best_errors','correctkey_errors','old_stride1_errors','tail']} for r in controls],real=[{k:v for k,v in r.items() if k in ['page','score','best_id','tail']} for r in reals],searches=4*(nc+1)+2*(nr+1),top1_cells=4*(4*(nc+1)+2*(nr+1)),control_nulls=nc,real_nulls=nr,seed=330826,rng_after=repr(rng.getstate())))
if __name__=='__main__':pilot() if sys.argv[1]=='pilot' else run()
