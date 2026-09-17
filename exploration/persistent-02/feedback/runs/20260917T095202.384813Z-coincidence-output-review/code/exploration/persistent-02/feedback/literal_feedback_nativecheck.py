import json,random,pathlib,numpy as np
from literal_feedback_selftest import exhaustive
from literal_feedback import Engine
O=pathlib.Path(__file__).resolve().parent/'C05';rng=random.Random(2026092101);out=[]
for ix,c in enumerate([[0,4,0,9,2,0],[5,0,0,7,3,9]]):
 N=29;k=3;ends={1,4,5};L=np.array([rng.uniform(-5,0) for _ in range(30**3)]).reshape((30,)*3);rows=exhaustive(c,k,L,ends);result=Engine(k,L).solve(c,ends,block=2);want=max(r[0] for r in rows);assert abs(want-result['maximum'])<1e-10
 valid={(r[2],r[3]):r[0] for r in rows}
 for alt in result['alternatives']:assert abs(valid[(tuple(alt['plain']),tuple(alt['literal_positions']))]-alt['total'])<1e-10
 out.append(dict(cipher=c,k=k,ends=sorted(ends),paths=len(rows),result=result,exhaustive_maximum=want));np.savez_compressed(O/f'nativecheck{ix}.npz',logprob=L);print(ix,len(rows),want,result['maximum'],flush=True)
(O/'nativechecks.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
