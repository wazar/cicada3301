import json,random,itertools,pathlib,importlib.util
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];s=importlib.util.spec_from_file_location('author',R/'exploration/persistent-02/section/coincidence/core.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);rng=random.Random(2026092305);results=[]
for case in range(180):
 n=case%9;c=[0 if rng.random()<.7 else rng.randrange(29) for _ in range(n)];key=[rng.randrange(29) for _ in range(1+case%7)];periodic=case%3!=0;position=rng.randrange(len(key)+1);sign=(-1)**case;old=[rng.randrange(4) for _ in range(29)];expected=[];sites=[i for i,x in enumerate(c) if x==0]
 for bits in itertools.product([False,True],repeat=len(sites)):
  mask={i for i,b in zip(sites,bits) if b};pos=position;p=[]
  for i,x in enumerate(c):
   if i in mask:y=0
   else:
    if not periodic and pos>=len(key):break
    y=(x+sign*key[pos%len(key)])%29;pos+=1
   p.append(y)
  else:
   h=[p.count(r) for r in range(29)];score=sum(v*(v-1)+2*o*v for o,v in zip(old,h));expected.append(dict(plain=p,literal_positions=sorted(mask),position=pos%len(key) if periodic else pos,counts=[x+y for x,y in zip(old,h)],score=score))
 try:out=a.segment(c,key,sign,periodic,position=position,counts=old)
 except a.Unresolved:assert not expected;results.append(dict(case=case,legal=0));continue
 assert len(out['rows'])==len(expected)
 for row in out['rows']:assert {k:row[k] for k in expected[0]} in expected
 maximum=max(r['score'] for r in expected);assert out['maximum']==maximum
 groups={}
 for row in out['rows']:
  if row['score']==maximum:groups.setdefault((row['position'],tuple(row['counts'])),[]).append(row['mask'])
 actual={(g['position'],tuple(g['counts'])):g['masks'] for g in out['future_states']};assert groups==actual
 results.append(dict(case=case,legal=len(expected),maximum=maximum,future_states=len(groups)))
(O/'segment-review.json').write_text(json.dumps(dict(status='PASS',cases=results),indent=2)+'\n');print('PASS',len(results))
