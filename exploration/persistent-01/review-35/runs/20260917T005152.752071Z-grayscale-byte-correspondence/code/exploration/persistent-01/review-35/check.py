from pathlib import Path
import json,hashlib,io
import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation
R=Path(__file__).parent;B=R.parent;ROOT=B.parent.parent;S=B/'worker-s';old=json.loads((S/'S07-result.json').read_text());new=json.loads((S/'S07b-result.json').read_text());sources=[ROOT/f'liber-primus/data/relikd/p{i}.jpg' for i in [0,1]];images=[np.array(Image.open(p).convert('L')) for p in sources];(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in sources+list(S.glob('S07*.json'))+list(S.glob('S07*.npz'))+[S/'S07-CARD.md',S/'S07b-CARD.md',S/'s07.py',S/'s07b.py']:
 raw=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
 if p.suffix in ['.json','.md','.py']:(R/'snapshots'/p.name).write_bytes(raw)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2));oldcoords=np.load(S/'S07-residual-coordinates.npz');newcoords=np.load(S/'S07b-residual-coordinates.npz');crops={};corrected={}
for page,img in enumerate(images):
 assert img.shape==(3600,2400)
 for key,roi in old['rois'].items():
  x0,y0,x1,y1=roi;a=img[y0:y1,x0:x1];assert np.array_equal(a,np.array(Image.open(S/'S07-pixels'/f'p{page}-{key}.png')));crops[page,key]=a
 for key,roi in new['corrected_rois'].items():
  x0,y0,x1,y1=roi;a=np.pad(img[y0:y1,x0:x1],32,constant_values=255);assert np.array_equal(a,np.array(Image.open(S/'S07b-pixels'/f'p{page}-{key}.png')));corrected[page,key]=a
strips=json.loads((S/'S07b-removed-source-strips.json').read_text());striparrays=np.load(S/'S07b-removed-source-strips.npz');print('stripkeys',striparrays.files,flush=True)
for row in strips:
 x0,y0,x1,y1=row['roi'];a=images[row['page']][y0:y1,x0:x1];assert a.size==row['pixels'] and int((a<128).sum())==row['dark128'];assert any(np.array_equal(a,striparrays[k]) for k in striparrays.files)
def shiftstats(a,b):
 h,w=a.shape;aa=[int.from_bytes(v.tobytes(),'little') for v in np.packbits(a<128,axis=1,bitorder='little')];bb=[int.from_bytes(v.tobytes(),'little') for v in np.packbits(b<128,axis=1,bitorder='little')];mask=(1<<w)-1;scores={}
 for dx in range(-16,17):
  k=dx%w;bs=[((v<<k)|(v>>(w-k)))&mask for v in bb]
  for dy in range(-16,17):scores[dy,dx]=sum((v&bs[(i-dy)%h]).bit_count() for i,v in enumerate(aa))
 return [[scores[dy,dx],dy*dy+dx*dx,dy,dx] for dy in range(-16,17) for dx in range(-16,17)]
def verify(a,b,name,result,fresh=False):
 shifts=shiftstats(a,b);assert shifts==result['all_shifts' if fresh else 'all_shift_intersections'];best=min(shifts,key=lambda x:(-x[0],x[1],x[2],x[3]));dy,dx=best[2:];assert [dy,dx]==result['shift_dy_dx'];bs=np.roll(b,(dy,dx),(0,1));margins=[]
 for arr in [a,b]:
  y,x=np.where(arr<128);margins.append(int(min(x.min(),arr.shape[1]-1-x.max(),y.min(),arr.shape[0]-1-y.max())))
 assert margins==(result['margins'] if fresh else [result['margins']['a'],result['margins']['b']])
 for threshold in ([128] if fresh else [64,128,192]):
  ma=a<threshold;mb=bs<threshold;coord=np.argwhere(ma!=mb);assert np.array_equal(coord,(newcoords[name] if fresh else oldcoords[name+f'_diff{threshold}']));iou=float((ma&mb).sum()/max(1,(ma|mb).sum()));stat=result if fresh else result['thresholds'][str(threshold)];assert abs(iou-stat['iou128' if fresh else 'iou'])<1e-14;assert len(coord)==stat['different128' if fresh else 'difference_pixels']
 if min(margins)>=16:
  # Independent white-fill shift must agree with circular ink, proving no wraparound at tested displacements.
  pad=np.pad(b,16,constant_values=255);linear=pad[16-dy:16-dy+b.shape[0],16-dx:16-dx+b.shape[1]];assert np.array_equal(linear<128,bs<128)
 return dy,dx

def jpeg(a):
 f=io.BytesIO();Image.fromarray(a).save(f,format='JPEG',quality=92);return np.array(Image.open(io.BytesIO(f.getvalue())).convert('L'))
a=crops[0,'rightcross'];controls={'control-shift':np.roll(a,(7,-5),(0,1)),'control-jpeg92':jpeg(a)};erase=a.copy();y,x=old['control_erase_yx'];erase[y:y+12,x:x+12]=255;add=a.copy();y,x=old['control_add_yx'];assert np.all(a[y:y+12,x:x+12]>192);add[y:y+12,x:x+12]=0
# Independent direct sliding-window sum checks darkest patch choice.
from numpy.lib.stride_tricks import sliding_window_view
sums=sliding_window_view(a<128,(12,12)).sum(axis=(-1,-2));assert list(np.unravel_index(np.argmax(sums),sums.shape))==old['control_erase_yx']
controls['control-erased']=jpeg(erase);controls['control-added']=jpeg(add)
for key,b in controls.items():
 verify(a,b,key,old['results'][key])
 if key in ['control-erased','control-added']:assert np.array_equal(b,np.array(Image.open(S/'S07-pixels'/(key+'.png'))))
for key in old['rois']:verify(crops[0,key],crops[1,key],'crosspage-'+key,old['results']['crosspage-'+key])
for page in [0,1]:
 for family,left,right in [('cross','leftcross','rightcross'),('loop','toploop','bottomloop')]:
  for rotation in [0,180]:
   name=f'p{page}-{family}-rotation{rotation}';b=crops[page,right];verify(crops[page,left],b if rotation==0 else np.flip(b),name,old['results'][name])
for key in new['corrected_rois']:verify(corrected[0,key],corrected[1,key],'crosspage-'+key,new['loop_results']['crosspage-'+key],True)
for page in [0,1]:
 for rotation in [0,180]:
  name=f'p{page}-loop-rotation{rotation}';b=corrected[page,'bottomloop'];verify(corrected[page,'toploop'],b if rotation==0 else np.flip(b),name,new['loop_results'][name],True)
refs={'crosspage-rightcross':crops[0,'rightcross'],'crosspage-leftcross':crops[0,'leftcross'],'p0-cross-rotation180':crops[0,'leftcross'],'p1-cross-rotation180':crops[1,'leftcross']}
refs.update({k:crops[0,'rightcross'] for k in controls})
for key,arr in refs.items():
 mask=arr<128;pad=np.pad(mask,1);boundary=np.zeros_like(mask)
 for dy,dx in [(0,1),(0,-1),(1,0),(-1,0)]:boundary|=mask!=pad[1+dy:1+dy+mask.shape[0],1+dx:1+dx+mask.shape[1]]
 near=binary_dilation(boundary,structure=np.ones((5,5),bool));coords=oldcoords[key+'_diff128'];far=coords[~near[coords[:,0],coords[:,1]]];assert np.array_equal(far,newcoords[key+'_far_from_outline']);assert len(far)==new['cross_outline_results'][key]['farther_than2_from_reference_boundary']
result={'status':'PASS','registrations':len(old['results'])+len(new['loop_results']),'shift_scores':1089*(len(old['results'])+len(new['loop_results'])),'removed_strips':strips,'corrected_loop_results':{k:{a:b for a,b in v.items() if a!='all_shifts'} for k,v in new['loop_results'].items()},'cross_outline_results':new['cross_outline_results']};(R/'result.json').write_text(json.dumps(result,indent=2));print('ALL PIXEL/REGISTRATION CHECKS PASS')
