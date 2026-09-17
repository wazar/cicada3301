import json,pathlib,sys,hashlib,itertools
import numpy as np
from enumerate import scalar,ROOT,O
sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'));from p03_frozen import LM
lm=LM();weights=np.array([lm.step((a,b),c)[1] for a,b,c in itertools.product(range(30),repeat=3)]).reshape(30,30,30);base=ROOT/'exploration/persistent-02/feedback/C05';cases=json.loads((base/'plants.json').read_text())['cases'];rows=[];alts=0;maxerror=0.
for ix,c in enumerate(cases):
 r=json.loads((base/f'plant{ix:02d}.json').read_text());score,truth,u=scalar(c['cipher'],c['seed'],set(c['literal_positions']),set(c['ends']),weights);assert truth==c['truth'];assert abs(score-r['truth_score'])<1e-8
 for a in r['result']['alternatives']:
  sc,p,used=scalar(c['cipher'],a['seed'],set(a['literal_positions']),set(c['ends']),weights);assert p==a['plain'];error=abs(sc-a['total']);assert error<1e-8;maxerror=max(maxerror,error);alts+=1
 assert r['selected_rune_errors']==sum(a!=b for a,b in zip(c['truth'],r['result']['alternatives'][0]['plain']))
 assert abs(r['truth_gap']-(r['result']['maximum']-r['truth_score']))<1e-8
 rows.append(dict(index=ix,id=c['id'],k=c['k'],selected_rune_errors=r['selected_rune_errors'],truth_gap=r['truth_gap'],source=c['source'],max_states=r['result']['peak_states']))
result=dict(passed=True,plants=len(cases),alternatives_checked=alts,max_abs_scalar_score_error=maxerror,source_identity_scope='Cipher/seed/literal mapping and output scoring independently checked for all32. Underlying source/selection is producer pinned; this does not independently re-fetch sources or claim blind controls.',rows=rows)
(O/'plants-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
