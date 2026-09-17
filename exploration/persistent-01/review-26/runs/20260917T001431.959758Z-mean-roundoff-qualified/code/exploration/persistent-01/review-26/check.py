from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image
R=Path(__file__).parent;P=R.parent/'worker-r/R06';source=R.parent/'worker-p/P16/input.bin';pin='3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290';assert hashlib.sha256(source.read_bytes()).hexdigest()==pin
(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in [P.parent/'R06.py',P.parent/'R06-card.md',P.parent/'R06-REPORT.md',source]+sorted(P.glob('*')):
 if not p.is_file():continue
 b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 if p.suffix in ('.json','.md','.py','.bin'):(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
def bitmap(b):return [[(b[y*8+x//8]>>(7-x%8))&1 for x in range(64)] for y in range(32)]
mask=sum(1<<(55-8*j) for j in range(7))
def statistic(b):
 rows=[int.from_bytes(b[i:i+8],'big') for i in range(0,256,8)]
 h=sum(7-((v^(v>>1))&mask).bit_count() for v in rows)
 v=sum(64-(a^b).bit_count() for a,b in zip(rows,rows[1:]));return h,v,62*h+7*v
# Independent coordinate-predicate plants (not the worker's array-slice renderer).
glyphs=['10000/10000/10000/10000/10000/10000/11111','11110/10001/10001/11110/10000/10000/10000']
def glyph(x,y):
 for k,text in enumerate(glyphs):
  a=x-(13+19*k);b=y-5
  if 0<=a<15 and 0<=b<21:return int(text.split('/')[b//3][a//3])
 return 0
predicates={'horizontal_rows':lambda x,y:y in [6,7,16,17,26,27],'vertical_bars':lambda x,y:13<=x<=15 or 45<=x<=47,'filled_rectangle':lambda x,y:16<=x<=47 and 8<=y<=23,'diamond_outline':lambda x,y:abs(x-32)+abs(y-16)==12,'LP_glyphs':glyph,'box_connector':lambda x,y:(10<=x<=53 and y in [6,16,25]) or (6<=y<=25 and x in [10,53]),'blank':lambda x,y:False,'single_pixel':lambda x,y:(x,y)==(31,15),'checkerboard':lambda x,y:(x+y)%2}
points=set(map(int,np.random.default_rng(476100).choice(2048,8,replace=False)));predicates['eight_points']=lambda x,y:y*64+x in points
order=['horizontal_rows','vertical_bars','filled_rectangle','diamond_outline','LP_glyphs','box_connector','blank','single_pixel','eight_points','checkerboard']
rows=[];total=permutations=0
for f in sorted(P.glob('*.npz')):
 name=f.stem;d=np.load(f);b=d['input_bytes'].tobytes();meta=json.loads(f.with_suffix('.json').read_text());assert len(b)==256 and b==(P/(name+'.bin')).read_bytes();assert hashlib.sha256(b).hexdigest()==meta['input_sha256'];bits=bitmap(b);assert np.array_equal(bits,d['bits']);expected=None
 if name=='actual':assert b==source.read_bytes();seed=478000;n=9999
 elif name.startswith('ordinary'):
  ix=int(name.split('-')[1]);density=[.05,.5,.95][ix//10];rng=np.random.default_rng(476200+ix);expected=(rng.random(2048)<density).reshape(32,64);seed=477000+ix;n=999
 else:expected=[[int(predicates[name](x,y)) for x in range(64)] for y in range(32)];seed=476000+order.index(name);n=999
 if expected is not None:assert np.array_equal(bits,expected)
 native=np.asarray(Image.open(P/(name+'-native.png')).convert('L'));assert np.array_equal(native,255-255*np.array(bits,dtype=np.uint8));assert len(d['permutations'])==n and meta['seed']==seed and meta['nulls']==n
 h,v,t=statistic(b);assert (h,v)==(meta['horizontal_agree'],meta['vertical_agree']);assert meta['horizontal_total']==224 and meta['vertical_total']==1984 and abs(t/27776-meta['statistic'])<2e-16;assert meta['ones']==sum(sum(row) for row in bits)
 rng=np.random.default_rng(seed);upper=0;floatupper=0;counts=[]
 for j,perm in enumerate(d['permutations']):
  assert np.array_equal(perm,rng.permutation(256)) and sorted(map(int,perm))==list(range(256));ordered=bytes(b[int(i)] for i in perm);hh,vv,tt=statistic(ordered);assert (hh,vv)==tuple(d['null_counts'][j]);assert abs(tt/27776-d['null_scores'][j])<2e-16;upper+=tt>=t;floatupper+=d['null_scores'][j]>=meta['statistic'];counts.append(tt)
 assert upper==floatupper and (upper+1)/(n+1)==meta['p_upper'];assert abs(np.mean(counts)/27776-meta['null_mean'])<1e-14
 rows.append({'name':name,'seed':seed,'nulls':n,'H':h,'V':v,'integer_statistic':t,'upper_count':upper,'tail':meta['p_upper']});total+=n+1;permutations+=n
actual=np.asarray(Image.open(P/'actual-native.png').convert('L'));view=np.asarray(Image.open(P/'actual-view.png').convert('L'));assert view.shape==(512,1024)
assert np.array_equal(view,actual[np.arange(512)//16][:,np.arange(1024)//16])
maprows=json.loads((P/'actual-pixel-map.json').read_text());b=source.read_bytes();assert len(maprows)==2048
for i,m in enumerate(maprows):
 y,x=divmod(i,64);assert m=={'x':x,'y':y,'byte_index':8*y+x//8,'msb_first_bit_index':x%8,'bit_value':(b[8*y+x//8]>>(7-x%8))&1}
summary=json.loads((P/'controls-summary.json').read_text());by={r['name']:r for r in rows};assert summary['viable']==(by['horizontal_rows']['tail']<=.01 and by['filled_rectangle']['tail']<=.01);assert summary['ordinary_at_01']==sum(r['tail']<=.01 for r in rows if r['name'].startswith('ordinary'))
out={'status':'PASS','panels':total,'permutations':permutations,'input_panels':len(rows),'pixel_map_entries':len(maprows),'rows':rows,'integer_statistic':'62*H+7*V; S=T/27776','rational_and_float_tail_counts_agree':True};(R/'result.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k!='rows'});print(by['actual'])
