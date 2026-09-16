import pathlib,json,hashlib,datetime,io,sys
import numpy as np
from PIL import Image
from scipy.spatial.distance import cdist
R=pathlib.Path(__file__).parent;I=R.parents[1]/'worker-i';W=128;H=160

def gate():
 assert not (R.parents[1]/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(n,x):(R/n).write_text(json.dumps(x,indent=2))
def imarray(x):return Image.fromarray(np.clip(np.rint(x),0,255).astype('uint8'))
def transform(x,angle=0,dx=0,dy=0,jpeg=False):
 im=imarray(x)
 if angle:im=im.rotate(float(angle),Image.Resampling.BICUBIC,expand=False,fillcolor=255)
 if dx or dy:im=im.transform((W,H),Image.Transform.AFFINE,(1,0,-float(dx),0,1,-float(dy)),Image.Resampling.BICUBIC,fillcolor=255)
 if jpeg:
  stream=io.BytesIO();im.save(stream,format='JPEG',quality=92);stream.seek(0);im=Image.open(stream).convert('L')
 return np.array(im,dtype=np.uint8)
def features(images):
 out=[]
 for x in images:
  yy,xx=np.where(x<128);assert len(xx);box=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1));out.append(np.asarray(imarray(x).crop(box).resize((24,48),Image.Resampling.BILINEAR),dtype=float).ravel()/255)
 return np.array(out)
def prepare():
 gate();records=json.loads((I/'route-mapping.json').read_text())['records'];assert len(records)==418;shapes=sorted({r['shape_class'] for r in records});train=np.array([r['train'] for r in records]);labels=np.array([r['shape_class'] for r in records]);eligible=[c for c in shapes if sum((labels==c)&train)>=4 and sum((labels==c)&~train)>=4]
 images={p:Image.open(f'liber-primus/data/relikd/p{p}.jpg').convert('L') for p in [0,1]};canvases=[];cropmaps=[]
 for r in records:
  im=images[r['page']].crop((r['x'],r['y'],r['right'],r['bottom']));out=Image.new('L',(W,H),255);left=(W-im.width)//2;top=(H-im.height)//2;out.paste(im,(left,top));canvases.append(np.array(out));cropmaps.append({'source':r,'canvas_box':[left,top,left+im.width,top+im.height],'crop_sha256':hashlib.sha256(im.tobytes()).hexdigest()})
 canvases=np.array(canvases);F=features(canvases);identity=np.array([F[train&(labels==c)].mean(axis=0) for c in shapes]);templates=np.array([canvases[train&(labels==c)].mean(axis=0) for c in shapes]);masks=[]
 for c in shapes:
  widths=[r['width'] for r in records if r['shape_class']==c and r['train']];heights=[r['height'] for r in records if r['shape_class']==c and r['train']];cw=int(np.median(widths));ch=int(np.median(heights));left=(W-cw)//2+4;right=(W+cw)//2-4;top=(H-ch)//2+8;bottom=(H+ch)//2-8;mask=np.zeros((H,W),bool);mask[top:bottom,left:right]=True;assert mask.sum()>0;masks.append(mask)
 np.savez_compressed(R/'inputs.npz',pixels=canvases,train=train,labels=labels,shapes=shapes,eligible=eligible,identity=identity,templates=templates,masks=masks);save('maps.json',cropmaps);save('inputs.json',{'n':len(records),'shapes':shapes,'eligible':eligible,'eligible_instances':int(np.isin(labels,eligible).sum()),'files':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [I/'route-mapping.json',I/'width-arrays.npz']]+[{'path':f'liber-primus/data/relikd/p{p}.jpg','sha256':hashlib.sha256(pathlib.Path(f'liber-primus/data/relikd/p{p}.jpg').read_bytes()).hexdigest()} for p in [0,1]]});print('prepared mapped pixels',len(records),'eligible',len(eligible))
def fit(images,D):
 train=D['train'];labels=D['labels'];shapes=D['shapes'];eligible=D['eligible'];F=features(images);dist=cdist(F,D['identity'],'sqeuclidean')/F.shape[1];pred=shapes[dist.argmin(axis=1)].copy();pred[np.sqrt(dist.min(axis=1))>.16]=-1;scope=np.isin(labels,eligible);active=scope&np.isin(pred,eligible);angles=np.full(len(images),np.nan);shifts=np.full((len(images),2),np.nan);mse=np.full(len(images),np.nan);allerrors=[]
 for ci,c in enumerate(shapes):
  if c not in eligible:continue
  training=(pred==c)&train
  if not training.any():continue
  template=images[training].mean(axis=0);mask=D['masks'][ci];bank=[];params=[]
  for angle in np.arange(-3,3.01,.5):
   rotated=transform(template,angle)
   for dx in [-.5,0,.5]:
    for dy in [-.5,0,.5]:bank.append(transform(rotated,0,dx,dy)[mask]/255);params.append((float(angle),dx,dy))
  bank=np.array(bank);ids=np.flatnonzero(active&(pred==c));targets=images[ids][:,mask]/255;err=cdist(targets,bank,'sqeuclidean')/bank.shape[1];best=err.argmin(axis=1)
  for j,k in enumerate(ids):angles[k]=params[best[j]][0];shifts[k]=params[best[j]][1:];mse[k]=err[j,best[j]]
  allerrors.append({'class':int(c),'ids':ids,'errors':err})
 active&=np.isfinite(angles);tr=angles[active&train];te=angles[active&~train];assert len(tr)>1 and len(te)>1;choices=[]
 for centers in [np.percentile(tr,[25,75]),np.array([tr.min(),tr.max()])]:
  centers=np.sort(centers)
  for iteration in range(30):
   states=np.argmin((tr[:,None]-centers)**2,axis=1)
   if len(set(states))<2:break
   nxt=np.array([tr[states==k].mean() for k in [0,1]])
   if np.array_equal(nxt,centers):break
   centers=np.sort(nxt)
  choices.append((float(np.min((tr[:,None]-centers)**2,axis=1).sum()),centers))
 _,centers=min(choices,key=lambda z:z[0]);state=np.full(len(images),-1);state[active]=np.argmin((angles[active,None]-centers)**2,axis=1);one=float(np.mean((te-tr.mean())**2));two=float(np.mean(np.min((te[:,None]-centers)**2,axis=1)));minority=min(float(np.mean(state[active&train]==0)),float(np.mean(state[active&train]==1)));bothclasses=sum(len(set(state[(pred==c)&active]))==2 for c in eligible);coverage=float(np.mean(active[scope&~train]));summary={'centers':centers.tolist(),'separation':float(centers[1]-centers[0]),'training_minority':minority,'held_mse_gain':1-two/max(one,1e-12),'held_coverage':coverage,'identity_accuracy':float(np.mean(pred[scope]==labels[scope])),'held_identity_accuracy':float(np.mean(pred[scope&~train]==labels[scope&~train])),'both_state_classes':bothclasses,'eligible_held':int(sum(scope&~train)),'active_held':int(sum(active&~train))};summary['actual_gate']=bool(summary['separation']>=1.5 and minority>=.2 and summary['held_mse_gain']>=.5 and coverage>=.95 and bothclasses>=3)
 return summary,{'angles':angles,'shifts':shifts,'mse':mse,'states':state,'predicted_classes':pred,'identity_distances':dist,'active':active,'scope':scope,'errors':allerrors}
def archive(name,summary,arrays,images,extra):
 dense={k:v for k,v in arrays.items() if k!='errors'};dense['pixels']=images
 for x in arrays['errors']:dense[f"class_{x['class']}_ids"]=x['ids'];dense[f"class_{x['class']}_errors"]=x['errors']
 dense.update(extra);np.savez_compressed(R/(name+'.npz'),**dense);save(name+'.json',summary)
def controls():
 gate();D=dict(np.load(R/'inputs.npz'));rows=[]
 for rep in range(2):
  rng=np.random.default_rng(470600+rep);bits=np.zeros(len(D['labels']),int)
  for c in D['shapes']:
   for split in [False,True]:
    ids=np.flatnonzero((D['labels']==c)&(D['train']==split));z=np.arange(len(ids))%2;rng.shuffle(z);bits[ids]=z
  offsets=rng.uniform(-.5,.5,(len(bits),2));images=np.array([transform(x,2*bit,*shift,jpeg=True) for x,bit,shift in zip(D['pixels'],bits,offsets)]);s,a=fit(images,D);held=a['scope']&~D['train'];s['held_state_accuracy']=float(np.mean(a['states'][held]==bits[held]));s['control_pass']=bool(s['held_state_accuracy']>=.9 and s['held_identity_accuracy']>=.95 and s['held_coverage']>=.95);archive(f'positive-{rep}',s,a,images,{'bits':bits,'offsets':offsets});rows.append({'type':'positive','rep':rep,**s})
  rng=np.random.default_rng(470700+rep);off=rng.uniform(-.5,.5,(len(bits),2));nullimages=np.array([transform(D['templates'][list(D['shapes']).index(c)],0,*shift,jpeg=True) for c,shift in zip(D['labels'],off)]);s,a=fit(nullimages,D);archive(f'raster-null-{rep}',s,a,nullimages,{'offsets':off});rows.append({'type':'raster_null','rep':rep,**s});gate()
 viable=all(x['control_pass'] for x in rows if x['type']=='positive');save('controls-summary.json',{'viable':viable,'rows':rows});print(json.dumps({'viable':viable,'rows':rows}))
def actual():
 gate();assert json.loads((R/'controls-summary.json').read_text())['viable'],'controls do not authorize actual stats';D=dict(np.load(R/'inputs.npz'));s,a=fit(D['pixels'],D);archive('actual',s,a,D['pixels'],{});rows=[]
 for rep in range(2):
  rng=np.random.default_rng(470800+rep);off=rng.uniform(-.5,.5,(len(D['labels']),2));images=np.array([transform(x,0,*shift,jpeg=True) for x,shift in zip(D['pixels'],off)]);ss,aa=fit(images,D);held=a['scope']&~D['train'];ss['held_state_agreement']=float(np.mean(aa['states'][held]==a['states'][held]));archive(f'actual-raster-{rep}',ss,aa,images,{'offsets':off});rows.append(ss)
 save('actual-summary.json',{'actual':s,'raster_sensitivity':rows});print(json.dumps({'actual':s,'raster_sensitivity':rows}))
if __name__=='__main__':{'prepare':prepare,'controls':controls,'actual':actual}[sys.argv[1]]()
