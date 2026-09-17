from pathlib import Path
import ast,json,hashlib,math
import numpy as np
from PIL import Image,ImageFilter
from scipy.ndimage import distance_transform_edt as edt
R=Path(__file__).parent;P=R.parent/'worker-r';Q=R.parent/'worker-q/Q06';D=dict(np.load(Q/'inputs.npz'));B=dict(np.load(P/'R05-bank.npz'));labels=D['labels'];train=D['train'];scope=np.isin(labels,D['eligible']);held=scope&~train;weights=[i/4 for i in range(-6,7)];angles=[i/2 for i in range(-2,3)];bank=B['features']
ns=globals();tree=ast.parse((R.parent/'review-23/check.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['feature','transform']],type_ignores=[]),'pixelhelpers','exec'),ns)
tree=ast.parse((R/'check.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'review24-functions','exec'),ns)
selected=sorted(set(int(np.flatnonzero((labels==c)&(train==split))[0]) for c in D['eligible'] for split in [False,True]));checks=[];inputs={};base_states=None
assert json.loads((P/'R05-controls-summary.json').read_text())['viable']
for name in ['R05-actual','R05-actual-raster-0','R05-actual-raster-1']:
 p=P/(name+'.npz');inputs[str(p)]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size};z=dict(np.load(p));s=json.loads((P/(name+'.json')).read_text());(R/'snapshots'/(name+'.json')).write_bytes((P/(name+'.json')).read_bytes())
 if name=='R05-actual':assert np.array_equal(z['pixels'],D['pixels'])
 else:
  rng=np.random.default_rng(475800+int(name[-1]));blur=rng.uniform(0,.75,418);gamma=rng.uniform(.8,1.2,418);offsets=rng.uniform(-.5,.5,(418,2));assert np.array_equal(blur,z['blur']) and np.array_equal(gamma,z['gamma']) and np.array_equal(offsets,z['offsets'])
  for i in range(418):assert np.array_equal(render(D['pixels'][i],0,blur[i],gamma[i],offsets[i]),z['pixels'][i])
 for i in range(418):assert np.array_equal(feature(z['pixels'][i]),z['features'][i])
 for i in selected:
  cost=np.concatenate([np.mean((bank[start:start+585]-z['features'][i])**2,axis=1) for start in range(0,len(bank),585)]);assert cost[int(z['best_bank_index'][i])]-cost.min()<1e-12;assert np.max(abs(cost.reshape(29,13,45).min(2)-z['identity_weight_cost'][i]))<1e-12
 result=metrics(z,s);assert not result['gate']
 if base_states is None:base_states=z['states'].copy()
 else:assert np.mean(z['states'][held]==base_states[held])==s['held_state_agreement']
 outliers=[{'id':int(i),'shape':int(labels[i]),'train':bool(train[i]),'weight':float(z['weights'][i])} for i in np.flatnonzero(scope&(z['weights']==-1.5))]
 checks.append({'name':name,**result,'lower_grid_bound_instances':outliers})
(R/'actual-inputs.json').write_text(json.dumps(inputs,indent=2));(R/'actual-result.json').write_text(json.dumps({'status':'PASS','direct_candidate_scores_checked':3*54*16965,'panels':checks},indent=2));print(checks)
