"""Exact fixed-seed-partition DP for sum feedback with shared-seed major resets."""
import numpy as np,time
class Engine:
 def __init__(self,seeds,L,max_states=500000):
  self.seeds=np.asarray(seeds,dtype=np.int64);assert self.seeds.ndim==2 and len(self.seeds)>0
  self.k=self.seeds.shape[1];self.L=np.asarray(L,dtype=np.float64);self.N=len(L)-1;self.S=self.N+1;assert self.L.shape==(self.S,)*3 and self.k>=1 and np.isfinite(self.L).all();assert np.all((self.seeds>=0)&(self.seeds<self.N))
  self.offset=np.array([sum(self.N**j for j in range(h)) for h in range(self.k+2)],dtype=np.int64);self.H=int(self.offset[-1]);self.mod=self.N**self.k;self.max_states=max_states
  assert len(self.seeds)*self.H*self.S*self.S<2**32,'uint32 compact parent bound'
  self.sums=np.array([sum((a//self.N**j)%self.N for j in range(self.k)) for a in range(self.N**self.k)],dtype=np.int64)
 def step(self,ids,scores,c,end,reset,parents=False):
  N,S=self.N,self.S;tmp=ids//(S*S);sid=tmp//self.H;hidx=tmp%self.H;b=ids%S;a=(ids//S)%S;h=np.searchsorted(self.offset[1:],hidx,side='right');code=hidx-self.offset[h]
  if reset:h=np.zeros_like(h);code=np.zeros_like(code)
  key=np.where(h<self.k,self.seeds[sid,np.minimum(h,self.k-1)],self.sums[code]);rune=(c-key)%N;origin=np.arange(len(ids));newh=np.minimum(h+1,self.k);newcode=(code*N+rune)%self.mod;lit=np.zeros(len(ids),dtype=np.uint8);nsid=sid
  if c==0:
   origin=np.concatenate((origin,origin));rune=np.concatenate((rune,np.zeros(len(ids),dtype=np.int64)));newh=np.concatenate((newh,h));newcode=np.concatenate((newcode,code));lit=np.concatenate((lit,np.ones(len(ids),dtype=np.uint8)));nsid=np.concatenate((sid,sid))
  value=scores[origin]+self.L[a[origin],b[origin],rune]
  if end:value=value+self.L[b[origin],rune,N];aa=rune;bb=np.full(len(rune),N,dtype=np.int64)
  else:aa=b[origin];bb=rune
  child=((nsid*self.H+self.offset[newh]+newcode)*S+aa)*S+bb;order=np.lexsort((np.arange(len(child)),-value,child));ordered=child[order];keep=order[np.r_[True,ordered[1:]!=ordered[:-1]]]
  if len(keep)>self.max_states:raise MemoryError(f'exact state budget exceeded: {len(keep)} > {self.max_states}; unresolved, no approximate maximum')
  out=(child[keep],value[keep])
  if parents:return out+(ids[origin[keep]].astype(np.uint32),lit[keep],rune[keep].astype(np.uint8),len(child))
  return out+(len(child),)
 def solve(self,c,ends,resets,retain=16,block=32,initial_history=None,initial_context=None):
  start=time.monotonic();c=list(c);ends=set(ends);resets=set(resets);assert all(0<=x<self.N for x in c);assert all(0<=x<len(c) for x in ends|resets)
  history=[] if initial_history is None else list(initial_history);context=(self.N,self.N) if initial_context is None else tuple(initial_context)
  assert len(history)<=self.k and all(0<=p<self.N for p in history);assert len(context)==2 and all(0<=p<=self.N for p in context)
  assert not history or len(self.seeds)==1,'carried history requires one selected seed'
  hcode=0
  for p in history:hcode=hcode*self.N+p
  initials=(np.arange(len(self.seeds),dtype=np.int64)*self.H+self.offset[len(history)]+hcode)*self.S*self.S+context[0]*self.S+context[1];ids=initials.copy();scores=np.zeros(len(ids));snapshots={0:(ids.copy(),scores.copy())};peak=len(ids);expanded=0;counts=[]
  for i,v in enumerate(c):
   ids,scores,n=self.step(ids,scores,v,i in ends,i in resets);peak=max(peak,len(ids));expanded+=n;counts.append(len(ids))
   if (i+1)%block==0 or i+1==len(c):snapshots[i+1]=(ids.copy(),scores.copy())
  order=np.lexsort((ids,-scores))[:retain];chosen=ids[order].copy();seed_ids=chosen//(self.S*self.S)//self.H;totals=scores[order].copy();out=np.zeros((len(chosen),len(c)),dtype=np.uint8);masks=np.zeros_like(out,dtype=bool);endpos=len(c);peakback=0
  while endpos:
   begin=max(j for j in snapshots if j<endpos);ii,ss=(x.copy() for x in snapshots[begin]);trace=[]
   for pos in range(begin,endpos):
    ii,ss,parent,lit,rune,n=self.step(ii,ss,c[pos],pos in ends,pos in resets,parents=True);trace.append((ii.copy(),parent,lit,rune))
   assert np.array_equal(ii,snapshots[endpos][0]) and np.array_equal(ss,snapshots[endpos][1])
   peakback=max(peakback,sum(sum(a.nbytes for a in t) for t in trace))
   for pos in range(endpos-1,begin-1,-1):
    ids0,parent,lit,rune=trace[pos-begin];where=np.searchsorted(ids0,chosen);assert np.array_equal(ids0[where],chosen);out[:,pos]=rune[where];masks[:,pos]=lit[where];chosen=parent[where].astype(np.int64)
   endpos=begin
  assert np.array_equal(chosen,initials[seed_ids]);alts=[]
  for row,total in enumerate(totals):
   used=set();normal=len(history)
   for i in range(len(c)):
    if i in resets:normal=0
    if not masks[row,i]:
     if normal<self.k:used.add(normal)
     normal+=1
   alts.append(dict(total=float(total),score=float(total)/(len(c)+len(ends)) if c else 0.,plain=out[row].tolist(),literal_positions=np.flatnonzero(masks[row]).tolist(),seed=self.seeds[seed_ids[row]].tolist(),seed_slots_used=sorted(used),unused_seed_aliases=self.N**(self.k-len(used))))
  return dict(alternatives=alts,maximum=float(totals[0]),seed_count=len(self.seeds),peak_states=peak,forward_expansions=expanded,layer_state_counts=counts,snapshot_bytes=sum(a.nbytes for s in snapshots.values() for a in s),peak_backtrace_arrays_bytes=peakback,seconds=time.monotonic()-start,k=self.k,alphabet=self.N,block=block,retain_final_states=retain,scope='exact state maximum over supplied complete seed partition and all legal Fmasks; one representative per final state, not globaln-best or full tie/unused-seed census; state refusal unresolved')
def encode(plain,seed,literal,resets,N=29):
 literal=set(literal);resets=set(resets);history=[];cipher=[]
 for i,p in enumerate(plain):
  if i in resets:history=[]
  if i in literal:assert p==0;cipher.append(0)
  else:
   key=seed[len(history)] if len(history)<len(seed) else sum(history[-len(seed):]);cipher.append((p+key)%N);history.append(p)
 return cipher
