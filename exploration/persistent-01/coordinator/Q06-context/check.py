from pathlib import Path
import json,gzip,collections
O=Path(__file__).resolve().parent;ROOT=O.parents[3];pages={p['page']:p for p in json.load(open(ROOT/'exploration/persistent-01/worker-f/F06-maps.json'))}
real=json.load(gzip.open(O/'real.json.gz','rt'));checked=0
for r in real:
 p=pages[r['page']];groups=collections.defaultdict(list)
 for wi,w in enumerate(p['words']):
  for t in range(w['start']+2,w['end']):
   j=t-w['start'];key=tuple(([j] if r['clock'] else [])+p['indices'][t-2:t]);groups[key].append((wi,j,p['indices'][t]))
 expected={k:v for k,v in groups.items() if len({z[2] for z in v})>1};assert set(expected)=={tuple(c['context']) for c in r['conflicts']}
 assert r['contexts']==len(groups) and r['transitions']==sum(map(len,groups.values())) and r['compatible']==(not expected)
 for c in r['conflicts']:
  assert [(v['word'],v['word_position'],v['next']) for v in c['all_occurrences']]==expected[tuple(c['context'])]
  aa,bb=c['witness'];assert aa['context']==bb['context'] and aa['next']!=bb['next']
  if r['clock']:assert aa['word_position']==bb['word_position']
  for v in c['all_occurrences']:
   w=p['words'][v['word']];j=v['word_position'];ids=v['page_rune_positions'];assert ids==[w['start']+j-2,w['start']+j-1,w['start']+j]
   assert [p['indices'][i] for i in ids]==v['context']+[v['next']]
   assert v['source_char_positions']==w['source_char_positions'][j-2:j+1]
  checked+=1
controls=json.load(gzip.open(O/'controls.json.gz','rt'));n=0
for group in controls:
 for p in group['pages']:
  f={tuple(t['key']):t['value'] for t in p['table']};original=pages[p['page']]
  assert len(p['indices'])==len(original['indices'])
  for w in original['words']:
   for i in range(w['start']+2,w['end']):
    k=tuple(([i-w['start']] if group['clock'] else [])+p['indices'][i-2:i]);assert f[k]==p['indices'][i]
  n+=1
for q in json.load(gzip.open(O/'tiny.json.gz','rt')):
 d={};ok=True
 for i in range(2,len(q['sequence'])):
  k=tuple(q['sequence'][i-2:i]);v=q['sequence'][i]
  if k in d and d[k]!=v:ok=False
  d[k]=v
 assert q['valid_tables']==(3**(9-len(d)) if ok else 0)
r=dict(status='PASS',conflicting_contexts_checked=checked,control_page_cases=n,models=[dict(clock=c,incompatible=sum(not r['compatible'] for r in real if r['clock']==c),compatible_pages=[r['page'] for r in real if r['clock']==c and r['compatible']]) for c in [False,True]])
(O/'independent-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
