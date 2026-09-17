from pathlib import Path
import sys,json,numpy as np
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/decoder/reset-feedback';sys.path.insert(0,str(D));import model
s=json.loads((D/'inputs.json').read_text())['controls'][0];x=json.loads((D/'plants/00-p03.json').read_text());L=np.load(D/'model-p03.npz')['L'];arr=np.load(D/'plants/00-p03.npz');W,B,q,meta=model.factors(s['cipher'],s['ends'],s['k'],s['reset_before'],L);assert np.array_equal(W,arr['W']) and np.array_equal(B,arr['B']) and q==arr['q'].tolist();maxerr=0
for a in x['alternatives']:
 hist=[];p=[];score=0;aa=bb=29
 for i,v in enumerate(s['cipher']):
  if i in s['reset_before']:hist=[]
  key=a['seed'][len(hist)] if len(hist)<s['k'] else sum(hist[-s['k']:]);z=(v-key)%29;p.append(z);hist.append(z);score+=L[aa,bb,z];aa,bb=bb,z
  if i in s['ends']:score+=L[aa,bb,29];aa,bb=bb,29
 assert p==a['plaintext'];maxerr=max(maxerr,abs(score-a['score']));assert abs(score-a['score'])<1e-10
assert x['alternatives'][0]['plaintext']==s['truth']
out=dict(passed=True,case=x['id'],paths=len(x['alternatives']),max_direct_error=maxerr,leader_truth_exact=True,full_factor_arrays_equal=True);(Path(__file__).parent/'reset-plant-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
