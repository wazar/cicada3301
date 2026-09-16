"""Evidence replay and independent count-aggregated likelihood arithmetic."""
import json,gzip,random,math,hashlib
from collections import Counter
from pathlib import Path
D=Path('exploration/persistent-01/worker-n/N06')
M=json.loads((D/'snapshots/model.json').read_text());summary=json.loads((D/'results.json').read_text())
with gzip.open(D/'records.json.gz','rt') as f:rows=json.load(f)
scores=0;draws=0
for row in rows:
 rng=random.Random(row['source_seed']);erng=random.Random(row['emission_seed']);truth=summary['codebooks'][row['codebook']]['maps'][0]
 p=row['plain'];c=row['cipher'];cut=row['cut']
 for i,(v,u) in enumerate(zip(p,row['source_uniforms'])):
  assert rng.random()==u;draws+=1
  probs=M['u'] if i<2 else M['tri'][(p[i-2]*17+p[i-1])*17:(p[i-2]*17+p[i-1]+1)*17]
  lo=sum(math.exp(q) for q in probs[:v]);hi=lo+math.exp(probs[v]);assert lo<=u<hi
  group=[r for r in range(29) if truth[r]==v];initial,coin,redraw=row['emission_uniforms'][i]
  assert erng.random()==initial;draws+=1;out=group[math.floor(len(group)*initial)]
  eligible=i>0 and c[i-1]==out and len(group)>1
  assert (coin is not None)==eligible
  if eligible:
   assert erng.random()==coin;draws+=1;assert (redraw is not None)==(coin<.83)
   if redraw is not None:
    assert erng.random()==redraw;draws+=1;choices=[r for r in group if r!=out];out=choices[math.floor(redraw*len(choices))]
  assert out==c[i]
 for mi,mapping in enumerate(summary['codebooks'][row['codebook']]['maps']):
  decoded=[mapping[r] for r in c];sizes=Counter(mapping)
  for name,inds in [('prefix',range(cut)),('suffix',range(cut,len(c)))]:
   ucounts=Counter(decoded[i] for i in inds if i<2)
   tcounts=Counter(tuple(decoded[i-2:i+1]) for i in inds if i>=2)
   lm=sum(count*M['u'][a] for a,count in ucounts.items())+sum(count*M['tri'][(a*17+b)*17+d] for (a,b,d),count in tcounts.items())
   events=Counter()
   for i in inds:
    k=sizes[decoded[i]];typ='base' if i==0 or decoded[i-1]!=decoded[i] or k==1 else 'same' if c[i-1]==c[i] else 'other'
    events[k,typ]+=1
   em=0.
   for (k,typ),count in events.items():
    probability=1/k if typ=='base' else 17/(100*k) if typ=='same' else (100*(k-1)+83)/(100*k*(k-1))
    em+=count*math.log(probability)
   expected=row['scores'][mi]
   assert abs(lm-expected[name+'_lm'])<1e-8
   assert abs(em-expected[name+'_emission'])<1e-8;scores+=1
result=dict(status='PASS',samples=len(rows),random_draws_replayed=draws,map_partition_scores_checked=scores,records_sha256=hashlib.sha256((D/'records.json.gz').read_bytes()).hexdigest(),prefix_observed_equivalence=summary['all']['observed_label_equivalence_count'])
(D/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
