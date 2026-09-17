import json,hashlib,gzip,time,random,re,sys,datetime,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'exploration/persistent-01';OUT=BASE/'worker-p/P20'
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
MC=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789','.- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --.. ----- .---- ..--- ...-- ....- ..... -.... --... ---.. ----.'.split()))
def guard():
 assert not (BASE/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(n,x):
 b=json.dumps(x,separators=(',',':')).encode()
 if n.endswith('.gz'):
  with gzip.open(OUT/n,'wb') as f:f.write(b)
 else:(OUT/n).write_bytes(b+b'\n')
def clauses(pages):
 out=[];maps=[]
 for p in pages:
  s=p['indices']
  for n,sign in [(3,-1),(6,1)]:
   for i in range(len(s)-n+1):
    c=sorted(set(sign*(r+1) for r in s[i:i+n]))
    out.append(c);maps.append(dict(page=p['page'],start=i,length=n,indices=s[i:i+n],source_char_positions=p.get('source_char_positions',[])[i:i+n]))
 return out,maps
def solve(cs,n=29):
 start=time.monotonic();nodes=0;pm=[];nm=[]
 for c in cs:
  pm.append(sum(1<<(v-1) for v in c if v>0));nm.append(sum(1<<(-v-1) for v in c if v<0))
 def search(t,f):
  nonlocal nodes
  nodes+=1
  if nodes>1000000 or time.monotonic()-start>120:raise TimeoutError
  trail=[]
  while True:
   active=[];unit=None
   for i,(p,q) in enumerate(zip(pm,nm)):
    if p&t or q&f:continue
    u=(p|q)&~(t|f)
    if not u:return dict(trail=trail,conflict=i),None
    active.append((i,u))
    if u&(u-1)==0:unit=(i,u,bool(p&u));break
   if unit is None:break
   i,u,yes=unit;trail.append([i,u.bit_length() if yes else -u.bit_length()])
   if yes:t|=u
   else:f|=u
  if not active:return dict(trail=trail,sat=True),[(1 if t&(1<<i) else 0) for i in range(n)]
  # Most frequent in shortest currently active clauses, tie lowest ID.
  size=min(u.bit_count() for _,u in active);freq=[0]*n
  for _,u in active:
   if u.bit_count()==size:
    for j in range(n):freq[j]+=bool(u&(1<<j))
  v=max(range(n),key=lambda j:(freq[j],-j));bit=1<<v
  left,w=search(t,f|bit)
  if w is not None:return dict(trail=trail,variable=v,zero=left),w
  right,w=search(t|bit,f)
  return dict(trail=trail,variable=v,zero=left,one=right),w
 try:
  tree,w=search(0,0);return dict(status='SAT' if w is not None else 'UNSAT',witness=w,proof=tree,nodes=nodes,seconds=time.monotonic()-start)
 except TimeoutError:return dict(status='UNKNOWN',witness=None,proof=None,nodes=nodes,seconds=time.monotonic()-start)
def verify(cs,r):
 def val(v,a):return None if abs(v)-1 not in a else a[abs(v)-1]==(v>0)
 def walk(node,a):
  a=a.copy()
  for ci,v in node['trail']:
   c=cs[ci];assert not any(val(x,a) is True for x in c)
   undec=[x for x in c if val(x,a) is None];assert undec==[v]
   a[abs(v)-1]=v>0
  if 'conflict' in node:assert all(val(v,a) is False for v in cs[node['conflict']]);return
  if node.get('sat'):assert all(any(val(v,a) is True for v in c) for c in cs);return
  v=node['variable'];assert v not in a
  walk(node['zero'],a|{v:False})
  if 'one' in node:walk(node['one'],a|{v:True})
  else:assert r['status']=='SAT'
 if r['status']=='UNKNOWN':return
 walk(r['proof'],{})
 if r['status']=='SAT':assert all(any(bool(r['witness'][abs(v)-1])==(v>0) for v in c) for c in cs)
def run(name,pages,extra={}):
 guard();cs,maps=clauses(pages);r=solve(cs);verify(cs,r);r.update(clauses=cs,clause_maps=maps,pages=pages,**extra);save(name+'.json.gz',r);print(name,r['status'],len(cs),r['nodes'],r['seconds'],flush=True);return r
def encode(words,seed):
 rng=random.Random(seed);ids=list(range(29));rng.shuffle(ids);bins={'.':ids[:10],'-':ids[10:20],'g':ids[20:]};s=[];maps=[];trits=[]
 for wi,w in enumerate(words):
  for li,ch in enumerate(w):
   if li==0 and wi>0:
    for gi in range(2):trits.append(('g',dict(word=wi,letter=li,boundary='word',gap=gi)))
   elif li>0:trits.append(('g',dict(word=wi,letter=li,boundary='letter')))
   for mi,t in enumerate(MC[ch]):trits.append((t,dict(word=wi,letter=li,morse_index=mi,char=ch)))
 for t,m in trits:
  pool=[x for x in bins[t] if not s or x!=s[-1]];s.append(rng.choice(pool));maps.append(m|dict(trit=t,rune=s[-1]))
 inv={v:k for k,b in bins.items() for v in b};stream=''.join(inv[x] for x in s);reverse={v:k for k,v in MC.items()}
 recovered=[''.join(reverse[c] for c in w.split('g')) for w in stream.split('gg')]
 assert recovered==words and all(a!=b for a,b in zip(s,s[1:]))
 return s,dict(seed=seed,bins=bins,maps=maps,words=words,trits=stream)
def controls():
 rng=random.Random(520900);small=[]
 for k in range(200):
  n=8;cs=[]
  for _ in range(rng.randint(5,40)):
   vs=rng.sample(range(1,n+1),rng.randint(1,5));cs.append(sorted(v*rng.choice([-1,1]) for v in vs))
  brute=any(all(any(bool(a[abs(v)-1])==(v>0) for v in c) for c in cs) for a in itertools.product([0,1],repeat=n))
  r=solve(cs,n);verify(cs,r);assert (r['status']=='SAT')==brute;small.append(dict(clauses=cs,result=r))
 save('small-exhaustive.json.gz',small)
 translit={x['index']:x['transliteration'] for x in json.loads((ROOT/'KNOWLEDGE.json').read_text())['gematria_primus']['table']}
 rows=[]
 for ix,name in enumerate(['0_welcome','jpg107-167','p56_an_end','p57_parable']):
  f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');raw=f.read_text();words=[];wm=[]
  for m in re.finditer('['+ABC+']+',raw):
   w='';chars=[]
   for pos in range(m.start(),m.end()):
    tx=translit[ABC.index(raw[pos])]
    for ch in tx:chars.append(dict(source_char=pos,rune=ABC.index(raw[pos]),latin=ch));w+=ch
   words.append(w);wm.append(chars)
  s,x=encode(words,520100+ix);cut=len(s)//2
  p=[dict(page=0,indices=s[:cut]),dict(page=1,indices=s[cut:])]
  r=run('control-'+str(ix),p,x|dict(source=str(f.relative_to(ROOT)),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),word_maps=wm,cut=cut))
  assert r['status']=='SAT';rows.append(dict(name=name,status=r['status'],length=len(s),nodes=r['nodes'],seconds=r['seconds']))
 s,x=encode(['ABCDEFGHIJKLMNOPQRSTUVWXYZ','0123456789'],520104);r=run('alphabet-control',[dict(page=0,indices=s)],x);assert r['status']=='SAT'
 save('controls-summary.json',dict(small_cases=200,rows=rows,alphabet=r['status']))
def actual():
 assert (OUT/'controls-summary.json').exists()
 pages=[p for p in json.loads((BASE/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,1]];pages.sort(key=lambda p:p['page']);assert [p['page'] for p in pages]==[0,1]
 run('actual-joint',pages)
 for p in pages:run('actual-page-'+str(p['page']),[p])
 for k in range(19):
  rng=random.Random(520300+k);ps=[]
  for p in pages:
   s=[p['indices'][0]]
   for a,b in zip(p['indices'],p['indices'][1:]):
    if a==b:s.append(s[-1])
    else:s.append(rng.choice([i for i in range(29) if i!=s[-1]]))
   ps.append(dict(page=p['page'],indices=s))
  run('null-'+str(k),ps,dict(seed=520300+k))
if __name__=='__main__':
 guard();{'controls':controls,'actual':actual}[sys.argv[1]]()
