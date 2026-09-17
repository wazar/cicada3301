import json, numpy as np
import s01 as s
s.rng=np.random.default_rng(1709202602)
controls={}; generated={}; witnesses=[]
for p in s.pages:
 x=p['indices']
 for wi,w in enumerate(p['words']):
  for a in range(w['start'],w['end']):
   for b in range(a+1,w['end']):
    if x[a]==x[b]: witnesses.append({'page':p['page'],'word':wi,'positions':[a,b],'source_char_positions':[p['source_char_positions'][a],p['source_char_positions'][b]],'rune_index':x[a],'distance':b-a})
old=json.loads((s.BASE/'S01-result.json').read_text())
for p,details in zip(s.pages,old['real']['details']):
 x=p['indices']; owners={i:wi for wi,w in enumerate(p['words']) for i in range(w['start'],w['end'])}
 for row in details:
  d=row['distance']; pairs=[(i,i+d) for i in range(len(x)-d)]
  same=[(a,b) for a,b in pairs if owners[a]==owners[b]]
  assert len(same)==row['within_pairs']
  assert sum(x[a]==x[b] for a,b in same)==row['within_equal']
for rho in [0,.25,.5,.75,1]:
 controls[str(rho)]=[]
 for rep in range(100):
  xs=[]
  for p in s.pages:
   x=np.full(len(p['indices']),-1,int)
   for w in p['words']:
    seen=set()
    for i in range(w['start'],w['end']):
     v=int(s.rng.integers(29))
     if i and v==x[i-1] and s.rng.random()<.83: v=int((x[i-1]+s.rng.integers(1,29))%29)
     if v in seen and s.rng.random()<rho: v=int(s.rng.choice(sorted(set(range(29))-seen)))
     x[i]=v; seen.add(v)
   xs.append(x); generated[f'rho{rho}_{rep}_page{p["page"]}']=x
  controls[str(rho)].append(s.evaluate(xs,999)[0])
np.savez_compressed(s.BASE/'S02-generated-controls.npz',**generated)
r={'seed':1709202602,'repetitions_each':100,'summary':{k:{'p_le_01':sum(a['p']<=.01 for a in v),'p_le_05':sum(a['p']<=.05 for a in v)} for k,v in controls.items()},'strict_witnesses':witnesses,'strict_violating_words':len(set((w['page'],w['word']) for w in witnesses)),'independent_observed_counts':'PASS','controls':controls}
(s.BASE/'S02-result.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({k:v for k,v in r.items() if k not in ['controls','strict_witnesses']},indent=2))
