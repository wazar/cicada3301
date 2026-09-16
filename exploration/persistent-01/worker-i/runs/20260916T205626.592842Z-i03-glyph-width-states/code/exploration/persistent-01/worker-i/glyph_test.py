import os,json,hashlib,pathlib,io
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
from scipy import ndimage
D=pathlib.Path('exploration/persistent-01/worker-i'); rng=np.random.default_rng(190017)
assert not pathlib.Path('exploration/persistent-01/STOP').exists()

def boxes(a,threshold=128):
 lab,n=ndimage.label(a<threshold); out=[]
 for sl in ndimage.find_objects(lab):
  if sl is None:continue
  ys,xs=sl; h=ys.stop-ys.start;w=xs.stop-xs.start
  if h>=5 and w>=3:out.append([xs.start,ys.start,xs.stop,ys.stop,w,h])
 return out

def model(v):
 v=np.asarray(v,float); a,b=np.percentile(v,[25,75])
 if a==b:a,b=min(v),max(v)
 for _ in range(20):
  cl=abs(v-b)<abs(v-a)
  if cl.all() or not cl.any(): break
  a,b=np.mean(v[~cl]),np.mean(v[cl])
 return sorted([float(a),float(b)])
def test(v,train):
 v=np.asarray(v,float); centers=model(v[train]); base=np.mean(v[train]);te=v[~train]
 mse1=np.mean((te-base)**2);mse2=np.mean(np.min((te[:,None]-centers)**2,axis=1));cl=np.argmin(abs(v[:,None]-centers),axis=1)
 frac=float(min(np.mean(cl[train]),1-np.mean(cl[train])))
 return dict(centers=centers,separation=centers[1]-centers[0],minority_fraction=frac,heldout_mse_single=float(mse1),heldout_mse_binary=float(mse2),improvement=float(1-mse2/max(mse1,1e-12)),geometric_gate=bool(centers[1]-centers[0]>=4 and frac>=.2 and mse2<=.5*mse1)),cl
allrows=[]; crops=[];rejected=[]; manifests=[]
for p in [0,1]:
 path=pathlib.Path(f'liber-primus/data/relikd/p{p}.jpg');raw=path.read_bytes(); manifests.append(dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest()))
 im=Image.open(path).convert('RGB');a=np.asarray(im);gray=a.min(axis=2);x0=600;y0=850 if p==0 else 650; roi=gray[y0:2880,x0:1800];bxs=boxes(roi)
 good=[b for b in bxs if 80<=b[5]<=140 and 5<=b[4]<=90];rejected.extend([dict(page=p,box=b) for b in bxs if b not in good])
 # cluster row top by rounded pitch, no identities consulted
 good.sort(key=lambda b:(round((b[1]+y0-673)/188),b[0]))
 rowids={}
 overlay=im.copy();draw=ImageDraw.Draw(overlay)
 for b in good:
  x,y,xx,yy,w,h=b;x+=x0;xx+=x0;y+=y0;yy+=y0; row=round((y-673)/188); j=rowids.get(row,0);rowids[row]=j+1
  allrows.append(dict(page=p,row=row,index=j,x=x,y=y,right=xx,bottom=yy,width=w,height=h,train=j%2==0))
  crop=Image.new('L',(w+16,h+30),255);crop.paste(Image.fromarray(gray[y:yy,x:xx]),(8,15));crops.append(crop)
  draw.rectangle((x,y,xx,yy),outline='blue',width=2)
 overlay.save(D/f'p{p}-segmentation.png')
(D/'inputs.json').write_text(json.dumps(manifests,indent=2));(D/'coordinates.json').write_text(json.dumps(allrows,indent=2));(D/'rejected-components.json').write_text(json.dumps(rejected,indent=2))
train=np.array([r['train'] for r in allrows]);height=np.array([r['height'] for r in allrows],float); bottom=np.array([r['bottom'] for r in allrows],float)
for p in [0,1]:
 for row in range(12):
  ix=np.array([r['page']==p and r['row']==row for r in allrows]); bottom[ix]-=np.median(bottom[ix])
summary={'n':len(allrows),'page_counts':{p:sum(r['page']==p for r in allrows) for p in [0,1]},'models':{}}
basecls={}
for name,v in [('height',height),('baseline',bottom)]:summary['models'][name],basecls[name]=test(v,train)
# Determine extent per crop, preserving pixel positions within the padded crop.
def extent(im,t=128):
 a=np.asarray(im);ys,xs=np.where(a<t)
 return (ys.max()-ys.min()+1,ys.max())
pert=[]
for t,blur in [(96,0),(160,0),(128,.35)]:
 vals=np.array([extent(im.filter(ImageFilter.GaussianBlur(blur)) if blur else im,t) for im in crops],float);dh=vals[:,0]-height
 # crop initial bottom is height+14; relative change remains source baseline change
 db=vals[:,1]-(height+14); entry={'threshold':t,'blur':blur,'height_delta_max':float(abs(dh).max()),'baseline_delta_max':float(abs(db).max())}
 for name,v,delta in [('height',height,dh),('baseline',bottom,db)]:
  cl=np.argmin(abs((v+delta)[:,None]-summary['models'][name]['centers']),axis=1);entry[name+'_agreement']=float(np.mean(cl==basecls[name]))
 pert.append(entry)
summary['perturbations']=pert
# Plant on actual crops by pixel resizing or padded placement; raw labels retained.
bits=rng.integers(0,2,len(crops));controls={}
for name in ['height','baseline']:
 v=[]
 for bit,im in zip(bits,crops):
  a=np.asarray(im);ys,xs=np.where(a<128); glyph=im.crop((0,int(ys.min()),im.width,int(ys.max()+1)))
  if name=='height':glyph=glyph.resize((glyph.width,glyph.height+8*int(bit)),Image.Resampling.BICUBIC);pos=15
  else:pos=15+8*int(bit)
  canvas=Image.new('L',(im.width,im.height+20),255);canvas.paste(glyph,(0,pos));h,b=extent(canvas);v.append(h if name=='height' else b-glyph.height)
 stats,cl=test(v,train);stats['bit_accuracy']=float(max(np.mean(cl==bits),np.mean(cl!=bits)));controls[name]=stats
summary['controls']=controls
# Matched subpixel + JPEG controls on original glyph patches. Each draw measures max departures and binary separation.
nulls=[]
for k in range(100):
 hh=[];bb=[]
 for im in crops:
  a=np.asarray(im);dx,dy=rng.uniform(-.5,.5,2);arr=ndimage.shift(a.astype(float),(dy,dx),order=1,mode='constant',cval=255);bio=io.BytesIO();Image.fromarray(arr.clip(0,255).astype('uint8')).save(bio,format='JPEG',quality=92);bio.seek(0);h,b=extent(Image.open(bio));hh.append(h);bb.append(b)
 hn=np.array(hh);bn=bottom+np.array(bb)-(height+14); hs,_=test(hn,train);bs,_=test(bn,train);nulls.append([hs['separation'],hs['improvement'],bs['separation'],bs['improvement']])
np.savez(D/'arrays.npz',height=height,baseline=bottom,train=train,bits=bits,nulls=nulls)
summary['null_max_separations']=np.max(np.array(nulls)[:,[0,2]],axis=0).tolist()
(D/'results.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
