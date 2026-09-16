from PIL import Image,ImageDraw
from scipy.ndimage import label,find_objects
import pathlib,json,numpy as np,io
O=pathlib.Path(__file__).parent;ROOT=O.parents[2]
def groups(im,roi,threshold):
 x0,y0,x1,y1=roi;a=np.array(im.convert('RGB'))[y0:y1,x0:x1];mask=np.min(a,axis=2)<threshold;lab,n=label(mask);items=[]
 for i,s in enumerate(find_objects(lab),1):
  yy,xx=np.where(lab[s]==i);h=s[0].stop-s[0].start;w=s[1].stop-s[1].start
  if not(4<=w<=22 and 4<=h<=22 and len(xx)>=16):continue
  items.append({'bounds':[s[1].start+x0,s[0].start+y0,s[1].stop+x0,s[0].stop+y0],'center':[float(xx.mean()+s[1].start+x0),float(yy.mean()+s[0].start+y0)],'area':len(xx)})
 todo=set(range(len(items)));clusters=[]
 while todo:
  stack=[todo.pop()];ids=[]
  while stack:
   i=stack.pop();ids.append(i);near=[j for j in todo if sum((items[i]['center'][k]-items[j]['center'][k])**2 for k in [0,1])<=26**2]
   for j in near:todo.remove(j);stack.append(j)
  components=[items[i]for i in ids];centers=np.array([c['center']for c in components]);clusters.append({'count':len(ids),'center':centers.mean(axis=0).tolist(),'components':components})
 return sorted(clusters,key=lambda g:(g['center'][1],g['center'][0]))
def jpeg(im):
 b=io.BytesIO();im.save(b,format='JPEG',quality=90);b.seek(0);return Image.open(b)
controls=[]
for count in [4,13]:
 im=Image.new('RGB',(160,160),'white');d=ImageDraw.Draw(im)
 pts=[(70,20+15*i)for i in [0,2,4,6,8]]+[(x,20+15*i)for i in [1,3,5,7]for x in [55,85]] if count==13 else [(70,40),(55,55),(85,55),(70,70)]
 for x,y in pts:d.rectangle((x,y,x+8,y+8),fill='black')
 for render,source in [('raw',im),('jpeg90',jpeg(im))]:
  for t in [90,130,170]:
   r=groups(source,(0,0,160,160),t);assert len(r)==1 and r[0]['count']==count;controls.append([count,render,t,r[0]['count']])
rune=Image.new('RGB',(160,160),'white');draw=ImageDraw.Draw(rune);draw.line([(30,140),(30,20),(110,80),(30,80)],fill='black',width=8);assert groups(rune,(0,0,160,160),130)==[]
result={'controls':controls,'connected_rune_control':True,'pages':{}}
for page,roi in [(3,(580,640,1800,3010)),(7,(580,640,1800,2600)),(17,(580,640,1800,2900))]:
 im=Image.open(ROOT/f'liber-primus/data/relikd/p{page}.jpg');rec={}
 for render,source in [('original',im),('jpeg90',jpeg(im))]:
  for threshold in [90,130,170]:rec[f'{render}-{threshold}']=groups(source,roi,threshold)
 result['pages'][page]=rec
(O/'g06-results.json').write_text(json.dumps(result,indent=2)+'\n')
from collections import Counter
print(json.dumps({p:{k:dict(Counter(g['count']for g in v))for k,v in rec.items()}for p,rec in result['pages'].items()},indent=2))
