import pathlib,json,hashlib,collections
import numpy as np
from PIL import Image
R=pathlib.Path(__file__).parent;D=np.load(R/'inputs.npz');maps=json.loads((R/'maps.json').read_text());images={p:Image.open(f'liber-primus/data/relikd/p{p}.jpg').convert('L') for p in [0,1]}
for j,m in enumerate(maps):
 r=m['source'];crop=images[r['page']].crop((r['x'],r['y'],r['right'],r['bottom']));assert hashlib.sha256(crop.tobytes()).hexdigest()==m['crop_sha256'];l,t,rr,b=m['canvas_box'];assert np.array_equal(np.array(crop),D['pixels'][j,t:b,l:rr])
rows=[]
for name in ['positive-0','positive-1','raster-null-0','raster-null-1']:
 z=np.load(R/(name+'.npz'));s=json.loads((R/(name+'.json')).read_text());scope=z['scope'];held=scope&~D['train'];active=z['active'];trainactive=active&D['train'];a=z['angles'];pred=z['predicted_classes'];state=z['states'];cent=np.array(s['centers']);assert np.array_equal(state[active],np.argmin((a[active,None]-cent)**2,axis=1));assert s['active_held']==sum(held&active);assert s['held_coverage']==np.mean(active[held]);assert s['held_identity_accuracy']==np.mean(pred[held]==D['labels'][held]);assert s['separation']==cent[1]-cent[0]
 flat={}
 for c in D['eligible']:
  ids=z[f'class_{c}_ids'];err=z[f'class_{c}_errors'];best=err.argmin(axis=1);angles=-3+.5*(best//9);assert np.array_equal(a[ids],angles);assert np.allclose(z['mse'][ids],err[np.arange(len(ids)),best]);f=np.ptp(err,axis=1)<1e-14
  if any(f):flat[int(c)]=int(sum(f))
 row={'case':name,'held_total':int(sum(held)),'held_unclassified':int(sum((pred==-1)&held)),'held_wrong_identified_class':int(sum((pred!=-1)&(pred!=D['labels'])&held)),'flat_orientation_banks':flat}
 if name.startswith('positive'):
  assert s['held_state_accuracy']==np.mean(state[held]==z['bits'][held]);row['maximum_possible_accuracy_at_retained_coverage']=s['held_coverage']
 rows.append(row)
assert not (R/'actual-summary.json').exists();save={'status':'PASS','exact_source_crops_verified':len(maps),'eligible_classes':len(D['eligible']),'eligible_instances':int(sum(np.isin(D['labels'],D['eligible']))),'controls':rows,'actual_statistics_not_run':True};(R/'check.json').write_text(json.dumps(save,indent=2));print(json.dumps(save))
