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
   a=np.concatenate([p[phase:phase+(len(p)-phase)//5*5].reshape(-1,5) for p in ps]);v=a@m.T%29
   freqs=np.array([np.bincount(v[:,j],minlength=29) for j in range(5)]);ex=len(v)/29
   score=float(np.sum((freqs-ex)**2/ex));out.append({'matrix':label,'phase':phase,'score':score,'column_counts':freqs.tolist()})
 return out
rng=np.random.default_rng(2026091704);plain=np.empty((2000,5),dtype=np.int64)
for j in range(5):
 w=1+.8*np.cos(2*np.pi*np.arange(29)/29+2*np.pi*j/5);w/=w.sum();plain[:,j]=rng.choice(29,2000,p=w)
cipher=(plain@mat[0][1].T)%29
assert np.array_equal(cipher@mat[1][1].T%29,plain)
ctr=scan([cipher.ravel()]);truth=next(x for x in ctr if x['matrix']=='0_inverse' and x['phase']==0)
f=np.bincount(plain.ravel(),minlength=29);pooled=float(np.sum((f-len(plain.ravel())/29)**2/(len(plain.ravel())/29)))
real=scan(pages);mx=max(x['score'] for x in real);t=time.monotonic();null=[];null_all=[]
for k in range(1000):
 scores=scan([rng.permutation(p) for p in pages]);null_all.append([x['score'] for x in scores]);null.append(max(x['score'] for x in scores))
cn=[]
for k in range(100):cn.append(max(x['score'] for x in scan([rng.permutation(cipher.ravel())])))
x={'real_candidates':real,'max_score':mx,'family_p':(1+sum(n>=mx for n in null))/(1+len(null)),'null_reps':len(null),'null_quantiles':np.quantile(null,[.5,.95,.99]).tolist(),'null_max':max(null),'control_truth':truth,'control_pooled_score':pooled,'control_rank':1+sum(x['score']>truth['score'] for x in ctr),'control_null_max':max(cn),'control_detected':truth['score']>max(cn),'seconds':time.monotonic()-t}
(R/'experiment04-result.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({k:v for k,v in x.items() if k not in ['real_candidates','control_truth']},indent=2))

import gzip
def gz(name,obj):
 with gzip.open(R/name,'wt') as f:json.dump(obj,f)
gz('experiment04-evidence.json.gz',{'null_all_scores':null_all,'control_null_maxima':cn,'control_plain':plain.tolist(),'control_cipher':cipher.tolist(),'control_candidates':ctr,'rng_seed':2026091704,'ordering':'synthetic plain,1000real shuffles,100control shuffles','transformed_outputs':'same exact20fixed transforms as experiment02-evidence.json.gz'})
