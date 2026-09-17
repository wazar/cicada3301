from pathlib import Path
import json,gzip,collections,hashlib
R=Path(__file__).parent;B=R.parent;S=B/'worker-s';Q=B/'coordinator/Q06-context';pages={p['page']:p for p in json.loads((B/'worker-f/F06-maps.json').read_text())};read=lambda p:json.load(gzip.open(p,'rt'));result={}
r=json.loads((S/'S13-result.json').read_text())
for item in r['real']:
 p=pages[item['page']];tot=collections.Counter();rhs=0
 for term in item['source_certificate']:
  w=p['words'][term['word_index']];seq=p['indices'][w['start']:w['end']];assert w==term['map'] and seq==term['runes'];rhs+=term['multiplier']
  for v in seq:tot[v]+=term['multiplier']
 assert not any(tot.values()) and rhs==item['weighted_rhs']!=0
 assert item['A']==[[p['indices'][w['start']:w['end']].count(v) for v in range(29)] for w in p['words']]
ctrl=read(S/'S13-controls.json.gz');nodes=0
for c in ctrl:
 ar={int(k):v for k,v in c['arity'].items()};assert sorted(collections.Counter(ar.values()).items())==[(0,13),(1,8),(2,8)]
 for panel in c['pages']:
  flat=[]
  for tree,trace,w in zip(panel['trees'],panel['stack_traces'],pages[panel['page']]['words']):
   stack=[(tree,False)];seq=[]
   while stack:
    t,visited=stack.pop();assert len(t['children'])==ar[t['operator']]
    if visited:seq.append(t['operator']);nodes+=1
    else:stack.append((t,True));stack.extend((x,False) for x in reversed(t['children']))
   assert len(seq)==w['end']-w['start'];h=0;heights=[]
   for v in seq:assert h>=ar[v];h+=1-ar[v];heights.append(h)
   assert h==1 and heights==trace;flat+=seq
  assert flat==panel['runes']
result['S13']={'certificates':2,'controls':20,'tree_nodes':nodes,'rhs':[x['weighted_rhs'] for x in r['real']]}
actual=read(Q/'real.json.gz');conflicts=0
for a in actual:
 p=pages[a['page']];d=collections.defaultdict(list)
 for wi,w in enumerate(p['words']):
  for pos in range(w['start']+2,w['end']):
   j=pos-w['start'];pair=p['indices'][pos-2:pos];key=tuple(([j] if a['clock'] else [])+pair);row=dict(word=wi,word_position=j,context=pair,next=p['indices'][pos],page_rune_positions=[pos-2,pos-1,pos],source_char_positions=p['source_char_positions'][pos-2:pos+1]);d[key].append(row)
 bad={k:v for k,v in d.items() if len({z['next'] for z in v})>1};assert len(d)==a['contexts'] and sum(map(len,d.values()))==a['transitions'] and (not bad)==a['compatible'];assert set(bad)=={tuple(x['context']) for x in a['conflicts']}
 for x in a['conflicts']:
  assert x['all_occurrences']==bad[tuple(x['context'])];u,v=x['witness'];assert u in x['all_occurrences'] and v in x['all_occurrences'] and u['next']!=v['next']
 conflicts+=len(bad)
ct=read(Q/'controls.json.gz')
for group in ct:
 for c in group['pages']:
  table={tuple(x['key']):x['value'] for x in c['table']};p=pages[c['page']]
  for w in p['words']:
   for pos in range(w['start']+2,w['end']):
    j=pos-w['start'];key=tuple(([j] if group['clock'] else [])+c['indices'][pos-2:pos]);assert table[key]==c['indices'][pos]
for t in read(Q/'tiny.json.gz'):
 d=collections.defaultdict(set);seq=t['sequence']
 for a,b,c in zip(seq,seq[1:],seq[2:]):d[a,b].add(c)
 n=0 if any(len(x)>1 for x in d.values()) else 3**(9-len(d));assert n==t['valid_tables'] and bool(n)==t['compatible']
result['Q06']={'source_conflicts':conflicts,'control_pages':360,'tiny_counts':8}
(R/'exact-result.json').write_text(json.dumps(result,indent=2));print(result)
