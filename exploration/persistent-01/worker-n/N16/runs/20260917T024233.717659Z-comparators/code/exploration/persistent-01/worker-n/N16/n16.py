import json,gzip,time,itertools,sys,hashlib,datetime
from pathlib import Path
D=Path(__file__).parent;O=Path('exploration/persistent-01/worker-p/P20')
MC=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789','.- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --.. ----- .---- ..--- ...-- ....- ..... -.... --... ---.. ----.'.split()))
CODES=set(MC.values());CHARS='.-g';CAPSEC=120;CAPN=1000000
SUF={w[i:] for w in CODES for i in range(len(w))};PRE={w[:i] for w in CODES for i in range(1,len(w)+1)};SUB={w[i:j] for w in CODES for i in range(len(w)) for j in range(i+1,len(w)+1)}
def grammar(t):
 if 'ggg' in t:return False
 parts=t.split('g')
 if len(parts)==1:return t in SUB
 return (not parts[0] or parts[0] in SUF) and (not parts[-1] or parts[-1] in PRE) and all(not x or x in CODES for x in parts[1:-1])
def parse(t):
 rev={v:k for k,v in MC.items()};runs=[];start=0
 for i in range(len(t)+1):
  if i==len(t) or t[i]=='g':
   if i>start:
    w=t[start:i];edge=start==0 or i==len(t);possible=sorted(k for k,v in MC.items() if (w in v if start==0 and i==len(t) else v.endswith(w) if start==0 else v.startswith(w) if i==len(t) else w==v));runs.append({'start':start,'end':i,'marks':w,'edge_partial_allowed':edge,'possible_letters':possible})
   start=i+1
 return runs
def constraints(c,positions=None):
 clauses=[];maps=[]
 def add(ids,req,kind,start):
  d={}
  for v,m in zip(ids,req):d[v]=d.get(v,7)&m
  if any(v==0 for v in d.values()):return
  clauses.append(sorted(d.items()));maps.append({'kind':kind,'start':start,'runes':ids,'required_masks':req,'source_char_positions':positions[start:start+len(ids)] if positions else None})
 n=len(c)
 for i in range(n-2):add(c[i:i+3],[4]*3,'three-gaps',i)
 for i in range(n-5):add(c[i:i+6],[3]*6,'six-marks',i)
 for size in range(1,6):
  for bits in itertools.product('.-',repeat=size):
   word=''.join(bits);m=[1 if t=='.' else 2 for t in word]
   if word not in CODES:
    for i in range(n-size-1):add(c[i:i+size+2],[4]+m+[4],'invalid-complete-code',i)
   if size<n:
    if word not in SUF:add(c[:size+1],m+[4],'invalid-left-edge',0)
    if word not in PRE:add(c[-size-1:],[4]+m,'invalid-right-edge',n-size-1)
   elif size==n and word not in SUB:add(c,m,'invalid-whole-fragment',0)
 return clauses,maps
def solve(clauses,n=29):
 start=time.monotonic();nodes=0
 def rec(dom):
  nonlocal nodes
  nodes+=1
  if nodes>CAPN or time.monotonic()-start>CAPSEC or datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc):raise TimeoutError
  dom=dom.copy();trail=[]
  while True:
   active=[];unit=None
   for ci,cl in enumerate(clauses):
    undec=[];satisfied=False
    for v,m in cl:
     if dom[v]&m==0:satisfied=True;break
     if dom[v]&~m:undec.append((v,m))
    if satisfied:continue
    if not undec:return {'trail':trail,'conflict':ci},None
    if len(undec)==1:unit=(ci,*undec[0]);break
    active.append(undec)
   if unit is None:break
   ci,v,m=unit;dom[v]&=~m;trail.append([ci,v,dom[v]])
  if not active:
   a=[next(i for i in range(3) if mask&(1<<i)) for mask in dom];return {'trail':trail,'sat':a},a
  freq=[0]*n;short=min(len(x) for x in active)
  for cl in active:
   if len(cl)==short:
    for v,m in cl:freq[v]+=1
  var=max((v for v in range(n) if dom[v].bit_count()>1),key=lambda v:(freq[v],-dom[v].bit_count(),-v));children=[]
  for value in range(3):
   if dom[var]&(1<<value):
    dd=dom.copy();dd[var]=1<<value;child,w=rec(dd);children.append([value,child])
    if w is not None:return {'trail':trail,'var':var,'children':children},w
  return {'trail':trail,'var':var,'children':children},None
 try:
  tree,w=rec([7]*n);return {'status':'SAT' if w is not None else 'UNSAT','map':w,'proof':tree,'nodes':nodes,'seconds':time.monotonic()-start}
 except TimeoutError:return {'status':'UNKNOWN','map':None,'proof':None,'nodes':nodes,'seconds':time.monotonic()-start}
def save(name,obj):
 with gzip.open(D/(name+'.json.gz'),'wt') as f:json.dump(obj,f,separators=(',',':'))
def run(name,c,extra={},second=False):
 cs,maps=constraints(c,extra.get('source_char_positions'));r=solve(cs);r.update(cipher=c,clauses=cs,clause_maps=maps,**extra)
 if r['status']=='SAT':
  t=''.join(CHARS[r['map'][v]] for v in c);assert grammar(t);r.update(trits=t,decoded_runs=parse(t))
  if second:
   blocking=[(v,1<<r['map'][v]) for v in sorted(set(c))];s=solve(cs+[blocking]);r['second_map_result']=s
   if s['status']=='SAT':
    tt=''.join(CHARS[s['map'][v]] for v in c);assert tt!=t and grammar(tt);s.update(trits=tt,decoded_runs=parse(tt))
 save(name,r);print(name,r['status'],r['nodes'],r['seconds'],r.get('second_map_result',{}).get('status'),flush=True);return r
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='pilot':
  # Complete ternary enumeration compares independently expressed stream grammar with clauses.
  fixtures=[]
  for c in [[0],[0,1],[0,0,1],[0,1,2,0],[0,1,2,3,0,1,2],[0,1,2,3,4,0,1,2],[0,0,0],[0]*6]:
   cs,cm=constraints(c);ok=0
   for a in itertools.product(range(3),repeat=max(c)+1):
    t=''.join(CHARS[a[v]] for v in c);sat=all(not all(m&(1<<a[v]) for v,m in cl) for cl in cs);assert sat==grammar(t),(c,a,t);ok+=sat
   result=solve(cs,max(c)+1);assert (result['status']=='SAT')==bool(ok);fixtures.append({'cipher':c,'assignments':3**(max(c)+1),'valid':ok,'result':result})
  save('tiny-exhaustive',fixtures)
  # Three literal examples exercise full letters and word gaps with known category IDs.
  for text in ['...g---g...','.-gg-...','-----g.----']:
   c=[CHARS.index(v) for v in text];cs,_=constraints(c);assert grammar(text);assert all(not all(m&(1<<v) for v,m in cl) for cl in cs)
  fixture=json.load(gzip.open(O/'control-0.json.gz','rt'));c=sum([p['indices'] for p in fixture['pages']],[]);assert ''.join(fixture['maps'][i]['trit'] for i in range(len(c)))==fixture['trits'];run('control-0',c,{'source_fixture':str(O/'control-0.json.gz'),'source_sha256':hashlib.sha256((O/'control-0.json.gz').read_bytes()).hexdigest(),'planted_trits':fixture['trits']})
 elif mode=='controls':
  for k in range(1,4):
   path=O/f'control-{k}.json.gz';f=json.load(gzip.open(path,'rt'));run(f'control-{k}',sum([p['indices'] for p in f['pages']],[]),{'source_fixture':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'planted_trits':f['trits']})
 elif mode=='actual':
  for k in range(4):assert json.load(gzip.open(D/f'control-{k}.json.gz','rt'))['status']=='SAT'
  for p in json.loads(Path('exploration/persistent-01/worker-f/F06-maps.json').read_text()):
   if p['page'] in [0,1]:run(f"actual-{p['page']}",p['indices'],{'page':p['page'],'source_char_positions':p['source_char_positions']},True)
 elif mode=='nulls':
  for k in range(19):
   path=O/f'null-{k}.json.gz';f=json.load(gzip.open(path,'rt'))
   for p in f['pages']:run(f"null-{k}-{p['page']}",p['indices'],{'page':p['page'],'P20_seed':f['seed'],'source_fixture':str(path),'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
