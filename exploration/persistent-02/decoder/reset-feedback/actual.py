import argparse,json,numpy as np,resource
from common import *
from model import *
from solver import solve

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=0);ap.add_argument('--stop',type=int,default=20);args=ap.parse_args();data=json.loads((O/'inputs.json').read_text());s=data['actual'];out=O/'actual';out.mkdir(exist_ok=True)
 assert (O/'REVIEW-CLEARANCE.md').exists(),'fresh reviewer clearance required'
 for idx in range(args.start,args.stop):
  c=s['panels'][idx];ends=s['ends'];resets=s['reset_before'];cut=s['prefix_length']
  for name in ('p03','complementary'):
   L=load_table(name)
   for mode,n in [('full',len(c)),('prefix',cut)]:
    for k in s['band']:
     guard();stem=f'{idx:02d}-{name}-{mode}-k{k}';path=out/(stem+'.json');assert not path.exists();ee=[i for i in ends if i<n];rr=[i for i in resets if i<n];W,B,q,meta=factors(c[:n],ee,k,rr,L);z=solve(W,B);norm=n+len(ee)
     for a in z['alternatives']:
      a['seed']=[(-v)%29 for v in a['offset'][:-1]];a['plaintext']=decode(c,a['seed'],resets);a['fit_total']=direct_score(a['plaintext'][:n],ee,L);assert abs(a['fit_total']-a['score'])<1e-8
      a['fit_score']=a['fit_total']/norm;a['full_total']=direct_score(a['plaintext'],ends,L);a['full_score']=a['full_total']/(len(c)+len(ends));pe=[i for i in ends if i<cut];a['prefix_total']=direct_score(a['plaintext'][:cut],pe,L);a['continuation_score']=(a['full_total']-a['prefix_total'])/(len(c)-cut+len(ends)-len(pe))
     z.update(panel=idx,model=name,mode=mode,k=k,norm=norm,maximum_normalized=z['maximum']/norm,upper_normalized=z['upper_bound']/norm,input_sha256=digest(O/'inputs.json'),table_sha256=next(x['table_sha256'] for x in data['models'] if x['name']==name),meta=meta,maxrss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss);path.write_text(json.dumps(z,indent=2)+'\n');np.savez_compressed(out/(stem+'.npz'),W=W,B=B,q=q);print(json.dumps(dict(panel=idx,model=name,mode=mode,k=k,score=z['maximum_normalized'],gap=z['gap'],seconds=z['seconds'])),flush=True)
if __name__=='__main__':main()
