from pathlib import Path
import json,gzip,random,itertools,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3]
def encode(s,d):
 out=[];i=0
 while i<len(s):
  hit=max((j for j,w in enumerate(d) if s.startswith(w,i)),key=lambda j:len(d[j]));out.append(hit);i+=len(d[hit])
 return out
def forbidden(d,merges):
 out=[]
 for u,v,w in merges:
  assert d[w]==d[u]+d[v]
  a,b=(u,v) if u!=v else (u,w)
  assert a!=b and encode(d[a]+d[b],d)[0]!=a
  out.append([a,b])
 return out
rng=random.Random(6081717);controls=[];ncases=0
for k in [2,3]:
 for rep in range(12):
  d=list('ABC'[:k]);m=[]
  while len(d)<k+4:
   u,v=rng.randrange(len(d)),rng.randrange(len(d));w=d[u]+d[v]
   if w in d or len(w)>12:continue
   m.append([u,v,len(d)]);d.append(w)
  bad=forbidden(d,m);cases=[]
  for n in range(1,8):
   for t in itertools.product('ABC'[:k],repeat=n):
    s=''.join(t);out=encode(s,d);pairs=set(zip(out,out[1:]));assert not any(tuple(p) in pairs for p in bad);cases.append([s,out]);ncases+=1
  controls.append(dict(base=k,dictionary=d,merges=m,forbidden=bad,cases=cases))
# Actual source-backed positive panel: dictionary chosen in card, no training.
src=R/'audit/parallel-01/reference/sources/solved_welcome.txt'
if not src.exists():
 candidates=sorted((R/'audit/parallel-01/reference/sources').glob('solved_*.txt'));src=candidates[0]
import ast
gp=R/'liber-primus/src/lp/gematria.py'
node=ast.parse(gp.read_text()); table=next(ast.literal_eval(n.value) for n in node.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GEMATRIA' for t in n.targets))
trans={r:t for _,r,t,_ in table};text=''.join(trans.get(c,' ') for c in src.read_text());import re
words=re.findall('[A-Z]+',text);assert len(words)>10;d=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')+['TH','HE','IN'];m=[[19,7,26],[7,4,27],[8,13,28]];bad=forbidden(d,m);perm=list(range(29));rng.shuffle(perm);outs=[]
for word in words:
 ids=encode(word,d);out=[perm[i] for i in ids];assert ''.join(d[i] for i in ids)==word;outs.append(dict(source=word,tokens=ids,runes=out))
pairs={(a,b) for r in outs for a,b in zip(r['runes'],r['runes'][1:])};assert all((perm[a],perm[b]) not in pairs for a,b in bad)
control=dict(source=str(src.relative_to(R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),transliteration_table_sha256=hashlib.sha256(gp.read_bytes()).hexdigest(),dictionary=d,merges=m,permutation=perm,forbidden=bad,words=outs)
with gzip.open(O/'controls.json.gz','wt') as f:json.dump(dict(tiny=controls,source=control),f,separators=(',',':'))
# Only now apply necessary condition to real admitted units.
p=R/'exploration/persistent-01/worker-f/F06-maps.json';pages=json.loads(p.read_text());counts={};witness={};total=0
for page in pages:
 assert page['page'] not in [4,9,14,19,24,29,34,39,44,50,54]
 for wi,w in enumerate(page['words']):
  seq=page['indices'][w['start']:w['end']]
  for j,(a,b) in enumerate(zip(seq,seq[1:])):
   key=f'{a},{b}';counts[key]=counts.get(key,0)+1;total+=1
   witness.setdefault(key,dict(page=page['page'],word=wi,within_word=j,runes=[a,b],rune_positions=[w['start']+j,w['start']+j+1],source_char_positions=w['source_char_positions'][j:j+2]))
missing=[[a,b] for a in range(29) for b in range(29) if a!=b and f'{a},{b}' not in counts]
result=dict(input_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),pages=[p['page'] for p in pages],total_edges=total,distinct_edges=len(counts),missing_nonself=missing,compatible=bool(missing),counts=counts,witnesses=witness,control_strings=ncases,source_control_words=len(words),scope='shared longest-prefix dictionary containing a binary merge with retained children; necessary-condition compatibility only')
(O/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['counts','witnesses']}))
