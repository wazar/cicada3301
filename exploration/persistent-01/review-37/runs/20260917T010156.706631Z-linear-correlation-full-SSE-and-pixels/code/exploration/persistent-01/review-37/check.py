from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
from scipy.signal import fftconvolve
R=Path(__file__).parent;B=R.parent;ROOT=B.parent.parent;S=B/'worker-s';z=json.loads((S/'S08-result.json').read_text());raw=[np.array(Image.open(ROOT/f'liber-primus/data/relikd/p{i}.jpg').convert('L')) for i in [0,1]];ref=np.pad(raw[0][2930:2995,1110:1270],64,constant_values=255);assert np.array_equal(raw[0][2930:2995,1110:1270],raw[1][2930:2995,1110:1270]);(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in list(S.glob('S08-*.npz'))+[S/'S08-result.json',S/'S08-CARD.md',S/'s08.py']+[ROOT/f'liber-primus/data/relikd/p{i}.jpg' for i in [0,1]]:
 b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 if p.suffix in ['.json','.md','.py']:(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2));angles=[i*.25 for i in range(-32,33)];phases=[(0,0),(0,.5),(.5,0),(.5,.5)];assert z['angles']==angles and z['phases_dx_dy']==[list(p) for p in phases] and z['integer_shifts']==list(range(-16,17));h,w=ref.shape

def render(source,angle,phase):
 im=Image.fromarray(source).rotate(angle,Image.Resampling.BICUBIC,expand=False,fillcolor=255)
 if phase!=(0,0):im=im.transform((w,h),Image.Transform.AFFINE,(1,0,-phase[0],0,1,-phase[1]),Image.Resampling.BICUBIC,fillcolor=255)
 return np.array(im)
def jpeg(source):
 buffer=io.BytesIO();Image.fromarray(source).save(buffer,format='JPEG',quality=92);return np.array(Image.open(io.BytesIO(buffer.getvalue())).convert('L'))
variants=[render(ref,a,p) for a in angles for p in phases];margins=[]
for v in variants:
 y,x=np.where(v<192);margins.append(int(min(x.min(),w-1-x.max(),y.min(),h-1-y.max())))
assert min(margins)>16
settings=[(-5.5,(0,.5),(7,-5)),(-2.25,(.5,0),(-6,4)),(2.75,(.5,.5),(3,-4)),(5.25,(0,0),(-2,6))];targets={'control-exact':ref}
for i,(angle,phase,shift) in enumerate(settings):targets[f'control-copy{i}']=jpeg(np.roll(render(ref,angle,phase),shift,(0,1)))
from numpy.lib.stride_tricks import sliding_window_view
sums=sliding_window_view(ref<128,(12,12)).sum(axis=(-1,-2));y,x=np.unravel_index(np.argmax(sums),sums.shape);erase=ref.copy();erase[y:y+12,x:x+12]=255;add=ref.copy();add[22:34,22:34]=0;assert np.all(ref[22:34,22:34]==255)
for name,edit in [('erase',erase),('add',add)]:
 assert np.array_equal(edit,np.array(Image.open(S/'S08-pixels'/f'control-{name}-source-edit.png')));targets[f'control-{name}']=jpeg(np.roll(render(edit,2.75,(.5,.5)),(3,-4),(0,1)))
for page in [1,0]:targets[f'p{page}-top']=np.pad(raw[page][600:665,1110:1270],64,constant_values=255)
allgrids=0;allres=0;results=[]
for name,target in targets.items():
 saved=np.load(S/f'S08-{name}-all-residuals.npz');grids=saved['scores'];residuals=saved['signed_residuals'];assert np.array_equal(saved['target'],target) and np.array_equal(saved['reference'],ref);record=z['results'][name];best=[];ti=255-target.astype(np.int64);energy=int((ti*ti).sum())
 for i,v in enumerate(variants):
  vi=255-v.astype(np.int64)
  # Full zero-padded linear convolution, independent of circular FFT implementation.
  conv=np.rint(fftconvolve(ti.astype(float),vi[::-1,::-1].astype(float),mode='full')).astype(np.int64);grid=energy+int((vi*vi).sum())-2*conv[h-17:h+16,w-17:w+16];assert np.array_equal(grid,grids[i]);flat=int(grid.argmin());dy,dx=flat//33-16,flat%33-16;pred=np.roll(v,(dy,dx),(0,1));res=target.astype(np.int16)-pred.astype(np.int16);assert np.array_equal(res,residuals[i]);assert int(np.square(res.astype(np.int64)).sum())==int(grid.min());row=dict(angle=angles[i//4],phase_dx_dy=list(phases[i%4]),shift_dy_dx=[dy,dx],sse=int(grid.min()));assert row==record['all_variant_best'][i];best.append(row);allgrids+=grid.size;allres+=1
 winner=min(range(260),key=lambda i:best[i]['sse']);assert best[winner]==record['best'];pred=target.astype(np.int16)-residuals[winner];assert np.array_equal(pred,np.array(Image.open(S/'S08-pixels'/f'{name}-predicted.png')));assert np.array_equal(target,np.array(Image.open(S/'S08-pixels'/f'{name}-target.png')));ma=target<128;mb=pred<128;diff=ma!=mb;union=(target<192)|(pred<192);assert np.array_equal(np.where(diff,0,255),np.array(Image.open(S/'S08-pixels'/f'{name}-residual128.png')));assert int(diff.sum())==record['different128'];assert abs(float((ma&mb).sum()/(ma|mb).sum())-record['iou128'])<1e-14;assert abs(float(np.abs(residuals[winner])[union].mean())-record['foreground_MAE'])<1e-12;assert abs(float(np.sqrt(best[winner]['sse']/target.size))-record['RMSE_full'])<1e-12;results.append({'name':name,**{k:v for k,v in record.items() if k!='all_variant_best'}})
assert allgrids==9*283140 and allres==9*260
out={'status':'PASS','targets':len(targets),'complete_linear_convolution_SSE_cells':allgrids,'full_signed_residual_images':allres,'variant_min_margin_192':min(margins),'results':results};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
