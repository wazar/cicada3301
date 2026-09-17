import pathlib,json,numpy as np
P=pathlib.Path(__file__).resolve().parent;D=np.load(P.parent/'worker-q/Q06/inputs.npz');B=np.load(P/'R05-bank.npz');out={}
for name in ['R05-positive-0','R05-positive-1','R05-actual','R05-actual-raster-0','R05-actual-raster-1']:
 R=np.load(P/(name+'.npz'));held=R['scope']&~D['train'];rows=[]
 for c in D['eligible']:
  mask=held&(D['labels']==c);z=dict(shape=int(c),held=int(mask.sum()),correct_identity=int(np.sum(mask&R['correct_identity'])),state0=int(np.sum(mask&(R['states']==0))),state1=int(np.sum(mask&(R['states']==1))),weights=R['weights'][mask].tolist())
  if 'bits' in R:z['joint_correct_state']=int(np.sum(mask&R['correct_identity']&(R['states']==R['bits'])))
  rows.append(z)
 out[name]=rows
R=np.load(P/'R05-actual.npz');ids=np.flatnonzero(R['active']&(R['states']==0));out['actual_low_state_details']=[]
for i in ids:
 ci=int(np.flatnonzero(B['shapes']==R['predicted_classes'][i])[0]);z=R['identity_weight_cost'][i,ci];out['actual_low_state_details'].append(dict(index=int(i),shape=int(D['labels'][i]),train=bool(D['train'][i]),weight=float(R['weights'][i]),identity_weight_mse=z.tolist(),tied_minimum_weights=B['weights'][np.isclose(z,z.min(),atol=1e-12,rtol=0)].tolist()))
(P/'R05-diagnosis.json').write_text(json.dumps(out,indent=2)+'\n');print('Retained per-class control/actual counts; low-state details',len(ids))
