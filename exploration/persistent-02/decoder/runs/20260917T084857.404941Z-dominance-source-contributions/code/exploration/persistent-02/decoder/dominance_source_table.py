import json
from compare import O,ROOT
TOKENS='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()+['BOUNDARY']
data=json.loads((O/'dominance.json').read_text());sources=json.loads((O/'fresh-controls.json').read_text())['sources'];raw=(ROOT/next(s['path'] for s in sources if s['id']=='shelley')).read_text();out=[]
for c in data['cases']:
 for s in c['segments']:
  spans=sorted(set(map(tuple,s['source_spans'])));text=raw[spans[0][0]:spans[-1][1]];rows=[]
  for a,b in zip(s['true_rows'],s['wrong_rows']):
   rows.append(dict(rune=a['i'],truth=TOKENS[a['emitted']],wrong=TOKENS[b['emitted']],truth_literal=a['literal'],wrong_literal=b['literal'],truth_contributions=[dict(context=[TOKENS[t] for t in x['context']],emitted=TOKENS[x['emitted']],weight=x['weight']) for x in a['contributions']],wrong_contributions=[dict(context=[TOKENS[t] for t in x['context']],emitted=TOKENS[x['emitted']],weight=x['weight']) for x in b['contributions']],weight_difference=b['local_weight']-a['local_weight']))
  out.append(dict(model=c['model'],source=next(s['path'] for s in sources if s['id']=='shelley'),source_words=text,source_spans=spans,start=s['start'],reconverged_after=s['reconverged_after'],wrong_minus_true=s['wrong_minus_true'],rows=rows))
(O/'dominance-source-tables.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
