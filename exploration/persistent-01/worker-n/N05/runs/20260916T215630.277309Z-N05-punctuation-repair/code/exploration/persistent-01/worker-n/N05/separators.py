import json,pathlib,collections
import numpy as np
from PIL import Image
from scipy.ndimage import label
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];I=R/'exploration/persistent-01/worker-i';records=sorted(json.loads((I/'route-mapping.json').read_text())['records'],key=lambda r:(r['page'],r['row'],r['index']));groups=collections.defaultdict(list)
for i,r in enumerate(records):groups[r['page'],r['row']].append(i)
images={p:np.array(Image.open(R/f'liber-primus/data/relikd/p{p}.jpg').convert('L')) for p in [0,1]};out=[]
for key,ix in groups.items():
 for a,b in zip(ix,ix[1:]):
  r,s=records[a],records[b]
  if s['source_char_position']-r['source_char_position']==1:continue
  box=[r['right'],min(r['y'],s['y']),s['x'],max(r['bottom'],s['bottom'])];crop=images[key[0]][box[1]:box[3],box[0]:box[2]];labs,n=label(crop<128);areas=np.bincount(labs.ravel());sizes=[int(v) for v in areas[1:] if v>=4];out.append({'after_record':a,'before_record':b,'page':key[0],'row':key[1],'box':box,'component_count':len(sizes),'areas':sizes})
(O/'separator-types.json').write_text(json.dumps(out,indent=2));print(collections.Counter(r['component_count'] for r in out));print([(r['page'],r['row'],r['component_count']) for r in out if r['component_count']!=1])
