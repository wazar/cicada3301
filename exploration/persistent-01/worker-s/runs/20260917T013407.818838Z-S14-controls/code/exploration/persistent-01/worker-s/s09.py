import json,pathlib,io,hashlib,numpy as np
from PIL import Image
BASE=pathlib.Path('exploration/persistent-01/worker-s');OUT=BASE/'S09-pixels';OUT.mkdir(exist_ok=True)
ROIS={'top':(1110,600,1270,665),'bottom':(1110,2930,1270,2995)};im0=Image.open('liber-primus/data/relikd/p0.jpg').convert('L');templates={'A_p0top':np.pad(np.asarray(im0.crop(ROIS['top'])),64,constant_values=255),'B_commonbottom':np.pad(np.asarray(im0.crop(ROIS['bottom'])),64,constant_values=255)}
ANGLES=[i/4 for i in range(-32,33)];PHASES=[(0.,0.),(0.,.5),(.5,0.),(.5,.5)];SHIFTS=list(range(-16,17));h,w=next(iter(templates.values())).shape

def render(a,angle,phase):
 im=Image.fromarray(a).rotate(angle,resample=Image.Resampling.BICUBIC,expand=False,fillcolor=255);dx,dy=phase
 if dx or dy:im=im.transform(im.size,Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),resample=Image.Resampling.BICUBIC,fillcolor=255)
 return np.asarray(im)
def jpeg(a):
 b=io.BytesIO();Image.fromarray(a).save(b,format='JPEG',quality=92);return np.asarray(Image.open(io.BytesIO(b.getvalue())).convert('L'))
models={}
for name,template in templates.items():
 variants=[render(template,a,p) for a in ANGLES for p in PHASES];models[name]=(variants,[np.fft.rfft2(255-v.astype(float)) for v in variants],[int(np.square(255-v.astype(np.int64)).sum()) for v in variants])
 for v in variants:
  yy,xx=np.where(v<192);assert min(xx.min(),w-1-xx.max(),yy.min(),h-1-yy.max())>16

def fit(target,name,template_name,save_all_residuals=False):
 variants,spectra,energies=models[template_name];tf=np.fft.rfft2(255-target.astype(float));energy=int(np.square(255-target.astype(np.int64)).sum());grids=[];rows=[];residuals=[];best_sse=None;best_res=None;best_row=None
 for i,v in enumerate(variants):
  cor=np.rint(np.fft.irfft2(tf*np.conj(spectra[i]),s=target.shape)).astype(np.int64);grid=energy+energies[i]-2*cor[np.ix_([d%h for d in SHIFTS],[d%w for d in SHIFTS])];iy,ix=np.unravel_index(np.argmin(grid),grid.shape);dy,dx=SHIFTS[iy],SHIFTS[ix];pred=np.roll(v,(dy,dx),(0,1));res=target.astype(np.int16)-pred.astype(np.int16);sse=int(np.square(res.astype(np.int64)).sum());assert sse==int(grid[iy,ix]);row={'angle':ANGLES[i//4],'phase_dx_dy':PHASES[i%4],'shift_dy_dx':[dy,dx],'sse':sse};rows.append(row);grids.append(grid)
  if save_all_residuals:residuals.append(res)
  if best_sse is None or sse<best_sse:best_sse=sse;best_res=res;best_row=row
 archive={'scores':np.stack(grids),'target':target,'reference':templates[template_name],'best_signed_residual':best_res}
 if save_all_residuals:archive['all_variant_best_signed_residuals']=np.stack(residuals)
 np.savez_compressed(BASE/f'S09-{name}-{template_name}-fits.npz',**archive)
 predicted=(target.astype(np.int16)-best_res).astype(np.uint8);ma=target<128;mb=predicted<128
 for suffix,a in [('target',target),('predicted',predicted),('residual128',np.where(ma^mb,0,255).astype(np.uint8))]:Image.fromarray(a).save(OUT/f'{name}-{template_name}-{suffix}.png')
 return {'best':best_row,'iou128':float((ma&mb).sum()/(ma|mb).sum()),'different128':int((ma^mb).sum()),'all_variant_best':rows}
settings=[(-5.5,(0.,.5),(7,-5)),(-2.25,(.5,0.),(-6,4)),(2.75,(.5,.5),(3,-4)),(5.25,(0.,0.),(-2,6))];controls=[]
for truth,template in templates.items():
 for i,setting in enumerate([None]+settings):
  target=template if setting is None else jpeg(np.roll(render(template,setting[0],setting[1]),setting[2],(0,1)));name=f'control-{truth}-{i}';fits={key:fit(target,name,key) for key in templates};controls.append({'name':name,'truth_template':truth,'truth_pose':setting,'fits':fits})
  if setting is None:assert fits[truth]['best']['sse']==0
threshold=4*max(c['fits'][c['truth_template']]['best']['sse'] for c in controls if c['truth_pose'] is not None)
def classify(fits):
 ordered=sorted(fits,key=lambda k:fits[k]['best']['sse']);winner,loser=ordered;win=fits[winner]['best']['sse'];lose=fits[loser]['best']['sse'];accepted=win<=threshold and lose>=4*win and lose>win
 return {'label':winner if accepted else 'AMBIGUOUS','winner':winner,'winner_sse':win,'loser_sse':lose,'loser_winner_ratio':float(lose/win) if win else None,'accepted':accepted}
for c in controls:c['classification']=classify(c['fits'])
gate=all(c['classification']['label']==c['truth_template'] for c in controls)
real=[];im2=Image.open('liber-primus/data/relikd/p2.jpg').convert('L')
for region,roi in ROIS.items():
 target=np.pad(np.asarray(im2.crop(roi)),64,constant_values=255);fits={key:fit(target,f'p2-{region}',key,True) for key in templates};real.append({'page':2,'region':region,'roi':roi,'fits':fits,'classification':classify(fits)})
inventory=[{'page':2,'status':'two comparable small loops','rois':ROIS}]+[{'page':p,'status':'no comparable small loop at top/bottom page positions; large side-scroll spirals are a different motif'} for p in [3,5,6]]
r={'inputs':[{'path':f'liber-primus/data/relikd/p{p}.jpg','sha256':hashlib.sha256(pathlib.Path(f'liber-primus/data/relikd/p{p}.jpg').read_bytes()).hexdigest()} for p in [0,2,3,5,6]],'inventory':inventory,'threshold_SSE':threshold,'control_gate':gate,'controls':controls,'real':real,'template_fit_calls':24,'evaluated_fits':24*283140}
(BASE/'S09-result.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'threshold':threshold,'gate':gate,'control_classifications':[c['classification'] for c in controls],'real':[{'region':v['region'],'classification':v['classification'],'best_fits':{k:v2['best'] for k,v2 in v['fits'].items()}} for v in real]},indent=2))
