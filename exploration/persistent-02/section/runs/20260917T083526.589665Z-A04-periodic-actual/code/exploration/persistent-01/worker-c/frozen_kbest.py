"""Frozen exact global top-k periodic literal-F decoder; audited worker-c/P10 sharedP13."""
import itertools,collections

def kbest(c,ends,key,sign,lm,retain=16,start_context=(29,29),start_used=0):
 states={(start_used%len(key),start_context):[(0.,start_used,b'',())]};expanded=0;pruned=0;maxstates=1;maxpaths=1
 for i,v in enumerate(c):
  nxt=collections.defaultdict(list)
  for (_,s),paths in states.items():
   for literal in ([False,True] if v==0 else [False]):
    # Same phase/context means same emittedrune and scoreincrement for all histories.
    r=0 if literal else (v+sign*key[paths[0][1]%len(key)])%29;ss,w=lm.extend(s,r,i in ends)
    for sc,u,p,path in paths:
     uu=u+(not literal);nxt[(uu%len(key),ss)].append((sc+w,uu,p+bytes([r]),path+(i,) if literal else path));expanded+=1
  states={}
  for state,paths in nxt.items():
   paths.sort(key=lambda x:x[0],reverse=True);pruned+=max(0,len(paths)-retain);states[state]=paths[:retain]
  maxstates=max(maxstates,len(states));maxpaths=max(maxpaths,sum(map(len,states.values())))
 ordered=sorted(itertools.chain.from_iterable(states.values()),key=lambda x:x[0],reverse=True)[:retain]
 return [dict(score=x[0]/(len(c)+len(ends)),used=x[1],plain=list(x[2]),literal_positions=list(x[3])) for x in ordered],dict(expanded=expanded,dominated_paths_discarded=pruned,maxstates=maxstates,maxpaths=maxpaths,retain=retain,exact='global topk path scores; scoreties may select any tied path')
