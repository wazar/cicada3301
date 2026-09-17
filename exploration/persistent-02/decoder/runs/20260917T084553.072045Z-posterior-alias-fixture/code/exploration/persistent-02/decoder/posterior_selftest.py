import random,itertools,json,math,time,hashlib
from posterior import analyze,beam_pool,mass,lse
from exact import decode
from compare import O,LM,beam,finite_beam
rng=random.Random(260917207);t=time.monotonic();totalpaths=0;checked=0;exhausted=0;maxerr=0.;digest=hashlib.sha256()
class Model:
 def __init__(self,mode):self.mode=mode
 def extend(self,ctx,r,end):
  # Independently simple nonrandom score functions with rational + real-valued modes.
  def w(a,b,c):return 0. if self.mode==0 else -((a*31+b*7+c*13)%17)/3. if self.mode==1 else -math.log(1+((a*31+b*7+c*13)%17))
  x=w(*ctx,r);s=(ctx[1],r)
  if end:x+=w(*s,29);s=(r,29)
  return s,x
for case in range(800):
 n=rng.randrange(0,13);c=[0 if rng.random()<.6 else rng.randrange(1,29) for _ in range(n)];key=[rng.randrange(29) for _ in range(rng.randrange(1,8))];sign=rng.choice([-1,1]);periodic=bool(case%2);start=rng.randrange(len(key)+1);ctx=tuple(rng.randrange(30) for _ in range(2));ends={i for i in range(n) if rng.random()<.3};lm=Model(case%3);sites=[i for i,v in enumerate(c) if v==0];allpaths=[]
 for decisions in itertools.product([0,1],repeat=len(sites)):
  literal={i for i,b in zip(sites,decisions) if b};u=start;s=ctx;score=0.;states=[(u%len(key) if periodic else u,s)]
  for i,v in enumerate(c):
   if i not in literal and not periodic and u>=len(key):break
   r=0 if i in literal else (v+sign*key[u%len(key)])%29;s,w=lm.extend(s,r,i in ends);score+=w;u+=i not in literal;states.append((u%len(key) if periodic else u,s))
  else:allpaths.append(dict(total=score,literal_positions=sorted(literal),states=states))
 try:got=analyze(c,key,lm.extend,sign=sign,periodic=periodic,start=start,ends=ends,context=ctx,cuts=range(n+1))
 except ValueError:assert not allpaths;exhausted+=1;continue
 assert allpaths;z=lse(x['total'] for x in allpaths);error=abs(z-got['log_partition']);assert error<1e-10;maxerr=max(maxerr,error);assert int(got['number_of_legal_decision_paths'])==len(allpaths)
 for b in got['branch_marginals']:
  expected=sum(math.exp(p['total']-z) for p in allpaths if b['position'] in p['literal_positions']);error=abs(expected-b['literal']['probability']);assert error<1e-10;maxerr=max(maxerr,error)
 for join in got['joins']:
  cut=join['cut_after_rune_count'];expected={}
  for p in allpaths:st=p['states'][cut];expected[st]=expected.get(st,0.)+math.exp(p['total']-z)
  for st in join['states']:
   error=abs(st['probability']-expected.get((st['position'],tuple(st['context'])),0.));assert error<1e-10;maxerr=max(maxerr,error)
 best,bd=decode(c,key,lm.extend,sign=sign,periodic=periodic,start=start,ends=ends,context=ctx,retain=16);m=mass(best,got['log_partition']);ordered=sorted(allpaths,key=lambda x:-x['total'])[:16];assert abs(m['mass']-sum(math.exp(p['total']-z) for p in ordered))<1e-10
 checked+=1;totalpaths+=len(allpaths);digest.update(json.dumps([case,got['log_partition'],got['number_of_legal_decision_paths']],sort_keys=True).encode())
# Same-score real P03 beam pool mirrors old top16 exactly for both periodic and finite.
lm=LM();beamchecks=0
for i in range(100):
 c=[0 if rng.random()<.5 else rng.randrange(29) for _ in range(30)];key=[rng.randrange(29) for _ in range(35 if i%2 else 7)];ends={j for j in range(30) if rng.random()<.3};periodic=not i%2;sign=rng.choice([-1,1])
 for width in [16,64,256]:
  pool=beam_pool(c,key,lm,sign=sign,periodic=periodic,ends=ends,width=width);old,_=beam(c,ends,key,sign,lm,width) if periodic else finite_beam(c,ends,key,sign,lm,width)
  for a,b in zip(pool[:16],old):assert a['plain']==b['plain'] and a['literal_positions']==b['literal_positions'] and a['total']/(len(c)+len(ends))==b['score']
  beamchecks+=1
out=dict(passed=True,cases=800,legal=checked,exhausted=exhausted,complete_paths=totalpaths,max_absolute_error=maxerr,beam_pool_checks=beamchecks,results_sha256=digest.hexdigest(),seconds=time.monotonic()-t,scope='Independent complete decision masks, branch/state/phase marginals, partition/pathcount/top16mass; signs, initial context, phase/finiteposition, boundaries, ties, exhaustion, empty input.100 P03 beam fixtures ×3widths.')
(O/'posterior-selftest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
