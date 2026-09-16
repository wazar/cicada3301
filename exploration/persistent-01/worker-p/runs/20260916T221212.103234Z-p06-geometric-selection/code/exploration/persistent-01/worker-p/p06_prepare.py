import json,pathlib,hashlib,random
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
D=pathlib.Path('exploration/persistent-01/worker-p/P06');assert not D.parents[1].joinpath('STOP').exists();data=json.load(open('audit/parallel-01/inputs/dataset.json'));pages={p['original_page']:p for p in data['pages'] if p['original_page'] in [56,57]};rois={56:[(770,650,1800,810),(770,840,1800,1000),(770,1030,1800,1190),(590,1870,1800,2030),(590,2050,1800,2220)],57:[(885,900,1800,1050),(885,1080,1800,1240),(885,1330,1800,1490),(885,1510,1800,1680),(590,1700,1800,1870)]};records=[];audit=[];inputs=[]
for page in [56,57]:
 p=pathlib.Path(f'audit/parallel-01/inputs/sources/{page}.jpg');im=Image.open(p).convert('RGB');a=np.array(im);gray=np.min(a,axis=2);inputs.append(dict(page=page,path=str(p),size=im.size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()));draw=ImageDraw.Draw(im)
 for row,box in enumerate(rois[page]):
  x0,y0,x1,y1=box;lab,n=ndimage.label(gray[y0:y1,x0:x1]<128);good=[]
  for sl in ndimage.find_objects(lab):
   if sl is None:continue
   yy,xx=sl;w=xx.stop-xx.start;h=yy.stop-yy.start
   if 80<=h<=140 and w>=5:good.append([x0+xx.start,y0+yy.start,x0+xx.stop,y0+yy.stop])
  good.sort();expected=len(pages[page]['lines'][row]['indices'])-(row==0);audit.append(dict(page=page,row=row,roi=box,components=len(good),expected=expected));
  for j,b in enumerate(good):
   x,y,xx,yy=b;pix=a[y:yy,x:xx];ink=gray[y:yy,x:xx]<128;red=float(np.mean((pix[:,:,0].astype(float)-pix[:,:,1])[ink]));black=red<30;idx=pages[page]['lines'][row]['rune_start']+j+(row==0);records.append(dict(page=page,row=row,row_component=j,box=b,black=black,red_dominance=red,page_rune_index=idx,source_char_position=pages[page]['source_char_positions'][idx] if idx<len(pages[page]['indices']) else None));draw.rectangle(b,outline='blue' if black else 'green',width=2)
 im.save(D/f'{page}-segmentation.png')
(D/'geometry-audit.json').write_text(json.dumps(dict(inputs=inputs,rows=audit,records=records),indent=2));print(json.dumps(dict(inputs=inputs,rows=audit,eligible_black=sum(r['black'] for r in records)),indent=2));assert all(r['components']==r['expected'] for r in audit),'STOP: geometric row-count mismatch before sample selection'
eligible=[r for r in records if r['black']];chosen=random.Random(130106).sample(eligible,100);(D/'selection.json').write_text(json.dumps(chosen,indent=2));labels=[pages[r['page']]['indices'][r['page_rune_index']] for r in chosen];(D/'hidden-labels.json').write_text(json.dumps(labels));ims={page:Image.open(f'audit/parallel-01/inputs/sources/{page}.jpg').convert('RGB') for page in [56,57]}
for sheet in range(5):
 canvas=Image.new('RGB',(1000,960),'white');dr=ImageDraw.Draw(canvas)
 for cell in range(20):
  i=sheet*20+cell;r=chosen[i];x,y,xx,yy=r['box'];crop=ims[r['page']].crop((x-4,y-6,xx+4,yy+6));ratio=min(150/crop.width,190/crop.height);crop=crop.resize((round(crop.width*ratio),round(crop.height*ratio)),Image.Resampling.NEAREST);cx=cell%5*200;cy=cell//5*240;canvas.paste(crop,(cx+(200-crop.width)//2,cy+30));dr.text((cx+8,cy+8),str(i+1),fill='black');dr.rectangle((cx,cy,cx+199,cy+239),outline='#cccccc')
 canvas.save(D/f'sheet-{sheet+1}.png')
print('sample100saved; labels hidden, not printed')
