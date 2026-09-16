from pathlib import Path
import sys,json,gzip,hashlib,time,datetime
import numpy as np
from scipy.special import logsumexp,softmax
from scipy.optimize import minimize
O=Path(__file__).resolve().parent;D=O.parents[1]/'coordinator/Q01'
def guard():
 assert not (O.parents[1]/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
def load(name):
 path=D/(name+'.json.gz')
 with gzip.open(path,'rt') as f:return json.load(f)
def augmented(C):
 n=len(C);P=np.full((n,n),.5/(n-1));np.fill_diagonal(P,0);return C+P
def objective(z,A):
 n=len(A);theta=np.r_[z,0.];choice=np.broadcast_to(theta,(n,n)).copy();np.fill_diagonal(choice,-np.inf)
 logp=choice-logsumexp(choice,axis=1)[:,None];prob=np.exp(logp);total=A.sum();logp[np.diag_indices(n)]=0
 value=-np.sum(A*logp)/total;gradient=(A.sum(1)@prob-A.sum(0))/total
 return value,gradient[:-1]
def fit(C):
 A=augmented(C);initial=np.log(A.sum(0));initial-=initial[-1]
 opt=minimize(objective,initial[:-1],args=(A,),jac=True,method='L-BFGS-B',options=dict(maxiter=300,gtol=1e-9,ftol=1e-14,maxls=40))
 value,g=objective(opt.x,A);theta=np.r_[opt.x,0.];lp=np.broadcast_to(theta,(len(C),len(C))).copy();np.fill_diagonal(lp,-np.inf);lp-=logsumexp(lp,axis=1)[:,None]
 ok=bool(opt.success and np.isfinite(value) and np.all(np.isfinite(theta)) and max(abs(g))<=1e-7)
 return dict(theta=theta.tolist(),weights=softmax(theta).tolist(),objective=float(value),gradient_max=float(max(abs(g))),success=bool(opt.success),qualified=ok,status=int(opt.status),message=str(opt.message),iterations=int(opt.nit),evaluations=int(opt.nfev)),lp
def panel(name):
 guard();start=time.monotonic();old=load(name);vs=old['cipher'];counts=np.zeros((29,2,29,29));base=np.zeros((29,29));records=[]
 for ordinal,c in enumerate(vs):
  prev=np.array(c[:-1]);cur=np.array(c[1:]);nonrepeat=prev!=cur;states=np.cumsum(prev[None,:]==np.arange(29)[:,None],axis=1)%2
  prev=prev[nonrepeat];cur=cur[nonrepeat];states=states[:,nonrepeat];records.append((prev,cur,states))
  if ordinal%2==0:
   np.add.at(base,(prev,cur),1)
   for m in range(29):np.add.at(counts[m],(states[m],prev,cur),1)
 baseline,blp=fit(base);fits=[];probs=np.zeros((29,2,29,29))
 for m in range(29):
  pair=[]
  for state in range(2):
   f,lp=fit(counts[m,state]);pair.append(f);probs[m,state]=lp
  fits.append(pair)
 gains=np.zeros((29,45))
 for page,(prev,cur,states) in enumerate(records):
  for m in range(29):gains[m,page]=np.sum(probs[m,states[m],prev,cur]-blp[prev,cur])
 training=gains[:,::2].sum(1);held=gains[:,1::2].sum(1);marker=int(np.argmax(training));den=sum(len(records[i][0]) for i in range(1,45,2));allfits=[baseline]+[x for pair in fits for x in pair]
 out=dict(name=name,input_sha256=hashlib.sha256((D/(name+'.json.gz')).read_bytes()).hexdigest(),baseline_fit=baseline,state_fits=fits,train_total=training.tolist(),held_total=held.tolist(),perpage_gain=gains.tolist(),selected_marker=marker,score=float(held[marker]/den),held_nonrepeat_count=den,qualified=all(f['qualified'] for f in allfits),max_gradient=max(f['gradient_max'] for f in allfits),seconds=time.monotonic()-start,original_score=old['score'],original_marker=old['selected_marker'])
 (O/'panels').mkdir(exist_ok=True)
 with gzip.open(O/'panels'/(name+'.json.gz'),'wt') as f:json.dump(out,f)
 return out
def main():
 guard();mode=sys.argv[1]
 if mode=='pilot':
  r=panel('real');out={k:v for k,v in r.items() if k not in ['baseline_fit','state_fits','perpage_gain','train_total','held_total']};out['projected_440_seconds']=r['seconds']*440;(O/'pilot.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert r['qualified'];return
 raise ValueError(mode)
if __name__=='__main__':main()
