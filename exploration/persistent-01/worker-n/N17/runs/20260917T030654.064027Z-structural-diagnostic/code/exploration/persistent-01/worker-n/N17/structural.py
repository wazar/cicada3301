from pathlib import Path
from math import gcd
from functools import reduce
from collections import Counter
import json,numpy as np
D=Path(__file__).parent;inp=json.loads((D/'inputs.json').read_text())
def lf(c):
 pairs=sorted((v,i) for i,v in enumerate(c));out=[0]*len(c)
 for destination,(v,source) in enumerate(pairs):out[source]=destination
 return out
def cycles(p):
 unseen=set(range(len(p)));out=[]
 while unseen:
  i=min(unseen);c=[]
  while i in unseen:unseen.remove(i);c.append(i);i=p[i]
  out.append(c)
 return out
controls=[];baseline=[]
for c in inp['controls']:
 arr=c['carrier'];f=lf(arr);cyc=cycles(f);g=reduce(gcd,Counter(arr).values());assert g==1 and len(cyc)==1;baseline.append(f);controls.append({'control':c['control'],'inventory_count_gcd':g,'LF_cycle_lengths':[len(x) for x in cyc]})
rows=[]
for job in inp['jobs']:
 f=baseline[job['control']];i,j=job['positions'];expected=f.copy();expected[i],expected[j]=expected[j],expected[i];npz=np.load(D/f"swap-{job['job']:04d}.npz");assert expected==npz['lf'].tolist();cyc=cycles(expected);assert len(cyc)==2;rows.append({'job':job['job'],'cycle_lengths':[len(x) for x in cyc]})
(D/'structural.json').write_text(json.dumps({'controls':controls,'swaps':rows},indent=2));print('controls',controls,'swaps',len(rows))
