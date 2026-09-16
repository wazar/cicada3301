"""Frozen finite-key exact globaltop16 runeLM F decoder; C15/sharedP16 controls."""
import collections

def finite(c,ends,key,sign,lm,retain=16):
 rem=[0]*(len(c)+1)
 for i in range(len(c)-1,-1,-1):rem[i]=rem[i+1]+(c[i]!=0)
 if len(key)<rem[0]:return [],dict(infeasible=True,expanded=0,maxstates=0)
 states={(0,(29,29)):[(0.,b'',())]};expanded=0;maxstates=1;infeasible=0
 for i,v in enumerate(c):
  nxt=collections.defaultdict(list)
  for (u,s),paths in states.items():
   choices=[]
   if u<len(key):choices.append(((v+sign*key[u])%29,u+1,False))
   if v==0:choices.append((0,u,True))
   for r,uu,literal in choices:
    if len(key)-uu<rem[i+1]:infeasible+=len(paths);continue
    ss,w=lm.extend(s,r,i in ends)
    for sc,p,path in paths:nxt[(uu,ss)].append((sc+w,p+bytes([r]),path+(i,) if literal else path));expanded+=1
  states={}
  for st,paths in nxt.items():paths.sort(key=lambda x:x[0],reverse=True);states[st]=paths[:retain]
  maxstates=max(maxstates,len(states))
 ordered=sorted([(sc,u,p,path) for (u,s),paths in states.items() for sc,p,path in paths],key=lambda x:x[0],reverse=True)[:retain]
 return [dict(score=sc/(len(c)+len(ends)),used=u,plain=list(p),literal_positions=list(path)) for sc,u,p,path in ordered],dict(infeasible=False,expanded=expanded,maxstates=maxstates,infeasible_prefixes=infeasible)
