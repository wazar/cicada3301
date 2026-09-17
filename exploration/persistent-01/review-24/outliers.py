from pathlib import Path
import numpy as np,json
r=Path(__file__).parent;p=r.parent/'worker-r';d=np.load(r.parent/'worker-q/Q06/inputs.npz');held=np.isin(d['labels'],d['eligible'])&~d['train'];a=np.load(p/'R05-actual.npz');z=np.load(p/'R05-positive-1.npz');ids=np.flatnonzero(held&((z['states']!=z['bits'])|~z['correct_identity']));outliers=[]
for i in np.flatnonzero(a['scope']&(a['weights']==-1.5)):
 curve=a['identity_weight_cost'][i,0];assert curve.argmin()==0 and np.sum(curve==curve.min())==1;outliers.append({'id':int(i),'train':bool(d['train'][i]),'shape':int(d['labels'][i]),'cost_curve':curve.tolist(),'second_best_gap':float(np.partition(curve,1)[1]-curve[0])})
assert ids.tolist()==[11,17,135] and all(d['labels'][i]==1 for i in ids);assert [x['id'] for x in outliers]==[63,78,100,254]
(r/'error-outliers.json').write_text(json.dumps({'large_control_error_ids':ids.tolist(),'actual_lower_bound_outliers':outliers},indent=2));print('PASS 3 control errors, 4 unique boundary-weight minima')
