import pathlib,json,hashlib,numpy as np
from PIL import Image
base=pathlib.Path('exploration/persistent-01/worker-s');rois={'top':(1110,600,1270,665),'bottom':(1110,2930,1270,2995)};images=[Image.open(f'liber-primus/data/relikd/p{p}.jpg').convert('L') for p in [0,1,2]];crops={(p,name):np.asarray(im.crop(roi)) for p,im in enumerate(images) for name,roi in rois.items()}
comparisons=[]
for a,b,name in [(1,2,'top'),(0,1,'bottom'),(0,2,'bottom')]:
 x,y=crops[a,name],crops[b,name];comparisons.append({'pages':[a,b],'region':name,'roi':rois[name],'pixel_equal':bool(np.array_equal(x,y)),'pixels_different':int((x!=y).sum()),'sha256':[hashlib.sha256(v.tobytes()).hexdigest() for v in [x,y]],'representation':'decoded PIL grayscale uint8 crop rowmajor bytes'})
(base/'S09-exact-comparison.json').write_text(json.dumps(comparisons,indent=2)+'\n');print(json.dumps(comparisons,indent=2))
