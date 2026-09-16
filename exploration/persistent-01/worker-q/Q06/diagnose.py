from pathlib import Path
import numpy as np,json
R=Path(__file__).parent;D=np.load(R/'inputs.npz');out=[]
for rep in range(2):
 z=np.load(R/f'positive-{rep}.npz');held=z['scope']&~D['train'];rmse=np.sqrt(z['identity_distances'].min(axis=1));rows=[]
 for bit in [0,1]:
  sel=held&(z['bits']==bit);rows.append({'planted_rotation_deg':2*bit,'held_n':int(sum(sel)),'classified':int(sum((z['predicted_classes']!=-1)&sel)),'median_nearest_identity_RMSE':float(np.median(rmse[sel])),'min':float(min(rmse[sel])),'max':float(max(rmse[sel]))})
 out.append({'rep':rep,'by_state':rows})
(R/'identity-rejection-diagnosis.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
