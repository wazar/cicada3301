import pathlib,json,hashlib,io
import numpy as np
from PIL import Image
BASE=pathlib.Path('exploration/persistent-01/worker-s'); OUT=BASE/'S07-pixels';OUT.mkdir(exist_ok=True)
ROIS={'rightcross':(1800,600,2390,1950),'leftcross':(10,1650,600,3000),'toploop':(1110,600,1270,675),'bottomloop':(1110,2930,1270,3005)}
paths=[pathlib.Path(f'liber-primus/data/relikd/p{p}.jpg') for p in [0,1]];ims=[Image.open(p).convert('L') for p in paths];assert all(im.size==(2400,3600) for im in ims)
crops={(p,name):np.asarray(im.crop(roi)) for p,im in enumerate(ims) for name,roi in ROIS.items()}
for (p,name),a in crops.items():Image.fromarray(a).save(OUT/f'p{p}-{name}.png')
results={};arrays={}
def compare(a,b,name):
 assert a.shape==b.shape
 aa=a<128;bb=b<128;h,w=a.shape
 # rfft crosscorrelation returns dot(a,roll(b,offset)).
 corr=np.rint(np.fft.irfft2(np.fft.rfft2(aa)*np.conj(np.fft.rfft2(bb)),s=aa.shape)).astype(int)
 shifts=[(int(corr[dy%h,dx%w]),dx*dx+dy*dy,dy,dx) for dy in range(-16,17) for dx in range(-16,17)];best=sorted(shifts,key=lambda v:(-v[0],v[1],v[2],v[3]))[0];overlap,_,dy,dx=best;bshift=np.roll(b,(dy,dx),(0,1))
 assert int((aa&(bshift<128)).sum())==overlap
 margins={}
 for label,m in [('a',aa),('b',bb)]:
  yy,xx=np.where(m);margins[label]=int(min(xx.min(),w-1-xx.max(),yy.min(),h-1-yy.max())) if len(xx) else None
 stats={}
 for threshold in [64,128,192]:
  ma=a<threshold;mb=bshift<threshold;diff=ma^mb;union=ma|mb;yy,xx=np.where(diff)
  stats[str(threshold)]={'a_ink':int(ma.sum()),'b_ink':int(mb.sum()),'difference_pixels':int(diff.sum()),'union_pixels':int(union.sum()),'iou':float((ma&mb).sum()/max(1,union.sum()))}
  arrays[f'{name}_diff{threshold}']=np.column_stack([yy,xx]).astype(np.int16)
 diff=np.abs(a.astype(int)-bshift.astype(int));union=(a<192)|(bshift<192)
 r={'shift_dy_dx':[dy,dx],'margins':margins,'circular_safe':all(v is not None and v>=16 for v in margins.values()),'thresholds':stats,'foreground_grayscale_MAE':float(diff[union].mean()),'full_ROI_equal_fraction':float((a==bshift).mean()),'all_shift_intersections':shifts}
 results[name]=r;Image.fromarray(np.where((a<128)^(bshift<128),0,255).astype(np.uint8)).save(OUT/f'{name}-residual128.png');return r

def jpeg(a):
 buff=io.BytesIO();Image.fromarray(a).save(buff,format='JPEG',quality=92);return np.asarray(Image.open(io.BytesIO(buff.getvalue())).convert('L'))
template=crops[(0,'rightcross')];control=np.roll(template,(7,-5),(0,1));r=compare(template,control,'control-shift');assert r['shift_dy_dx']==[-7,5] and r['thresholds']['128']['difference_pixels']==0
compare(template,jpeg(template),'control-jpeg92')
# Integral-image darkest12x12 window, deterministic tie ordering.
a=(template<128).astype(int);integral=np.pad(a,((1,0),(1,0))).cumsum(0).cumsum(1);sums=integral[12:,12:]-integral[:-12,12:]-integral[12:,:-12]+integral[:-12,:-12];yy,xx=np.unravel_index(np.argmax(sums),sums.shape)
erased=template.copy();erased[yy:yy+12,xx:xx+12]=255;added=template.copy();added[22:34,22:34]=0
assert np.all(template[22:34,22:34]>192)
for label,a in [('erased',erased),('added',added)]:
 a=jpeg(a);Image.fromarray(a).save(OUT/f'control-{label}.png');r=compare(template,a,f'control-{label}');assert r['thresholds']['128']['difference_pixels']>=100
for name in ROIS:compare(crops[(0,name)],crops[(1,name)],f'crosspage-{name}')
for p in [0,1]:
 for family,left,right in [('cross','leftcross','rightcross'),('loop','toploop','bottomloop')]:
  for rotation in [0,180]:
   b=crops[(p,right)];b=b if rotation==0 else b[::-1,::-1];compare(crops[(p,left)],b,f'p{p}-{family}-rotation{rotation}')
np.savez_compressed(BASE/'S07-residual-coordinates.npz',**arrays)
record={'inputs':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],'rois':ROIS,'control_erase_yx':[int(yy),int(xx)],'control_add_yx':[22,22],'results':results};(BASE/'S07-result.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({name:{k:v for k,v in r.items() if k not in ['all_shift_intersections','thresholds']}|{'iou128':r['thresholds']['128']['iou'],'different128':r['thresholds']['128']['difference_pixels']} for name,r in results.items()},indent=2))
