"""Independent effective-page seeds do not impose a physical cipher reset."""
import extend as ex,json,random
from invariant import simple_baseline,collisions
O=ex.O/'C07';rng=random.Random(2026092201);rows=[]
for k in [2,5,11,17,34]:
 p=[rng.randrange(29) for _ in range(716)];seed=[rng.randrange(29) for _ in range(k)];c=ex.q.enc(p,seed)
 for start,n in [(13,66),(77,121),(249,249)]:
  cc=c[start:start+n];pp=p[start:start+n];effective=[(a-b)%29 for a,b in zip(cc[:k],pp[:k])];assert ex.q.decode(cc,effective)==pp
  q=simple_baseline(cc,k);a,b,_=collisions(q,k+1);aa,bb,_=collisions(pp,k+1);assert(a,b)==(aa,bb);rows.append(dict(k=k,start=start,n=n,source_seed=seed,effective_seed=effective,cipher=cc,plain=pp,collision_numerator=a,denominator=b))
(O/'slice-identity.json').write_text(json.dumps(dict(passed=True,scope='independent effective initial conditions cover contiguous slices of a continuous recurrence; no required pageclock reset',cases=rows),separators=(',',':'))+'\n');print('PASS',len(rows))
