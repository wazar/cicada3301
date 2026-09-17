import random,itertools,json,time,pathlib,hashlib
from selftest import enumeration,LM
from exact import decode
rng=random.Random(260917204);weights={t:-rng.random()*15 for t in itertools.product(range(30),repeat=3)};lm=LM(weights);ncase=1000;paths=0;h=hashlib.sha256();t=time.monotonic()
for case in range(ncase):
 n=rng.randrange(1,18);c=[0 if rng.random()<.55 else rng.randrange(29) for _ in range(n)];key=[rng.randrange(29) for _ in range(rng.randrange(1,12))];sign=rng.choice([-1,1]);periodic=bool(case%2);start=rng.randrange(len(key)+1);ends={i for i in range(n) if rng.random()<.3};ex=enumeration(c,key,lm,sign,periodic,start,ends)
 try:got,d=decode(c,key,lm.extend,sign=sign,periodic=periodic,start=start,ends=ends,retain=16)
 except ValueError:assert not ex;continue
 assert [x['total'] for x in got]==[x['total'] for x in ex[:16]]
 expected={(x['mask'],tuple(x['plain'])) for x in ex}
 assert all((x['mask'],tuple(x['plain'])) in expected for x in got)
 assert int(d['optimal_path_ties_lower_bound'])<=sum(x['total']==ex[0]['total'] for x in ex)
 paths+=len(ex);h.update(json.dumps([case,got],sort_keys=True).encode())
def extend(ctx,r,end):return (ctx[1],r),(-1e-16 if ctx==(29,29) and r==0 else -100. if r==1 else 0.)
x,d=decode([0,1,1,2],[1],extend,retain=16);assert len(x)==2 and all(r['total']==-100. for r in x);assert int(d['optimal_path_ties_lower_bound'])==2
x1,d1=decode([0,1,1,2],[1],extend,retain=1);assert int(d1['optimal_path_ties_lower_bound'])==1
out=dict(passed=True,cases=ncase,exhaustive_paths=paths,results_sha256=h.hexdigest(),seconds=time.monotonic()-t,rounding_fixture=dict(retain16=d,retain1=d1),tie_scope='Lower bound only. Retain1 demonstrably cannot count every rounded tie; no uniqueness inference. nbest objective scores checked exactly, tied identities membership checked.')
p=pathlib.Path(__file__).parent/'float-selftest.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
