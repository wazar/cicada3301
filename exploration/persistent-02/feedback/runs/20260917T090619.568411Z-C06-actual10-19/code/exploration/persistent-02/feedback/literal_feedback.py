"""Exact maximum for unknown-seed sum feedback excluding literal Fs from history.

Packed sparse state = (normal-history length capped k, last k normal plaintext
symbols, last two score tokens). Immutable NumPy snapshots every block; recover
selected complete paths by recomputing blocks with compact parent arrays.
Alternatives are one best representative per selected final state, not global
n-best paths. Tie representatives follow deterministic candidate generation.
"""
import numpy as np,time
class Engine:
 def __init__(self,k,L,max_states=500000):
  self.k=k;self.L=np.asarray(L,dtype=np.float64);self.N=len(L)-1;self.S=self.N+1;assert self.L.shape==(self.S,)*3 and k>=1 and np.isfinite(self.L).all()
  self.offset=np.array([sum(self.N**j for j in range(h)) for h in range(k+2)],dtype=np.int64);self.mod=self.N**(k-1);self.max_states=max_states
  assert self.offset[-1]*self.S*self.S<2**32,'packed state does not fit recorded uint32 parent arrays'
  self.sums=np.array([sum((a//self.N**j)%self.N for j in range(k)) for a in range(self.N**k)],dtype=np.int64)
 def step(self,ids,scores,c,end,parents=False):
  N,S=self.N,self.S;hidx=ids//(S*S);b=ids%S;a=(ids//S)%S;h=np.searchsorted(self.offset[1:],hidx,side='right');code=hidx-self.offset[h]
  immature=np.flatnonzero(h<self.k);mature=np.flatnonzero(h==self.k)
  ii=np.repeat(immature,N);pp=np.tile(np.arange(N,dtype=np.int64),len(immature));jj=mature;qq=(c-self.sums[code[jj]])%N
  origin=np.concatenate((ii,jj));rune=np.concatenate((pp,qq));newh=np.concatenate((h[ii]+1,h[jj]));newcode=np.concatenate((code[ii]*N+pp,(code[jj]%self.mod)*N+qq));lit=np.zeros(len(origin),dtype=np.uint8)
  if c==0:
   origin=np.concatenate((origin,np.arange(len(ids))));rune=np.concatenate((rune,np.zeros(len(ids),dtype=np.int64)));newh=np.concatenate((newh,h));newcode=np.concatenate((newcode,code));lit=np.concatenate((lit,np.ones(len(ids),dtype=np.uint8)))
  value=scores[origin]+self.L[a[origin],b[origin],rune]
  if end:value=value+self.L[b[origin],rune,N];aa=rune;bb=np.full(len(rune),N,dtype=np.int64)
  else:aa=b[origin];bb=rune
  child=((self.offset[newh]+newcode)*S+aa)*S+bb
  order=np.lexsort((np.arange(len(child)),-value,child));ordered=child[order];keep=order[np.r_[True,ordered[1:]!=ordered[:-1]]]
  if len(keep)>self.max_states:raise MemoryError(f'exact state budget exceeded: {len(keep)} > {self.max_states}; no approximate result')
  out=(child[keep],value[keep])
  if parents:return out+(ids[origin[keep]].astype(np.uint32),lit[keep],rune[keep].astype(np.uint8),len(child))
  return out+(len(child),)
 def solve(self,c,ends,retain=16,block=32):
  start=time.monotonic();c=list(c);ends=set(ends);assert all(0<=x<self.N for x in c);assert all(0<=x<len(c) for x in ends)
  initial=self.N*self.S+self.N;ids=np.array([initial],dtype=np.int64);scores=np.array([0.]);snapshots={0:(ids.copy(),scores.copy())};peak=1;expanded=0;counts=[]
  for i,v in enumerate(c):
   ids,scores,n=self.step(ids,scores,v,i in ends);peak=max(peak,len(ids));expanded+=n;counts.append(len(ids))
   if (i+1)%block==0 or i+1==len(c):snapshots[i+1]=(ids.copy(),scores.copy())
  order=np.lexsort((ids,-scores))[:retain];chosen=ids[order].copy();totals=scores[order].copy();out=np.zeros((len(chosen),len(c)),dtype=np.uint8);masks=np.zeros_like(out,dtype=bool);endpos=len(c);peakback=0
  while endpos:
   begin=max(j for j in snapshots if j<endpos);ii,ss=(x.copy() for x in snapshots[begin]);trace=[]
   for pos in range(begin,endpos):
    ii,ss,parent,lit,rune,n=self.step(ii,ss,c[pos],pos in ends,parents=True);trace.append((ii.copy(),parent,lit,rune))
   assert np.array_equal(ii,snapshots[endpos][0]) and np.array_equal(ss,snapshots[endpos][1]),'block recomputation changed scores/state order'
   peakback=max(peakback,sum(sum(a.nbytes for a in t) for t in trace))
   for pos in range(endpos-1,begin-1,-1):
    ids0,parent,lit,rune=trace[pos-begin];where=np.searchsorted(ids0,chosen);assert np.array_equal(ids0[where],chosen);out[:,pos]=rune[where];masks[:,pos]=lit[where];chosen=parent[where].astype(np.int64)
   endpos=begin
  assert np.all(chosen==initial);alts=[]
  for row,total in enumerate(totals):
   normals=[i for i in range(len(c)) if not masks[row,i]];seed=[(c[i]-int(out[row,i]))%self.N for i in normals[:self.k]];seed+=[None]*(self.k-len(seed));p=out[row].tolist();literal=np.flatnonzero(masks[row]).tolist()
   alts.append(dict(total=float(total),score=float(total)/(len(c)+len(ends)) if c else 0.,plain=p,literal_positions=literal,seed=seed,normal_symbols=len(normals),unspecified_seed_completions=self.N**sum(s is None for s in seed)))
  return dict(alternatives=alts,maximum=float(totals[0]),peak_states=peak,forward_expansions=expanded,layer_state_counts=counts,snapshot_bytes=sum(a.nbytes for s in snapshots.values() for a in s),peak_backtrace_arrays_bytes=peakback,seconds=time.monotonic()-start,k=self.k,alphabet=self.N,block=block,retain_final_states=retain,scope='exact state maximum for fixed local float64 scoring order; one representative per final state; not global n-best or full tie count; MemoryError stops without approximate result')
def encode(plain,seed,literal,N=29):
 literal=set(literal);history=[];cipher=[]
 for i,p in enumerate(plain):
  if i in literal:assert p==0;cipher.append(0)
  else:
   key=seed[len(history)] if len(history)<len(seed) else sum(history[-len(seed):]);cipher.append((p+key)%N);history.append(p)
 return cipher
