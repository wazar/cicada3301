import k01 as k
independent=k.procedure
import k02
pooled=k02.procedure
import numpy as np,json
k.rng=np.random.default_rng(33010113);O=k.O
sources=json.loads((O/'k02-results.json').read_text())['sources']
def enc(src,keys,accept):
 c=[];used=[];rejected=[]
 for i,x in enumerate(src):
  y=int(keys[len(c)%len(keys),x])
  if c and y==c[-1] and k.rng.random()>=accept:rejected.append(i)
  else:c.append(y);used.append(i)
 assert len(c)+len(rejected)==len(src)
 assert all(c[j]==keys[j%len(keys),src[i]] for j,i in enumerate(used))
 return {'cipher':c,'accepted_source_positions':used,'rejected_source_positions':rejected,'accepted_plaintext':[src[i] for i in used],'observed_repeat_fraction':sum(a==b for a,b in zip(c,c[1:]))/(len(c)-1)}
rows=[]
for method,panels,fn in [('independent',[[s] for s in sources],independent),('pooled',[sources[:5],sources[5:]],pooled)]:
 k.procedure=fn
 for pi,panel in enumerate(panels):
  for period in [1,3,8]:
   for accept in [.17,0.]:
    keys=np.array([k.rng.permutation(29) for _ in range(period)]);outputs=[enc(s['indices'],keys,accept) for s in panel];cs=[np.array(x['cipher']) for x in outputs];r=k.evaluate(cs,99);row={'method':method,'panel':pi,'names':[s['name'] for s in panel],'period':period,'repeat_acceptance':accept,'permutations':keys.tolist(),'outputs':outputs,'result':r};rows.append(row);print(method,pi,period,accept,[len(c) for c in cs],r['selected_period'],r['statistic'],r['p'],flush=True)
    with (O/'k03-controls.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
out={'seed':33010113,'source_sha256':{s['name']:s['sha256'] for s in sources},'count':len(rows),'summary':[{k:x[k] for k in ['method','panel','names','period','repeat_acceptance']}|{'p':x['result']['p'],'statistic':x['result']['statistic'],'selected_period':x['result']['selected_period'],'lengths':[len(y['cipher']) for y in x['outputs']]} for x in rows],'model_fits':len(rows)*100*8,'decoded_candidates':0,'path_expansions':0};(O/'k03-results.json').write_text(json.dumps(out,indent=2))
