import gzip,json
import numpy as np
from search import OWNER,dump
lane=OWNER/'r04-wide';s=json.loads((lane/'checkpoint.json').read_text());rows=[]
for p in lane.glob('cell-*.json.gz'):
 with gzip.open(p,'rt') as f:rows.extend(json.load(f))
real=[r for r in rows if not r['control']];random=[r for r in rows if r['control']]
for r in real:r.update(positions=[0,len(r['rune_indices'])],free_parameters=f'{r["period"]} adjustable mod29 key symbols,4restarts,5sweeps maximum',validation_limit='Key fitted only to first75%; top-continuation ranking is adaptive exploratory selection, not independent validation')
dump(lane/'top_candidates.json',sorted(real,key=lambda r:r['train_score'],reverse=True)[:20]);dump(lane/'top_continuation_candidates.json',sorted(real,key=lambda r:r['continuation_score'],reverse=True)[:20]);out={'completed_cells':s['cursor'],'fitted_keys':s['trials'],'variant_evaluations':s['evaluations'],'actual_objective_evaluations':s['evaluations']+s['evaluations']//29+4*s['trials'],'skipped_cells':len(json.loads((lane/'definition.json').read_text())['skipped']),'real_check_max':max(r['continuation_score'] for r in real),'random_check_max':max(r['continuation_score'] for r in random),'real_check_mean':float(np.mean([r['continuation_score'] for r in real])),'random_check_mean':float(np.mean([r['continuation_score'] for r in random]))};dump(lane/'summary.json',out);print(out)
