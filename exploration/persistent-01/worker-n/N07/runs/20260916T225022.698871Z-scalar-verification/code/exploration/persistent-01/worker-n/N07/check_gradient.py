import n07 as m
import numpy as np,json
from scipy.special import softmax
rng=np.random.default_rng(1707001);checks=[];maxerr=0.
for n in [3,5,29]:
 for rep in range(4):
  C=rng.integers(0,40,size=(n,n)).astype(float);np.fill_diagonal(C,0);A=m.augmented(C);z=rng.normal(size=n-1);v,g=m.objective(z,A);fd=[]
  for j in range(n-1):
   plus=z.copy();minus=z.copy();plus[j]+=1e-5;minus[j]-=1e-5;fd.append((m.objective(plus,A)[0]-m.objective(minus,A)[0])/2e-5)
  err=float(max(abs(g-fd)));maxerr=max(maxerr,err);assert err<2e-9;checks.append(dict(n=n,rep=rep,max_error=err))
controls=[]
for n in [3,5,29]:
 truth=softmax(np.linspace(-1.5,1.5,n));P=np.tile(truth,(n,1));np.fill_diagonal(P,0);P/=P.sum(1)[:,None]
 pseudo=np.full((n,n),.5/(n-1));np.fill_diagonal(pseudo,0)
 # Augmented matrix has exact model expectation, so known theta is the exact optimum.
 C=100000*P-pseudo;np.fill_diagonal(C,0);f,lp=m.fit(C);assert f['qualified'];error=float(max(abs(np.array(f['weights'])-truth)));assert error<1e-7
 # Integer finite counts: compare corrected objective against original destination estimator.
 integer=np.rint(10000*P);ff,_=m.fit(integer);old=np.log(m.augmented(integer).sum(0));old-=old[-1]
 oldobjective=m.objective(old[:-1],m.augmented(integer))[0];assert ff['qualified'] and ff['objective']<=oldobjective+1e-12
 controls.append(dict(n=n,exact_control_weight_error=error,integer_objective_improvement=oldobjective-ff['objective'],fit=f,integer_fit=ff))
out=dict(status='PASS',gradient_cases=len(checks),max_fd_error=maxerr,controls=controls);(m.O/'gradient-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
