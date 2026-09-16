"""Scalar saved-fit likelihood/gradient audit; no optimization."""
from pathlib import Path
from collections import Counter
import json,gzip,math
O=Path(__file__).resolve().parent;D=O.parents[1]/'coordinator/Q01';results=[]
def load(p):
 with gzip.open(p,'rt') as f:return json.load(f)
for name in ['real','control-0','control-6']:
 original=load(D/(name+'.json.gz'));saved=load(O/'panels'/(name+'.json.gz'));counts=[Counter() for _ in range(59)];records=[]
 for page,c in enumerate(original['cipher']):
  states=[0]*29;row=[]
  for i in range(1,len(c)):
   x,y=c[i-1:i+1];states[x]^=1
   if x==y:continue
   row.append((x,y,states[:]))
   if page%2==0:
    counts[0][x,y]+=1
    for m in range(29):counts[1+2*m+states[m]][x,y]+=1
  records.append(row)
 fits=[saved['baseline_fit']]+[f for pair in saved['state_fits'] for f in pair];maxerr=0.;min_improvement=1e10
 for idx,(cnt,fit) in enumerate(zip(counts,fits)):
  theta=fit['theta'];w=[math.exp(t-max(theta)) for t in theta];w=[v/sum(w) for v in w];aug={(x,y):cnt[x,y]+.5/28 for x in range(29) for y in range(29) if x!=y};total=sum(aug.values());gradient=[0.]*29;obj=0.
  old=[sum(v for (x,y),v in aug.items() if y==j)/total for j in range(29)];oldobj=0.
  for x in range(29):
   den=sum(w[j] for j in range(29) if j!=x);old_den=sum(old[j] for j in range(29) if j!=x);rowtotal=sum(aug[x,j] for j in range(29) if j!=x)
   for y in range(29):
    if x==y:continue
    prob=w[y]/den;obj-=aug[x,y]*math.log(prob)/total;oldobj-=aug[x,y]*math.log(old[y]/old_den)/total;gradient[y]+=(rowtotal*prob-aug[x,y])/total
  assert abs(obj-fit['objective'])<1e-10;assert max(abs(v) for v in gradient[:28])<=1e-7
  maxerr=max(maxerr,max(abs(v) for v in gradient[:28]));assert obj<=oldobj+1e-12;min_improvement=min(min_improvement,oldobj-obj)
 gains=[[0.]*45 for _ in range(29)]
 for page,row in enumerate(records):
  for x,y,states in row:
   b=fits[0]['weights'];bp=b[y]/sum(v for j,v in enumerate(b) if j!=x)
   for m in range(29):
    w=fits[1+2*m+states[m]]['weights'];prob=w[y]/sum(v for j,v in enumerate(w) if j!=x);gains[m][page]+=math.log(prob/bp)
 for m in range(29):
  for page in range(45):assert abs(gains[m][page]-saved['perpage_gain'][m][page])<1e-8
 training=[sum(g[::2]) for g in gains];marker=max(range(29),key=training.__getitem__);assert marker==saved['selected_marker']
 score=sum(gains[marker][1::2])/saved['held_nonrepeat_count'];assert abs(score-saved['score'])<1e-10
 results.append(dict(name=name,checked_fits=59,max_gradient=maxerr,minimum_penalized_objective_improvement=min_improvement,marker=marker,score=score))
(O/'verification.json').write_text(json.dumps(dict(status='PASS',panels=results),indent=2));print(json.dumps(results,indent=2))
