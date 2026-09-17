import json,hashlib,time
from pathlib import Path
import numpy as np
D=Path(__file__).parent;O=D.parent/'N14';M=json.loads((O/'maps.json').read_text());N=[len(m['route']) for m in M];E=[np.array(m['novel_edges']) for m in M]
def run(name,mode,B,seed):
 path=O/(name+'.npz');c=np.load(path)['cipher'];rng=np.random.default_rng(seed);generated=[];stats=np.zeros(B,int);actual=0;off=0
 for n,e in zip(N,E):
  a=c[off:off+n];z=np.empty((B,n),dtype=np.uint8)
  if mode=='A':
   z[:,0]=a[0]
   for i in range(1,n):
    if a[i]==a[i-1]:z[:,i]=z[:,i-1]
    else:
     r=rng.integers(28,size=B);z[:,i]=r+(r>=z[:,i-1])
  else:
   for b in range(B):z[b]=rng.permutation(a)
  actual+=int(sum(a[e[:,0]]==a[e[:,1]]));stats+=(z[:,e[:,0]]==z[:,e[:,1]]).sum(axis=1);generated.append(z);off+=n
 out={'name':name,'model':mode,'B':B,'seed':seed,'input':str(path),'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'actual':actual,'null_mean':float(stats.mean()),'null_min':int(min(stats)),'tail':(1+int(sum(stats<=actual)))/(B+1)}
 np.savez_compressed(D/f'{name}-{mode}.npz',cipher=c,nulls=np.concatenate(generated,axis=1),null_stats=stats)
 (D/f'{name}-{mode}.json').write_text(json.dumps(out,indent=2));return out
if __name__=='__main__':
 t=time.time();controls=[run(f'control-{k}',mode,99,616000+2*k+i) for k in range(12) for i,mode in enumerate('AB')];actual=[run('actual',mode,999,615900+i) for i,mode in enumerate('AB')];out={'actual':actual,'controls':controls,'seconds':time.time()-t};(D/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({'actual':actual,'power':{m:sum(x['tail']<=.05 for x in controls if x['model']==m) for m in 'AB'},'seconds':time.time()-t},indent=2))
