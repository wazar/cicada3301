from pathlib import Path
import json,gzip,collections,re,ast,random,hashlib,itertools
R=Path(__file__).parent;B=R.parent;Q=B/'coordinator/Q08-token-grammar';data=json.load(gzip.open(Q/'controls.json.gz','rt'));rng=random.Random(6081717)
def parse(s,d):
 trie={}
 for i,w in enumerate(d):
  at=trie
  for c in w:at=at.setdefault(c,{})
  assert 'id' not in at;at['id']=i
 ids=[];pos=0
 while pos<len(s):
  at=trie;j=pos;last=None
  while j<len(s) and s[j] in at:
   at=at[s[j]];j+=1
   if 'id' in at:last=(j,at['id'])
  assert last;pos,v=last;ids.append(v)
 return ids
n=0;selfmerges=0
for rec in data['tiny']:
 k=rec['base'];d=list('ABC'[:k]);merges=[]
 while len(d)<k+4:
  u,v=rng.randrange(len(d)),rng.randrange(len(d));w=d[u]+d[v]
  if w in d or len(w)>12:continue
  merges.append([u,v,len(d)]);d.append(w)
 assert d==rec['dictionary'] and merges==rec['merges'];forbidden=[]
 for u,v,w in merges:
  assert d[w]==d[u]+d[v] and d[u] and d[v];pair=[u,v] if u!=v else [u,w];assert pair[0]!=pair[1] and parse(d[pair[0]]+d[pair[1]],d)[0]!=pair[0];forbidden.append(pair);selfmerges+=u==v
 assert forbidden==rec['forbidden'];expected=[''.join(t) for size in range(1,8) for t in itertools.product('ABC'[:k],repeat=size)];assert expected==[x[0] for x in rec['cases']]
 for s,ids in rec['cases']:
  out=parse(s,d);assert out==ids and ''.join(d[i] for i in out)==s and not any(tuple(p) in set(zip(ids,ids[1:])) for p in forbidden);n+=1
src=data['source'];p=Path(src['source']);raw=p.read_text();assert hashlib.sha256(p.read_bytes()).hexdigest()==src['source_sha256'];gp=Path('liber-primus/src/lp/gematria.py');table=next(ast.literal_eval(x.value) for x in ast.parse(gp.read_text()).body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='GEMATRIA' for y in x.targets));trans={r:t for _,r,t,_ in table};words=[];current=[]
for ch in raw:
 if ch in trans:current.append(trans[ch])
 elif current:words.append(''.join(current));current=[]
if current:words.append(''.join(current))
assert words==[x['source'] for x in src['words']] and len(words)==208;perm=list(range(29));rng.shuffle(perm);assert perm==src['permutation']
for word,row in zip(words,src['words']):
 ids=parse(word,src['dictionary']);assert ids==row['tokens'] and [perm[i] for i in ids]==row['runes']
actual=json.loads((Q/'result.json').read_text());f= B/'worker-f/F06-maps.json';pages=json.loads(f.read_text());counts=collections.Counter();witness={}
for p in pages:
 assert p['page'] not in [4,9,14,19,24,29,34,39,44,50,54]
 for wi,w in enumerate(p['words']):
  for j in range(w['start'],w['end']-1):
   a,b=p['indices'][j:j+2];key=f'{a},{b}';counts[key]+=1;witness.setdefault(key,dict(page=p['page'],word=wi,within_word=j-w['start'],runes=[a,b],rune_positions=[j,j+1],source_char_positions=p['source_char_positions'][j:j+2]))
assert dict(counts)==actual['counts'] and witness==actual['witnesses'];assert all(f'{a},{b}' in counts for a in range(29) for b in range(29) if a!=b);assert actual['compatible']==False and actual['missing_nonself']==[];assert len(counts)==836 and sum(counts.values())==8111 and n==42396
out=dict(status='PASS',control_strings=n,self_merge_cases=selfmerges,source_words=len(words),all_observed_pair_witnesses=len(counts),nonself_types=812,total_occurrences=sum(counts.values()),scope='Theoretical generalization of existing P24 complete-pair certificate; no new cipher coverage')
(R/'result.json').write_text(json.dumps(out,indent=2));print(out)
