from pathlib import Path
import json,gzip,math,collections
import numpy as np
R=Path(__file__).parent;S=R.parent/'worker-r';rng=np.random.default_rng(2828);C=rng.integers(0,50,(29,29)).astype(float);np.fill_diagonal(C,0);C+=.5/28*(1-np.eye(29));rows=C.sum(1);total=C.sum();z=rng.normal(0,.4,29);z[-1]=0
# Scalar exclusion likelihood and expectation/covariance derivatives.
def calc(theta):
 v=0.;g=np.zeros(29);H=np.zeros((29,29))
 for x in range(29):
  weights=[0 if x==y else math.exp(theta[y]) for y in range(29)];p=np.array(weights)/sum(weights)
  for y in range(29):
   if x!=y:v-=C[x,y]*math.log(p[y])
  g+=rows[x]*p-C[x];H+=rows[x]*(np.diag(p)-np.outer(p,p))
 return v/total,g[:-1]/total,H[:-1,:-1]/total
v,g,H=calc(z);eps=1e-5;ng=[];nh=[]
for i in range(28):
 a=z.copy();b=z.copy();a[i]+=eps;b[i]-=eps;va,ga,_=calc(a);vb,gb,_=calc(b);ng.append((va-vb)/(2*eps));nh.append((ga-gb)/(2*eps))
errg=float(max(abs(np.array(ng)-g)));errh=float(np.max(abs(np.array(nh).T-H)));assert errg<1e-8 and errh<1e-8;assert np.linalg.eigvalsh(H).min()>0
loc=json.loads((S/'R07-failure-location.json').read_text());rep=json.loads((S/'R07-repair-check.json').read_text());assert loc['failed_seed']==503019==rep['failed_seed'];assert max(f['pre_gradient_max'] for f in rep['fits'])>1e-7;assert max(f['gradient_max'] for f in rep['fits'])<1e-7
with gzip.open(S/'R07-controls-initial-failed-full.jsonl.gz','rt') as f:old=[json.loads(x) for x in f]
assert len(old)==320 and old[-1]['seed']==503018
with gzip.open(S/'R07-controls-full.jsonl.gz','rt') as f:
 new=[json.loads(x) for x in f]
assert all(a['streams']==b['streams'] for a,b in zip(old,new[:320]));assert new[320]['seed']==503019;assert new[320]['streams']==rep['streams']
D=json.loads((S/'R01-input.json').read_text());gaptypes=collections.Counter(g['text'] for p in D for g in p['gaps'] if g['type']=='hyphen');special=[{'page':p['page'],**g} for p in D for g in p['gaps'] if g['type']=='hyphen' and g['text']=='-7-']
out={'gradient_finite_difference_error':errg,'hessian_finite_difference_error':errh,'hessian_min_eigenvalue':float(np.linalg.eigvalsh(H).min()),'initial_failed_panels':len(old),'failed_seed':503019,'all_initial_streams_preserved_on_rerun':True,'gap_text_counts':dict(gaptypes),'composite_gap':special};(R/'repair.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
