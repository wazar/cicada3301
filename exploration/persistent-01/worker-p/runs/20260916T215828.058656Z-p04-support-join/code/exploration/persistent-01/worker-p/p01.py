import pathlib,json,hashlib,datetime
import numpy as np
from PIL import Image
from scipy import ndimage,signal
D=pathlib.Path('exploration/persistent-01/worker-p');P=pathlib.Path('liber-primus/data/relikd/p13.jpg')
assert not pathlib.Path('exploration/persistent-01/STOP').exists()
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
assert hashlib.sha256(P.read_bytes()).hexdigest()=='3481daeed3ab2bea6effbe36eec22f74955bce87ca4b4ae8674be1d3f84ea08d'
im=Image.open(P).convert('L');box=(1820,650,2330,2900);crop=im.crop(box).resize((255,1125),Image.Resampling.BOX);crop.save(D/'ornament-roi.png');a=np.array(crop);mask=np.abs((np.arange(255)*2+1820)-2075)>=35
# Dice with tolerance, fixed off-stem mask; all raw scores and displacement map retained.
def score(x,y,name):
 x=x&mask[None,:];y=y&mask[None,:]
 xd=ndimage.binary_dilation(x,iterations=2);yd=ndimage.binary_dilation(y,iterations=2)
 cor=signal.fftconvolve(x.astype(float),yd[::-1,::-1].astype(float),mode='full')+signal.fftconvolve(xd.astype(float),y[::-1,::-1].astype(float),mode='full')
 # sums of matched foreground in both directions / total foreground
 cy,cx=np.array(x.shape)-1;s=cor[cy-60:cy+61,cx-20:cx+21]/max(1,x.sum()+y.sum());j,i=np.unravel_index(s.argmax(),s.shape)
 np.save(D/(name+'-scores.npy'),s)
 return dict(score=float(s[j,i]),translation_original_pixels=[int((i-20)*2),int((j-60)*2)],foreground=[int(x.sum()),int(y.sum())])
results={};arrays={}
for t in [128,96,160]:
 x=a<t;arrays['binary'+str(t)]=x
 results[str(t)]={k:score(x,y,f'{t}-{k}') for k,y in [('rotate180',x[::-1,::-1]),('vertical_reflect',x[::-1]),('horizontal_reflect',x[:,::-1])]}
x=a<128
# control has even height to avoid arbitrary middle-row mismatch
h=x.shape[0]//2;top=x[:h];plant=np.concatenate([top,top[::-1,::-1]],axis=0)
results['plant']=score(plant,plant[::-1,::-1],'plant');arrays['plant']=plant
rng=np.random.default_rng(130013);null=[];orders=[]
# 15 equal-height bands preserves all pixels, randomly permutes vertical placement
for i in range(100):
 order=rng.permutation(15);z=x.reshape(15,75,255)[order].reshape(x.shape);orders.append(order);null.append(score(x,z[::-1,::-1],f'null-{i:03}'))
arrays['null_band_orders']=np.array(orders);np.savez_compressed(D/'raw-arrays.npz',**arrays)
results['null']=null;results['null_scope']='exploratory band-order comparison, not independent drawing model or formal p value';results['image']=dict(path=str(P),sha256=hashlib.sha256(P.read_bytes()).hexdigest(),size=im.size,roi=box)
results['mapping']=dict(original_page=13,segment_id=13,source_region_id=13,stream_start=3194,stream_end=3466,runes=272)
(D/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps({k:v for k,v in results.items() if k!='null'},indent=2));print('null percentiles',np.percentile([r['score'] for r in null],[0,50,95,100]).tolist())
