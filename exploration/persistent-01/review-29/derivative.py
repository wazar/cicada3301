from pathlib import Path
import json,math
import numpy as np
R=Path(__file__).parent;D=np.load(R.parent/'worker-p/P19/metric.npz')['D'];rng=np.random.default_rng(2929);C=rng.integers(0,20,(29,29));np.fill_diagonal(C,0);z=rng.normal(0,.2,29);z[-1]=.4
# Independent scalar negative loglikelihood and derivatives over allowed destinations.
def calc(z):
 a=list(z[:28])+[0];b=z[-1];v=0.;g=np.zeros(29)
 for x in range(29):
  w=[math.exp(a[y]+b*D[x,y]) if y!=x else 0 for y in range(29)];den=sum(w);n=sum(C[x])
  for y in range(29):
   if y==x:continue
   p=w[y]/den;v-=C[x,y]*math.log(p);err=n*p-C[x,y]
   if y<28:g[y]+=err
   g[-1]+=err*D[x,y]
 return v/C.sum(),g/C.sum()
v,g=calc(z);fd=[]
for i in range(29):
 a=z.copy();b=z.copy();a[i]+=1e-5;b[i]-=1e-5;fd.append((calc(a)[0]-calc(b)[0])/2e-5)
err=float(np.max(abs(g-fd)));assert err<1e-8
result=json.loads((R/'result.json').read_text());disposition=json.loads((R.parent/'worker-p/P19/disposition.json').read_text());assert result['conservative_rank_interval']==disposition['conservative_rank_tail_interval'];assert disposition['tail'] is None and not disposition['qualified'];(R/'derivative.json').write_text(json.dumps({'gradient_finite_difference_error':err,'conservative_disposition_matches':True},indent=2));print(err)
