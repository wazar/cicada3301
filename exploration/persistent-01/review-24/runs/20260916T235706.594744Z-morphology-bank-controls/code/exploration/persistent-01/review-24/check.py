from pathlib import Path
import ast,json,hashlib,sys,math
import numpy as np
from scipy.ndimage import distance_transform_edt as edt
from PIL import Image,ImageFilter
R=Path(__file__).parent;P=R.parent/'worker-r';Q=R.parent/'worker-q/Q06';sys.path.insert(0,str(P));import R05 as subject
helpers=ast.parse((R.parent/'review-23/check.py').read_text());ns={};exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'review23-pixelhelpers','exec'),ns)
transform=ns['transform'];feature=ns['feature'];D=dict(np.load(Q/'inputs.npz'));B=dict(np.load(P/'R05-bank.npz'));labels=D['labels'];train=D['train'];scope=np.isin(labels,D['eligible']);held=scope&~train;assert sum(scope)==393 and sum(held)==196 and len(D['eligible'])==27
(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in [P/'R05.py',P/'R05-card.md',P/'R04.py',P/'R05-bank.npz']+sorted(P.glob('R05-*.json'))+sorted(P.glob('R05-*.npz')):
 b=p.read_bytes();inputs[str(p)]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 if p.suffix!='.npz':(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
def stroke(x,t,brute=False):
 x=np.clip(np.rint(x),0,255).astype(np.uint8);ink=x<128
 if brute:
  black=list(zip(*np.nonzero(ink)));white=list(zip(*np.nonzero(~ink)));assert black and white;d=np.zeros(x.shape)
  for i in range(x.shape[0]):
   for j in range(x.shape[1]):
    targets=white if ink[i,j] else black;v=math.sqrt(min((i-a)**2+(j-b)**2 for a,b in targets));d[i,j]=(.5-v) if ink[i,j] else (v-.5)
 else:
  d=np.where(ink,.5-edt(ink),edt(~ink)-.5)
 d=np.where(abs(d)<=1,x/255-.5,d)
 change=255*(np.minimum(1,np.maximum(0,d+.5-t))-np.minimum(1,np.maximum(0,d+.5)))
 return np.rint(np.minimum(255,np.maximum(0,x.astype(float)+change))).astype(np.uint8)
# Independent nearest-opposite-pixel Euclidean distances on mixed grayscale fixtures.
fixture=[]
for case in range(30):
 rng=np.random.default_rng(62400+case);x=rng.integers(0,256,(7,9),dtype=np.uint8);outs=[]
 for t in np.arange(-1.5,1.5001,.25):
  a=stroke(x,t,True);assert np.array_equal(a,subject.stroke(x,t));outs.append(a)
 assert np.array_equal(outs[6],x) and all(np.all(a>=b) for a,b in zip(outs,outs[1:]));fixture.append({'case':case,'pixels':x.tolist()})
weights=[i/4 for i in range(-6,7)];angles=[i/2 for i in range(-2,3)];shifts=[(x,y) for x in [-.5,0,.5] for y in [-.5,0,.5]];bank=B['features'];k=0
for ci,c in enumerate(D['shapes']):
 ids=np.flatnonzero(train&(labels==c));template=sum(D['pixels'][i].astype(float) for i in ids)/len(ids);assert np.array_equal(template,B['templates'][ci]);before=None
 for t in weights:
  morph=stroke(template,t);assert np.array_equal(morph,subject.stroke(template,t))
  if t==0:assert np.array_equal(morph,np.rint(template).astype(np.uint8))
  if before is not None:assert np.all(morph<=before)
  before=morph
  for a in angles:
   for dx,dy in shifts:assert np.array_equal(feature(transform(morph,a,dx,dy)),bank[k]);k+=1
assert k==16965

def render(x,t,blur,gamma,xy):
 im=Image.fromarray(stroke(x,t)).filter(ImageFilter.GaussianBlur(float(blur)));adjusted=np.rint(255*(np.asarray(im,dtype=float)/255)**gamma).astype(np.uint8);return transform(adjusted,0,*xy,jpeg=True)
def metrics(z,s,bits=None):
 flat=z['identity_weight_cost'].reshape(418,-1);arg=flat.argmin(1);best=arg*45+z['identity_weight_nuisance_argmin'].reshape(418,-1)[np.arange(418),arg];assert np.array_equal(best,z['best_bank_index']);rmse=np.sqrt(flat.min(1));pred=B['shapes'][best//585].copy();pred[rmse>.16]=-1;active=scope&np.isin(pred,D['eligible']);correct=active&(pred==labels);w=np.array(weights)[(best//45)%13]
 assert np.array_equal(pred,z['predicted_classes']) and np.array_equal(active,z['active']) and np.array_equal(correct,z['correct_identity']) and np.array_equal(w,z['weights']);assert np.array_equal(np.array(angles)[(best//9)%5],z['angles']) and np.array_equal(best%9,z['shift_index'])
 tr=w[active&train];te=w[active&~train];options=[]
 for centers in [np.percentile(tr,[25,75]),[min(tr),max(tr)]]:
  centers=sorted(centers)
  for _ in range(30):
   st=[int(abs(v-centers[1])<abs(v-centers[0])) for v in tr]
   if len(set(st))<2:break
   new=sorted(sum(float(v) for v,k in zip(tr,st) if k==j)/st.count(j) for j in [0,1])
   if new==centers:break
   centers=new
  options.append((sum(min((v-c)**2 for c in centers) for v in tr),centers))
 centers=min(options,key=lambda q:q[0])[1];assert np.allclose(centers,s['centers'],atol=1e-12,rtol=0);states=np.full(418,-1)
 for i in np.flatnonzero(active):states[i]=int(abs(w[i]-centers[1])<abs(w[i]-centers[0]))
 assert np.array_equal(states,z['states']);coverage=sum(correct&held)/196;minority=min(sum(states[active&train]==j)/len(tr) for j in [0,1]);gain=1-sum(min((v-c)**2 for c in centers) for v in te)/max(sum((v-sum(tr)/len(tr))**2 for v in te),len(te)*1e-12);both=sum(set(states[active&(pred==c)])=={0,1} for c in D['eligible']);gate=bool(centers[1]-centers[0]>=1 and minority>=.2 and gain>=.5 and coverage>=.95 and both>=3)
 assert gate==s['channel_gate'] and abs(gain-s['held_mse_gain'])<1e-10 and coverage==s['held_correct_identity_coverage'];joint=None
 if bits is not None:joint=sum((states==bits)&correct&held)/196;assert joint==s['held_joint_state_accuracy'] and s['control_pass']==(joint>=.9 and coverage>=.95)
 return {'coverage':float(coverage),'joint':None if joint is None else float(joint),'centers':centers,'minority':float(minority),'gain':float(gain),'both':both,'gate':gate}
selected=sorted(set(int(np.flatnonzero((labels==c)&(train==split))[0]) for c in D['eligible'] for split in [False,True]));panels=[];scores_checked=0;maxerror=0.
for positive in [True,False]:
 for rep in range(2):
  name=f'R05-{"positive" if positive else "ordinary"}-{rep}';z=dict(np.load(P/(name+'.npz')));s=json.loads((P/(name+'.json')).read_text());rng=np.random.default_rng((475600 if positive else 475700)+rep);bits=np.zeros(418,int)
  if positive:
   for c in D['shapes']:
    for split in [False,True]:
     ids=np.flatnonzero((labels==c)&(train==split));b=np.arange(len(ids))%2;rng.shuffle(b);bits[ids]=b
  assert np.array_equal(bits,z['bits']);blur=rng.uniform(0,.45 if positive else .75,418);gamma=rng.uniform(.9 if positive else .8,1.1 if positive else 1.2,418);offsets=rng.uniform(-.5,.5,(418,2));assert np.array_equal(blur,z['blur']) and np.array_equal(gamma,z['gamma']) and np.array_equal(offsets,z['offsets']);ts=([.75,1.25][rep]*(2*bits-1)) if positive else np.zeros(418);assert np.array_equal(ts,z['planted_weights'])
  for i in range(418):
   image=D['pixels'][i] if positive else B['templates'][list(B['shapes']).index(labels[i])];assert np.array_equal(render(image,ts[i],blur[i],gamma[i],offsets[i]),z['pixels'][i]);assert np.array_equal(feature(z['pixels'][i]),z['features'][i])
  for i in selected:
   # Chunk comparisons limit memory while keeping independent direct arithmetic.
   cost=np.concatenate([np.mean((bank[start:start+585]-z['features'][i])**2,axis=1) for start in range(0,len(bank),585)]);err=float(np.max(abs(cost.reshape(29,13,45).min(2)-z['identity_weight_cost'][i])));maxerror=max(maxerror,err);assert err<1e-12;assert cost[int(z['best_bank_index'][i])]-cost.min()<1e-12;scores_checked+=len(cost)
  panels.append({'name':name,**metrics(z,s,bits if positive else None)})
summary=json.loads((P/'R05-controls-summary.json').read_text());viable=all(p['joint']>=.9 and p['coverage']>=.95 for p in panels if p['joint'] is not None) and all(not p['gate'] for p in panels if p['joint'] is None);assert viable==summary['viable']
out={'status':'PASS','brute_distance_fixtures':fixture,'bank_features_checked':k,'direct_candidate_scores_checked':scores_checked,'max_distance_error':maxerror,'viable':viable,'panels':panels};(R/'result.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='brute_distance_fixtures'})
