from PIL import Image
import numpy as np,json,pathlib,gzip,datetime
R=pathlib.Path(__file__).parent;M=json.load(open(R/'F01-maps.json'));rng=np.random.default_rng(2026091714);D=json.load(open('audit/parallel-01/inputs/dataset.json'));p=next(p for p in D['pages'] if p['original_page']==1);a=np.asarray(Image.open('liber-primus/data/relikd/p1.jpg').convert('L'));samples=[[] for _ in range(29)];rows=[]
for j,l in enumerate(p['lines']):
 y0=650+j*188;y1=y0+150;b=a[y0:y1,580:1800]<90;cols=np.flatnonzero(b.any(0));chunks=np.split(cols,np.where(np.diff(cols)>1)[0]+1);cc=[]
 for c in chunks:
  ys=np.flatnonzero(b[:,c].any(1));h=int(ys[-1]-ys[0]+1);cc.append({'x':int(c[0]+580),'width':len(c),'height':h})
 tall=[v for v in cc if v['height']>75];accepted=len(tall)==len(l['indices']);rows.append({'line':j,'crop':[580,y0,1800,y1],'components':cc,'runes':l['indices'],'accepted':accepted})
 if accepted:
  for rune,c in zip(l['indices'],tall):samples[rune].append(c['width'])
assert all(samples),[i for i,s in enumerate(samples) if not s]
w=np.array([np.median(s)+5 for s in samples]);hist=np.zeros(29);start=np.zeros(29);lengths=[]
for m in M:
 x=np.array(m['indices']);b=np.array(m['labels'][2]);b[0]=0;hist+=np.bincount(x,minlength=29);start+=np.bincount(x[b==1],minlength=29)
freq=hist/hist.sum();biased=freq*w;biased/=biased.sum()
def G(s,p):
 e=p*s.sum();ok=s>0;return float(2*np.sum(s[ok]*np.log(s[ok]/e[ok])))
def sim(width):
 counts=np.zeros(29);maps=[]
 for m in M:
  x=m['indices'];ends=m['labels'][1];used=float(rng.uniform(0,1180));ss=[]
  for i,r in enumerate(x):
   adv=width[r]
   if used+adv>1180:
    used=0
    if i>0:ss.append(i);counts[r]+=1
   used+=adv+14*ends[i]
  maps.append(ss)
 return counts,maps
raw=[];rawmaps=[];equal=[]
for rep in range(1000):
 if rep%100==0:
  assert not (R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
 s,mm=sim(w);raw.append(s);rawmaps.append(mm)
for rep in range(200):s,mm=sim(np.full(29,w.mean()));equal.append(s)
raw=np.array(raw);equal=np.array(equal);g0=G(start,freq);g1=G(start,biased);null0=np.array([G(s,freq) for s in raw]);null1=np.array([G(s,biased) for s in raw]);eq0=np.array([G(s,freq) for s in equal]);enrich=start/(freq*start.sum());result={'widths':w.tolist(),'samples':samples,'accepted_rows':[r['line'] for r in rows if r['accepted']],'start_count':int(start.sum()),'source_counts':hist.tolist(),'start_counts':start.tolist(),'independence_G':g0,'width_corrected_G':g1,'width_enrichment_correlation':float(np.corrcoef(w,enrich)[0,1]),'observed_start_mean_width':float(start@w/start.sum()),'all_mean_width':float(hist@w/hist.sum()),'sim_G_quantiles':np.quantile(null0,[.025,.5,.975]).tolist(),'sim_width_corrected_G_quantiles':np.quantile(null1,[.025,.5,.975]).tolist(),'tail_independence_G':float((1+(null0>=g0).sum())/1001),'tail_corrected_G':float((1+(null1>=g1).sum())/1001),'sim_start_count_range':[int(raw.sum(1).min()),int(raw.sum(1).max())],'equal_width_G_quantiles':np.quantile(eq0,[.025,.5,.975]).tolist(),'counts':{'greedy_layouts':1000,'equal_width_controls':200},'seed':2026091714}
with gzip.open(R/'F04-evidence.json.gz','wt') as f:json.dump({'rows':rows,'sim_counts':raw.tolist(),'sim_start_maps':rawmaps,'equal_width_counts':equal.tolist(),'sim_independence_G':null0.tolist(),'sim_corrected_G':null1.tolist(),'equal_G':eq0.tolist()},f)
(R/'F04-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
