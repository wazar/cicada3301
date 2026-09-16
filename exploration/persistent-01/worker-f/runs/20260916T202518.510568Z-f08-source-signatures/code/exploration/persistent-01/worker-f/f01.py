import pathlib,json,re,numpy as np,gzip,hashlib,datetime,time
R=pathlib.Path(__file__).parent; root=R.parents[2]; rng=np.random.default_rng(2026091711)
def guard():
 assert not (R.parent/'STOP').exists(),'STOP'
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc),'deadline'
D=json.load(open('audit/parallel-01/inputs/dataset.json')); reserved={4,9,14,19,24,29,34,39,44,54}; ps=[]; maps=[]
for p in D['pages']:
 if p['original_page'] in reserved or p['original_page']>55:continue
 x=np.array(p['indices']);labels=np.zeros((4,len(x)),dtype=np.int64);words=[]
 for l in p['lines']:
  if not l['indices']:continue
  labels[2,l['rune_start']]=1;labels[3,l['rune_end']-1]=1;cursor=l['rune_start']
  for m in re.finditer('['+D['alphabet']+']+',l['raw']):
   n=len(m[0]);labels[0,cursor]=1;labels[1,cursor+n-1]=1
   words.append({'start':cursor,'end':cursor+n,'source_line':l['source_line'],'raw_start':m.start(),'raw_end':m.end()});cursor+=n
  assert cursor==l['rune_end']
 ps.append((x,labels)); maps.append({'page':p['original_page'],'indices':x.tolist(),'labels':labels.tolist(),'source_char_positions':p['source_char_positions'],'words':words})
assert len(ps)==45
(R/'F01-maps.json').write_text(json.dumps(maps))
def g(a):
 a=a.reshape(2,-1).astype(float);n=a.sum();e=a.sum(1)[:,None]*a.sum(0)[None,:]/max(n,1);m=a>0
 return float(2*np.sum(a[m]*np.log(a[m]/e[m])))
def stats(ps,offsets=None,trim=False):
 tabs=[np.zeros(58),np.zeros(58),np.zeros(1682),np.zeros(4)]*2
 tabs=[a.copy() for a in tabs]
 for j,(x,l) in enumerate(ps):
  if offsets is not None:l=np.roll(l,int(offsets[j]),axis=1)
  if trim:x=x[1:-1];l=l[:,1:-1]
  same=x[:-1]==x[1:];pair=x[:-1]*29+x[1:]
  for k in range(2):
   tabs[k*4]+=np.bincount(l[2*k]*29+x,minlength=58)
   tabs[k*4+1]+=np.bincount(l[2*k+1]*29+x,minlength=58)
   b=l[2*k,1:];tabs[k*4+2]+=np.bincount((b*841+pair)[~same],minlength=1682)
   tabs[k*4+3]+=np.bincount(b*2+same,minlength=4)
 return np.array([g(a) for a in tabs])
def trial(ps,n,trim=False):
 real=stats(ps,trim=trim);null=[];off=[]
 for i in range(n):
  if i%50==0:guard()
  o=[int(rng.integers(len(x))) for x,l in ps];off.append(o);null.append(stats(ps,o,trim))
 null=np.array(null);tails=(1+(null>=real).sum(0))/(n+1)
 return {'real':real.tolist(),'null':null.tolist(),'offsets':off,'tails':tails.tolist(),'bonferroni8':np.minimum(1,8*tails).tolist()}
def encode(typ):
 out=[]
 for original,l in ps:
  x=[]
  for i in range(len(original)):
   b=bool(l[0,i]);prev=x[-1] if x else None
   if prev is not None and typ=='successor' and b and rng.random()<.65:v=(prev+1)%29
   else:
    rp=(.15 if b else .001) if typ=='repeat' else .0066
    if prev is not None and rng.random()<rp:v=prev
    else:
     v=int(rng.integers(7 if typ=='alphabet' and b and rng.random()<.7 else 29))
     while v==prev:v=int(rng.integers(29))
   x.append(v)
  out.append((np.array(x),l))
 return out
controls=[]
for typ in ['baseline','alphabet','successor','repeat']:
 for rep in range(8):
  cp=encode(typ);t=trial(cp,199);t.update(type=typ,rep=rep,streams=[x.tolist() for x,l in cp],repeats=sum(int(np.sum(x[:-1]==x[1:])) for x,l in cp));controls.append(t)
 print('control',typ,flush=True)
real=trial(ps,999);trim=trial(ps,999,True)
def strip(t):return {k:v for k,v in t.items() if k not in ['null','offsets','streams']}
result={'names':[k+'_'+s for k in ['word','line'] for s in ['start_rune','end_rune','nonself_pair','doublet']], 'pages':[m['page'] for m in maps],'runes':sum(len(x) for x,l in ps),'word_count':sum(len(m['words']) for m in maps),'real':strip(real),'trim':strip(trim),'controls':[strip(t) for t in controls], 'counts':{'real':2,'real_null':1998,'controls':32,'control_null':6368},'seed':2026091711}
result['control_detection']={typ:sum(min(t['bonferroni8'])<=.05 for t in controls if t['type']==typ) for typ in ['baseline','alphabet','successor','repeat']}
with gzip.open(R/'F01-evidence.json.gz','wt') as f:json.dump({'real':real,'trim':trim,'controls':controls},f)
(R/'F01-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
