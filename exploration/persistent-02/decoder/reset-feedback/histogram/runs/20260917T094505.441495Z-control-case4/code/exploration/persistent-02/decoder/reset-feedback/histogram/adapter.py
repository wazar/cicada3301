import pathlib,sys,json,argparse,numpy as np,resource
H=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(H.parent))
from common import O,R,P,guard,digest,load_table
from model import factors,decode,direct_score
from solver import solve
SOURCE=P/'coordinator/histogram-reset/panels.json'

def freeze():
 guard();assert not (H/'pins.json').exists();data=json.loads(SOURCE.read_text());old=json.loads((O/'inputs.json').read_text());assert len(data['cases'])==5
 for i,c in enumerate(data['cases']):
  assert len(c['panels'])==20 and all(len(x)==716 for x in c['panels']);assert c['prefix_length']==249
  if i==0:
   s=old['actual'];assert c['panels'][0]==s['panels'][0] and c['ends']==s['ends'] and c['reset_before']==s['reset_before']
  else:
   matches=[s for s in old['controls'] if s['k']==8 and len(s['truth'])==716 and s['cipher']==c['panels'][0]];assert len(matches)==1;s=matches[0];assert c['truth']==s['truth'] and c['seed']==s['seed'] and c['ends']==s['ends'] and c['reset_before']==s['reset_before']
 paths=[SOURCE,O/'inputs.json',O/'model-p03.npz',O/'model-complementary.npz',O/'model.py',O/'solver.py',O/'actual.py',O/'summary.py',H/'adapter.py',H/'aggregate.py',H/'PREREG.md']+sorted((O/'actual').glob('00-*.json'));pins={str(p.relative_to(R)):digest(p) for p in paths};(H/'pins.json').write_text(json.dumps(pins,indent=2)+'\n');print(json.dumps(dict(status='frozen',cases=5,panels=100,pins=pins)))

def run(args):
 guard();assert (H/'REVIEW-CLEARANCE.md').exists()
 if args.case==0:assert all((H/f'summary-case{i}.json').exists() for i in range(1,5)),'controls first'
 pins=json.loads((H/'pins.json').read_text());assert all(digest(R/p)==h for p,h in pins.items());data=json.loads(SOURCE.read_text());s=data['cases'][args.case];old=json.loads((O/'inputs.json').read_text());out=H/'cells'/f'case{args.case}';out.mkdir(parents=True,exist_ok=True)
 for panel in range(args.start,args.stop):
  c=s['panels'][panel];ends=s['ends'];resets=s['reset_before'];cut=s['prefix_length']
  for name in ('p03','complementary'):
   L=load_table(name)
   for mode,n in [('full',len(c)),('prefix',cut)]:
    for k in (5,6,7,8):
     guard();stem=f'{panel:02d}-{name}-{mode}-k{k}';path=out/(stem+'.json');assert not path.exists()
     if args.case==0 and panel==0:
      src=O/'actual'/(stem+'.json');z=json.loads(src.read_text());z.update(reused_original_path=str(src.relative_to(R)),reused_original_sha256=digest(src));assert z['panel']==0
     else:
      ee=[i for i in ends if i<n];rr=[i for i in resets if i<n];W,B,q,meta=factors(c[:n],ee,k,rr,L);z=solve(W,B);norm=n+len(ee)
      for a in z['alternatives']:
       a['seed']=[(-v)%29 for v in a['offset'][:-1]];a['plaintext']=decode(c,a['seed'],resets);a['fit_total']=direct_score(a['plaintext'][:n],ee,L);assert abs(a['fit_total']-a['score'])<1e-8;a['fit_score']=a['fit_total']/norm;a['full_total']=direct_score(a['plaintext'],ends,L);a['full_score']=a['full_total']/(len(c)+len(ends));pe=[i for i in ends if i<cut];a['prefix_total']=direct_score(a['plaintext'][:cut],pe,L);a['continuation_score']=(a['full_total']-a['prefix_total'])/(len(c)-cut+len(ends)-len(pe))
      z.update(panel=panel,model=name,mode=mode,k=k,norm=norm,maximum_normalized=z['maximum']/norm,upper_normalized=z['upper_bound']/norm,table_sha256=next(x['table_sha256'] for x in old['models'] if x['name']==name),meta=meta,maxrss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss);np.savez_compressed(out/(stem+'.npz'),W=W,B=B,q=q)
     z.update(case_index=args.case,case_id=s['id'],histogram_panels_sha256=digest(SOURCE),pins_sha256=digest(H/'pins.json'))
     if panel==0 and 'truth' in s:
      for a in z['alternatives']:a['truth_errors']=sum(x!=y for x,y in zip(a['plaintext'],s['truth']))
     path.write_text(json.dumps(z,indent=2)+'\n');print(json.dumps(dict(case=args.case,panel=panel,model=name,mode=mode,k=k,gap=z['gap'],reused='reused_original_path' in z)),flush=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('action',choices=['freeze','run']);ap.add_argument('--case',type=int,default=0,choices=range(5));ap.add_argument('--start',type=int,default=0);ap.add_argument('--stop',type=int,default=20);a=ap.parse_args();assert 0<=a.start<a.stop<=20
 if a.action=='freeze':freeze()
 else:run(a)
if __name__=='__main__':main()
