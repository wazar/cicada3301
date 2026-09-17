"""Pure reset recurrence and factor assembly, no data reads or score fitting."""
import numpy as np
def validate(c,k,resets,ends=None):
 if type(k)!=int or k<2:raise ValueError('k>=2 required')
 if any(type(x)!=int or not 0<=x<29 for x in c):raise ValueError('runes')
 if any(type(i)!=int or not 0<=i<len(c) for i in resets):raise ValueError('reset index')
 if ends is not None:
  if any(type(i)!=int or not 0<=i<len(c) for i in ends):raise ValueError('end index')
  if any(i>0 and i-1 not in ends for i in resets):raise ValueError('factorization requires explicit boundary before reset')

def decode(c,seed,resets=()):
 c=list(c);seed=list(seed);k=len(seed);resets=set(resets);validate(c,k,resets)
 if any(type(x)!=int or not 0<=x<29 for x in seed):raise ValueError('seed')
 p=[];start=0
 for i,v in enumerate(c):
  if i in resets:start=i
  j=i-start;p.append((v-(seed[j] if j<k else sum(p[i-k:i])))%29)
 return p

def encipher(p,seed,resets=()):
 p=list(p);k=len(seed);resets=set(resets);validate(p,k,resets);start=0;c=[]
 for i,v in enumerate(p):
  if i in resets:start=i
  j=i-start;c.append((v+(seed[j] if j<k else sum(p[i-k:i])))%29)
 return c

def phases(n,k,resets):
 out=[];start=0;resets=set(resets)
 for i in range(n):
  if i in resets:start=i
  out.append((i-start)%(k+1))
 return out

def factors(c,ends,k,resets,L):
 c=list(c);ends=set(ends);resets=set(resets);validate(c,k,resets,ends)
 if L.shape!=(30,30,30) or not np.isfinite(L).all():raise ValueError('finite30^3 token log weights required')
 q=decode(c,[0]*k,resets);phase=phases(len(c),k,resets);m=k+1;W=np.zeros((m,29,29,29));B=np.zeros((m,29,29));G=[np.arange(29).reshape(29,1,1),np.arange(29).reshape(1,29,1),np.arange(29).reshape(1,1,29)];context=[-1,-1];crossings=0;tokens=0
 for i in range(len(c)):
  for current in ([i,-1] if i in ends else [i]):
   refs=context+[current];j=phase[i]
   if current==i and i in resets and i>0:
    assert refs==[i-1,-1,i] and j==0
    # Axes B[r,x0,xr]. r may itself be0; evaluation then takes the diagonal.
    r=phase[i-1];x0=(q[i]+np.arange(29)[:,None])%29;xr=(q[i-1]+np.arange(29)[None,:])%29;B[r]+=L[xr,29,x0];crossings+=1
   else:
    inds=[]
    for ref in refs:
     if ref<0:inds.append(29);continue
     delta=(phase[ref]-j)%m
     if delta not in [(m-2)%m,(m-1)%m,0]:raise AssertionError(('unexpected nonlocal factor',i,refs,phase))
     axis={((m-2)%m):0,((m-1)%m):1,0:2}[delta];inds.append((q[ref]+G[axis])%29)
    W[j]+=L[tuple(inds)]
   context=[context[-1],current];tokens+=1
 assert tokens==len(c)+len(ends)
 return W,B,q,dict(phases=phase,crossing_factors=crossings,token_factors=tokens,local_factors=tokens-crossings)

def value(W,B,x):
 m=len(x);return float(sum(W[j,x[(j-2)%m],x[(j-1)%m],x[j]]+B[j,x[0],x[j]] for j in range(m)))

def direct_score(p,ends,L):
 context=(29,29);total=0.;ends=set(ends)
 for i,r in enumerate(p):
  w=float(L[context+(r,)]);context=(context[1],r)
  if i in ends:w+=float(L[context+(29,)]);context=(context[1],29)
  total+=w
 return total
