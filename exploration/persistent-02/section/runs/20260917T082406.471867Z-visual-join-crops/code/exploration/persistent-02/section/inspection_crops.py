"""Image-only inspection crops; no OCR, glyph selection or scientific input changes."""
import pathlib,json,hashlib
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];(O/'inspection').mkdir(exist_ok=True)
regions=[('p0-heading',0,[580,630,1830,1010]),('p0-lastrow',0,[580,2710,1830,2910]),('p1-firstrow',1,[580,630,1830,820]),('p1-lastrow',1,[580,2710,1830,2910]),('p2-firstrow',2,[580,630,1830,820]),('p2-terminal',2,[580,2150,1830,2420]),('p0-line3-4-join',0,[580,1220,1830,1580]),('p1-line4-5-join',1,[580,1400,1830,1780])]
records=[]
for name,p,bbox in regions:
 src=R/f'liber-primus/data/relikd/p{p}.jpg';dst=O/'inspection'/f'{name}.png';im=Image.open(src);assert im.size==(2400,3600);im.crop(bbox).save(dst);records.append(dict(name=name,page=p,bbox=bbox,source=str(src.relative_to(R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),crop=str(dst.relative_to(R)),crop_sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
(O/'inspection'/'crops.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records))
