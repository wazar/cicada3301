from pathlib import Path
import ast,json,hashlib
import numpy as np
R=Path(__file__).parent;P=R.parent/'worker-r';Q=R.parent/'worker-q/Q06'
# Load only this review's independent pixel helper definitions, no worker function calls.
tree=ast.parse((R/'check.py').read_text());ns={};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'review-helper-functions','exec'),ns)
D=dict(np.load(Q/'inputs.npz'));B=dict(np.load(P/'R04-bank.npz'));labels=D['labels'];train=D['train'];scope=np.isin(labels,D['eligible']);held=scope&~train;selected=sorted(set(int(np.flatnonzero((labels==c)&(train==split))[0]) for c in D['eligible'] for split in [False,True]));bank=B['features'];checks=[];hashes={};base_states=None
assert json.loads((P/'R04-controls-summary.json').read_text())['viable']
for name in ['R04-actual','R04-actual-raster-0','R04-actual-raster-1']:
 path=P/(name+'.npz');z=dict(np.load(path));s=json.loads((P/(name+'.json')).read_text());hashes[str(path)]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size};(R/'snapshots'/(name+'.json')).write_bytes((P/(name+'.json')).read_bytes())
 if name=='R04-actual':assert np.array_equal(z['pixels'],D['pixels'])
 else:
  rep=int(name[-1]);rng=np.random.default_rng(474800+rep);offsets=rng.uniform(-.5,.5,(418,2));assert np.array_equal(offsets,z['offsets'])
  for i,xy in enumerate(offsets):assert np.array_equal(ns['transform'](D['pixels'][i],0,*xy,jpeg=True),z['pixels'][i])
 features=np.array([ns['feature'](im) for im in z['pixels']]);assert np.array_equal(features,z['features'])
 for i in selected:
  scores=np.mean((bank-features[i])**2,axis=1);assert scores[int(z['best_bank_index'][i])]-scores.min()<1e-12;assert np.max(abs(scores.reshape(29,13,9).min(2)-z['identity_angle_cost'][i]))<1e-12
 flat=z['identity_angle_cost'].reshape(418,-1);arg=flat.argmin(1);best=arg*9+z['identity_angle_translation_argmin'].reshape(418,-1)[np.arange(418),arg];assert np.array_equal(best,z['best_bank_index']);rmse=np.sqrt(flat.min(1));pred=B['shapes'][best//117].copy();pred[rmse>.16]=-1;active=scope&np.isin(pred,D['eligible']);correct=active&(pred==labels);angles=B['angles'][(best//9)%13];assert np.array_equal(pred,z['predicted_classes']) and np.array_equal(angles,z['angles']) and np.array_equal(active,z['active'])
 tr=angles[active&train];te=angles[active&~train];choices=[]
 for centers in [np.percentile(tr,[25,75]),[min(tr),max(tr)]]:
  centers=sorted(centers)
  for _ in range(30):
   st=[int(abs(v-centers[1])<abs(v-centers[0])) for v in tr]
   if len(set(st))<2:break
   new=sorted(sum(float(v) for v,k in zip(tr,st) if k==j)/st.count(j) for j in [0,1])
   if new==centers:break
   centers=new
  choices.append((sum(min((v-c)**2 for c in centers) for v in tr),centers))
 centers=min(choices,key=lambda a:a[0])[1];assert np.allclose(centers,s['centers'],atol=1e-12,rtol=0);states=np.full(418,-1)
 for i in np.flatnonzero(active):states[i]=int(abs(angles[i]-centers[1])<abs(angles[i]-centers[0]))
 assert np.array_equal(states,z['states']);coverage=sum(correct&held)/196;minority=min(sum(states[active&train]==k)/len(tr) for k in [0,1]);gain=1-sum(min((v-c)**2 for c in centers) for v in te)/max(sum((v-sum(tr)/len(tr))**2 for v in te),1e-12*len(te));both=sum(set(states[active&(pred==c)])=={0,1} for c in D['eligible']);sep=centers[1]-centers[0]
 gate=bool(sep>=1.5 and minority>=.2 and gain>=.5 and coverage>=.95 and both>=3);assert gate==s['channel_gate'] and not gate and abs(gain-s['held_mse_gain'])<1e-10 and minority==s['training_minority'] and both==s['both_state_classes']
 if base_states is None:base_states=states.copy()
 else:assert np.mean(states[held]==base_states[held])==s['held_state_agreement']
 checks.append({'name':name,'coverage':coverage,'centers':centers,'separation':sep,'minority':minority,'both':both,'gain':gain,'gate':gate})
(R/'actual-inputs.json').write_text(json.dumps(hashes,indent=2));(R/'actual-result.json').write_text(json.dumps({'status':'PASS','candidate_distances_checked':3*54*3393,'panels':checks},indent=2));print(checks)
