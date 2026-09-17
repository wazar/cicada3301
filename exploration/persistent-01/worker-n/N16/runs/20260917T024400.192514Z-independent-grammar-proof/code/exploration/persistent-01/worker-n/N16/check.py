import json,gzip,itertools,hashlib,random
from pathlib import Path
from collections import Counter
D=Path(__file__).parent;O=Path('exploration/persistent-01/worker-p/P20');GP='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';TR=['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA']
words='.- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- .-- -..- -.-- --.. ----- .---- ..--- ...-- ....- ..... -.... --... ---.. ----.'.split();codes=set(words);MC=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',words));symbols='.-g'
# Independent automaton: all nonempty valid code prefixes plus one/two gap states.
states={v[:i] for v in codes for i in range(1,len(v)+1)}|{'G','GG'}
def transition(s,t):
 if t=='g':return 'GG' if s=='G' else 'G' if s in codes else None
 x=t if s in {'G','GG'} else s+t
 return x if x in states else None
def valid(text):
 active=states.copy()
 for t in text:active={u for s in active if (u:=transition(s,t)) is not None}
 return bool(active)
def rebuilt(c):
 out=[];n=len(c)
 def push(start,req):
  allowed={}
  for j,mask in enumerate(req):
   rune=c[start+j];allowed[rune]=allowed.get(rune,{0,1,2})&{v for v in range(3) if mask>>v&1}
  if any(not x for x in allowed.values()):return
  out.append(tuple(sorted((r,sum(1<<v for v in values)) for r,values in allowed.items())))
 for i in range(n-2):push(i,[4]*3)
 for i in range(n-5):push(i,[3]*6)
 for length in range(1,6):
  for seq in itertools.product((0,1),repeat=length):
   w=''.join(symbols[x] for x in seq);mask=[1<<x for x in seq]
   if w not in codes:
    for i in range(n-length-1):push(i,[4]+mask+[4])
   if length<n:
    if not any(v.endswith(w) for v in codes):push(0,mask+[4])
    if not any(v.startswith(w) for v in codes):push(n-length-1,[4]+mask)
   elif length==n and not any(w in v for v in codes):push(0,mask)
 return out
visited=0
def proof(tree,cs,domains):
 global visited
 visited+=1;ds=[x.copy() for x in domains]
 for ci,v,newmask in tree['trail']:
  cl=cs[ci];unfixed=[]
  for x,m in cl:
   req={a for a in range(3) if m>>a&1};assert ds[x]&req
   if ds[x]-req:unfixed.append((x,req))
  assert len(unfixed)==1 and unfixed[0][0]==v
  ds[v]-=unfixed[0][1];assert sum(1<<a for a in ds[v])==newmask and ds[v]
 if 'conflict' in tree:
  assert all(ds[v]<={a for a in range(3) if m>>a&1} for v,m in cs[tree['conflict']]);return False
 if 'sat' in tree:
  a=tree['sat'];assert all(v in d for v,d in zip(a,ds));assert all(any(not(m>>a[v]&1) for v,m in cl) for cl in cs);return True
 v=tree['var'];assert len(ds[v])>1;seen=[];sat=False
 for value,ch in tree['children']:
  assert value in ds[v] and value not in seen;seen.append(value);dd=[x.copy() for x in ds];dd[v]={value};result=proof(ch,cs,dd)
  if result:assert ch is tree['children'][-1][1];sat=True
 if not sat:assert set(seen)==ds[v]
 return sat
small=json.load(gzip.open(D/'tiny-exhaustive.json.gz','rt'));assignments=0
for case in small:
 c=case['cipher'];cs=rebuilt(c);good=0
 for a in itertools.product(range(3),repeat=max(c)+1):
  t=''.join(symbols[a[v]] for v in c);grammar=valid(t);constraints=all(any(not(m>>a[v]&1) for v,m in cl) for cl in cs);assert grammar==constraints;good+=grammar;assignments+=1
 assert good==case['valid'];assert proof(case['result']['proof'],cs,[{0,1,2} for _ in range(max(c)+1)])==(case['result']['status']=='SAT')
rows=[];controls=[]
for file in sorted(D.glob('*.json.gz')):
 if file.name=='tiny-exhaustive.json.gz':continue
 r=json.load(gzip.open(file,'rt'));c=r['cipher'];cs=[tuple(map(tuple,x)) for x in r['clauses']];assert cs==rebuilt(c);assert len(cs)==len(r['clause_maps'])
 for cl,m in zip(cs,r['clause_maps']):
  start=m['start'];assert c[start:start+len(m['runes'])]==m['runes']
  if r.get('source_char_positions'):assert m['source_char_positions']==r['source_char_positions'][start:start+len(m['runes'])]
 if r['status']!='UNKNOWN':assert proof(r['proof'],cs,[{0,1,2} for _ in range(29)])==(r['status']=='SAT')
 if r['status']=='SAT':
  text=''.join(symbols[r['map'][v]] for v in c);assert text==r['trits'] and valid(text)
  for run in r['decoded_runs']:
   assert text[run['start']:run['end']]==run['marks'];assert run['possible_letters']
 if 'second_map_result' in r:
  s=r['second_map_result'];cc=cs+[tuple((v,1<<r['map'][v]) for v in sorted(set(c)))]
  if s['status']!='UNKNOWN':assert proof(s['proof'],cc,[{0,1,2} for _ in range(29)])==(s['status']=='SAT')
  if s['status']=='SAT':assert valid(s['trits']) and s['trits']==''.join(symbols[s['map'][v]] for v in c) and s['trits']!=r['trits']
 if 'source_fixture' in r:
  path=Path(r['source_fixture']);assert hashlib.sha256(path.read_bytes()).hexdigest()==r['source_sha256'];f=json.load(gzip.open(path,'rt'))
  if file.name.startswith('control'):
   assert c==sum([p['indices'] for p in f['pages']],[]);assert r['planted_trits']==f['trits'];inv={x:k for k,b in f['bins'].items() for x in b};assert ''.join(inv[x] for x in c)==f['trits'];assert valid(f['trits'])
   raw=Path(f['source']).read_text();assert hashlib.sha256(Path(f['source']).read_bytes()).hexdigest()==f['source_sha256'];ww=[];word=''
   for ch in raw+' ':
    if ch in GP:word+=TR[GP.index(ch)]
    elif word:ww.append(word);word=''
   assert ww==f['words'];expected='gg'.join('g'.join(MC[x] for x in w) for w in ww);assert expected==f['trits'];controls.append({'name':file.name,'map_errors':sum(symbols[r['map'][v]]!=inv[v] for v in set(c)),'trit_errors':sum(a!=b for a,b in zip(r['trits'],f['trits']))})
  else:
   pages=[p for p in json.loads(Path('exploration/persistent-01/worker-f/F06-maps.json').read_text()) if p['page'] in [0,1]];rg=random.Random(f['seed'])
   for p,fp in zip(pages,f['pages']):
    z=[p['indices'][0]]
    for a,b in zip(p['indices'],p['indices'][1:]):z.append(z[-1] if a==b else rg.choice([i for i in range(29) if i!=z[-1]]))
    assert z==fp['indices']
   assert c==next(p['indices'] for p in f['pages'] if p['page']==r['page'])
 elif file.name.startswith('actual'):
  pp=next(p for p in json.loads(Path('exploration/persistent-01/worker-f/F06-maps.json').read_text()) if p['page']==r['page']);assert c==pp['indices'] and r['source_char_positions']==pp['source_char_positions']
 rows.append({'name':file.name,'status':r['status'],'nodes':r['nodes'],'seconds':r['seconds'],'second_status':r.get('second_map_result',{}).get('status')})
result={'PASS':True,'independent_automaton_exhaustive_assignments':assignments,'proof_nodes_verified':visited,'rows':rows,'controls':controls};(D/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
