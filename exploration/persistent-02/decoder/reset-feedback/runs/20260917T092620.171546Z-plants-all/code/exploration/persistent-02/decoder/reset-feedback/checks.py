import itertools,json,numpy as np
from common import *
from model import *
from solver import solve

def main():
 guard();rng=np.random.default_rng(40917);counts=dict(random=0,exhaustive=0,caps=0)
 for t in range(140):
  k=2+t%7;n=int(rng.integers(3,35));p=rng.integers(29,size=n).tolist();seed=rng.integers(29,size=k).tolist();ends={i for i in range(n) if rng.random()<.35};resets={i+1 for i in ends if i+1<n and rng.random()<.8};c=[];start=0
  for i,r in enumerate(p):
   if i in resets:start=i
   key=seed[i-start] if i-start<k else sum(p[i-k:i]);c.append((r+key)%29)
  assert decode(c,seed,resets)==p and encipher(p,seed,resets)==c
  L=rng.normal(size=(30,30,30));W,B,q,meta=factors(c,ends,k,resets,L);x=[(-s)%29 for s in seed]+[sum(seed)%29];assert [(q[i]+x[j])%29 for i,j in enumerate(meta['phases'])]==p
  assert abs(value(W,B,x)-direct_score(p,ends,L))<1e-10;counts['random']+=1
 for k in (2,3,4):
  n=12;c=rng.integers(29,size=n).tolist();ends={0,2,5,8,11};resets={1,3,9};L=rng.normal(size=(30,30,30));W,B,q,meta=factors(c,ends,k,resets,L)
  free=np.indices((29,)*k,dtype=np.int16).reshape(k,-1).T;x=np.column_stack((free,(-free.sum(axis=1))%29));seeds=(-free)%29;pl=[];start=0;context=[np.full(len(x),29),np.full(len(x),29)];scores=np.zeros(len(x))
  for i,r in enumerate(c):
   if i in resets:start=i
   key=seeds[:,i-start] if i-start<k else sum(pl[i-k:i]);p=(r-key)%29;pl.append(p);scores+=L[context[0],context[1],p];context=[context[1],p]
   if i in ends:scores+=L[context[0],context[1],29];context=[context[1],np.full(len(x),29)]
  fs=sum(W[j,x[:,(j-2)%(k+1)],x[:,(j-1)%(k+1)],x[:,j]]+B[j,x[:,0],x[:,j]] for j in range(k+1));assert np.max(np.abs(scores-fs))<1e-9;truth=float(scores.max())
  for cap in (0,1,100000):
   z=solve(W,B,max_nodes=cap,max_seconds=30);assert z['maximum']<=truth+1e-9 and z['upper_bound']>=truth-1e-9
   if cap==100000:assert abs(z['maximum']-truth)<1e-9 and z['certified_within_1e_10']
   counts['caps']+=1
  counts['exhaustive']+=len(x)
 dump('checks.json',dict(status='PASS',counts=counts));print(counts)
if __name__=='__main__':main()
