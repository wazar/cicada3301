"""Exact modular affine influence; supplied masks, no search or language model."""
import itertools,json,random
from pathlib import Path

def rank(rows,q):
 a=[list(r) for r in rows];r=0
 for col in range(len(a[0]) if a else 0):
  pivot=next((j for j in range(r,len(a)) if a[j][col]%q),None)
  if pivot is None:continue
  a[r],a[pivot]=a[pivot],a[r];v=pow(a[r][col]%q,-1,q);a[r]=[(x*v)%q for x in a[r]]
  for j in range(len(a)):
   if j!=r:
    v=a[j][col]%q;a[j]=[(x-v*y)%q for x,y in zip(a[j],a[r])]
  r+=1
  if r==len(a):break
 return r

def trace(cipher,k,literal,q=29,emitted=True):
 literal=set(literal);hist=[];phase=0;forms=[];ranks=[];phases=[]
 for i,c in enumerate(cipher):
  if i in literal:
   assert c==0;v=[0]*(k+1)
  elif phase<k:
   v=[c]+[0]*k;v[phase+1]=-1;phase+=1
  else:
   v=[(c-sum(h[0] for h in hist))%q]+[(-sum(h[j+1] for h in hist))%q for j in range(k)]
  v=[x%q for x in v];forms.append(v)
  if emitted or i not in literal:hist=(hist+[v])[-k:]
  ranks.append(rank([h[1:] for h in hist],q));phases.append(min(phase,k))
 return dict(forms=forms,ranks=ranks,phases=phases,first_mature_zero=next((i for i,(r,p) in enumerate(zip(ranks,phases)) if r==0 and p==k),None))

def scalar(cipher,seed,literal,q,emitted):
 h=[];out=[];j=0
 for i,c in enumerate(cipher):
  if i in literal:p=0
  else:p=(c-(seed[j] if j<len(seed) else sum(h[-len(seed):])))%q;j+=1
  out.append(p)
  if emitted or i not in literal:h.append(p)
 return out

def main():
 rng=random.Random(202609171012);cases=0;evaluations=0
 for q,k,n in itertools.product([2,3,5],[1,2,3],[0,1,4,9]):
  for _ in range(6):
   c=[rng.randrange(q) for _ in range(n)];lit=[i for i,v in enumerate(c) if v==0 and rng.randrange(2)]
   for emitted in [False,True]:
    t=trace(c,k,lit,q,emitted);cases+=1
    mature=[r for r,p in zip(t['ranks'],t['phases']) if p==k]
    assert all(b<=a for a,b in zip(mature,mature[1:]))
    if not emitted:assert all(r==k for r in mature)
    for seed in itertools.product(range(q),repeat=k):
     actual=scalar(c,seed,lit,q,emitted);pred=[(f[0]+sum(a*b for a,b in zip(f[1:],seed)))%q for f in t['forms']]
     assert actual==pred;evaluations+=1
 witnesses={}
 for name,c,k,lit in [('early_zero',[0,1,2],2,[0]),('mature_erase',[1,2,0,0,4,5],2,[2,3]),('separated',[1,2,0,4,0,5,0,6],2,[2,4,6])]:
  witnesses[name]={'cipher':c,'k':k,'literal':lit,'emitted':trace(c,k,lit),'normal_only':trace(c,k,lit,emitted=False)}
 result=dict(cases=cases,seed_evaluations=evaluations,passed=True,witnesses=witnesses,scope='Fixed masks only; rank zero after seed phase complete implies future seed independence for identical future mask/cipher.')
 Path(__file__).with_name('selftest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='witnesses'}))
if __name__=='__main__':main()
