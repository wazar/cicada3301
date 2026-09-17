import json,pathlib
import numpy as np
from PIL import Image
from scipy import ndimage
D=pathlib.Path('exploration/persistent-01/worker-p');assert not pathlib.Path('exploration/persistent-01/STOP').exists();r=json.loads((D/'results.json').read_text());z=np.load(D/'raw-arrays.npz');x=z['binary128'];m=np.abs(np.arange(255)*2+1820-2075)>=35
out=[]
for name,y in [('rotate180',x[::-1,::-1]),('vertical_reflect',x[::-1]),('horizontal_reflect',x[:,::-1])]:
 xx=x&m[None,:]; yy=y&m[None,:];dx,dy=r['128'][name]['translation_original_pixels'];sy,sx=dy//2,dx//2
 def move(v):
  a=np.zeros_like(v);h,w=v.shape
  a[max(sy,0):min(h,h+sy),max(sx,0):min(w,w+sx)]=v[max(-sy,0):min(h,h-sy),max(-sx,0):min(w,w-sx)];return a
 xd=ndimage.binary_dilation(xx,iterations=2);yd=ndimage.binary_dilation(yy,iterations=2)
 n=int(np.sum(xx&move(yd))+np.sum(xd&move(yy)));s=n/(xx.sum()+yy.sum());assert abs(s-r['128'][name]['score'])<1e-12
 out.append(dict(transform=name,numerator=n,denominator=int(xx.sum()+yy.sum()),score=s))
 if name=='rotate180':
  a=np.full((*xx.shape,3),255,dtype=np.uint8);target=move(yy);a[xx]=[220,30,30];a[target]=[30,50,220];a[xx&target]=[30,10,30];Image.fromarray(a).save(D/'rotation-overlay.png')
(D/'replay-results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
