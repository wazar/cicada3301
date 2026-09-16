"""Independent scalar replay of real K01/K02 training and frozen prediction."""
from pathlib import Path
from collections import Counter
import json,math,hashlib
B=Path('exploration/persistent-01');K=B/'worker-k'
manifest=json.loads((K/'CHECKPOINT-MANIFEST.json').read_text())
for row in manifest['artifacts']:
 p=Path(row['path']);assert len(p.read_bytes())==row['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
res={}
for name in ['k01','k02']:
 d=json.loads((K/(name+'-results.json')).read_text());cs=[p['indices'] for p in d['real']];r=d['result'];v=[];t=[]
 for period in range(1,9):
  pooled=[Counter() for _ in range(period)]
  for c in cs:
   for i,x in enumerate(c[:len(c)//2]):pooled[i%period][x]+=1
  vs=ts=0.
  for j,c in enumerate(cs):
   a=len(c)//2;b=3*len(c)//4;ct=Counter(c[:a]);q0=[(ct[x]+1)/(a+29) for x in range(29)]
   lam=max(.01,min(2,sum(c[i]==c[i-1] for i in range(1,a))/(a-1)/sum(x*x for x in q0)))
   hist=pooled if name=='k02' else [Counter(c[i] for i in range(a) if i%period==z) for z in range(period)]
   q=[[(row[x]+1)/(sum(row.values())+29) for x in range(29)] for row in hist]
   stored=r['fitted'][j]['models'][period-1]['probabilities'] if name=='k01' else r['fitted'][period-1]['probabilities']
   assert max(abs(x-y) for row,row2 in zip(q,stored) for x,y in zip(row,row2))<1e-14
   for i in range(a,len(c)):
    row=q[i%period];den=sum(w*(lam if x==c[i-1] else 1) for x,w in enumerate(row));val=math.log(row[c[i]]*(lam if c[i]==c[i-1] else 1)/den)
    if i<b:vs+=val
    else:ts+=val
  v.append(vs);t.append(ts)
 choice=max(range(8),key=lambda x:v[x]);gain=t[choice]-t[0]
 assert choice+1==r['selected_period'];assert abs(gain-r['statistic'])<1e-9
 assert max(abs(v[i]-v[0]-r['validation_gain'][i]) for i in range(8))<1e-9
 tail=(1+sum(n['statistic']>=r['statistic'] for n in r['null']))/(1+len(r['null']));assert tail==r['p']
 res[name]={'selected_period':choice+1,'held_gain':gain,'tail':tail,'training_tables_reconstructed':True}
out={'scope':'Independent scalar real K01/K02 fit and prediction, manifest integrity; no new search or null resimulation. Worker scalar checks cover additional control cases.','manifest_files':len(manifest['artifacts']),'results':res}
(B/'coordinator/K-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
