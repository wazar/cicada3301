import os,json,hashlib,pathlib,gzip,time
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).resolve().parent
MS=[1,2,4];SEED=33012701

def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def metrics(cs,details=False):
 totals=np.zeros((2,3,2));rows=[]
 for j,c in enumerate(cs):
  keep=np.r_[True,np.diff(c)!=0];idx=np.flatnonzero(keep);x=np.asarray(c)[keep];page=[]
  for k,m in enumerate(MS):
   B=29*m;ph=[]
   for r in range(B):
    n=(len(x)-r)//B
    if n<1:continue
    z=x[r:r+n*B].reshape(n,B);counts=np.array([np.bincount(v,minlength=29) for v in z]);ex=int(np.maximum(counts-m,0).sum());ph.append([r,ex,n*B])
   if not ph:page.append({'m':m,'phases':[]});continue
   best=min(ph,key=lambda a:(a[1]/a[2],a[0]));totals[j%2,k]+=[best[1],best[2]]
   page.append({'m':m,'best':best,'phases':ph})
  if details:rows.append({'page_index':j,'compressed':x.tolist(),'source_indices':idx.tolist(),'models':page})
 return totals[:,:,0]/totals[:,:,1],rows

def generate(lengths,q,rng,m=0,corrupt=0):
 cs=[]
 for n in lengths:
  if not m:
   c=[int(rng.integers(29))]
   while len(c)<n:
    if rng.random()<q:c.append(c[-1])
    else:
     v=int(rng.integers(28));c.append(v+(v>=c[-1]))
  else:
   base=[];prev=-1
   while len(base)<n+29*m:
    while True:
     bag=rng.permutation(np.repeat(np.arange(29),m))
     if bag[0]!=prev and np.all(bag[1:]!=bag[:-1]):break
    base.extend(map(int,bag));prev=base[-1]
   off=int(rng.integers(29*m));base=base[off:]
   if corrupt:
    base=[int(rng.integers(29)) if rng.random()<corrupt else v for v in base]
   c=[base[0]];i=1
   while len(c)<n:
    if rng.random()<q:c.append(c[-1])
    else:c.append(base[i]);i+=1
  cs.append(np.array(c,dtype=int))
 return cs

def main():
 t=time.monotonic();cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());data=ROOT/'audit/parallel-01/inputs/dataset.json';mp=ROOT/'audit/parallel-01/inputs/page-map.json'
 assert hashlib.sha256(data.read_bytes()).hexdigest()==cfg['dataset_sha256'];assert hashlib.sha256(mp.read_bytes()).hexdigest()==cfg['map_sha256']
 pages=sorted([p for p in json.loads(data.read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']],key=lambda p:p['original_page']);assert len(pages)==45
 cs=[np.array(p['indices']) for p in pages];lengths=list(map(len,cs));train=cs[::2];q=sum(np.sum(c[1:]==c[:-1]) for c in train)/sum(len(c)-1 for c in train)
 out=O/'l1';out.mkdir(exist_ok=True);rng=np.random.default_rng(SEED);dump(out/'input-manifest.json',{'pages':[p['original_page'] for p in pages],'lengths':lengths,'dataset_sha256':cfg['dataset_sha256'],'map_sha256':cfg['map_sha256'],'generator_seed':SEED,'q_train':q,'split':'sorted-page-index parity; 0 train,1 held','models':MS})
 allstats=[]
 with gzip.open(out/'generated-full-outputs.jsonl.gz','wt') as f:
  def sim(kind,i,m=0,corrupt=0):
   c=generate(lengths,q,rng,m,corrupt);v,_=metrics(c);f.write(json.dumps({'kind':kind,'replicate':i,'m':m,'corrupt':corrupt,'pages':[x.tolist() for x in c],'metrics':v.tolist()})+'\n');return v
  cal=np.array([sim('calibration',i) for i in range(80)]);mu=cal.mean(0);sd=cal.std(0,ddof=1)
  controls={}
  for m in MS:
   for corruption in [0,.01]:
    a=np.array([sim('control',i,m,corruption) for i in range(20)]);zs=(a-mu)/sd;choices=np.argmin(zs[:,0,:],axis=1);controls[f'bag{m}-corrupt{corruption}']={'scores':a.tolist(),'selected_m':[MS[x] for x in choices],'true_model_zero_excess':int(np.sum(np.all(a[:,:,MS.index(m)]==0,axis=1))),'n':20}
    if corruption==0:assert controls[f'bag{m}-corrupt{corruption}']['true_model_zero_excess']==20
  null=np.array([sim('wholeprocedure-null',i) for i in range(200)])
  nz=(null-mu)/sd;sel=np.argmin(nz[:,0,:],axis=1);nst=-nz[np.arange(len(null)),1,sel]
  # Actual discovery evaluated only after exact controls pass.
  real,maps=metrics(cs,True);z=(real-mu)/sd;choice=int(np.argmin(z[0]));stat=-z[1,choice];p=(1+int(np.sum(nst>=stat)))/(len(nst)+1)
  dump(out/'maps-full-phases.json',maps);dump(out/'calibration.json',{'scores':cal.tolist(),'mean':mu.tolist(),'sd':sd.tolist()});dump(out/'controls.json',controls);dump(out/'null-arrays.json',{'scores':null.tolist(),'selected_m':[MS[x] for x in sel],'statistics':nst.tolist()})
  summary={'real_scores':real.tolist(),'real_z':z.tolist(),'selected_m':MS[choice],'held_statistic':float(stat),'wholeprocedure_p':p,'controls':{k:{a:b for a,b in v.items() if a!='scores'} for k,v in controls.items()},'hypotheses':{'inventory_sizes':3,'max_phases_per_page':203,'train_page_count':23,'held_page_count':22,'calibration_reps':80,'control_reps':120,'null_reps':200},'seconds':time.monotonic()-t};dump(out/'summary.json',summary);print(json.dumps(summary))
if __name__=='__main__':main()
