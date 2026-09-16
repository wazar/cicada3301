import json,gzip,pathlib,numpy as np
from PIL import Image
R=pathlib.Path('exploration/persistent-01/review-02');F=R.parent/'worker-f';M=json.load(open(F/'F01-maps.json'));J=json.load(open(F/'F04-result.json'));E=json.load(gzip.open(F/'F04-evidence.json.gz','rt'));a=np.array(Image.open('liber-primus/data/relikd/p1.jpg').convert('L'));p=next(m for m in M if m['page']==1);samples=[[] for _ in range(29)];rows=[]
for row in E['rows']:
 x0,y0,x1,y1=row['crop'];mask=a[y0:y1,x0:x1]<90;cc=[];start=None
 for x in range(mask.shape[1]+1):
  on=x<mask.shape[1] and mask[:,x].any()
  if on and start is None:start=x
  if not on and start is not None:
   yy=np.where(mask[:,start:x].any(1))[0];cc.append({'x':start+x0,'width':x-start,'height':int(yy[-1]-yy[0]+1)});start=None
 assert cc==row['components'];idx=[i for w in p['words'] if w['source_line']==row['line'] for i in range(w['start'],w['end'])];runes=[p['indices'][i] for i in idx];assert runes==row['runes'];tall=[c for c in cc if c['height']>75];accepted=len(tall)==len(runes);assert accepted==row['accepted']
 if accepted:
  for r,c in zip(runes,tall):samples[r].append(c['width'])
 rows.append({'row':row['line'],'runes':len(runes),'tall_components':len(tall),'accepted':accepted})
w=np.array([np.median(s)+5 for s in samples]);assert samples==J['samples'];assert np.array_equal(w,J['widths']);rng=np.random.default_rng(2026091714)
def simulate(width):
 counts=np.zeros(29);maps=[]
 for m in M:
  remain=1180-float(rng.uniform(0,1180));starts=[]
  for i,r in enumerate(m['indices']):
   if width[r]>remain:
    remain=1180
    if i:counts[r]+=1;starts.append(i)
   remain-=width[r]+14*m['labels'][1][i]
  maps.append(starts)
 return counts,maps
for j in range(1000):
 c,mm=simulate(w);assert c.tolist()==E['sim_counts'][j];assert mm==E['sim_start_maps'][j]
for j in range(200):
 c,mm=simulate(np.ones(29)*w.mean());assert c.tolist()==E['equal_width_counts'][j]
h=np.bincount([r for m in M for r in m['indices']],minlength=29);s=np.bincount([r for m in M for i,r in enumerate(m['indices']) if i and m['labels'][2][i]],minlength=29);freq=h/h.sum();biased=freq*w;biased/=biased.sum()
def g(c,p):return float(2*sum(v*np.log(v/(sum(c)*p[i])) for i,v in enumerate(c) if v))
raw=np.array([g(c,freq) for c in E['sim_counts']]);corrected=np.array([g(c,biased) for c in E['sim_counts']]);assert np.allclose(raw,E['sim_independence_G']);assert np.allclose(corrected,E['sim_corrected_G']);out={'source_image':'liber-primus/data/relikd/p1.jpg','image_shape':list(a.shape),'rows':rows,'widths_reproduced':True,'all_1200_simulations_reproduced':True,'all_1000_start_maps_reproduced':True,'raw_tail':(1+sum(raw>=g(s,freq)))/1001,'corrected_tail':(1+sum(corrected>=g(s,biased)))/1001,'caveats':['component-count matching does not certify every glyph identity','ink width plus5 is approximate advance','fixed1180 and separator14 not calibrated to all pages','simulation start count466..484 differs from435 actual','G here is multinomial against full-stream frequencies; F03 uses2x29 contingency after first-rune removals']};(R/'width-findings.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
