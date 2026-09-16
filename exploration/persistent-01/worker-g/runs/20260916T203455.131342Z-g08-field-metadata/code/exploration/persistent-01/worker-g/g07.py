import pathlib,json,io
import numpy as np
from PIL import Image
O=pathlib.Path(__file__).parent;ROOT=O.parents[2];boxes=[(150,650,580,1550),(150,1550,580,2960),(1820,650,2250,1550),(1820,1550,2250,2960)]
def mask(im):return np.min(np.array(im.convert('RGB')),axis=2)<130
def iou(a,b,box,dx,dy):
 x0,y0,x1,y1=box;u=a[y0:y1,x0:x1];v=b[y0+dy:y1+dy,x0+dx:x1+dx];return float(np.count_nonzero(u&v)/np.count_nonzero(u|v))
aimage=Image.open(ROOT/'liber-primus/data/relikd/p3.jpg');bimage=Image.open(ROOT/'liber-primus/data/relikd/p7.jpg');a=mask(aimage);b=mask(bimage)
def run(b):
 fits=[{'dx':dx,'dy':dy,'iou':iou(a,b,boxes[0],dx,dy)}for dx in range(-8,9)for dy in range(-8,9)];best=max(fits,key=lambda f:f['iou']);return {'fits':fits,'best':best,'predictions':[{'box':box,'iou':iou(a,b,box,best['dx'],best['dy'])}for box in boxes[1:]]}
buf=io.BytesIO();aimage.save(buf,format='JPEG',quality=90);buf.seek(0);control=run(mask(Image.open(buf)));result={'real':run(b),'recompression_control':control,'fitted_choices':289}
assert control['best']['iou']>.95 and min(v['iou']for v in control['predictions'])>.95
(O/'g07-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:{kk:vv for kk,vv in v.items()if kk!='fits'}if isinstance(v,dict)else v for k,v in result.items()},indent=2))
