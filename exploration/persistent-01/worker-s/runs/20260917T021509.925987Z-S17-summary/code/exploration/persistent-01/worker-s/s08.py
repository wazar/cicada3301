import pathlib,json,io,hashlib
import numpy as np
from PIL import Image
BASE=pathlib.Path('exploration/persistent-01/worker-s');OUT=BASE/'S08-pixels';OUT.mkdir(exist_ok=True)
raw=[Image.open(f'liber-primus/data/relikd/p{p}.jpg').convert('L') for p in [0,1]]
reference=np.pad(np.asarray(raw[0].crop((1110,2930,1270,2995))),64,constant_values=255)
assert np.array_equal(np.asarray(raw[0].crop((1110,2930,1270,2995))),np.asarray(raw[1].crop((1110,2930,1270,2995))))
ANGLES=[i/4 for i in range(-32,33)];PHASES=[(0.,0.),(0.,.5),(.5,0.),(.5,.5)];SHIFTS=list(range(-16,17));h,w=reference.shape

def render(a,angle,phase):
 im=Image.fromarray(a).rotate(angle,resample=Image.Resampling.BICUBIC,expand=False,fillcolor=255)
 dx,dy=phase
 if dx or dy:im=im.transform(im.size,Image.Transform.AFFINE,(1,0,-dx,0,1,-dy),resample=Image.Resampling.BICUBIC,fillcolor=255)
 return np.asarray(im)
variants=[render(reference,a,p) for a in ANGLES for p in PHASES];spectra=[np.fft.rfft2(255-v.astype(float)) for v in variants];energies=[int(np.square(255-v.astype(np.int64)).sum()) for v in variants]
for v in variants:
 yy,xx=np.where(v<192);assert min(xx.min(),w-1-xx.max(),yy.min(),h-1-yy.max())>16

def jpeg(a):
 b=io.BytesIO();Image.fromarray(a).save(b,format='JPEG',quality=92);return np.asarray(Image.open(io.BytesIO(b.getvalue())).convert('L'))
results={}
def fit(target,name,truth=None):
 tf=np.fft.rfft2(255-target.astype(float));energy=int(np.square(255-target.astype(np.int64)).sum());grids=[];residuals=[];candidatebest=[]
 for i,v in enumerate(variants):
  corr=np.rint(np.fft.irfft2(tf*np.conj(spectra[i]),s=target.shape)).astype(np.int64);grid=energy+energies[i]-2*corr[np.ix_([d%h for d in SHIFTS],[d%w for d in SHIFTS])];iy,ix=np.unravel_index(np.argmin(grid),grid.shape);dy,dx=SHIFTS[iy],SHIFTS[ix];pred=np.roll(v,(dy,dx),(0,1));res=target.astype(np.int16)-pred.astype(np.int16);sse=int(np.square(res.astype(np.int64)).sum());assert sse==int(grid[iy,ix]);grids.append(grid);residuals.append(res);candidatebest.append({'angle':ANGLES[i//4],'phase_dx_dy':PHASES[i%4],'shift_dy_dx':[dy,dx],'sse':sse})
 best=min(range(len(candidatebest)),key=lambda i:candidatebest[i]['sse']);b=candidatebest[best];res=residuals[best];prediction=target.astype(np.int16)-res;ma=target<128;mb=prediction<128;union=(target<192)|(prediction<192)
 r={'truth':truth,'best':b,'candidate_count':len(variants)*1089,'RMSE_full':float(np.sqrt(b['sse']/target.size)),'foreground_MAE':float(np.abs(res)[union].mean()),'iou128':float((ma&mb).sum()/(ma|mb).sum()),'different128':int((ma^mb).sum()),'all_variant_best':candidatebest}
 np.savez_compressed(BASE/f'S08-{name}-all-residuals.npz',scores=np.stack(grids),signed_residuals=np.stack(residuals),target=target,reference=reference)
 for suffix,a in [('target',target),('predicted',prediction.astype(np.uint8)),('residual128',np.where(ma^mb,0,255).astype(np.uint8))]:Image.fromarray(a).save(OUT/f'{name}-{suffix}.png')
 results[name]=r;return r
assert fit(reference,'control-exact')['best']['sse']==0
settings=[(-5.5,(0.,.5),(7,-5)),(-2.25,(.5,0.),(-6,4)),(2.75,(.5,.5),(3,-4)),(5.25,(0.,0.),(-2,6))]
for i,(angle,phase,shift) in enumerate(settings):
 target=jpeg(np.roll(render(reference,angle,phase),shift,(0,1)));fit(target,f'control-copy{i}',{'angle':angle,'phase_dx_dy':phase,'shift_dy_dx':shift})
black=(reference<128).astype(int);integ=np.pad(black,((1,0),(1,0))).cumsum(0).cumsum(1);sums=integ[12:,12:]-integ[:-12,12:]-integ[12:,:-12]+integ[:-12,:-12];y,x=np.unravel_index(np.argmax(sums),sums.shape)
erase=reference.copy();erase[y:y+12,x:x+12]=255;add=reference.copy();add[22:34,22:34]=0;assert np.all(reference[22:34,22:34]==255)
for name,a,patch in [('erase',erase,(int(y),int(x))),('add',add,(22,22))]:
 Image.fromarray(a).save(OUT/f'control-{name}-source-edit.png');target=jpeg(np.roll(render(a,2.75,(.5,.5)),(3,-4),(0,1)));fit(target,f'control-{name}',{'angle':2.75,'phase_dx_dy':(.5,.5),'shift_dy_dx':(3,-4),'edit_top_left_yx':patch,'edit_size':12})
for p in [1,0]:fit(np.pad(np.asarray(raw[p].crop((1110,600,1270,665))),64,constant_values=255),f'p{p}-top')
record={'angles':ANGLES,'phases_dx_dy':PHASES,'integer_shifts':SHIFTS,'source_roi':(1110,2930,1270,2995),'target_roi':(1110,600,1270,665),'padding':64,'interpolation':'PIL BICUBIC','results':results};(BASE/'S08-result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:{x:y for x,y in v.items() if x!='all_variant_best'} for k,v in results.items()},indent=2))
