"""Recount immutable publication tables; descriptive null comparison, no new search."""
from pathlib import Path
import json,gzip,collections
R=Path(__file__).resolve().parents[3];P=R/'exploration/persistent-01/worker-a/publication/cycle1';O=Path(__file__).parent
cfg=json.loads((R/'exploration/persistent-01/config.json').read_text());banned=set(cfg['reserved_original_pages'])|{50}
results={}
for label in ['real','null']:
 n=0;ids=set();pages=collections.Counter();best={}
 for path in sorted((P/label).glob('scores-*.jsonl.gz')):
  with gzip.open(path,'rt') as f:
   for line in f:
    x=json.loads(line);assert x['id'] not in ids;ids.add(x['id']);p=x['original_page'];assert p not in banned and p<=55;pages[p]+=1;n+=1
    best[p]=max(best.get(p,float('-inf')),x['score'])
 assert n==181659 and len(pages)==45
 results[label]=dict(count=n,maximum=max(best.values()),per_page_counts=dict(pages),per_page_maxima=best)
assert results['real']['per_page_counts']==results['null']['per_page_counts'];wins=sum(results['real']['per_page_maxima'][p]>v for p,v in results['null']['per_page_maxima'].items());assert wins==13
stored=json.loads((P/'p01-comparison.json').read_text())
for label in ['real','null']:assert results[label]['maximum']==stored[label]['max']
results['real_beats_paired_null_pages']=wins;results['limit']='Independent row/count/max replay. One matched shuffle perpage is a descriptive comparison, not significance. Arithmetic/score checks are separately retained workerA replay.'
(O/'A-table-review.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({label:{k:v for k,v in results[label].items() if k in ['count','maximum']} for label in ['real','null']}|{'paired_wins':wins}))
