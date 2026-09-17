import pathlib,json,time,sys
import numpy as np
from PIL import Image,ImageFilter
from scipy.ndimage import distance_transform_edt
from scipy.spatial.distance import cdist
import R04
P=R04.P;Q=R04.Q;guard=R04.guard;save=R04.save
WEIGHTS=np.arange(-1.5,1.5001,.25);ANGLES=np.arange(-1,1.001,.5);SHIFTS=R04.SHIFTS

def stroke(x,t):
 x=np.clip(np.rint(x),0,255).astype('uint8');ink=x<128;d=distance_transform_edt(~ink)-distance_transform_edt(ink);d=np.sign(d)*(np.abs(d)-.5);near=np.abs(d)<=1;d[near]=x[near]/255-.5;base=np.clip(d+.5,0,1)*255;result=np.clip(np.clip(d-t+.5,0,1)*255+(x.astype(float)-base),0,255)
 return np.rint(result).astype('uint8')
def render(x,t=0,angle=0,dx=0,dy=0):return R04.transform(stroke(x,t),angle,dx,dy)
def nuisance(x,t,blur,gamma,dx,dy):
 im=Image.fromarray(stroke(x,t)).filter(ImageFilter.GaussianBlur(float(blur)));z=np.rint(255*(np.asarray(im,dtype=float)/255)**gamma).astype('uint8');return R04.transform(z,0,dx,dy,jpeg=True)
def prepare():
 guard();D=dict(np.load(Q/'inputs.npz'));templates=np.array([D['pixels'][D['train']&(D['labels']==c)].mean(0) for c in D['shapes']]);bank=[]
 for template in templates:
  z=np.rint(template).astype('uint8');assert np.array_equal(stroke(z,0),z);assert np.all(stroke(z,.75)<=z) and np.all(stroke(z,-.75)>=z)
  for t in WEIGHTS:
   morphed=stroke(template,t)
   for a in ANGLES:
    for dx,dy in SHIFTS:bank.append(R04.feature(R04.transform(morphed,a,dx,dy)))
 np.savez_compressed(P/'R05-bank.npz',features=bank,templates=templates,shapes=D['shapes'],weights=WEIGHTS,angles=ANGLES,shifts=SHIFTS);print('BANK',len(bank))
def fit(images,D,B):
 guard();F=np.array([R04.feature(x) for x in images]);dist=cdist(F,B['features'],'sqeuclidean')/F.shape[1];cost=dist.reshape(len(images),len(B['shapes']),len(WEIGHTS),len(ANGLES)*len(SHIFTS));byweight=cost.min(3);argn=cost.argmin(3).astype('uint8');best=dist.argmin(1);ci=best//(len(WEIGHTS)*len(ANGLES)*len(SHIFTS));wi=(best//(len(ANGLES)*len(SHIFTS)))%len(WEIGHTS);ai=(best//len(SHIFTS))%len(ANGLES);si=best%len(SHIFTS);rmse=np.sqrt(dist[np.arange(len(images)),best]);pred=B['shapes'][ci].copy();pred[rmse>.16]=-1;labels=D['labels'];train=D['train'];scope=np.isin(labels,D['eligible']);active=scope&np.isin(pred,D['eligible']);correct=active&(pred==labels);weight=WEIGHTS[wi];tr=weight[active&train];te=weight[active&~train];choices=[]
 for initial in [np.percentile(tr,[25,75]),np.array([tr.min(),tr.max()])]:
  centers=np.sort(initial)
  for iteration in range(30):
   state=np.argmin((tr[:,None]-centers)**2,axis=1)
   if len(set(state))<2:break
   new=np.sort([tr[state==k].mean() for k in [0,1]])
   if np.array_equal(new,centers):break
   centers=new
  choices.append((float(np.min((tr[:,None]-centers)**2,axis=1).sum()),centers))
 _,centers=min(choices,key=lambda z:z[0]);state=np.full(len(images),-1);state[active]=np.argmin((weight[active,None]-centers)**2,axis=1);held=scope&~train;one=float(np.mean((te-tr.mean())**2));two=float(np.mean(np.min((te[:,None]-centers)**2,axis=1)));minority=min(float(np.mean(state[active&train]==0)),float(np.mean(state[active&train]==1)));both=sum(len(set(state[(pred==c)&active]))==2 for c in D['eligible']);summary=dict(centers=centers.tolist(),separation=float(centers[1]-centers[0]),training_minority=minority,held_mse_gain=1-two/max(one,1e-12),eligible_held=int(held.sum()),active_held=int(np.sum(held&active)),correct_identity_held=int(np.sum(held&correct)),held_predicted_coverage=float(active[held].mean()),held_correct_identity_coverage=float(correct[held].mean()),rejected_held=int(np.sum(pred[held]<0)),misclassified_held=int(np.sum((pred[held]>=0)&(pred[held]!=labels[held]))),both_state_classes=int(both))
 summary['channel_gate']=bool(summary['separation']>=1 and minority>=.2 and summary['held_mse_gain']>=.5 and summary['held_correct_identity_coverage']>=.95 and both>=3)
 arrays=dict(pixels=images,features=F,identity_weight_cost=byweight,identity_weight_nuisance_argmin=argn,predicted_classes=pred,rmse=rmse,weights=weight,angles=ANGLES[ai],shift_index=si,states=state,active=active,scope=scope,correct_identity=correct,best_bank_index=best)
 return summary,arrays
def archive(n,s,a,extra={}):np.savez_compressed(P/(n+'.npz'),**a,**extra);save(n+'.json',s)
def panel(D,B,seed,amplitude=None,actual=False):
 rng=np.random.default_rng(seed);bits=np.zeros(len(D['labels']),int)
 if amplitude is not None:
  for c in D['shapes']:
   for split in [False,True]:
    ids=np.flatnonzero((D['labels']==c)&(D['train']==split));z=np.arange(len(ids))%2;rng.shuffle(z);bits[ids]=z
 blur=rng.uniform(0,.45 if amplitude is not None else .75,len(bits));gamma=rng.uniform(.9 if amplitude is not None else .8,1.1 if amplitude is not None else 1.2,len(bits));off=rng.uniform(-.5,.5,(len(bits),2));base=D['pixels'] if amplitude is not None or actual else np.array([B['templates'][list(B['shapes']).index(c)] for c in D['labels']]);ts=amplitude*(2*bits-1) if amplitude is not None else np.zeros(len(bits));images=np.array([nuisance(x,t,b,g,*xy) for x,t,b,g,xy in zip(base,ts,blur,gamma,off)]);return images,dict(bits=bits,planted_weights=ts,blur=blur,gamma=gamma,offsets=off)
def controls():
 D=dict(np.load(Q/'inputs.npz'));B=dict(np.load(P/'R05-bank.npz'));rows=[]
 for rep,amp in enumerate([.75,1.25]):
  for positive in [True,False]:
   seed=(475600 if positive else 475700)+rep;images,extra=panel(D,B,seed,amp if positive else None);s,a=fit(images,D,B);s.update(positive=positive,seed=seed,amplitude=amp if positive else 0)
   if positive:
    held=a['scope']&~D['train'];s['held_joint_state_accuracy']=float(np.mean((a['states'][held]==extra['bits'][held])&a['correct_identity'][held]));s['control_pass']=bool(s['held_joint_state_accuracy']>=.9 and s['held_correct_identity_coverage']>=.95)
   name=f'R05-{"positive" if positive else "ordinary"}-{rep}';archive(name,s,a,extra);rows.append(s);print(name,s,flush=True)
 viable=all(z['control_pass'] for z in rows if z['positive']) and all(not z['channel_gate'] for z in rows if not z['positive']);save('R05-controls-summary.json',dict(viable=viable,rows=rows));print('VIABLE',viable)
def actual():
 assert json.loads((P/'R05-controls-summary.json').read_text())['viable'];D=dict(np.load(Q/'inputs.npz'));B=dict(np.load(P/'R05-bank.npz'));s,a=fit(D['pixels'],D,B);archive('R05-actual',s,a);rows=[]
 for rep in range(2):
  images,extra=panel(D,B,475800+rep,actual=True);ss,aa=fit(images,D,B);held=a['scope']&~D['train'];ss['held_state_agreement']=float(np.mean(aa['states'][held]==a['states'][held]));archive(f'R05-actual-raster-{rep}',ss,aa,extra);rows.append(ss)
 save('R05-actual-summary.json',dict(actual=s,raster=rows));print(json.dumps(dict(actual=s,raster=rows)))
if __name__=='__main__':
 t=time.monotonic();{'prepare':prepare,'controls':controls,'actual':actual}[sys.argv[1]]();print('SECONDS',time.monotonic()-t)
