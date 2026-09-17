import pathlib,json,numpy as np
from PIL import Image
base=pathlib.Path('exploration/persistent-01/worker-s');out={};metadata=[]
for p in [0,1]:
 im=np.asarray(Image.open(f'liber-primus/data/relikd/p{p}.jpg').convert('L'))
 for name,roi in [('toploop',(1110,665,1270,675)),('bottomloop',(1110,2995,1270,3005))]:
  x0,y0,x1,y1=roi;crop=im[y0:y1,x0:x1];out[f'p{p}_{name}']=crop;metadata.append({'page':p,'region':name,'roi':roi,'pixels':int(crop.size),'dark128':int((crop<128).sum())})
np.savez_compressed(base/'S07b-removed-source-strips.npz',**out);(base/'S07b-removed-source-strips.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(metadata))
