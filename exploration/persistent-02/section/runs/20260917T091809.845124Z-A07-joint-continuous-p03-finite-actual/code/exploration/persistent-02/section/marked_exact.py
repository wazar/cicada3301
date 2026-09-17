"""Exact conditional n-best literal-F paths with fixed visible key-reset positions.
Adapted from decoder/exact.py: reset state positions, retain score context, no state cap.
Decision-path n-best; arbitrary tied-cutoff representatives. No complete tie-count claim.
"""
from dataclasses import dataclass
from collections import defaultdict
import math,time
@dataclass(slots=True)
class Node:
 score:float
 parent:object
 rune:int
 literal:bool
 used:int
 mask:int
 position:int

def decode(c,key,extend,*,sign=-1,periodic=True,start=0,ends=(),retain=16,context=(29,29),reset_before=()):
 c=tuple(c);key=tuple(key);ends=frozenset(ends);resets=frozenset(reset_before)
 if not key or any(type(x)!=int or not 0<=x<29 for x in c+key):raise ValueError('runes/key')
 if sign not in [-1,1] or type(sign)!=int:raise ValueError('sign')
 if type(start)!=int or start<0 or (not periodic and start>len(key)):raise ValueError('start')
 if type(retain)!=int or retain<1:raise ValueError('retain')
 if any(type(i)!=int or not 0<=i<len(c) for i in ends|resets):raise ValueError('boundary/reset')
 if len(context)!=2 or any(type(x)!=int or not 0<=x<=29 for x in context):raise ValueError('context')
 t=time.monotonic();pos=start%len(key) if periodic else start;root=Node(0.,None,-1,False,0,0,pos);states={(pos,tuple(context)):[root]};expanded=0;peakstates=1;peakpaths=1;merged=0
 for i,v in enumerate(c):
  if i in resets:
   group=defaultdict(list)
   for (_,ctx),paths in states.items():group[(0,ctx)].extend(paths)
   merged+=len(states)-len(group);states={st:sorted(paths,key=lambda p:(-p.score,p.mask))[:retain] for st,paths in group.items()}
  nxt=defaultdict(list)
  for (pos,ctx),paths in states.items():
   choices=[]
   if periodic or pos<len(key):choices.append(((v+sign*key[pos])%29,(pos+1)%len(key) if periodic else pos+1,False))
   if v==0:choices.append((0,pos,True))
   for rune,nextpos,literal in choices:
    ss,w=extend(ctx,rune,i in ends);w=float(w)
    if not math.isfinite(w):raise ValueError('finite local score required')
    for p in paths:nxt[(nextpos,ss)].append(Node(p.score+w,p,rune,literal,p.used+int(not literal),(p.mask<<1)|literal,nextpos));expanded+=1
  if not nxt:raise ValueError(f'no legal path at rune{i}')
  states={st:sorted(paths,key=lambda p:(-p.score,p.mask))[:retain] for st,paths in nxt.items()};peakstates=max(peakstates,len(states));peakpaths=max(peakpaths,sum(map(len,states.values())))
 best=sorted((p for ps in states.values() for p in ps),key=lambda p:(-p.score,p.mask))[:retain];out=[]
 for p in best:
  cur=p;plain=[];literal=[]
  for i in range(len(c)-1,-1,-1):
   plain.append(cur.rune)
   if cur.literal:literal.append(i)
   cur=cur.parent
  out.append(dict(total=p.score,score=p.score/(len(c)+len(ends)) if c else p.score,plain=plain[::-1],literal_positions=literal[::-1],used=p.used,position=p.position,mask=str(p.mask)))
 return out,dict(expanded=expanded,maxstates=peakstates,max_live_paths=peakpaths,reset_state_merges=merged,seconds=time.monotonic()-t,scope='global conditional n-best decision paths under fixed resets/local objective; arbitrary cutoff ties; no state cap')

def encipher(plain,key,sign,literal,*,periodic=True,start=0,reset_before=()):
 pos=start%len(key) if periodic else start;resets=set(reset_before);out=[];used=0
 for i,r in enumerate(plain):
  if i in resets:pos=0
  if i in literal:
   assert r==0;out.append(0)
  else:
   if not periodic and pos>=len(key):raise ValueError('key exhausted')
   out.append((r-sign*key[pos])%29);used+=1;pos=(pos+1)%len(key) if periodic else pos+1
 return out,pos,used
