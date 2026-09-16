"""Measure the explicitly observed red field; no OCR or inferred rune mapping."""
import pathlib,json,hashlib
import numpy as np
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[3]; OUT=pathlib.Path(__file__).parent

def spans(mask):
 a=np.flatnonzero(np.diff(np.r_[False,mask,False].astype(np.int8)))
 return [list(map(int,z)) for z in zip(a[::2],a[1::2])]
def measure(a):
 red=(a[:,:,0]>150)&(a[:,:,1]<100)&(a[:,:,2]<100)
 ys,xs=np.nonzero(red)
 return dict(red_pixels=int(red.sum()),bbox_xyxy=None if not len(xs) else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],row_spans=spans(red.any(1)),column_spans=spans(red.any(0)))
control=np.full((20,30,3),255,dtype=np.uint8);control[3:8,7:16]=[180,20,20];control[10:12,3:5]=0
assert measure(control)['bbox_xyxy']==[7,3,16,8] and measure(control)['red_pixels']==45
rows=[]
for page in (0,1):
 f=ROOT/f'liber-primus/data/relikd/p{page}.jpg';a=np.array(Image.open(f).convert('RGB'))
 rows.append(dict(page=page,path=str(f.relative_to(ROOT)),sha256=hashlib.sha256(f.read_bytes()).hexdigest(),size=[a.shape[1],a.shape[0]],**measure(a)))
out=dict(strategy='outside-box-v1',rule='Fixed RGB threshold R>150,G<100,B<100 after viewing only originals0/1; exploratory color measurement, not glyph recognition.',control='Exact rectangle and black exclusion pass',pages=rows,limits='JPEG/compression/color thresholds affect pixel counts; no symbol accuracy or cipher-channel inference. Text/source mapping is provisional and not used to decode.')
(OUT/'layout-color.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
