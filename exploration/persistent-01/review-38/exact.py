from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).parent;B=R.parent;ROOT=B.parent.parent;records=json.loads((B/'worker-s/S09-exact-comparison.json').read_text());out=[]
for row in records:
 crops=[]
 for page in row['pages']:
  im=Image.open(ROOT/f'liber-primus/data/relikd/p{page}.jpg').convert('L');crops.append(np.array(im.crop(row['roi'])))
 assert np.array_equal(*crops) and all(hashlib.sha256(c.tobytes()).hexdigest()==sha for c,sha in zip(crops,row['sha256']));out.append({'pages':row['pages'],'region':row['region'],'byte_identical':True})
(R/'exact-check.json').write_text(json.dumps(out,indent=2));print(out)
