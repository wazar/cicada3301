import json,pathlib,gzip,math
import numpy as np
from l2 import fit,value,guard,O,dump

def main():
 guard();d=O/'l2';inp=json.loads((d/'inputs-and-maps.json').read_text());src=inp['sources'];rows=inp['rows'];models=[];support=[]
 for k in range(9):
  model,_=fit([w for j,s in enumerate(src) if j!=k for w in s['units']]);_,pool=fit(src[k]['units']);models.append(model);support.append(set(pool)&set(model))
 null=[[] for _ in range(9)];trans={}
 for line in gzip.open(d/'full-generated-output.jsonl.gz','rt'):
  r=json.loads(line)
  if r['kind']=='leave-source-out-transfer':trans[r['source_held']]=r
  if r['kind']!='conditional-null':continue
  for k in range(9):
   total=sum(value(x,models[k]) for row,x in zip(rows,r['collapsed_outputs']) if row['part']==1 and len(x) in support[k]);null[k].append(total)
 checks=[]
 for n in range(1,8):
  patterns=[(0,)]
  for i in range(1,n):patterns=[p+(v,) for p in patterns for v in range(max(p)+2) if v!=p[-1]]
  mass=sum(math.prod(range(29,29-len(set(p)),-1))/(29*28**(n-1)) for p in patterns);assert abs(mass-1)<1e-12;checks.append({'length':n,'pattern_count':len(patterns),'total_probability':mass})
 result=[]
 for k,a in enumerate(null):
  actual=trans[k]['scores'][1];result.append({'source_held':k,'held_score':actual,'null_held_range':[min(a),max(a)],'null_99percentile':float(np.quantile(a,.99)),'p':(1+sum(x>=actual for x in a))/(len(a)+1),'eligible_units_held':trans[k]['eligible_counts'][1]})
 dump(d/'transfer-null-arrays.json',null);dump(d/'transfer-verification.json',{'analytic_probability_checks':checks,'transfers':result,'reused_null_count':400,'new_real_hypotheses':0});print(json.dumps(result))
if __name__=='__main__':main()
