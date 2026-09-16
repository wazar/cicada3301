import json,pathlib,gzip,hashlib,collections,time
import numpy as np
from l2 import O,ROOT,guard,dump
SEED=33012704

def metric(cs):
 totals=np.zeros((2,4),dtype=int);rows=[]
 for j,c in enumerate(cs):
  c=np.asarray(c);neq=c[1:]!=c[:-1];eligible=neq[:-1]&neq[1:];hit=eligible&(c[:-2]==c[2:]);v=[int(hit.sum()),int(eligible.sum()),int((~neq).sum()),len(c)-1];totals[j%2]+=v;rows.append(v)
 return (totals[:,0]/totals[:,1]).tolist(),totals.tolist(),rows

def main():
 guard();t=time.monotonic();out=O/'l3';out.mkdir(exist_ok=True);rng=np.random.default_rng(SEED);cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());p=ROOT/'audit/parallel-01/inputs/dataset.json';assert hashlib.sha256(p.read_bytes()).hexdigest()==cfg['dataset_sha256'];pages=sorted([p for p in json.loads(p.read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']],key=lambda p:p['original_page']);cs=[np.array(p['indices']) for p in pages];q=sum(np.sum(c[1:]==c[:-1]) for c in cs[::2])/sum(len(c)-1 for c in cs[::2]);s=(1-29*q)*29/28;assert 0<=s<=1
 dump(out/'input-manifest.json',{'pages':[p['original_page'] for p in pages],'lengths':list(map(len,cs)),'dataset_sha256':cfg['dataset_sha256'],'map_sha256':cfg['map_sha256'],'seed':SEED,'q_train':q,'s_fitted':s,'analytic_q':(1-s*28/29)/29});controls=[];null=[]
 with gzip.open(out/'full-generated-output.jsonl.gz','wt') as f:
  for rep in range(200):
   if rep%20==0:guard()
   emitted=[];metadata=[]
   for c in cs:
    base=rng.integers(29,size=len(c)+1);x=base.copy();swaps=[]
    for i in range(1,len(c)):
     if x[i]==x[i-1] and rng.random()<s and x[i+1]!=x[i]:x[i],x[i+1]=x[i+1],x[i];swaps.append(i)
    assert collections.Counter(base)==collections.Counter(x)
    recovered=x.copy()
    for i in reversed(swaps):recovered[i],recovered[i+1]=recovered[i+1],recovered[i]
    assert np.array_equal(recovered,base);emitted.append(x[:-1]);metadata.append({'iid_queue':base.tolist(),'emitted':x[:-1].tolist(),'terminal_buffer':int(x[-1]),'swap_positions':swaps})
   rates,totals,rows=metric(emitted);controls.append({'rates':rates,'totals':totals});f.write(json.dumps({'kind':'swap-control','replicate':rep,'rates':rates,'totals':totals,'pages':metadata})+'\n')
  for rep in range(200):
   if rep%20==0:guard()
   emitted=[]
   for c in cs:
    starts=np.flatnonzero(np.r_[True,np.diff(c)!=0]);runs=np.diff(np.r_[starts,len(c)]);x=[int(rng.integers(29))]
    for _ in range(len(starts)-1):
     z=int(rng.integers(28));x.append(z+(z>=x[-1]))
    emitted.append(np.repeat(x,runs))
   rates,totals,rows=metric(emitted);null.append({'rates':rates,'totals':totals});f.write(json.dumps({'kind':'conditional-null','replicate':rep,'rates':rates,'totals':totals,'pages':[x.tolist() for x in emitted]})+'\n')
  ca=np.array([v['rates'] for v in controls]);na=np.array([v['rates'] for v in null]);crit=float(np.quantile(na[:,1],.99));power=int(np.sum(ca[:,1]>crit));assert power==200,'positive control gate fails';real,totals,rows=metric(cs);pnull=(1+int(np.sum(na[:,1]>=real[1])))/201;pswap=(1+int(np.sum(ca[:,1]<=real[1])))/201;ct=np.array([v['totals'] for v in controls]);qs=ct[:,:,2]/ct[:,:,3]
  result={'real_rates_train_held':real,'real_totals':totals,'per_page_counts':rows,'held_upper_tail_vs_M1':pnull,'held_lower_tail_vs_fitted_swap':pswap,'swap_rate_mean':ca.mean(0).tolist(),'swap_rate_range_held':[float(ca[:,1].min()),float(ca[:,1].max())],'M1_rate_mean':na.mean(0).tolist(),'M1_held99percentile':crit,'swap_controls_above_M1bar':power,'control_n':200,'doublet_rate_mean':qs.mean(0).tolist(),'doublet_rate_sd':qs.std(0,ddof=1).tolist(),'q_train':q,'s_fitted':s,'hypotheses':1,'seconds':time.monotonic()-t};dump(out/'null-and-control-arrays.json',{'null':null,'controls':controls});dump(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
