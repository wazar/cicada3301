import json,gzip
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import numpy as np
D=Path('exploration/persistent-01/coordinator/Q01');O=Path('exploration/persistent-01/review-14')
rows=[];byseed=defaultdict(list)
for name in ['control-'+str(i) for i in range(12)]+['real']:
 seed=330901+sum(name.encode());rng=np.random.default_rng(seed)
 with gzip.open(D/(name+'-null-0-draws.json.gz'),'rt') as f:draws=json.load(f)
 for d in draws:assert np.array_equal(rng.random(len(d)),d)
 rows.append(dict(name=name,seed=seed,first_null_full_draws_verified=True));byseed[seed].append(name)
for i in range(12):byseed[330902+i].append('control-generation-'+str(i))
collisions={str(k):v for k,v in byseed.items() if len(v)>1};assert not collisions
# Exact counterexample to interpreting destination frequencies as transition weights.
w=[F(1,2),F(1,3),F(1,6)];z=sum(x*(1-x) for x in w);pi=[x*(1-x)/z for x in w]
P=[[F(0) if i==j else w[j]/(1-w[i]) for j in range(3)] for i in range(3)]
assert all(sum(pi[i]*P[i][j] for i in range(3))==pi[j] for j in range(3))
assert pi!=w
out=dict(status='PASS',null_seeds=rows,all_25_seed_collisions=collisions,documented_real_seed=330901,actual_real_seed=331321,estimator_example=dict(weights=list(map(str,w)),stationary_destination_frequencies=list(map(str,pi)),interpretation='For an all-nonrepeat homogeneous chain, stationary counts estimate normalized w*(1-w), not w. Counts+.5 remain the frozen estimator, but plug-in nulls are not an exact calibrated composite-null test.'))
(O/'seeds-and-estimator.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
