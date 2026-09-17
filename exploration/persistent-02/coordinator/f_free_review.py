from pathlib import Path
import importlib.util,itertools,json,random,hashlib
root=Path(__file__).resolve().parents[3];source=root/'exploration/persistent-02/decoder/f-free-invariant/invariant.py';spec=importlib.util.spec_from_file_location('inv',source);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
rng=random.Random(111230);cases=0;pairs=0
for emitted,k in itertools.product([False,True],[2,3]):
 for n in [0,1,2,3,4,7,25,80]:
  for t in range(30):
   plain=[rng.randrange(29) for _ in range(n)];lit=set()
   for i in range(n):
    if rng.randrange(5)==0:plain[i]=0;lit.add(i)
   seed=[rng.randrange(29) for _ in range(k)];history=[];phase=0;c=[]
   for i,p in enumerate(plain):
    if i in lit:c.append(0)
    else:
     c.append((p+(seed[phase] if phase<k else sum(history[-k:])))%29);phase+=1
    if emitted or i not in lit:history.append(p)
   runs=[];run=[]
   for i,v in enumerate(c):
    if v:run.append(i)
    elif run:runs.append(run);run=[]
   if run:runs.append(run)
   numerator=denominator=0
   for run in runs:
    for i in run:
     for j in run:
      if i!=j and (i-j)%(k+1)==0:denominator+=1;numerator+=plain[i]==plain[j]
   actual=mod.statistic(c,k);assert actual['numerator']==numerator and actual['denominator']==denominator
   cases+=1;pairs+=denominator
out={'cases':cases,'ordered_pairs':pairs,'status':'PASS','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'independent scalar constructors and all within-run same-phase pairs; no actual ranks'}
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
