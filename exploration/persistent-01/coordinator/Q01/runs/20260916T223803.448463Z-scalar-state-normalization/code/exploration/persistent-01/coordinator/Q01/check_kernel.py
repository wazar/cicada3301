import itertools,sys,pathlib
import numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).parent));import q01
cases=0
for n in range(1,7):
 for seq in itertools.product(range(3),repeat=n):
  a=np.array(seq);v=np.cumsum(a[None,:-1]==np.arange(3)[:,None],axis=1)%2
  for marker in range(3):
   state=0
   for i in range(1,n):
    state^=int(seq[i-1]==marker);assert state==v[marker,i-1];cases+=1
rng=np.random.default_rng(12)
for k in range(100):
 w=rng.dirichlet(np.full(29,.5));p=np.zeros((29,29))
 for x in range(29):
  for y in range(29):p[x,y]=0 if x==y else w[y]/(1-w[x])
 assert np.max(abs(p.sum(1)-1))<1e-14
print('PASS scalar parity positions',cases,'normalized conditional tables',100)
