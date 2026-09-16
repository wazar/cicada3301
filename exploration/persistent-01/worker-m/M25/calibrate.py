import json,pathlib,random
import m25
R=pathlib.Path(__file__).parent;rng=random.Random(330827);rows=[]
def generate(c):
 out=[rng.randrange(29)]
 for a,b in zip(c,c[1:]):
  if a==b:out.append(out[-1])
  else:
   q=rng.randrange(28);out.append(q+(q>=out[-1]))
 assert all((a==b)==(x==y) for a,b,x,y in zip(c,c[1:],out,out[1:]));return out
fixtures=[m25.fixture(i) for i in range(4)];real=json.load(open(R/'real.json'))
for x in real:
 c,ends=m25.parse(x['map']['raw_joined']);fixtures.append(dict(name='real-'+str(x['page']),cipher=c,ends=sorted(ends)))
for f in fixtures:
 original=m25.search(f['name'],f['cipher'],set(f['ends']));count=99 if f['name'].startswith('real-') else 19;null=[]
 for rep in range(count):
  c=generate(f['cipher']);r=m25.search(f['name']+'-conditional'+str(rep),c,set(f['ends']));null.append(dict(name=r['name'],score=r['score'],repeat_count=sum(a==b for a,b in zip(c,c[1:]))))
 row=dict(name=f['name'],score=original['score'],null=null,tail=(1+sum(x['score']>=original['score'] for x in null))/(count+1));rows.append(row);m25.dump('calibration',dict(seed=330827,results=rows,rng_after=repr(rng.getstate())));print(f['name'],row['tail'],flush=True)
