import argparse,json,numpy as np
from common import *
from model import *
from solver import solve

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=0);ap.add_argument('--stop',type=int,default=44);args=ap.parse_args();data=json.loads((O/'inputs.json').read_text());out=O/'plants';out.mkdir(exist_ok=True)
 for idx,s in enumerate(data['controls'][args.start:args.stop],args.start):
  for model in ('p03','complementary'):
   guard();path=out/f'{idx:02d}-{model}.json';assert not path.exists();L=load_table(model);W,B,q,meta=factors(s['cipher'],s['ends'],s['k'],s['reset_before'],L);result=solve(W,B);x=[(-v)%29 for v in s['seed']]+[sum(s['seed'])%29];truthscore=direct_score(s['truth'],s['ends'],L);assert abs(truthscore-value(W,B,x))<1e-8
   for a in result['alternatives']:
    a['seed']=[(-v)%29 for v in a['offset'][:-1]];a['plaintext']=decode(s['cipher'],a['seed'],s['reset_before']);a['errors']=sum(p!=q for p,q in zip(a['plaintext'],s['truth']));a['direct_score']=direct_score(a['plaintext'],s['ends'],L);assert abs(a['direct_score']-a['score'])<1e-8
   result.update(id=s['id'],index=idx,model=model,k=s['k'],input_sha256=digest(O/'inputs.json'),truth_score=truthscore,truth_offset=x,truth_gap=result['maximum']-truthscore,source=s['source'],meta=meta);path.write_text(json.dumps(result,indent=2)+'\n');np.savez_compressed(out/f'{idx:02d}-{model}.npz',W=W,B=B,q=q);print(json.dumps(dict(index=idx,model=model,k=s['k'],errors=result['alternatives'][0]['errors'],gap=result['gap'],seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
