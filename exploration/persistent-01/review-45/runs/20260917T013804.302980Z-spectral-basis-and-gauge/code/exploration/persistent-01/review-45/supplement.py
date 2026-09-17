import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json,numpy as np
R=Path(__file__).parent;P=R.parent/'worker-p/P26';old=json.loads((P/'diagnostic-before-translation.json').read_text())['previous'];minsv=1.;controls=[];files=[]
for path in P.glob('*.json'):
 r=json.loads(path.read_text())
 if 'eigenvectors' not in r:continue
 assert len(r['eigenvectors'])==29 and sorted(x['index'] for x in r['eigenvectors'])==list(range(29));V=np.array([np.array(x['real'])+1j*np.array(x['imag']) for x in r['eigenvectors']]).T;s=float(np.linalg.svd(V,compute_uv=False)[-1]);assert s>1e-12;minsv=min(minsv,s);files.append(path.name)
for i in range(4):
 r=json.loads((P/f'control-{i}.json').read_text());prior=old[f'control-{i}.json'];assert len(prior)==len(r['order_recovery'])
 for a,b in zip(prior,r['order_recovery']):assert a['maximum_matches']==b['anchored_maximum_matches'] and a['exact']==b['exact']
 k=r['selected'];controls.append(dict(control=i,old=prior[k],corrected=r['order_recovery'][k]))
# A concrete counterexample to using the exact-match gauge for approximate matching.
g=np.arange(29);f=(g+1)%29;f[0],f[28]=f[28],f[0];assert f[0]==0 and len(set(f))==29
scores=[(int(sum(f==(a*g+b)%29)),a,b) for a in range(1,29) for b in range(29)];best=max(n for n,a,b in scores);anchored=max(n for n,a,b in scores if b==0);assert best==27 and anchored<best
out=dict(panels=len(files),all_full_eigenbases=True,min_singular_value=minsv,controls=controls,gauge_counterexample=dict(f=f.tolist(),g=g.tolist(),best=best,anchored=anchored),exact_equivalence='If f(0)=g(0)=0 and every rune matches, b must be zero; this does not apply to partial matches.')
(R/'supplement.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
