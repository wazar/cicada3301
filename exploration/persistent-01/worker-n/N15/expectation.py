import json
from pathlib import Path
import numpy as np
D=Path(__file__).parent;M=json.loads((D.parent/'N14/maps.json').read_text());c=np.load(D/'actual-A.npz')['cipher'];off=0;out=[]
for m in M:
 n=len(m['route']);a=c[off:off+n];nonrep=np.r_[0,np.cumsum(a[1:]!=a[:-1])];ea=0
 for x,y in m['novel_edges']:
  k=int(abs(nonrep[x]-nonrep[y]));ea+=1/29+28/29*(-1/28)**k
 cnt=np.bincount(a,minlength=29);eb=len(m['novel_edges'])*sum(int(x)*(int(x)-1) for x in cnt)/(n*(n-1));out.append({'page':m['page'],'A_expected':ea,'B_expected':eb});off+=n
r={'formula_A':'sum_edges [1/29+(28/29)*(-1/28)^k], k=ordinary nonrepeat transitions between endpoints','formula_B':'sum_pages edges*sum_r n_r(n_r-1)/(N(N-1))','A_exact_expectation':sum(x['A_expected'] for x in out),'B_exact_expectation':sum(x['B_expected'] for x in out),'pages':out};(D/'exact-expectations.json').write_text(json.dumps(r,indent=2));print({k:v for k,v in r.items() if k!='pages'})
