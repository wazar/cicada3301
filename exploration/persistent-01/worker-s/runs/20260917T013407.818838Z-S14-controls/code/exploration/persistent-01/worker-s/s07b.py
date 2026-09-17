import json,pathlib,numpy as np
from PIL import Image
BASE=pathlib.Path('exploration/persistent-01/worker-s');OUT=BASE/'S07b-pixels';OUT.mkdir(exist_ok=True);old=json.loads((BASE/'S07-result.json').read_text());raw=[np.asarray(Image.open(f'liber-primus/data/relikd/p{p}.jpg').convert('L')) for p in [0,1]]
rois={'toploop':(1110,600,1270,665),'bottomloop':(1110,2930,1270,2995)};new={};results={};arrays={}
for p in [0,1]:
 for name,(x0,y0,x1,y1) in rois.items():
  a=np.pad(raw[p][y0:y1,x0:x1],32,constant_values=255);new[p,name]=a;Image.fromarray(a).save(OUT/f'p{p}-{name}.png')
def compare(a,b,key):
 ma=a<128;mb=b<128;h,w=a.shape;cor=np.rint(np.fft.irfft2(np.fft.rfft2(ma)*np.conj(np.fft.rfft2(mb)),s=a.shape)).astype(int)
 scores=[(int(cor[dy%h,dx%w]),dy*dy+dx*dx,dy,dx) for dy in range(-16,17) for dx in range(-16,17)];best=min(scores,key=lambda v:(-v[0],v[1],v[2],v[3]));_,_,dy,dx=best;bs=np.roll(b,(dy,dx),(0,1));mb=bs<128;assert int((ma&mb).sum())==best[0]
 margins=[]
 for m in [ma,b<128]:
  yy,xx=np.where(m);margins.append(int(min(xx.min(),w-1-xx.max(),yy.min(),h-1-yy.max())))
 assert min(margins)>=16
 diff=ma^mb;arrays[key]=np.argwhere(diff);r={'shift_dy_dx':[dy,dx],'margins':margins,'different128':int(diff.sum()),'iou128':float((ma&mb).sum()/(ma|mb).sum()),'foreground_grayscale_MAE':float(np.abs(a.astype(int)-bs.astype(int))[(a<192)|(bs<192)].mean()),'full_ROI_equal_fraction':float((a==bs).mean()),'all_shifts':scores};results[key]=r
for name in rois:compare(new[0,name],new[1,name],f'crosspage-{name}')
for p in [0,1]:
 for rot in [0,180]:
  b=new[p,'bottomloop'];compare(new[p,'toploop'],b if rot==0 else b[::-1,::-1],f'p{p}-loop-rotation{rot}')
residuals=np.load(BASE/'S07-residual-coordinates.npz');edges={}
for name,reference in [('crosspage-rightcross','p0-rightcross'),('crosspage-leftcross','p0-leftcross'),('p0-cross-rotation180','p0-leftcross'),('p1-cross-rotation180','p1-leftcross'),('control-shift','p0-rightcross'),('control-jpeg92','p0-rightcross'),('control-erased','p0-rightcross'),('control-added','p0-rightcross')]:
 a=np.asarray(Image.open(BASE/'S07-pixels'/f'{reference}.png'))<128;boundary=np.zeros_like(a)
 for dy,dx in [(1,0),(-1,0),(0,1),(0,-1)]:boundary|=a^np.roll(a,(dy,dx),(0,1))
 near=np.zeros_like(a)
 for dy in range(-2,3):
  for dx in range(-2,3):near|=np.roll(boundary,(dy,dx),(0,1))
 coords=residuals[f'{name}_diff128'];far=coords[~near[coords[:,0],coords[:,1]]] if len(coords) else coords;arrays[f'{name}_far_from_outline']=far
 edges[name]={'residual_pixels':len(coords),'farther_than2_from_reference_boundary':len(far)}
np.savez_compressed(BASE/'S07b-residual-coordinates.npz',**arrays);(BASE/'S07b-result.json').write_text(json.dumps({'corrected_rois':rois,'padding':32,'loop_results':results,'cross_outline_results':edges},indent=2)+'\n');print(json.dumps({'loops':{k:{a:b for a,b in r.items() if a!='all_shifts'} for k,r in results.items()},'cross_outline_results':edges},indent=2))
