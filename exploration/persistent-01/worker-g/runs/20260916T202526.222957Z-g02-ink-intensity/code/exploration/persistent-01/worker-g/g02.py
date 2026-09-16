from PIL import Image
import numpy as np,json,pathlib,hashlib
O=pathlib.Path(__file__).parent;ROOT=O.parents[2]
def rows(a,mask):
 out=[]
 for y in range(0,a.shape[0],32):
  for x in range(0,a.shape[1],32):
   m=mask[y:y+32,x:x+32]
   if m.sum()>=40:out.append({'xywh':[x,y,32,32],'pixels':int(m.sum()),'rgb_median':np.median(a[y:y+32,x:x+32][m],axis=0).tolist()})
 return out
def score(r):return float(np.percentile([v['rgb_median'][0]for v in r],90)-np.percentile([v['rgb_median'][0]for v in r],10)) if r else None
out={}
for p in [3,7,17]:
 f=ROOT/f'liber-primus/data/relikd/p{p}.jpg';a=np.asarray(Image.open(f)).astype('int16');r,g,b=a.transpose(2,0,1)
 m=(r>100)&(r>g+80)&(r>b+80)&(g<90)&(b<90);inner=m.copy()
 for dy in range(-2,3):
  for dx in range(-2,3):inner &= np.roll(np.roll(m,dy,0),dx,1)
 tile=rows(a,inner);control=a.copy();yy,xx=np.indices(m.shape);control[inner,0]=np.where(((xx//32)%2)[inner],160,220);control[inner,1:]=0
 neg=a.copy();neg[inner]=[190,0,0]
 out[p]={'input_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'saturated_pixels':int(m.sum()),'interior_pixels':int(inner.sum()),'tiles':tile,'spread_90_10':score(tile),'positive_spread':score(rows(control,inner)),'negative_spread':score(rows(neg,inner))}
 if tile:assert out[p]['positive_spread']>20 and out[p]['negative_spread']==0
(O/'g02-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({p:{k:v for k,v in d.items()if k!='tiles'}for p,d in out.items()},indent=2))
