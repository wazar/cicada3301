"""Exact sparse fixed-seed literal-F feedback with source-frozen resets."""
import time
class Refused(RuntimeError):pass
class Engine:
 def __init__(self,seed,L,max_states=100000,seconds=30):
  self.seed=tuple(seed);self.k=len(seed);self.L=L;self.N=len(L)-1;self.max_states=max_states;self.seconds=seconds
  assert self.k and all(0<=v<self.N for v in seed)
 def step(self,states,c,end,reset,parents=False):
  out={};trace={};expanded=0
  for state,value in states.items():
   hist,a,b=state;hist=() if reset else hist;key=self.seed[len(hist)] if len(hist)<self.k else sum(hist);p=(c-key)%self.N
   choices=[(p,(hist+(p,))[-self.k:],False)]
   if c==0:choices.append((0,hist,True))
   for p,h,literal in choices:
    expanded+=1;v=value+float(self.L[a,b,p]);aa,bb=b,p
    if end:v+=float(self.L[b,p,self.N]);aa,bb=p,self.N
    child=(h,aa,bb)
    if child not in out or v>out[child]:
     out[child]=v
     if parents:trace[child]=(state,p,literal)
  if len(out)>self.max_states:raise Refused(f'exact state refusal: {len(out)} > {self.max_states}; unresolved')
  return out,trace,expanded
 def solve(self,c,ends,resets,retain=16,block=16,initial_history=(),initial_context=None):
  start=time.monotonic();context=(self.N,self.N) if initial_context is None else tuple(initial_context);initial=(tuple(initial_history),*context);assert len(initial[0])<=self.k
  assert all(0<=v<self.N for v in initial[0]);assert all(0<=v<=self.N for v in context)
  ends=set(ends);resets=set(resets);states={initial:0.};snap={0:states.copy()};peak=1;exp=0;counts=[]
  def guard():
   if time.monotonic()-start>self.seconds:raise Refused(f'exact time refusal >{self.seconds}s including recovery; unresolved')
  for i,v in enumerate(c):
   guard();states,_,n=self.step(states,v,i in ends,i in resets);exp+=n;peak=max(peak,len(states));counts.append(len(states))
   if (i+1)%block==0 or i+1==len(c):snap[i+1]=states.copy()
  chosen=sorted(states,key=lambda s:(-states[s],s))[:retain];totals=[states[s] for s in chosen];plain=[[0]*len(c) for _ in chosen];literal=[[] for _ in chosen];endpos=len(c);maxback=0
  while endpos:
   begin=max(i for i in snap if i<endpos);cur=snap[begin].copy();trace=[]
   for i in range(begin,endpos):guard();cur,t,_=self.step(cur,c[i],i in ends,i in resets,True);trace.append(t)
   assert cur==snap[endpos];maxback=max(maxback,sum(len(t) for t in trace))
   for i in range(endpos-1,begin-1,-1):
    for j,s in enumerate(chosen):
     old,p,l=trace[i-begin][s];chosen[j]=old;plain[j][i]=p
     if l:literal[j].append(i)
   endpos=begin
  assert all(s==initial for s in chosen);alts=[dict(seed=list(self.seed),plain=p,literal_positions=sorted(l),total=t,score=t/(len(c)+len(ends)) if c else 0.) for p,l,t in zip(plain,literal,totals)]
  return dict(alternatives=alts,maximum=totals[0],peak_states=peak,forward_expansions=exp,layer_state_counts=counts,snapshot_states=sum(len(x) for x in snap.values()),peak_backtrace_states=maxback,seconds=time.monotonic()-start,block=block,scope='exact supplied fixed seed and legal F masks; retained final-state representatives, not global n-best')
