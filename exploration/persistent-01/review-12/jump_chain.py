"""Exact tiny analogue: accepted-swap clock is generally not uniform."""
import itertools,json
from collections import Counter
from fractions import Fraction
from pathlib import Path
states=[s for s in sorted(set(itertools.permutations([0,0,1,1,2,2]))) if not any(a==b for a,b in zip(s,s[1:]))]
edges={}
for s in states:
 neighbors=[]
 for i,j in itertools.combinations(range(6),2):
  z=list(s);z[i],z[j]=z[j],z[i];z=tuple(z)
  if s[i]!=s[j] and z in states:neighbors.append(z)
 edges[s]=neighbors
total=sum(map(len,edges.values()));rows=[]
for s in states:
 # Uniform distribution is stationary only if these column sums equal one.
 column=sum(Fraction(1,len(edges[t])) for t in states for z in edges[t] if z==s)
 weighted=sum(Fraction(len(edges[t]),total)/len(edges[t]) for t in states for z in edges[t] if z==s)
 assert weighted==Fraction(len(edges[s]),total)
 rows.append(dict(state=s,degree=len(edges[s]),uniform_column_sum=str(column),degree_stationary_mass=str(weighted)))
assert any(x['uniform_column_sum']!='1' for x in rows)
out=dict(states=len(states),degree_counts=dict(Counter(map(len,edges.values()))),rows=rows,interpretation='Symmetric proposal chain has uniform stationary law; stopping at a fixed number of accepted moves instead gives an embedded jump chain with degree-weighted stationary law within a connected component. No assertion about actual-page bias magnitude or mixing.')
Path('exploration/persistent-01/review-12/jump-chain.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='rows'}))
