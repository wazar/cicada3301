from oracle import forward,inverse
from fractions import Fraction
from pathlib import Path
import random,json
R=Path(__file__).parent;rows=[];nforward=ninverse=0
for ix in range(80):
 rng=random.Random(62000+ix);key=[rng.randrange(29) for _ in range(1+ix%11)];prev=[None,0,7,28][ix%4];start=ix%len(key)
 allf={p:forward(p,prev,key,start) for p in range(29)}
 for p,events in allf.items():
  assert sum(e['prob'] for e in events)==1;nforward+=1
 for c in range(29):
  truth=sorted((p,e['after'],e['prob']) for p,events in allf.items() for e in events if e['output']==c)
  inv=sorted((e['plain'],e['after'],e['prob']) for e in inverse(c,prev,key,start));assert truth==inv;ninverse+=1
 rows.append({'case':ix,'key':key,'previous':prev,'start':start,'exhaustion_mass_uniform_plain':str(sum(e['prob'] for events in allf.values() for e in events if e['output'] is None)/29)})
(R/'oracle-check.json').write_text(json.dumps({'status':'PASS','forward_distributions':nforward,'inverse_distributions':ninverse,'cases':rows},indent=2));print(nforward,ninverse,'PASS')
