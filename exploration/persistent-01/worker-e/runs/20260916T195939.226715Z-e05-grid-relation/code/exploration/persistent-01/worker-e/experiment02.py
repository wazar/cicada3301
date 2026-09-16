import json,pathlib,time,numpy as np
R=pathlib.Path(__file__).parent
D=json.load(open('audit/parallel-01/inputs/dataset.json')); S=json.load(open(R/'experiment01-result.json'))
pages=[np.array(p['indices'],dtype=np.int64) for p in D['pages'] if p['original_page'] in S['pages']]
def inv(m):
 a=np.concatenate((m.copy()%29,np.eye(5,dtype=np.int64)),axis=1)
 for j in range(5):
  z=next(i for i in range(j,5) if a[i,j]);a[[z,j]]=a[[j,z]];a[j]=a[j]*pow(int(a[j,j]),-1,29)%29
  for i in range(5):
   if i!=j:a[i]=(a[i]-a[i,j]*a[j])%29
 return a[:,5:]
mat=[]
for j,s in enumerate(S['sources']):
 m=np.array(s['values'],dtype=np.int64).reshape(5,5)%29; mi=inv(m);assert np.array_equal(m@mi%29,np.eye(5,dtype=np.int64))
 mat.extend([(str(j)+'_forward',m),(str(j)+'_inverse',mi)])
def scan(ps):
 out=[]
 for label,m in mat:
  for phase in range(5):
   chunks=[p[phase:phase+(len(p)-phase)//5*5].reshape(-1,5) for p in ps];a=np.concatenate(chunks);v=(a@m.T%29).ravel();f=np.bincount(v,minlength=29);expect=len(v)/29
   score=float(np.sum((f-expect)**2/expect));out.append({'matrix':label,'phase':phase,'n':len(v),'score':score,'counts':f.tolist()})
 return out
rng=np.random.default_rng(20260917);weights=np.arange(29,0,-1,dtype=float);weights/=weights.sum()
plain=rng.choice(29,10000,p=weights);cipher=plain.reshape(-1,5)@mat[0][1].T%29
assert np.array_equal((cipher@mat[1][1].T%29).ravel(),plain)
control=scan([cipher.ravel()]);truth=next(x for x in control if x['matrix']=='0_inverse' and x['phase']==0)
real=scan(pages);mx=max(x['score'] for x in real); null=[];t=time.monotonic()
for k in range(1000):null.append(max(x['score'] for x in scan([rng.permutation(p) for p in pages])))
controlnull=[]
for k in range(100):controlnull.append(max(x['score'] for x in scan([rng.permutation(cipher.ravel())])))
out={'candidates':real,'max_score':mx,'null_reps':len(null),'null_max':max(null),'null_quantiles':np.quantile(null,[.5,.95,.99]).tolist(),'family_p':(1+sum(v>=mx for v in null))/(1+len(null)),'control_truth':truth,'control_rank':1+sum(x['score']>truth['score'] for x in control),'control_null_max':max(controlnull),'control_detected':truth['score']>max(controlnull),'seconds':time.monotonic()-t}
(R/'experiment02-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='candidates'},indent=2))
