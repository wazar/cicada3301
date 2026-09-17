import p26 as m
from pathlib import Path
import numpy as np,json,sys,time,hashlib
OUT=m.BASE/'worker-p/P27'
def save(name,x):(OUT/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def reverse(seqs):
 C=m.count(seqs[23:]);H=m.count(seqs[:23]);b=m.baseline(C);L=m.logprob(np.array(b['a']));L[~m.MASK]=0;bltrain=float((C*L).sum());blheld=float((H*L).sum());A,eig,orders=m.candidates(C);cand=[];decoded=[]
 for cyc,aliases in sorted(orders.items()):
  f=np.empty(29,dtype=int);f[list(cyc)]=np.arange(29);D=(f[None,:]-f[:,None])%29;counts=np.bincount(D[m.MASK],weights=C[m.MASK],minlength=29);held=np.bincount(D[m.MASK],weights=H[m.MASK],minlength=29)
  q=np.r_[0.,(counts[1:]+.5)/(C.sum()+14)];lp=np.zeros(29);lp[1:]=np.log(q[1:]);tr=float(counts@lp);he=float(held@lp)
  cand.append(dict(cycle=list(cyc),f=f.tolist(),eigen_indices=aliases,q=q.tolist(),train_counts=counts.astype(int).tolist(),held_counts=held.astype(int).tolist(),train_ll=tr,held_ll=he,held_gain=he-blheld))
  decoded.append(np.concatenate([np.r_[255,(f[np.array(s[1:])]-f[np.array(s[:-1])])%29] for s in seqs]).astype(np.uint8))
 best=min(range(len(cand)),key=lambda i:(-cand[i]['train_ll'],cand[i]['cycle'])) if cand else None
 return dict(baseline=b,baseline_train_ll=bltrain,baseline_held_ll=blheld,eigenvectors=eig,candidates=cand,selected=best,held_gain=cand[best]['held_gain'] if best is not None else None,qualified=b['qualified'] and best is not None,train_counts=C.tolist(),held_counts=H.tolist(),train_events=int(C.sum()),held_events=int(H.sum())),np.array(decoded,dtype=np.uint8)
def panel(name):
 m.guard();path=OUT/(name+'.json')
 if path.exists():return json.loads(path.read_text())
 src=m.OUT/(name+'.json');npz=m.OUT/(name+'.npz');old=json.loads(src.read_text());a=np.load(npz);seqs=[v.tolist() for v in np.split(a['cipher'],np.cumsum(a['lengths'])[:-1])];t=time.monotonic();r,d=reverse(seqs);r.update(name=name,seconds=time.monotonic()-t,original_json_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),original_npz_sha256=hashlib.sha256(npz.read_bytes()).hexdigest(),forward_gain=old['held_gain'],both_qualified=old['qualified'] and r['qualified']);r['sum_gain']=r['held_gain']+old['held_gain'] if r['both_qualified'] else None
 if r['selected'] is not None and old['selected'] is not None:r['affine_agreement']=m.affine(r['candidates'][r['selected']]['cycle'],old['candidates'][old['selected']]['cycle'])
 if 'cycle' in old:r['truth_affine_agreement']=[m.affine(c['cycle'],old['cycle']) for c in r['candidates']]
 np.savez_compressed(OUT/(name+'.npz'),decoded=d);save(name+'.json',r);return r
def summary(prefix,n):
 main=panel(prefix);ns=[panel(f'{prefix}-null-{j:03}') for j in range(n)];unknown=sum(not x['both_qualified'] for x in ns);ge=sum(x['both_qualified'] and x['sum_gain']>=main['sum_gain'] for x in ns) if main['both_qualified'] else None;ga=sum(x['both_qualified'] and x['affine_agreement']['maximum_matches']>=main['affine_agreement']['maximum_matches'] for x in ns) if main['both_qualified'] else None
 r=dict(name=prefix,qualified=main['both_qualified'],forward_gain=main['forward_gain'],reverse_gain=main['held_gain'],sum_gain=main['sum_gain'],agreement=main.get('affine_agreement'),nulls=n,unknown=unknown,tail=(1+ge)/(n+1) if ge is not None and not unknown else None,tail_interval=[(1+ge)/(n+1),(1+ge+unknown)/(n+1)] if ge is not None else None,secondary_agreement_tail=(1+ga)/(n+1) if ga is not None and not unknown else None)
 if 'truth_affine_agreement' in main:r['reverse_selected_truth_agreement']=main['truth_affine_agreement'][main['selected']]
 save(prefix+'-summary.json',r);print(json.dumps(r),flush=True)
def controls():
 for i in range(4):summary(f'control-{i}',99)
def actual():
 assert all((OUT/f'control-{i}-summary.json').exists() for i in range(4));summary('actual',199)
if __name__=='__main__':
 m.guard();t=time.monotonic();{'controls':controls,'actual':actual}[sys.argv[1]]();print('SECONDS',time.monotonic()-t)
