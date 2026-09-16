import json,pathlib
import numpy as np
from PIL import Image,ImageDraw
from scipy.cluster.hierarchy import linkage,fcluster
from scipy.spatial.distance import pdist,cdist
D=pathlib.Path('exploration/persistent-01/worker-i');assert not pathlib.Path('exploration/persistent-01/STOP').exists()
r=json.loads((D/'coordinates.json').read_text());ims={p:Image.open(f'liber-primus/data/relikd/p{p}.jpg').convert('L') for p in [0,1]};crops=[ims[x['page']].crop((x['x'],x['y'],x['right'],x['bottom'])) for x in r];X=np.array([np.array(x.resize((24,48),Image.Resampling.BILINEAR)).reshape(-1)/255 for x in crops]);train=np.array([x['train'] for x in r]);ti=np.where(train)[0];vi=np.where(~train)[0]
c=fcluster(linkage(pdist(X[train])/np.sqrt(X.shape[1]),method='complete'),.16,criterion='distance');uc=np.unique(c);templates=np.array([X[ti[c==k]].mean(axis=0) for k in uc]);ds=cdist(X,templates)/np.sqrt(X.shape[1]);lab=uc[ds.argmin(axis=1)];lab[ds.min(axis=1)>.16]=-1;lab[ti]=c
eligible=[k for k in uc if sum(lab[ti]==k)>=4 and sum(lab[vi]==k)>=4];valid=np.isin(lab,eligible);width=np.array([x['width'] for x in r],float);res=width.copy()
for k in uc:res[lab==k]-=np.median(width[train&(lab==k)])
# Full vectors and cluster montage allow independent check, no transcription inferred.
canvas=Image.new('RGB',(720,((len(uc)+9)//10)*130),'white');draw=ImageDraw.Draw(canvas)
for j,k in enumerate(uc):
 z=ti[c==k][0];im=crops[z].resize((48,96));px=(j%10)*72;py=(j//10)*130;canvas.paste(im,(px,py));draw.text((px,py+98),f'{k}: {sum(lab==k)}',fill='black')
canvas.save(D/'shape-classes.png')
def twostate(v):
 a,b=np.percentile(v[train&valid],[25,75]);a,b=(min(v[train&valid]),max(v[train&valid])) if a==b else (a,b)
 for _ in range(30):
  cl=abs(v-b)<abs(v-a)
  if not any(cl&train&valid) or not any((~cl)&train&valid):break
  a=np.mean(v[(~cl)&train&valid]);b=np.mean(v[cl&train&valid])
 cl=abs(v-b)<abs(v-a);te=v[(~train)&valid];m1=np.mean((te-np.mean(v[train&valid]))**2);m2=np.mean(np.minimum((te-a)**2,(te-b)**2));frac=min(np.mean(cl[train&valid]),1-np.mean(cl[train&valid]));return dict(centers=[a,b],separation=abs(b-a),minority=frac,improvement=1-m2/max(m1,1e-12),gate=bool(abs(b-a)>=4 and frac>=.2 and m2<=.5*m1)),cl
real,cl=twostate(res);rng=np.random.default_rng(190018);bits=rng.integers(0,2,len(r));pl=[]
for im,bit in zip(crops,bits):
 pp=im.resize((im.width+8*int(bit),im.height),Image.Resampling.BICUBIC);yy,xx=np.where(np.array(pp)<128);pl.append(xx.max()-xx.min()+1)
pl=np.array(pl)-width+res;control,pc=twostate(pl);control['bit_accuracy']=float(max(np.mean(pc[valid]==bits[valid]),np.mean(pc[valid]!=bits[valid])))
per=[]
for k in eligible:
 sel=lab==k;per.append(dict(shape_class=int(k),n=int(sum(sel)),width_min=float(min(width[sel])),width_max=float(max(width[sel])),heldout_n=int(sum(sel&~train)),heldout_residual_min=float(min(res[sel&~train])),heldout_residual_max=float(max(res[sel&~train]))))
pert=[]
for t in [96,160]:
 widths=[]
 for im in crops:
  yy,xx=np.where(np.array(im)<t);widths.append(xx.max()-xx.min()+1)
 pert.append(widths)
np.savez(D/'width-arrays.npz',X=X,classes=lab,template_classes=uc,templates=templates,eligible=eligible,valid=valid,width=width,residual=res,train=train,bits=bits,plant=pl,perturbed_width=pert)
out=dict(n=len(r),shape_classes=len(uc),eligible_classes=len(eligible),eligible_instances=int(sum(valid)),real=real,control=control,per_class=per,maximum_threshold_width_change=float(np.max(np.abs(np.array(pert)-width))))
(D/'width-results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
