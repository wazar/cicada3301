import json,collections
from common import *
def main():
 rows=[json.loads(p.read_text()) for p in sorted((O/'plants').glob('*.json'))];assert len(rows)==88;out={}
 for name in ('p03','complementary'):
  rr=[r for r in rows if r['model']==name];out[name]=dict(cases=len(rr),exact_recovery=sum(r['alternatives'][0]['errors']==0 for r in rr),certified=sum(r['certified_within_1e_10'] for r in rr),misses=[dict(id=r['id'],errors=r['alternatives'][0]['errors'],truth_gap=r['truth_gap'],bound_gap=r['gap']) for r in rr if r['alternatives'][0]['errors']],max_bound_gap=max(r['gap'] for r in rr))
 dump('plant-summary.json',out);print(json.dumps(out))
if __name__=='__main__':main()
