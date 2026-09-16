import pathlib,json,re,numpy as np,gzip,datetime,hashlib
from PIL import Image
R=pathlib.Path(__file__).parent;D=json.load(open('audit/parallel-01/inputs/dataset.json'));P={p['original_page']:p for p in D['pages'] if p['original_page'] in [10,36,37,38]};A=D['alphabet'];rng=np.random.default_rng(2026091720);joined='';coordinates=[];obs=[]
for n in [36,37,38]:
 p=P[n];raw=''.join(l['raw'] for l in p['lines']);ridx=0
 for i,c in enumerate(raw):
  coordinates.append({'page':n,'raw_joined_char':i,'rune_index':ridx if c in A else None});ridx+=int(c in A)
 joined+=raw
for n in [10,36,37,38]:
 path=pathlib.Path(f'liber-primus/data/relikd/p{n}.jpg');img=np.array(Image.open(path).convert('RGB'));mask=(img[:,:,0]>100)&(img[:,:,0]>img[:,:,1]*1.5)&(img[:,:,0]>img[:,:,2]*1.5)&(img[:,:,1]<130);ys=np.flatnonzero(mask.sum(1)>3);groups=np.split(ys,np.where(np.diff(ys)>4)[0]+1);boxes=[]
 for g in groups:
  if not len(g):continue
  yy,xx=np.where(mask[g[0]:g[-1]+1]);
  if len(xx)>20:boxes.append([int(xx.min()),int(g[0]),int(xx.max()+1),int(g[-1]+1)])
 obs.append({'page':n,'image':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'red_boxes':boxes})
digits=list(re.finditer('[1-5]',joined));assert [m[0] for m in digits]==list('12345');end=joined.index('&',digits[-1].end());regions=[]
for j,m in enumerate(digits):
 stop=digits[j+1].start() if j<4 else end;raw=joined[m.end():stop];chars=[(i,A.index(c)) for i,c in enumerate(raw) if c in A];units=[];start=0
 for k,((i,r),(ii,s)) in enumerate(zip(chars,chars[1:])):
  gap=raw[i+1:ii]
  if gap and not gap.isspace():units.append([r for i,r in chars[start:k+1]]);start=k+1
 if chars:units.append([r for i,r in chars[start:]])
 regions.append({'label':int(m[0]),'label_coordinate':coordinates[m.start()],'joined_span':[m.end(),stop],'raw':raw,'units':units,'rune_coordinates':[coordinates[m.end()+i] for i,r in chars],'rune_count':len(chars),'unit_lengths':[len(w) for w in units]})
ls=[np.array(r['unit_lengths']) for r in regions]
def stat(ls):
 d=[]
 for mode in [0,1]:
  ar=np.array([x[:4] if mode==0 else x[-4:] for x in ls]);d.append(int(sum(np.abs(ar[i]-ar[j]).sum() for i in range(5) for j in range(i+1,5))))
 return -min(d),d
def trial(ls,n):
 real,dist=stat(ls);null=[];perms=[]
 for rep in range(n):
  pp=[rng.permutation(len(x)) for x in ls];perms.append([p.tolist() for p in pp]);null.append(stat([x[p] for x,p in zip(ls,pp)])[0])
 return {'real':real,'prefix_suffix_distances':dist,'null':null,'permutations':perms,'tail':(1+sum(v>=real for v in null))/(n+1)}
real=trial(ls,999);cp=[np.r_[np.array([2,4,3,5]),rng.integers(1,10,size=len(x)-4)] for x in ls];positive=trial(cp,199);positive['unit_lengths']=[x.tolist() for x in cp];baseline=[]
for rep in range(8):
 assert not (R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
 cp=[rng.permutation(x) for x in ls];t=trial(cp,199);t['unit_lengths']=[x.tolist() for x in cp];baseline.append(t)
r10=P[10];raw10=''.join(l['raw'] for l in r10['lines']);pos7=raw10.index('7');ob7={'raw_position':pos7,'runes_before':sum(c in A for c in raw10[:pos7]),'raw_context':raw10[pos7-12:pos7+13]}
res={'regions':[{'label':r['label'],'rune_count':r['rune_count'],'unit_count':len(r['units']),'unit_lengths':r['unit_lengths'],'label_coordinate':r['label_coordinate']} for r in regions],'same_rune_counts':len({r['rune_count'] for r in regions})==1,'same_complete_length_signature':all(np.array_equal(ls[0],x) for x in ls[1:]),'template':{k:v for k,v in real.items() if k not in ['null','permutations']},'positive_control':{k:v for k,v in positive.items() if k not in ['null','permutations','unit_lengths']},'baseline_tails':[t['tail'] for t in baseline],'inline7':ob7,'image_observations':obs,'counts':{'real':1,'real_null':999,'positive_control':1,'positive_null':199,'baseline':8,'baseline_null':1592},'seed':2026091720}
with gzip.open(R/'F10-evidence.json.gz','wt') as f:json.dump({'regions':regions,'joined_raw':joined,'coordinates':coordinates,'real':real,'positive':positive,'baseline':baseline},f)
(R/'F10-result.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
