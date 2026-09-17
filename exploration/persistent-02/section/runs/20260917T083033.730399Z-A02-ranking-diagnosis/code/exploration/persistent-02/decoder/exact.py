"""Sparse exact n-best paths for fixed literal-F key and local additive score.
No caps on states. n-best paths are not n-best distinct plaintexts. A lower bound on optimum path ties is propagated separately. Float rounding
can coalesce unequal prefix scores later; global tie completeness/order is not claimed.
"""
from collections import defaultdict
from dataclasses import dataclass
import math,time
@dataclass(slots=True)
class Node:
 score: float
 parent: object
 rune: int
 literal: bool
 used: int
 mask: int

def decode(c,key,extend,*,sign=-1,periodic=True,start=0,ends=(),retain=16,context=(29,29)):
 c=tuple(c);key=tuple(key);ends=frozenset(ends)
 if not key or any(type(v)!=int or not 0<=v<29 for v in c+key):raise ValueError('runes/key must be nonempty-key integers 0..28')
 if type(sign)!=int or sign not in (-1,1):raise ValueError('sign')
 if type(start)!=int or start<0 or (not periodic and start>len(key)):raise ValueError('start')
 if type(retain)!=int or retain<1:raise ValueError('retain')
 if any(type(i)!=int or not 0<=i<len(c) for i in ends):raise ValueError('ends')
 if len(context)!=2 or any(type(x)!=int or not 0<=x<=29 for x in context):raise ValueError('context')
 t=time.monotonic();initial=(start%len(key) if periodic else start,tuple(context));root=Node(0.,None,-1,False,0,0)
 states={initial:[root]};counts={initial:(0.,1)};peak=1;peakpaths=1;expanded=0;nodes=1
 for i,v in enumerate(c):
  nxt=defaultdict(list);nc={}
  for (pos,ctx),paths in states.items():
   choices=[]
   if periodic or pos<len(key):choices.append(((v+sign*key[pos])%29,(pos+1)%len(key) if periodic else pos+1,False))
   if v==0:choices.append((0,pos,True))
   for r,np,lit in choices:
    ss,w=extend(ctx,r,i in ends);w=float(w)
    if not math.isfinite(w):raise ValueError('finite local scores required')
    st=(np,ss);bs,bc=counts[(pos,ctx)];val=bs+w
    if st not in nc or val>nc[st][0]:nc[st]=(val,bc)
    elif val==nc[st][0]:nc[st]=(val,nc[st][1]+bc)
    for p in paths:
     nxt[st].append(Node(p.score+w,p,r,lit,p.used+int(not lit),(p.mask<<1)|lit));expanded+=1
  if not nxt:raise ValueError(f'no legal path at rune {i}')
  states={st:sorted(ps,key=lambda p:(-p.score,p.mask))[:retain] for st,ps in nxt.items()};counts=nc
  live=sum(map(len,states.values()));nodes+=live;peak=max(peak,len(states));peakpaths=max(peakpaths,live)
 best=sorted((p for ps in states.values() for p in ps),key=lambda p:(-p.score,p.mask))[:retain]
 score=best[0].score;ties=sum(count for value,count in counts.values() if value==score)
 out=[]
 for p in best:
  cur=p;plain=[];literals=[]
  for i in range(len(c)-1,-1,-1):
   plain.append(cur.rune)
   if cur.literal:literals.append(i)
   cur=cur.parent
  out.append(dict(total=p.score,score=p.score/(len(c)+len(ends)) if c else p.score,plain=plain[::-1],literal_positions=literals[::-1],used=p.used,mask=str(p.mask)))
 return out,dict(expanded=expanded,maxstates=peak,max_live_paths=peakpaths,retained_nodes_across_layers=nodes,optimal_path_ties_lower_bound=str(max(ties,sum(p.score==score for p in best))),retained=len(out),seconds=time.monotonic()-t,exact='global n-best decision paths; arbitrary representatives at tied cutoffs; prefix-best tie count is a lower bound under float rounding')
