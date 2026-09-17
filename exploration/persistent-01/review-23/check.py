from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
R=Path(__file__).parent;P=R.parent/'worker-r';Q=R.parent/'worker-q/Q06';D=dict(np.load(Q/'inputs.npz'));B=dict(np.load(P/'R04-bank.npz'));maps=json.loads((Q/'maps.json').read_text());(R/'snapshots').mkdir(exist_ok=True)
inputs={}
files=[P/'R04.py',P/'R04-card.md',P/'R04-bank.npz',P/'R04-inputs.json',Q/'inputs.npz',Q/'maps.json',Q/'REPORT.md',Q/'controls-summary.json']+sorted(P.glob('R04-*.json'))+sorted(P.glob('R04-legacy-*.npz'))+sorted(P.glob('R04-fresh-*.npz'))
for p in set(files):
 b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 # Keep large pixel arrays immutable by hash; small metadata/code snapshots are copied.
 if p.suffix!='.npz':(R/'snapshots'/((('Q06-' if p.parent==Q else '')+p.name))).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
labels=D['labels'];train=D['train'];shapes=D['shapes'];eligible=[int(c) for c in shapes if sum((labels==c)&train)>=4 and sum((labels==c)&~train)>=4];assert eligible==D['eligible'].tolist() and len(eligible)==27
scope=np.isin(labels,eligible);held=scope&~train;assert sum(scope)==393 and sum(held)==196
sources={pid:Image.open(f'liber-primus/data/relikd/p{pid}.jpg').convert('L') for pid in [0,1]}
for i,m in enumerate(maps):
 r=m['source'];crop=sources[r['page']].crop((r['x'],r['y'],r['right'],r['bottom']));assert hashlib.sha256(crop.tobytes()).hexdigest()==m['crop_sha256']
 canvas=Image.new('L',(128,160),255);canvas.paste(crop,((128-crop.width)//2,(160-crop.height)//2));assert np.array_equal(np.asarray(canvas),D['pixels'][i])
 assert r['shape_class']==labels[i] and r['train']==train[i]
def transform(x,angle,dx,dy,jpeg=False):
 im=Image.fromarray(np.clip(np.rint(x),0,255).astype(np.uint8))
 if angle!=0:im=im.rotate(float(angle),resample=Image.Resampling.BICUBIC,expand=False,fillcolor=255)
 if dx!=0 or dy!=0:im=im.transform((128,160),Image.Transform.AFFINE,(1,0,-float(dx),0,1,-float(dy)),resample=Image.Resampling.BICUBIC,fillcolor=255)
 if jpeg:
  buf=io.BytesIO();im.save(buf,'JPEG',quality=92);buf.seek(0);im=Image.open(buf).convert('L')
 return np.asarray(im,dtype=np.uint8)
def feature(x):
 box=Image.fromarray(np.where(x<128,255,0).astype(np.uint8)).getbbox();assert box
 return np.asarray(Image.fromarray(x).crop(box).resize((32,64),Image.Resampling.BILINEAR),dtype=float).reshape(-1)/255
angles=[i/2 for i in range(-6,7)];shifts=[(x,y) for x in [-.5,0,.5] for y in [-.5,0,.5]];bank=[]
for ci,c in enumerate(shapes):
 ids=np.flatnonzero(train&(labels==c));template=sum((D['pixels'][i].astype(float) for i in ids))/len(ids);assert np.array_equal(template,B['templates'][ci])
 for a in angles:
  for dx,dy in shifts:bank.append(feature(transform(template,a,dx,dy)))
bank=np.array(bank);assert np.array_equal(bank,B['features']);assert len(bank)==3393
selected=sorted(set(int(np.flatnonzero((labels==c)&(train==split))[0]) for c in eligible for split in [False,True]));assert len(selected)==54
panels=[];costschecked=0;maxerr=0.
for origin in ['legacy','fresh']:
 for kind in ['positive','raster-null']:
  for rep in range(2):
   name=f'R04-{origin}-{kind}-{rep}';z=dict(np.load(P/(name+'.npz')));summary=json.loads((P/(name+'.json')).read_text())
   if origin=='legacy':
    old=dict(np.load(Q/(f'{kind}-{rep}.npz')));assert np.array_equal(z['pixels'],old['pixels']);assert np.array_equal(z['offsets'],old['offsets'])
    if kind=='positive':assert np.array_equal(z['bits'],old['bits'])
   else:
    rng=np.random.default_rng((474600 if kind=='positive' else 474700)+rep)
    if kind=='positive':
     bits=np.zeros(len(labels),int)
     for c in shapes:
      for split in [False,True]:
       ids=np.flatnonzero((labels==c)&(train==split));b=np.arange(len(ids))%2;rng.shuffle(b);bits[ids]=b
     assert np.array_equal(bits,z['bits'])
    offsets=rng.uniform(-.5,.5,(len(labels),2));assert np.array_equal(offsets,z['offsets'])
    for i,xy in enumerate(offsets):
     image=D['pixels'][i] if kind=='positive' else B['templates'][list(shapes).index(labels[i])];angle=(1.5 if rep==0 else 2)*(2*bits[i]-1) if kind=='positive' else 0
     assert np.array_equal(transform(image,angle,*xy,jpeg=True),z['pixels'][i])
   F=np.array([feature(im) for im in z['pixels']]);assert np.array_equal(F,z['features'])
   # Direct difference-and-square distances, independent of scipy.cdist.
   for i in selected:
    scores=np.mean((bank-F[i])**2,axis=1);matrix=scores.reshape(29,13,9);by=matrix.min(axis=2);err=float(np.max(abs(by-z['identity_angle_cost'][i])));maxerr=max(maxerr,err);assert err<1e-12
    chosen=int(z['best_bank_index'][i]);assert scores[chosen]-scores.min()<1e-12;assert abs(np.sqrt(scores[chosen])-z['rmse'][i])<1e-12
    assert int(z['shift_index'][i])==chosen%9;assert z['angles'][i]==angles[(chosen//9)%13]
    expected=int(shapes[chosen//117]) if z['rmse'][i]<=.16 else -1;assert z['predicted_classes'][i]==expected;costschecked+=len(scores)
   # Reconstruct full all-instance argmin from saved per-angle minima and shift minimizers.
   flat=z['identity_angle_cost'].reshape(len(labels),-1);arg=flat.argmin(1);best=arg*9+z['identity_angle_translation_argmin'].reshape(len(labels),-1)[np.arange(len(labels)),arg]
   assert np.array_equal(best,z['best_bank_index']);rmse=np.sqrt(flat.min(1));assert np.allclose(rmse,z['rmse'],atol=1e-12,rtol=0)
   pred=shapes[best//117].copy();pred[rmse>.16]=-1;active=scope&np.isin(pred,eligible);correct=active&(pred==labels);assert np.array_equal(pred,z['predicted_classes']) and np.array_equal(active,z['active']) and np.array_equal(correct,z['correct_identity'])
   vals=np.array(angles)[(best//9)%13];tr=vals[active&train];te=vals[active&~train];options=[]
   for centers in [np.percentile(tr,[25,75]),[min(tr),max(tr)]]:
    centers=sorted(centers)
    for step in range(30):
     memberships=[0 if abs(v-centers[0])<=abs(v-centers[1]) else 1 for v in tr]
     if len(set(memberships))<2:break
     new=sorted(sum(float(v) for v,k in zip(tr,memberships) if k==state)/memberships.count(state) for state in [0,1])
     if new==centers:break
     centers=new
    options.append((sum(min((v-c)**2 for c in centers) for v in tr),centers))
   centers=min(options,key=lambda q:q[0])[1];assert np.allclose(centers,summary['centers'],atol=1e-12,rtol=0)
   states=np.full(len(labels),-1)
   for i in np.flatnonzero(active):states[i]=0 if abs(vals[i]-centers[0])<=abs(vals[i]-centers[1]) else 1
   assert np.array_equal(states,z['states'])
   coverage=sum(correct&held)/196;gain=1-sum(min((v-c)**2 for c in centers) for v in te)/max(sum((v-sum(tr)/len(tr))**2 for v in te),1e-12*len(te));minority=min(sum(states[active&train]==b)/len(tr) for b in [0,1]);both=sum(set(states[active&(pred==c)])=={0,1} for c in eligible)
   gate=bool(centers[1]-centers[0]>=1.5 and minority>=.2 and gain>=.5 and coverage>=.95 and both>=3)
   assert gate==summary['channel_gate'] and abs(gain-summary['held_mse_gain'])<1e-10 and coverage==summary['held_correct_identity_coverage'] and both==summary['both_state_classes']
   joint=None
   if kind=='positive':joint=sum((states==z['bits'])&correct&held)/196;assert joint==summary['held_joint_state_accuracy'];assert summary['control_pass']==(joint>=.9 and coverage>=.95)
   panels.append({'name':name,'correct_identity':int(sum(correct&held)),'joint_correct':None if joint is None else int(round(joint*196)),'coverage':coverage,'joint':joint,'gate':gate,'centers':centers})
old=json.loads((Q/'controls-summary.json').read_text());assert not old['viable'];assert all(r['held_coverage']<.6 for r in old['rows'] if r['type']=='positive')
new=json.loads((P/'R04-controls-summary.json').read_text());assert new['viable']==all(p['joint']==1 for p in panels if p['joint'] is not None) and all(not p['gate'] for p in panels if p['joint'] is None)
out={'status':'PASS','eligible_classes':eligible,'eligible_count':27,'eligible_instances':393,'held':196,'bank_entries_rebuilt':len(bank),'source_canvases_rebuilt':len(maps),'direct_candidate_scores_checked':costschecked,'max_distance_error':maxerr,'panels':panels,'q06_stays_failed':True}
(R/'result.json').write_text(json.dumps(out,indent=2));print(out)
