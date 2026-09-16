import json,itertools,time
from pathlib import Path
O=Path(__file__).resolve().parent

def possible(p,c,key,sign,causal=True):
 states={-1};history=[]
 for i,(r,v) in enumerate(zip(p,c)):
  k=key+(p[:i] if causal else p);nxt=set()
  for last in states:
   for skip in range(1 if i==0 else 4):
    at=last+1+skip
    if at>=len(k):continue
    if (r-sign*k[at])%29!=v:continue
    if any((r-sign*k[j])%29!=c[i-1] for j in range(last+1,at)):continue
    nxt.add(at)
  states=nxt;history.append(sorted(states))
 return dict(representable=bool(states),first_impossible=next((i for i,x in enumerate(history) if not x),None),pointer_sets=history)

def brute(p,c,key,sign,causal):
 def rec(i,j):
  if i==len(p):return True
  k=key+(p[:i] if causal else p)
  for d in range(1 if i==0 else 4):
   a=j+d
   if a>=len(k):continue
   if (p[i]-sign*k[a])%29!=c[i]:continue
   if any((p[i]-sign*k[t])%29!=c[i-1] for t in range(j,a)):continue
   if rec(i+1,a+1):return True
  return False
 return rec(0,0)

start=time.monotonic();checks=0
for n in range(1,5):
 for p in itertools.product(range(2),repeat=n):
  for c in itertools.product(range(2),repeat=n):
   for sign in [-1,1]:
    for causal in [False,True]:
     assert possible(list(p),list(c),[0,1,0,1],sign,causal)['representable']==brute(list(p),list(c),[0,1,0,1],sign,causal);checks+=1
rows=[]
for r in json.loads((O/'event-clock/controls-results.json').read_text())['results']:
 if r['mode']!='plant':continue
 cell=r['plant_cell'];row=dict(source=r['source'],n=r['n'],cell=cell,inherited_true_key=r['inherited_true_key'])
 for causal in [True,False]:row['accepted_output_causal' if causal else 'accepted_output_known_future']=possible(r['truth'],r['cipher'],cell['key'],cell['sign'],causal)
 rows.append(row)
result=dict(exhaustive_cases=checks,results=rows,elapsed=time.monotonic()-start)
(O/'event-clock/representability.json').write_text(json.dumps(result,indent=2)+'\n')
for r in rows:print(r['source'],r['accepted_output_causal']['first_impossible'],r['accepted_output_known_future']['first_impossible'])
print('complete',checks,result['elapsed'])
