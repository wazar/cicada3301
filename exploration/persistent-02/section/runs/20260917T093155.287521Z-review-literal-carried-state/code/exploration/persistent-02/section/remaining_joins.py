"""Native image-only physical-line join sheets for the selected section."""
from PIL import Image,ImageDraw
import numpy as np,pathlib,json,hashlib
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];out=O/'inspection'/'remaining-joins';out.mkdir(exist_ok=True);records=[]
for page,n in [(0,12),(1,12),(2,9)]:
 src=R/f'liber-primus/data/relikd/p{page}.jpg';im=Image.open(src);a=np.array(im);ink=(a[:,:,0]<110)&(a[:,:,1]<110)&(a[:,:,2]<110);projection=ink[:,770:1810].sum(1);ys=np.flatnonzero((projection>35)&(np.arange(len(projection))>=650)&(np.arange(len(projection))<(2320 if page==2 else 2890)));groups=[]
 for y in ys:
  if not groups or y-groups[-1][-1]>25:groups.append([int(y)])
  else:groups[-1].append(int(y))
 bands=[[g[0]-8,g[-1]+9] for g in groups];assert len(bands)==n,(page,bands)
 for begin in range(0,n-1,4):
  items=[]
  for i in range(begin,min(begin+4,n-1)):
   firstx=760 if page==0 and i+1 in [1,2] else 590;boxes=[[1620,bands[i][0],1830,bands[i][1]],[firstx,bands[i+1][0],firstx+235,bands[i+1][1]]];row=Image.new('RGB',(510,180),'white');draw=ImageDraw.Draw(row);draw.text((5,0),f'Page {page}: line {i} END -> line {i+1} START',fill='black');row.paste(im.crop(tuple(boxes[0])),(0,24));row.paste(im.crop(tuple(boxes[1])),(255,24));items.append(row);records.append(dict(page=page,previous_line=i,next_line=i+1,boxes=boxes,source=str(src.relative_to(R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),sheet=f'p{page}-joins-{begin:02}.png'))
  sheet=Image.new('RGB',(510,180*len(items)),'white')
  for j,row in enumerate(items):sheet.paste(row,(0,j*180))
  sheet.save(out/f'p{page}-joins-{begin:02}.png')
(out/'manifest.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(dict(joins=len(records),pages=[0,1,2],files=sorted(p.name for p in out.glob('*.png')))))
