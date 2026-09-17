from pathlib import Path
import itertools,random,json
from collections import Counter
import core
rng=random.Random(9174608);records=[];paths=0
for t in range(180):
 n=rng.randrange(2,10);cut=rng.randrange(1,n);c=[0 if rng.random()<.6 else rng.randrange(29) for _ in range(n)];periodic=t%2==0;key=[rng.randrange(29) for _ in range(rng.randrange(1,5) if periodic else n+1)];sign=[-1,1][t%2];resets={i for i in range(n) if rng.random()<.3};F=[i for i,v in enumerate(c) if v==0];rows=[]
 for bits in itertools.product([0,1],repeat=len(F)):
  lit={i for i,v in zip(F,bits) if v};p=[];pos=0
  for i,v in enumerate(c):
   if i in resets:pos=0
   if i in lit:p.append(0)
   else:p.append((v+sign*key[pos])%29);pos=(pos+1)%len(key) if periodic else pos+1
  totals=[];seen=[];score=0
  for i,v in enumerate(p):
   if i in resets:seen=[]
   score+=sum(2 for r in seen if r==v);seen.append(v);totals.append(score)
  rows.append((totals[cut-1],totals[-1],p));paths+=1
 got=core.gridcase(c,resets,cut,dict(id='test',key=key,sign=sign),periodic);pref=max(x[0] for x in rows);full=max(x[1] for x in rows);tail=max(x[1]-x[0] for x in rows if x[0]==pref);assert (got['full_maximum'],got['prefix_maximum'],got['continuation_maximum'])==(full,pref,tail)
 records.append(dict(t=t,n=n,cut=cut,cipher=c,reset_before=sorted(resets),periodic=periodic,key=key,sign=sign,full=full,prefix=pref,continuation=tail))
# Explicit cross-cut witness: one equal rune across the cut adds two pairs.
x=core.gridcase([1,1],[],1,dict(id='zero',key=[0],sign=-1),True);assert x['prefix_maximum']==0 and x['continuation_maximum']==2 and x['continuation_denominator']==2
for c,key,kwargs in [([0]*17,[1],dict(mask_cap=65536)),([1,1],[1],{})]:
 try:core.segment(c,key,-1,False,**kwargs)
 except (core.Unresolved,core.NoLegalPath):pass
 else:raise AssertionError('expected refusal')
w=core.gridcase([0,22],[],1,dict(id='finite',key=[2],sign=-1),False);assert w['continuation_maximum']==0 and sum(not a['feasible'] for a in w['continuations'])==1
out=dict(passed=True,cases=records,exhaustive_paths=paths,cross_cut_witness=True,mask_and_finite_refusal=True);(Path(__file__).parent/'selftest.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(records),paths=paths)))
