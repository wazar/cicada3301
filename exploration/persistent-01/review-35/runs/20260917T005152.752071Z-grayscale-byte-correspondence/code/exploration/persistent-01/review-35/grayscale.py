from PIL import Image
import numpy as np,json
from pathlib import Path
r=Path(__file__).parent;s=r.parent/'worker-s';z=json.load(open(s/'S07b-result.json'));errors=[]
for name,v in z['loop_results'].items():
 if name.startswith('crosspage-'):
  key=name.split('crosspage-')[1];a=np.array(Image.open(s/'S07b-pixels'/f'p0-{key}.png'));b=np.array(Image.open(s/'S07b-pixels'/f'p1-{key}.png'))
 else:
  page=int(name[1]);a=np.array(Image.open(s/'S07b-pixels'/f'p{page}-toploop.png'));b=np.array(Image.open(s/'S07b-pixels'/f'p{page}-bottomloop.png'))
  if name.endswith('180'):b=np.flip(b)
 b=np.roll(b,v['shift_dy_dx'],axis=(0,1));union=(a<192)|(b<192);err=float(np.abs(a.astype(int)-b.astype(int))[union].mean());assert abs(err-v['foreground_grayscale_MAE'])<1e-12;assert float((a==b).mean())==v['full_ROI_equal_fraction'];errors.append({'name':name,'MAE':err})
assert np.array_equal(np.array(Image.open(s/'S07b-pixels/p0-bottomloop.png')),np.array(Image.open(s/'S07b-pixels/p1-bottomloop.png')))
(r/'grayscale-check.json').write_text(json.dumps({'bottom_byte_identical':True,'loops':errors},indent=2));print('PASS')
