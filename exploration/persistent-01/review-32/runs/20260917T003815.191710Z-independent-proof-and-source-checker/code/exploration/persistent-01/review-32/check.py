from pathlib import Path
import json,gzip,hashlib,itertools,random,re,collections
R=Path(__file__).parent;B=R.parent;ROOT=B.parent.parent;P=B/'worker-p/P20';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';MC=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789','.- -... -.-. -.. . ..-. --. .... .. .--- -.- .-.. -- -. --- .--. --.- .-. ... - ..- ...- --.?' .split())) if False else {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.'}
D=[p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,1]];(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in list(P.glob('*'))+[B/'worker-p/p20.py',B/'worker-f/F06-maps.json',ROOT/'KNOWLEDGE.json']:
 if p.is_file():
  raw=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
  if p.suffix!='.gz':(R/'snapshots'/p.name).write_bytes(raw)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
nodecount=0;leafcount=0;clauseuse=collections.Counter()
def checkproof(cs,r):
 global nodecount,leafcount
 def reduce(c,assignment):
  pending=[]
  for lit in c:
   v=abs(lit)-1
   if v not in assignment:pending.append(lit)
   elif assignment[v]==int(lit>0):return None
  return pending
 def visit(tree,assignment):
  global nodecount,leafcount
  nodecount+=1;assignment=assignment.copy()
  for cid,lit in tree['trail']:
   assert 0<=cid<len(cs);assert reduce(cs[cid],assignment)==[lit];v=abs(lit)-1;assert v not in assignment;assignment[v]=int(lit>0);clauseuse[cid]+=1
  if 'conflict' in tree:
   assert 'variable' not in tree and not tree.get('sat');assert reduce(cs[tree['conflict']],assignment)==[];clauseuse[tree['conflict']]+=1;leafcount+=1;return False
  if tree.get('sat'):
   assert r['status']=='SAT';assert all(reduce(c,assignment) is None for c in cs);leafcount+=1;return True
  v=tree['variable'];assert v not in assignment;left=visit(tree['zero'],assignment|{v:0})
  if 'one' not in tree:assert r['status']=='SAT' and left;return True
  right=visit(tree['one'],assignment|{v:1});return left or right
 if r['status']=='UNKNOWN':assert r['proof'] is None and r['witness'] is None;return
 before=nodecount;sat=visit(r['proof'],{});assert sat==(r['status']=='SAT');assert nodecount-before==r['nodes']
 if sat:
  a=r['witness'];assert all(any(a[abs(v)-1]==int(v>0) for v in c) for c in cs)
 else:assert r['witness'] is None

def sourceclauses(pages):
 cs=[];maps=[]
 for p in pages:
  for length,sign in [(3,-1),(6,1)]:
   for start in range(len(p['indices'])-length+1):
    runes=p['indices'][start:start+length];cs.append(sorted({sign*(r+1) for r in runes}));maps.append(dict(page=p['page'],start=start,length=length,indices=runes,source_char_positions=p.get('source_char_positions',[])[start:start+length]))
 return cs,maps
small=json.load(gzip.open(P/'small-exhaustive.json.gz','rt'))
for q in small:
 cs=q['clauses'];brute=any(all(any(a[abs(v)-1]==int(v>0) for v in c) for c in cs) for a in itertools.product(range(2),repeat=8));assert brute==(q['result']['status']=='SAT');checkproof(cs,q['result'])
records=[];realproofclauses=None
for path in sorted(P.glob('*.json.gz')):
 if path.name in ['small-exhaustive.json.gz','controls-summary.json']:continue
 z=json.load(gzip.open(path,'rt'))
 if not isinstance(z,dict) or 'clauses' not in z:continue
 cs,maps=sourceclauses(z['pages']);assert cs==z['clauses'] and maps==z['clause_maps'];checkproof(cs,z)
 if path.name.startswith('actual-'):
  actual=[p for p in D if path.name=='actual-joint.json.gz' or str(p['page'])==path.name.split('-')[2].split('.')[0]];assert z['pages']==actual
 elif path.name.startswith('null-'):
  rng=random.Random(z['seed']);ss=[]
  for p in D:
   a=[p['indices'][0]]
   for x,y in zip(p['indices'],p['indices'][1:]):a.append(a[-1] if x==y else rng.choice([k for k in range(29) if k!=a[-1]]))
   ss.append(a)
  assert ss==[p['indices'] for p in z['pages']]
 else:
  words=z['words'];rng=random.Random(z['seed']);ids=list(range(29));rng.shuffle(ids);bins={'.':ids[:10],'-':ids[10:20],'g':ids[20:]};assert bins==z['bins'];trits='gg'.join('g'.join(MC[ch] for ch in word) for word in words);assert trits==z['trits'];stream=[]
  for t in trits:stream.append(rng.choice([v for v in bins[t] if not stream or v!=stream[-1]]))
  assert stream==sum([p['indices'] for p in z['pages']],[]);assert all(x!=y for x,y in zip(stream,stream[1:]));roles={v:t for t,vs in bins.items() for v in vs};assert ''.join(roles[v] for v in stream)==trits
  assert all(m['rune']==v and m['trit']==t for m,v,t in zip(z['maps'],stream,trits));assert len(z['maps'])==len(stream)
  if 'source' in z:
   source=ROOT/z['source'];raw=source.read_text();assert hashlib.sha256(source.read_bytes()).hexdigest()==z['source_sha256'];table={r['index']:r['transliteration'] for r in json.loads((ROOT/'KNOWLEDGE.json').read_text())['gematria_primus']['table']};ww=[];wm=[]
   for match in re.finditer('['+ABC+']+',raw):
    chars=[]
    for i in range(match.start(),match.end()):chars.extend(dict(source_char=i,rune=ABC.index(raw[i]),latin=ch) for ch in table[ABC.index(raw[i])])
    ww.append(''.join(c['latin'] for c in chars));wm.append(chars)
   assert ww==words and wm==z['word_maps'];assert z['cut']==len(stream)//2
  planted=[int(v in bins['g']) for v in range(29)];assert all(any(planted[abs(v)-1]==int(v>0) for v in c) for c in cs)
 records.append({'file':path.name,'status':z['status'],'clauses':len(cs),'nodes':z['nodes']})
 if path.name=='actual-joint.json.gz':
  # Store source clauses actually cited by full refutation, separately from global counters.
  used=set()
  def collect(t):
   used.update(a for a,v in t['trail'])
   if 'conflict' in t:used.add(t['conflict'])
   for k in ['zero','one']:
    if k in t:collect(t[k])
  collect(z['proof']);realproofclauses=[dict(clause_id=i,clause=cs[i],source=maps[i]) for i in sorted(used)]
(R/'joint-proof-source-clauses.json').write_text(json.dumps(realproofclauses,indent=2));out={'status':'PASS','small_exhaustive_cases':len(small),'proof_nodes_checked':nodecount,'proof_leaves_checked':leafcount,'records':records,'joint_proof_distinct_source_clauses':len(realproofclauses)};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
