"""Seed/history-free equality invariant within ciphertext-nonzero runs."""
import collections,numpy as np

def runs(c):
 start=None;out=[]
 for i,v in enumerate(list(c)+[0]):
  if v!=0 and start is None:start=i
  if v==0 and start is not None:out.append((start,i));start=None
 return out

def statistic(c,k,detail=True):
 assert k in (2,3) and all(type(x)==int and 0<=x<29 for x in c);m=k+1;num=den=0;records=[]
 for a,b in runs(c):
  q=[0]*min(m,b-a)
  for j in range(m,b-a):q.append((q[j-m]+c[a+j]-c[a+j-1])%29)
  hh=[]
  for phase in range(m):
   count=collections.Counter(q[phase::m]);n=sum(count.values());num+=sum(v*(v-1) for v in count.values());den+=n*(n-1);hh.append([count[x] for x in range(29)])
  if detail:records.append(dict(start=a,stop=b,q=q,histograms=hh))
 return dict(k=k,numerator=num,denominator=den,collision=num/den if den else None,runs=records)

def family(panelrows):
 x=np.array([[r['collision'] for r in row] for row in panelrows],dtype=float);assert np.isfinite(x).all();mean=x.mean(axis=0);sd=x.std(axis=0);z=np.divide(x-mean,sd,out=np.zeros_like(x),where=sd>0);f=z.max(axis=1);return dict(raw=x.tolist(),pooled_mean=mean.tolist(),pooled_sd=sd.tolist(),standardized=z.tolist(),family=f.tolist(),rank_count_ge=int(sum(f>=f[0]-1e-12)),rank_fraction=float(sum(f>=f[0]-1e-12)/len(f)))
