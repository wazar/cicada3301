from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve
R=Path(__file__).parent;B=R.parent;ROOT=B.parent.parent;S=B/'worker-s';z=json.loads((S/'S09-result.json').read_text());(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in list(S.glob('S09-*.npz'))+list(S.glob('S09-*.json'))+[S/'S09-CARD.md',S/'s09.py']+[ROOT/f'liber-primus/data/relikd/p{i}.jpg' for i in [0,2,3,5,6]]:
 b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 if p.suffix in ['.json','.md','.py']:(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
for item in z['inputs']:assert hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()==item['sha256']
raw0=np.array(Image.open(ROOT/'liber-primus/data/relikd/p0.jpg').convert('L'));raw2=np.array(Image.open(ROOT/'liber-primus/data/relikd/p2.jpg').convert('L'));templates={'A_p0top':np.pad(raw0[600:665,1110:1270],64,constant_values=255),'B_commonbottom':np.pad(raw0[2930:2995,1110:1270],64,constant_values=255)};h,w=templates['A_p0top'].shape;angles=[i/4 for i in range(-32,33)];phases=[(0,0),(0,.5),(.5,0),(.5,.5)]
def render(a,angle,phase):
 im=Image.fromarray(a).rotate(angle,Image.Resampling.BICUBIC,expand=False,fillcolor=255)
 if phase!=(0,0):im=im.transform((w,h),Image.Transform.AFFINE,(1,0,-phase[0],0,1,-phase[1]),Image.Resampling.BICUBIC,fillcolor=255)
 return np.array(im)
def jpeg(a):
 b=io.BytesIO();Image.fromarray(a).save(b,format='JPEG',quality=92);return np.array(Image.open(io.BytesIO(b.getvalue())).convert('L'))
variants={k:[render(t,a,p) for a in angles for p in phases] for k,t in templates.items()};settings=[(-5.5,(0,.5),(7,-5)),(-2.25,(.5,0),(-6,4)),(2.75,(.5,.5),(3,-4)),(5.25,(0,0),(-2,6))];gridschecked=0;reschecked=0;records=[]
def checkfit(target,name,key,record,real):
 global gridschecked,reschecked
 saved=np.load(S/f'S09-{name}-{key}-fits.npz');assert np.array_equal(target,saved['target']) and np.array_equal(templates[key],saved['reference']);scores=saved['scores'];allres=saved['all_variant_best_signed_residuals'] if real else None;ti=255-target.astype(np.int64);energy=int((ti*ti).sum());rows=[];residuals=[]
 for i,v in enumerate(variants[key]):
  vi=255-v.astype(np.int64);con=np.rint(fftconvolve(ti.astype(float),vi[::-1,::-1].astype(float),mode='full')).astype(np.int64);grid=energy+int((vi*vi).sum())-2*con[h-17:h+16,w-17:w+16];assert np.array_equal(grid,scores[i]);index=int(grid.argmin());dy,dx=index//33-16,index%33-16;pred=np.roll(v,(dy,dx),(0,1));res=target.astype(np.int16)-pred.astype(np.int16);sse=int(np.square(res.astype(np.int64)).sum());assert sse==grid.min();row=dict(angle=angles[i//4],phase_dx_dy=list(phases[i%4]),shift_dy_dx=[dy,dx],sse=sse);assert row==record['all_variant_best'][i];rows.append(row);residuals.append(res);gridschecked+=1089
  if real:assert np.array_equal(res,allres[i]);reschecked+=1
 winner=min(range(260),key=lambda i:rows[i]['sse']);assert rows[winner]==record['best'] and np.array_equal(residuals[winner],saved['best_signed_residual']);pred=target.astype(np.int16)-residuals[winner];ma=target<128;mb=pred<128;assert record['different128']==int((ma!=mb).sum());assert abs(record['iou128']-float((ma&mb).sum()/(ma|mb).sum()))<1e-14
 for suffix,a in [('target',target),('predicted',pred),('residual128',np.where(ma!=mb,0,255))]:assert np.array_equal(a,np.array(Image.open(S/'S09-pixels'/f'{name}-{key}-{suffix}.png')))
 return rows[winner]['sse']
controlcorrect=[]
for control in z['controls']:
 truth=control['truth_template'];i=int(control['name'].rsplit('-',1)[1]);t=templates[truth]
 if i:angle,phase,shift=settings[i-1];t=jpeg(np.roll(render(t,angle,phase),shift,(0,1)));assert control['truth_pose']==[angle,list(phase),list(shift)]
 else:assert control['truth_pose'] is None
 vals={k:checkfit(t,control['name'],k,control['fits'][k],False) for k in templates};records.append((control,vals))
 if i:controlcorrect.append(vals[truth]);assert control['fits'][truth]['best']==dict(angle=angle,phase_dx_dy=list(phase),shift_dy_dx=list(shift),sse=vals[truth])
 else:assert vals[truth]==0
threshold=4*max(controlcorrect);assert threshold==z['threshold_SSE']
def classify(v):
 win,lose=sorted(v,key=v.get);a,b=v[win],v[lose];ok=a<=threshold and b>=4*a and b>a
 return dict(label=win if ok else 'AMBIGUOUS',winner=win,winner_sse=a,loser_sse=b,loser_winner_ratio=b/a if a else None,accepted=ok)
for control,vals in records:assert classify(vals)==control['classification'] and control['classification']['label']==control['truth_template']
assert z['control_gate']
real=[]
for r in z['real']:
 y0,y1=(600,665) if r['region']=='top' else (2930,2995);t=np.pad(raw2[y0:y1,1110:1270],64,constant_values=255);vals={k:checkfit(t,'p2-'+r['region'],k,r['fits'][k],True) for k in templates};assert classify(vals)==r['classification'];real.append(dict(region=r['region'],classification=classify(vals)))
assert gridschecked==24*283140 and reschecked==4*260
out={'status':'PASS','template_fit_calls':24,'all_SSE_cells':gridschecked,'actual_full_signed_residuals':reschecked,'threshold':threshold,'control_correct_SSE':controlcorrect,'control_gate':True,'real':real,'eligibility':'Independent full-image visual inspection:2 comparable loops,3/5/6 no comparable loops at frozen top/bottom positions; selection image-informed.'};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
