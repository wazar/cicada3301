import pathlib,json,gzip,hashlib,importlib.util,random,math,collections
R=pathlib.Path(__file__).parent;P=R.parent/'worker-p';Q=P/'P14'
spec=importlib.util.spec_from_file_location('subject',P/'p14.py');s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
load=lambda p:json.load(gzip.open(p,'rt'))
inputs={}
for p in [P/'p14.py',Q/'CARD.md']+sorted(Q.glob('*.gz')):
 b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};(R/'snapshots').mkdir(exist_ok=True);(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
# Direct smoothed conditional probability from frozen count tables, not LM.step/extend.
def emission(ctx,p,end):
 total=0
 for x in [p,29] if end else [p]:
  v=(s.lm.c[0][(x,)]+.5)/(s.lm.t[0][()]+15)
  v=(s.lm.c[1][ctx[-1:]+(x,)]+8*v)/(s.lm.t[1][ctx[-1:]]+8)
  v=(s.lm.c[2][ctx+(x,)]+5*v)/(s.lm.t[2][ctx]+5)
  total+=math.log(v);ctx=(ctx[1],x)
 return ctx,total
# Enumerate actual plaintext alternatives and every possible rejection count, with no DP merging.
def enumerate_paths(c,key,sign,ends,cuts,reset):
 todo=[(0,0,(29,29),0.,[],[])];out=[]
 while todo:
  i,j,ctx,score,p,ts=todo.pop()
  if i==len(c):out.append((score,p,ts,j));continue
  if i in cuts:ctx=(29,29)
  if reset and i in cuts:j=0
  prev=None if i==0 or reset and i in cuts else c[i-1]
  for plain in range(29):
   k=j;t=0
   while k<len(key):
    output=(plain-sign*key[k])%29
    if output==c[i]:
     cc,w=emission(ctx,plain,i in ends);w+=t*math.log(.83)+(math.log(.17) if prev==c[i] else 0)
     todo.append((i+1,k+1,cc,score+w,p+[plain],ts+[t]))
    if prev is None or output!=prev:break
    k+=2;t+=1
 return sorted(out,reverse=True,key=lambda a:a[0])
cases=[]
for ix in range(100):
 rng=random.Random(61900+ix);key=[rng.randrange(3) for _ in range(9)];c=[rng.randrange(3) for _ in range(4)];cuts={1,3} if ix%2 else {2};ends={0,2};sign=1 if ix%3 else -1;s.CAP=len(key)
 for reset in (False,True):
  brute=enumerate_paths(c,key,sign,ends,cuts,reset);got=s.decode(c,ends,cuts,{'key':key,'sign':sign},reset,16)
  assert len(got['alternatives'])==min(16,len(brute))
  for a,b in zip(got['alternatives'],brute):assert abs(a['total']-b[0])<2e-12
  cases.append({'case':ix,'key':key,'cipher':c,'cuts':sorted(cuts),'reset':reset,'paths':len(brute),'scores':[b[0] for b in brute[:16]]})
s.CAP=2048
# Independent arithmetic sequence construction by divisibility and gcd.
keys=load(Q/'keys.json.gz');pr=[];n=2
while len(pr)<2048:
 if all(n%d for d in range(2,math.isqrt(n)+1)):pr.append((n-1)%29)
 n+=1
phi=[sum(math.gcd(n,k)==1 for k in range(1,n+1))%29 for n in range(1,2049)]
for cell in keys:assert cell['key']==(pr if cell['family']=='prime_minus_one' else phi)
old=json.loads((R.parent/'worker-m/M25/keys.json').read_text());assert all(c['key'][:1024]==next(o['key'] for o in old if o['id']==c['id']) for c in keys)
# Every saved path, including reset diagnostics; scalar score resets LM only at declared cuts.
pathcount=positions=0;maxerr=0.;packetrows=[]
def replay(z,a,cell,reset):
 global pathcount,positions,maxerr
 c=z['cipher'];j=0;ctx=(29,29);score=0.;trace=[]
 for i,(p,t) in enumerate(zip(a['plain'],a['reject_counts'])):
  if i in z['cuts']:ctx=(29,29)
  if reset and i in z['cuts']:j=0
  prev=None if i==0 or reset and i in z['cuts'] else c[i-1]
  rejected=[];burned=[];start=j
  for k in range(t):
   assert prev is not None and (p-cell['sign']*cell['key'][j])%29==prev
   rejected.append(j);burned.append(j+1);j+=2
  assert j<2048 and (p-cell['sign']*cell['key'][j])%29==c[i]
  trace.append(dict(i=i,start=start,accepted=j,after=j+1,rejected=rejected,burned=burned));j+=1
  ctx,w=emission(ctx,p,i in z['ends']);score+=w+t*math.log(.83)+(math.log(.17) if prev==c[i] else 0)
 assert j==a['used'] and trace==a['walk'];err=abs(score-a['total']);maxerr=max(maxerr,err);assert err<1e-9
 assert abs(a['score']-score/(len(c)+len(z['ends'])))<1e-12
 pathcount+=1;positions+=len(c)
for path in sorted(Q.glob('*.json.gz')):
 if not(path.stem.startswith('control-') and not path.stem.startswith('control-summary') or path.name=='real.json.gz' or path.name.startswith('null-')):continue
 z=load(path)
 for row in z['rows']:
  cell=next(c for c in keys if c['id']==row['id'])
  for a in row['decode']['alternatives']:replay(z,a,cell,False)
 cell=next(c for c in keys if c['id']==z['rows'][0]['id'])
 for a in z['top16']['alternatives']:replay(z,a,cell,False)
 for row in z['reset']:
  cell=next(c for c in keys if c['id']==row['id'])
  for a in row['decode']['alternatives']:replay(z,a,cell,True)
 packetrows.append({'file':path.name,'best':z['rows'][0]['id'],'score':z['rows'][0]['score']})
controls=[]
for ix in range(4):
 f=load(Q/f'fixture-{ix}.json.gz');cell=next(c for c in keys if c['id']==f['cell_id']);rng=random.Random(f['seed']);c=[];j=0;events=[]
 for p in f['plain']:
  decisions=[];rejected=[];burned=[]
  while True:
   v=(p-cell['sign']*cell['key'][j])%29
   if c and v==c[-1]:
    u=rng.random();decisions.append(u)
    if u<.83:rejected.append(j);burned.append(j+1);j+=2;continue
   break
  c.append(v);events.append(dict(rejected=rejected,burned=burned,accepted=j,random_decisions=decisions));j+=1
 assert c==f['cipher'] and events==f['events'] and j==f['used']
 for src in f['maps']:
  p=pathlib.Path(src['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==src['sha256']
  raw=p.read_text();abc='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';plain=[abc.index(ch) for ch in raw if ch in abc];assert plain==f['plain'][src['start']:src['start']+src['length']]
 controls.append({'ix':ix,'used':j,'cuts':[{ 'index':cut,'event':events[cut],'previous':c[cut-1],'cipher':c[cut]} for cut in f['cuts']],'summary':load(Q/f'control-summary-{ix}.json.gz')})
out={'status':'PASS','tiny_cases':cases,'controls':controls,'keys_verified':4,'paths_replayed':pathcount,'positions_replayed':positions,'max_score_error':maxerr,'packets':packetrows}
(R/'result.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ('tiny_cases','controls','packets')})
