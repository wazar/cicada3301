import pathlib,sys,importlib.util,random,itertools,json,hashlib,time,resource
from exact import decode
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prototype',ROOT/'exploration/persistent-02/bootstrap/literal_f_exact_dp.py');proto=importlib.util.module_from_spec(spec);sys.modules['prototype']=proto;spec.loader.exec_module(proto)
sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'));from frozen_kbest import kbest
class LM:
 def __init__(self,weights):self.weights=weights
 def step(self,s,x):return (s[1],x),self.weights[s+(x,)]
 def extend(self,s,x,end):
  s,v=self.step(s,x)
  if end:s,w=self.step(s,29);v+=w
  return s,v

def enumeration(c,k,lm,sign,periodic,start,ends):
 fs=[i for i,v in enumerate(c) if v==0];out=[]
 for choices in itertools.product((False,True),repeat=len(fs)):
  literal={i for i,b in zip(fs,choices) if b};p=[];tokens=[29,29];u=0;score=0.;mask=0
  for i,v in enumerate(c):
   lit=i in literal;pos=start+u
   if not lit and not periodic and pos>=len(k):break
   r=0 if lit else (v+sign*k[pos%len(k)])%29
   # Context reconstructed from full emitted token history, no DP state.
   w=lm.weights[tuple(tokens[-2:])+(r,)];tokens.append(r)
   if i in ends:w+=lm.weights[tuple(tokens[-2:])+(29,)];tokens.append(29)
   score+=w;p.append(r);u+=not lit;mask=mask*2+lit
  else:out.append(dict(total=score,plain=p,literal_positions=sorted(literal),used=u,mask=str(mask)))
 return sorted(out,key=lambda r:(-r['total'],int(r['mask'])))
def main():
 rng=random.Random(260917202);weights={t:float(rng.randrange(-12,4)) for t in itertools.product(range(30),repeat=3)};lm=LM(weights);zero=LM({t:0. for t in weights});cases=[];paths=0
 # All small binary ciphertexts, key includes zero (same-rune ambiguity), signs, phases, finite exhaustion, boundary modes.
 for n in range(0,6):
  for c in itertools.product([0,7],repeat=n):
   for k in [(0,),(1,2),(0,3,0)]:
    for sign in [-1,1]:
     for periodic in [False,True]:
      for start in range(len(k)+1):
       for ends in [set(),set(range(n))]:cases.append((c,k,sign,periodic,start,ends,zero if len(c)%2 else lm))
 for _ in range(300):
  n=rng.randrange(1,13);k=tuple(rng.randrange(29) for _ in range(rng.randrange(1,9)));cases.append(([0 if rng.random()<.55 else rng.randrange(29) for _ in range(n)],k,rng.choice([-1,1]),bool(rng.randrange(2)),rng.randrange(len(k)+1),{i for i in range(n) if rng.random()<.3},lm))
 checked=0;exhausted=0;oldchecked=0;protochecked=0;dig=hashlib.sha256();t=time.monotonic()
 for c,k,sign,periodic,start,ends,model in cases:
  ex=enumeration(c,k,model,sign,periodic,start,ends);paths+=len(ex)
  try:got,d=decode(c,k,model.extend,sign=sign,periodic=periodic,start=start,ends=ends,retain=16)
  except ValueError:
   assert not ex;exhausted+=1;continue
  assert ex
  for x,y in zip(got,ex[:16]):assert all(x[a]==y[a] for a in ['total','plain','literal_positions','used','mask']),(x,y)
  assert len(got)==min(16,len(ex));assert int(d['optimal_path_ties'])==sum(x['total']==ex[0]['total'] for x in ex)
  p=proto.decode_exact(c,k,lambda ctx,x:model.weights[ctx+(x,)],sign=sign,periodic=periodic,start=start,ends=ends);assert p.score==ex[0]['total'];protochecked+=1
  if periodic and c:
   old,_=kbest(c,ends,k,sign,model,start_used=start);assert [x['score'] for x in old]==[x['total']/(len(c)+len(ends)) for x in ex[:16]];oldchecked+=1
  dig.update(json.dumps(ex,sort_keys=True).encode());checked+=1
 result=dict(passed=True,cases=len(cases),legal_cases=checked,exhausted_cases=exhausted,exhaustive_paths=paths,prototype_comparisons=protochecked,existing_kbest_comparisons=oldchecked,enumeration_sha256=dig.hexdigest(),seconds=time.monotonic()-t,maxrss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Independent mask enumeration; integer-valued float objective exact ties. Both signs, all starts, periodic/finite, consecutive F, boundaries, zero-key ambiguity, exhaustion, empty input.')
 (OUT/'selftest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
