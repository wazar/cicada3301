from pathlib import Path
import json,gzip,itertools
O=Path(__file__).resolve().parent;R=O.parents[3];c=json.load(gzip.open(O/'controls.json.gz','rt'));n=0
for panel in c['tiny']+[c['source']]:
 d=panel['dictionary'];trie={}
 for i,w in enumerate(d):
  t=trie
  for ch in w:t=t.setdefault(ch,{})
  t['END']=i
 def parse(s):
  out=[];start=0
  while start<len(s):
   t=trie;j=start;best=None
   while j<len(s) and s[j] in t:
    t=t[s[j]];j+=1
    if 'END' in t:best=(j,t['END'])
   assert best is not None;start,i=best;out.append(i)
  return out
 for u,v,w in panel['merges']:
  assert d[w]==d[u]+d[v]
  a,b=(u,v) if u!=v else (u,w)
  assert a!=b and d[a]+d[b]==''.join(d[t] for t in parse(d[a]+d[b]))
  assert parse(d[a]+d[b])[0]!=a
 rows=panel.get('cases',[[r['source'],r['tokens']] for r in panel.get('words',[])])
 for text,out in rows:
  assert parse(text)==out;n+=1
  assert not set(map(tuple,panel['forbidden'])) & set(zip(out,out[1:]))
r=json.load(open(O/'result.json'));p=json.load(open(R/'exploration/persistent-01/worker-f/F06-maps.json'));pc={x['page']:x for x in p};cnt={}
for page in p:
 for w in page['words']:
  for j in range(w['start'],w['end']-1):
   key=f"{page['indices'][j]},{page['indices'][j+1]}";cnt[key]=cnt.get(key,0)+1
assert cnt==r['counts']
for a,b in itertools.permutations(range(29),2):assert cnt[f'{a},{b}']>0
for key,w in r['witnesses'].items():
 page=pc[w['page']];word=page['words'][w['word']];j=w['within_word'];assert w['runes']==page['indices'][word['start']+j:word['start']+j+2];assert w['source_char_positions']==word['source_char_positions'][j:j+2]
out=dict(pass_=True,control_strings=n,source_words=len(c['source']['words']),all_nonself_pairs=812,all_witnesses=len(r['witnesses']),real_edges=sum(cnt.values()),independence='Separate trie parser and direct source counts; same coordinator, fresh-agent review pending')
(O/'check.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
