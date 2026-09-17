from pathlib import Path
import json,gzip,hashlib,math,bisect
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import lil_matrix
R=Path(__file__).parent;S=R.parent/'worker-r';D=json.loads((S/'R01-input.json').read_text());assert [p['page'] for p in D]==sorted(p['page'] for p in D)
assert not {4,9,14,19,24,29,34,39,44,50,54}&{p['page'] for p in D}
(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in list(S.glob('R07*'))+[S/'R01-input.json']:
 if p.is_file():
  b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
  if p.suffix in ['.py','.md','.json']:(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
heads=[];masks=[];gaps=0
for p in D:
 a=p['indices'];h=set()
 for g in p['gaps']:
  assert g['next']==g['previous']+1
  if g['type']=='hyphen':
   assert g['text']=='-';h.add(g['previous']);gaps+=1
 heads.append(h);masks.append([x==y for x,y in zip(a,a[1:])])
assert gaps==2176

def conditional(weights):
 return [[0. if i==j else weights[j]/sum(v for k,v in enumerate(weights) if k!=i) for j in range(29)] for i in range(29)]
def generate(weights,seed,pi=None,rate=0):
 rng=np.random.default_rng(seed);cdf=[[list(np.cumsum(row)) for row in conditional(w)] for w in weights];vs=[];echo=[]
 for loops,h in zip(masks,heads):
  a=[int(rng.integers(0,29))];us=rng.random(len(loops));coins=rng.random(len(loops));e=[]
  for j,loop in enumerate(loops):
   prev=a[-1]
   if loop:y=prev
   elif pi is not None and j in h and coins[j]<rate:y=pi[prev];e.append(j)
   else:y=bisect.bisect_right(cdf[int(j in h)][prev],us[j]);assert y<29
   a.append(y)
  vs.append(a);echo.append(e)
 return vs,echo

def count(vs):
 c=np.zeros((2,2,29,29),dtype=int)
 for page,a in enumerate(vs):
  assert [x==y for x,y in zip(a,a[1:])]==masks[page]
  for j,(x,y) in enumerate(zip(a,a[1:])):
   if x!=y:c[page%2,int(j in heads[page]),x,y]+=1
 return c
prior=np.full((29,29),.5/28);np.fill_diagonal(prior,0)
# Assignment LP has integral vertices by total unimodularity; independent of Hungarian implementation.
edges=[(i,j) for i in range(29) for j in range(29) if i!=j];A=lil_matrix((58,len(edges)))
for k,(i,j) in enumerate(edges):A[i,k]=1;A[29+j,k]=1
A=A.tocsr();lpchecks=[];maxgrad=0.;maxdiff=0.;maxincrease=-math.inf;panels=0;summaries=[];seedset=set()
for mode in ['controls','real']:
 saved=json.loads((S/f'R07-{mode}-results.json').read_text());current=None;nullscores=[];origins=[]
 with gzip.open(S/f'R07-{mode}-full.jsonl.gz','rt') as file:
  for line in file:
   z=json.loads(line);f=z['fit'];vs=z['streams'];C=count(vs);assert np.array_equal(C[0],f['train_counts']) and np.array_equal(C[1],f['held_counts']);probs=[]
   for state,fit in enumerate(f['baseline_fits']):
    theta=np.array(fit['theta']);assert theta[-1]==0;w=np.exp(theta-theta.max());w/=w.sum();assert np.max(abs(w-np.array(fit['weights'])))<1e-14
    pr=np.array(conditional(w));probs.append(pr);aug=C[0,state]+prior;rows=aug.sum(axis=1);grad=(rows@pr-aug.sum(axis=0))/aug.sum();objective=-sum(aug[i,j]*math.log(pr[i,j]) for i,j in edges)/aug.sum();maxgrad=max(maxgrad,float(max(abs(grad[:-1]))));assert max(abs(grad[:-1]))<=1e-7 and fit['qualified'];assert abs(objective-fit['objective'])<1e-12;maxincrease=max(maxincrease,fit['objective']-fit['pre_objective']);assert fit['objective']<=fit['pre_objective']+1e-12
   pi=f['pi'];assert sorted(pi)==list(range(29)) and all(i!=j for i,j in enumerate(pi));train=C[0,1];held=C[1,1];observed=sum(int(held[i,pi[i]]) for i in range(29));expected=sum(int(held[i].sum())*probs[1][i,pi[i]] for i in range(29));score=(observed-expected)/held.sum();trainobj=sum(train[i,pi[i]]-train[i].sum()*probs[1][i,pi[i]] for i in range(29));assert observed==f['held_matches'];maxdiff=max(maxdiff,abs(expected-f['held_expected']),abs(score-f['score']),abs(trainobj-f['train_objective']));assert maxdiff<1e-10
   if z['kind']=='panel':
    if current is not None:origins.append((current,nullscores))
    current=z;nullscores=[];weights=[b['weights'] for b in f['baseline_fits']]
    if mode=='real':assert vs==[p['indices'] for p in D]
    else:
     n=int(z['tag']);seed=480000+1000*n;rng=np.random.default_rng(seed);truth=z['truth'];perm=list(map(int,rng.permutation(29)))
     while any(i==j for i,j in enumerate(perm)):perm=list(map(int,rng.permutation(29)))
     base=np.geomspace(1,5,29);base/=sum(base);ww=[rng.permutation(base).tolist(),rng.permutation(base).tolist()];assert perm==truth['pi'] and np.allclose(ww,truth['weights'],rtol=0,atol=1e-15);generated,echo=generate(ww,seed+1,perm,[1,.25,0][n//4]);assert generated==vs and echo==truth['echo_positions'];assert seed+1 not in seedset;seedset.add(seed+1)
    gain=train-train.sum(axis=1)[:,None]*probs[1];res=linprog([-gain[i,j] for i,j in edges],A_eq=A,b_eq=np.ones(58),bounds=(0,1),method='highs');assert res.success and abs(-res.fun-trainobj)<1e-8;lpchecks.append({'mode':mode,'tag':z['tag'],'objective':-res.fun,'status':res.status,'fractionality':float(np.max(abs(res.x-np.round(res.x))))})
   else:
    assert z['seed'] not in seedset;seedset.add(z['seed']);assert vs==generate(weights,z['seed'])[0];nullscores.append(score)
   panels+=1
 origins.append((current,nullscores))
 for (z,ns),s in zip(origins,saved['panels']):
  tail=(1+sum(v>=z['fit']['score'] for v in ns))/(1+len(ns));assert tail==s['p_upper'];assert np.max(abs(np.array(ns)-np.array(s['null_scores'])))<1e-12;summaries.append({'mode':mode,'tag':z['tag'],'tail':tail,'score':z['fit']['score'],'held_matches':z['fit']['held_matches'],'expected':z['fit']['held_expected'],'nulls':len(ns)})
assert panels==1600
out={'status':'PASS','panels':panels,'gaps':gaps,'max_gradient':maxgrad,'max_score_expected_difference':maxdiff,'max_objective_increase':maxincrease,'distinct_main_generation_and_bootstrap_seeds':len(seedset),'assignment_lp':lpchecks,'summaries':summaries};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
