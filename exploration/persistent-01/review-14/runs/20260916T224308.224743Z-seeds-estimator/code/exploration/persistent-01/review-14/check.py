"""Independent scalar Q01 audit; no imports from coordinator or worker-q."""
from pathlib import Path
from collections import Counter
from fractions import Fraction as F
import json,gzip,hashlib,math,itertools
import numpy as np
D=Path('exploration/persistent-01/coordinator/Q01');O=Path('exploration/persistent-01/review-14');inputs=[]
(O/'snapshots').mkdir(exist_ok=True)
def read(name):
 p=D/name;b=p.read_bytes();inputs.append(dict(path=str(p),sha256=hashlib.sha256(b).hexdigest()));return json.load(gzip.open(p,'rt') if name.endswith('.gz') else open(p))
for name in ['q01.py','card.md','result.json','input.json']:(O/'snapshots'/name).write_bytes((D/name).read_bytes())
result=read('result.json');maps=read('input.json');template=[m['indices'] for m in maps]
assert len(maps)==45 and [m['page'] for m in maps]==sorted(m['page'] for m in maps)
assert not set(m['page'] for m in maps)&{4,9,14,19,24,29,34,39,44,54}
def close(x,y):assert abs(x-y)<1e-8,(x,y)
def scalar(panel):
 counts=[[[.5]*29 for _ in range(2)] for _ in range(29)];hist=[.5]*29
 for ordinal,c in enumerate(panel):
  if ordinal%2:continue
  state=[0]*29
  for i in range(1,len(c)):
   state[c[i-1]]^=1
   if c[i]==c[i-1]:continue
   hist[c[i]]+=1
   for marker in range(29):counts[marker][state[marker]][c[i]]+=1
 base=[v/sum(hist) for v in hist];weights=[[[v/sum(row) for v in row] for row in pair] for pair in counts]
 gains=[[0.]*45 for _ in range(29)];heldn=0
 for ordinal,c in enumerate(panel):
  state=[0]*29
  for i in range(1,len(c)):
   prev,cur=c[i-1:i+1];state[prev]^=1
   if prev==cur:continue
   heldn+=ordinal%2
   bp=base[cur]/sum(v for k,v in enumerate(base) if k!=prev)
   for marker in range(29):
    w=weights[marker][state[marker]];prob=w[cur]/sum(v for k,v in enumerate(w) if k!=prev)
    gains[marker][ordinal]+=math.log(prob/bp)
 train=[sum(row[::2]) for row in gains];held=[sum(row[1::2]) for row in gains];winner=max(range(29),key=train.__getitem__)
 return dict(weights=weights,baseline=base,perpage_gain=gains,train_total=train,held_total=held,selected_marker=winner,held_nonrepeat_count=heldn,score=held[winner]/heldn)
subset=['real','control-0','control-6','control-11','real-null-0','real-null-198','control-0-null-0','control-6-null-18']
checked=[]
for name in subset:
 saved=read(name+'.json.gz');s=scalar(saved['cipher'])
 for field in ['weights','baseline','perpage_gain','train_total','held_total']:
  a=np.asarray(s[field]);b=np.asarray(saved[field]);assert a.shape==b.shape and np.max(abs(a-b))<1e-8,(name,field)
 for field in ['selected_marker','held_nonrepeat_count']:assert s[field]==saved[field]
 close(s['score'],saved['score']);checked.append(dict(name=name,score=s['score'],marker=s['selected_marker']))
 # Weights depend solely on training ordinals; reconstructing above never reads held targets.
packets=0;tails={};choices=[]
for row in result['controls']+[result['real']]:
 name=row['name'];main=read(name+'.json.gz');n=199 if name=='real' else 19;nullscores=[]
 for packet in [main]+[read(name+'-null-'+str(i)+'.json.gz') for i in range(n)]:
  assert len(packet['cipher'])==45;assert np.asarray(packet['weights']).shape==(29,2,29)
  marker=max(range(29),key=packet['train_total'].__getitem__);assert marker==packet['selected_marker']
  close(packet['score'],packet['held_total'][marker]/packet['held_nonrepeat_count']);packets+=1
  if packet is not main:nullscores.append(packet['score'])
 assert nullscores==row['null'];tail=(1+sum(v>=main['score'] for v in nullscores))/(n+1);close(tail,row['tail']);tails[name]=tail;choices.append(main['selected_marker'])
assert packets==440
# Replay source controls using saved uniforms and fresh seed regeneration.
def generate(old,weights,marker,draws):
 panel=[]
 for c,us in zip(old,draws):
  state=0;out=[]
  for i,u in enumerate(us):
   if i:state^=(out[-1]==marker) if marker is not None else 0
   if i and c[i]==c[i-1]:out.append(out[-1]);continue
   w=weights[state];den=sum(v for j,v in enumerate(w) if not i or j!=out[-1]);cdf=0.;chosen=None
   for j,p in enumerate(w):
    if i and j==out[-1]:continue
    cdf+=p/den
    if u<cdf:chosen=j;break
   assert chosen is not None;out.append(chosen)
  assert [a==b for a,b in zip(out,out[1:])]==[a==b for a,b in zip(c,c[1:])];panel.append(out)
 return panel
gens=[]
for ix in range(12):
 saved=read(f'control-{ix}-generation.json.gz');packet=read(f'control-{ix}.json.gz');rng=np.random.default_rng(330902+ix)
 w=rng.dirichlet(np.full(29,.5 if ix<6 else 2));w1=w[rng.permutation(29)];marker=int(rng.integers(29));assert marker==saved['marker']
 assert np.array_equal(np.asarray([w,w1]),saved['weights'])
 for c,draws in zip(template,saved['draws']):assert np.array_equal(rng.random(len(c)),draws)
 rebuilt=generate(template,saved['weights'],marker,saved['draws']);assert rebuilt==packet['cipher'];gens.append(dict(control=ix,marker=marker,firstpage_n=len(rebuilt[0])))
nullgen=[]
for name in ['real','control-0','control-6','control-11']:
 main=read(name+'.json.gz');draws=read(name+'-null-0-draws.json.gz');actual_seed=330901+sum(name.encode());rng=np.random.default_rng(actual_seed)
 for c,u in zip(main['cipher'],draws):assert np.array_equal(rng.random(len(c)),u)
 gen=generate(main['cipher'],[main['baseline']]*2,None,draws);assert gen==read(name+'-null-0.json.gz')['cipher'];nullgen.append(dict(name=name,actual_seed=actual_seed))
# Exact small-alphabet normalization, including deterministic repeated marker toggles.
normalizations=0
weights=[[F(1,2),F(1,3),F(1,6)],[F(1,6),F(1,2),F(1,3)]]
for marker in range(3):
 for mask in itertools.product([False,True],repeat=4):
  total=F(0)
  for sequence in itertools.product(range(3),repeat=5):
   if tuple(a==b for a,b in zip(sequence,sequence[1:]))!=mask:continue
   prob=weights[0][sequence[0]];state=0
   for i in range(1,5):
    state^=sequence[i-1]==marker
    if not mask[i-1]:prob*=weights[state][sequence[i]]/(1-weights[state][sequence[i-1]])
   total+=prob
  assert total==1;normalizations+=1
out=dict(status='PASS',scalar_panels=checked,all_packets=packets,marker_selections=440*29,tails=tails,control_generations_replayed=len(gens),null_generations_replayed=nullgen,exact_conditional_mask_normalizations=normalizations,real_documented_seed=330901,real_actual_seed=331321,control_marker_matches=sum(a['truth_marker']==a['selected_marker'] for a in result['controls']))
(O/'results.json').write_text(json.dumps(out,indent=2));(O/'inputs.json').write_text(json.dumps(inputs,indent=2));print(json.dumps(out,indent=2))
