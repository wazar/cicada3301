import pathlib,json,hashlib,datetime,io,sys,time
import numpy as np
from PIL import Image
from scipy.spatial.distance import cdist
P=pathlib.Path(__file__).resolve().parent;ROOT=P.parents[2];Q=P.parent/'worker-q/Q06';W=128;H=160
ANGLES=np.arange(-3,3.01,.5);SHIFTS=[(x,y) for x in [-.5,0,.5] for y in [-.5,0,.5]]
def guard():
 assert not (P.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(n,x):(P/n).write_text(json.dumps(x,indent=2)+'\n')
def transform(x,angle=0,dx=0,dy=0,jpeg=False):
 im=Image.fromarray(np.clip(np.rint(x),0,255).astype('uint8'))
 if angle:im=im.rotate(float(angle),Image.Resampling.BICUBIC,expand=False,fillcolor=255)
 if dx or dy:im=im.transform((W,H),Image.Transform.AFFINE,(1,0,-float(dx),0,1,-float(dy)),Image.Resampling.BICUBIC,fillcolor=255)
 if jpeg:
  b=io.BytesIO();im.save(b,format='JPEG',quality=92);b.seek(0);im=Image.open(b).convert('L')
 return np.asarray(im,dtype=np.uint8)
def feature(x):
 yy,xx=np.where(x<128)
 if not len(xx):return None
 box=(int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1));im=Image.fromarray(x.astype('uint8')).crop(box).resize((32,64),Image.Resampling.BILINEAR)
 return np.asarray(im,dtype=np.float64).ravel()/255

def prepare():
 guard();D=dict(np.load(Q/'inputs.npz'));shapes=D['shapes'];labels=D['labels'];train=D['train'];scope=np.isin(labels,D['eligible']);assert int(scope.sum())==393 and int((scope&~train).sum())==196
 templates=np.array([D['pixels'][train&(labels==c)].mean(0) for c in shapes]);bank=[]
 for template in templates:
  for a in ANGLES:
   for dx,dy in SHIFTS:bank.append(feature(transform(template,a,dx,dy)))
 np.savez_compressed(P/'R04-bank.npz',features=np.array(bank),templates=templates,shapes=shapes,angles=ANGLES,shifts=SHIFTS)
 save('R04-inputs.json',dict(n=len(labels),eligible_instances=int(scope.sum()),eligible_held=int((scope&~train).sum()),shape_classes=shapes.tolist(),eligible=D['eligible'].tolist(),bank_candidates=len(bank),files=[dict(path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [Q/'inputs.npz',Q/'maps.json',P.parent/'worker-i/route-mapping.json',ROOT/'liber-primus/data/relikd/p0.jpg',ROOT/'liber-primus/data/relikd/p1.jpg']]))
 print('BANK',len(bank),len(bank[0]))
def fit(images,D,B):
 guard();features=np.array([feature(x) for x in images]);dist=cdist(features,B['features'],'sqeuclidean')/features.shape[1];cost=dist.reshape(len(images),len(B['shapes']),len(ANGLES),len(SHIFTS));by_angle=cost.min(3);argshift=cost.argmin(3).astype('uint8');best=dist.argmin(1);ci=best//(len(ANGLES)*len(SHIFTS));ai=(best//len(SHIFTS))%len(ANGLES);si=best%len(SHIFTS);rmse=np.sqrt(dist[np.arange(len(images)),best]);pred=B['shapes'][ci].copy();pred[rmse>.16]=-1
 train=D['train'];labels=D['labels'];scope=np.isin(labels,D['eligible']);active=scope&np.isin(pred,D['eligible']);angle=ANGLES[ai].copy();tr=angle[active&train];te=angle[active&~train];assert len(tr)>1 and len(te)>1
 choices=[]
 for initial in [np.percentile(tr,[25,75]),np.array([tr.min(),tr.max()])]:
  centers=np.sort(initial)
  for iteration in range(30):
   state=np.argmin((tr[:,None]-centers)**2,axis=1)
   if len(set(state))<2:break
   new=np.sort([tr[state==k].mean() for k in [0,1]])
   if np.array_equal(new,centers):break
   centers=new
  choices.append((float(np.min((tr[:,None]-centers)**2,axis=1).sum()),centers))
 _,centers=min(choices,key=lambda z:z[0]);state=np.full(len(images),-1);state[active]=np.argmin((angle[active,None]-centers)**2,axis=1);held=scope&~train;correct=active&(pred==labels);one=float(np.mean((te-tr.mean())**2));two=float(np.mean(np.min((te[:,None]-centers)**2,axis=1)));minority=min(float(np.mean(state[active&train]==0)),float(np.mean(state[active&train]==1)));both=sum(len(set(state[(pred==c)&active]))==2 for c in D['eligible'])
 summary=dict(centers=centers.tolist(),separation=float(centers[1]-centers[0]),training_minority=minority,held_mse_gain=1-two/max(one,1e-12),eligible_held=int(held.sum()),active_held=int((active&held).sum()),correct_identity_held=int((correct&held).sum()),held_predicted_coverage=float(active[held].mean()),held_correct_identity_coverage=float(correct[held].mean()),held_identity_accuracy=float(np.mean(pred[held]==labels[held])),rejected_held=int(np.sum((pred[held]<0))),misclassified_held=int(np.sum((pred[held]>=0)&(pred[held]!=labels[held]))),both_state_classes=int(both),per_class=[dict(shape=int(c),held=int(np.sum(held&(labels==c))),correct=int(np.sum(held&correct&(labels==c))),predicted_state0=int(np.sum(active&(pred==c)&(state==0))),predicted_state1=int(np.sum(active&(pred==c)&(state==1)))) for c in D['shapes']])
 summary['channel_gate']=bool(summary['separation']>=1.5 and minority>=.2 and summary['held_mse_gain']>=.5 and summary['held_correct_identity_coverage']>=.95 and both>=3)
 arrays=dict(pixels=images,features=features,identity_angle_cost=by_angle,identity_angle_translation_argmin=argshift,predicted_classes=pred,rmse=rmse,angles=angle,shift_index=si,states=state,active=active,scope=scope,correct_identity=correct,best_bank_index=best)
 return summary,arrays
def archive(name,s,a,extra={}):
 np.savez_compressed(P/(name+'.npz'),**a,**extra);save(name+'.json',s)
def controls():
 guard();D=dict(np.load(Q/'inputs.npz'));B=dict(np.load(P/'R04-bank.npz'));rows=[]
 for rep in range(2):
  for typ in ['positive','raster-null']:
   old=dict(np.load(Q/f'{typ}-{rep}.npz'));s,a=fit(old['pixels'],D,B);extra={k:old[k] for k in ['bits','offsets'] if k in old};s.update(kind=typ,origin='legacy',rep=rep)
   if typ=='positive':evaluate(s,a,old['bits'],D)
   archive(f'R04-legacy-{typ}-{rep}',s,a,extra);rows.append(s);print('LEGACY',typ,rep,s.get('held_joint_state_accuracy'),s['held_correct_identity_coverage'],flush=True)
 for rep,amplitude in enumerate([1.5,2.0]):
  rng=np.random.default_rng(474600+rep);bits=np.zeros(len(D['labels']),int)
  for c in D['shapes']:
   for split in [False,True]:
    ids=np.flatnonzero((D['labels']==c)&(D['train']==split));z=np.arange(len(ids))%2;rng.shuffle(z);bits[ids]=z
  offsets=rng.uniform(-.5,.5,(len(bits),2));images=np.array([transform(x,amplitude*(2*bit-1),*shift,jpeg=True) for x,bit,shift in zip(D['pixels'],bits,offsets)]);s,a=fit(images,D,B);s.update(kind='positive',origin='fresh',rep=rep,amplitude=amplitude,seed=474600+rep);evaluate(s,a,bits,D);archive(f'R04-fresh-positive-{rep}',s,a,dict(bits=bits,offsets=offsets));rows.append(s);print('FRESH',rep,s.get('held_joint_state_accuracy'),s['held_correct_identity_coverage'],flush=True)
  rng=np.random.default_rng(474700+rep);off=rng.uniform(-.5,.5,(len(bits),2));images=np.array([transform(B['templates'][list(B['shapes']).index(c)],0,*shift,jpeg=True) for c,shift in zip(D['labels'],off)]);s,a=fit(images,D,B);s.update(kind='raster-null',origin='fresh',rep=rep,seed=474700+rep);archive(f'R04-fresh-raster-null-{rep}',s,a,dict(offsets=off));rows.append(s)
 viable=all(x['control_pass'] for x in rows if x['kind']=='positive') and all(not x['channel_gate'] for x in rows if x['kind']=='raster-null');save('R04-controls-summary.json',dict(viable=viable,rows=rows));print('VIABLE',viable)
def evaluate(s,a,bits,D):
 held=a['scope']&~D['train'];s['held_joint_state_accuracy']=float(np.mean((a['states'][held]==bits[held])&a['correct_identity'][held]));s['held_state_accuracy_unconditional_identity']=float(np.mean(a['states'][held]==bits[held]));s['control_pass']=bool(s['held_joint_state_accuracy']>=.9 and s['held_correct_identity_coverage']>=.95)
def actual():
 guard();assert json.loads((P/'R04-controls-summary.json').read_text())['viable'];D=dict(np.load(Q/'inputs.npz'));B=dict(np.load(P/'R04-bank.npz'));s,a=fit(D['pixels'],D,B);archive('R04-actual',s,a);rows=[]
 for rep in range(2):
  rng=np.random.default_rng(474800+rep);offsets=rng.uniform(-.5,.5,(len(D['labels']),2));images=np.array([transform(x,0,*shift,jpeg=True) for x,shift in zip(D['pixels'],offsets)]);ss,aa=fit(images,D,B);held=a['scope']&~D['train'];ss['held_state_agreement']=float(np.mean(aa['states'][held]==a['states'][held]));archive(f'R04-actual-raster-{rep}',ss,aa,dict(offsets=offsets));rows.append(ss)
 save('R04-actual-summary.json',dict(actual=s,raster=rows));print(json.dumps(dict(actual=s,raster=rows)))
if __name__=='__main__':
 t=time.monotonic();{'prepare':prepare,'controls':controls,'actual':actual}[sys.argv[1]]();print('SECONDS',time.monotonic()-t)
