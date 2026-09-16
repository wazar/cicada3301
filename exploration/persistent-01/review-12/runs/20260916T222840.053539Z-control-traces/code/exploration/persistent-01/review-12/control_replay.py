"""Recreate saved control RNG traces without importing upstream encoder."""
import random,math,json,gzip,hashlib
from pathlib import Path
from collections import Counter
D=Path('exploration/persistent-01/worker-p/P05');O=Path('exploration/persistent-01/review-12')
m=json.loads((D/'model.json').read_text());out=[]
for group in range(4):
 for rep in range(4):
  p=D/f'control-{group}-{rep}.json.gz'
  with gzip.open(p,'rt') as f:r=json.load(f)
  ct=r['control'];seed=130105+group*100+rep;assert ct['seed']==seed
  assert r['seed']==130205+group*100+rep;assert ct['plain']==m['sources'][group+5]['seq']
  sizes=[1]*17
  for _ in range(12):
   ratios=[math.exp(v)/k for v,k in zip(m['u'],sizes)];sizes[ratios.index(max(ratios))]+=1
  rng=random.Random(seed);ids=list(range(29));rng.shuffle(ids);groups=[];start=0
  for k in sizes:groups.append(ids[start:start+k]);start+=k
  mapping=[None]*29
  for label,rs in enumerate(groups):
   for rune in rs:mapping[rune]=label
  assert mapping==ct['truth'];cipher=[];trace=[];redraws=unary=0
  for i,label in enumerate(ct['plain']):
   rs=groups[label];initial=rs[rng.randrange(len(rs))];value=initial;coin=None
   if cipher and value==cipher[-1]:
    if len(rs)==1:unary+=1
    else:
     coin=rng.random()
     if coin<.83:
      options=[v for v in rs if v!=cipher[-1]];value=options[rng.randrange(len(options))];redraws+=1
   trace.append([i,label,initial,coin,value]);cipher.append(value)
  assert cipher==r['cipher'];assert redraws==ct['rejected'] and unary==ct['unary_repeat_events']
  out.append(dict(label=r['label'],source=m['sources'][group+5]['name'],sizes=sizes,redraws=redraws,unary=unary,trace=trace))
with gzip.open(O/'control-traces.json.gz','wt') as f:json.dump(out,f)
print(json.dumps(dict(status='PASS',controls=len(out),total_positions=sum(len(x['trace']) for x in out),redraws=sum(x['redraws'] for x in out),unary=sum(x['unary'] for x in out))))
