import pathlib,json,numpy as np,gzip,re,hashlib,collections,datetime
R=pathlib.Path(__file__).parent;M=json.load(open(R/'F06-maps.json'));rng=np.random.default_rng(2026091719);ps=[(np.array(m['indices']),np.array([w['end']-w['start'] for w in m['words']])) for m in M]
def units(ps):
 out=[]
 for x,ls in ps:
  starts=np.r_[0,np.cumsum(ls)[:-1]];out.append([tuple(int(r) for r in x[i:i+l]) for i,l in zip(starts,ls)])
 return out
def stat(ps):
 c=collections.Counter(w for page in units(ps) for w in page if len(w)>=2);return [sum(n*(n-1)//2 for n in c.values()),max(c.values(),default=0)]
def trial(ps,n):
 real=stat(ps);null=[];offsets=[]
 for rep in range(n):
  if rep%100==0:assert not (R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
  off=[int(rng.integers(len(x))) for x,l in ps];offsets.append(off);null.append(stat([(np.roll(x,-o),l) for (x,l),o in zip(ps,off)]))
 null=np.array(null);tails=(1+(null>=real).sum(0))/(n+1);return {'real':real,'null':null.tolist(),'offsets':offsets,'tails':tails.tolist(),'bonferroni2':np.minimum(1,2*tails).tolist()}
real=trial(ps,999);A='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';pool=collections.defaultdict(list);sources=[]
for f in sorted(pathlib.Path('audit/parallel-01/reference/sources').glob('solved_*.txt')):
 raw=f.read_text();matches=re.findall('['+A+']+',raw)
 # Merge whitespace-only rune-run gaps exactly, using original raw coordinates.
 chars=[(i,A.index(c)) for i,c in enumerate(raw) if c in A];start=0;words=[]
 for j,((i,r),(ii,s)) in enumerate(zip(chars,chars[1:])):
  gap=raw[i+1:ii]
  if gap and not gap.isspace():words.append(tuple(r for i,r in chars[start:j+1]));start=j+1
 if chars:words.append(tuple(r for i,r in chars[start:]))
 for w in words:pool[len(w)].append(w)
 sources.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'units':[list(w) for w in words]})
def randomword(n):
 w=[int(rng.integers(29))]
 for i in range(1,n):
  z=int(rng.integers(28));w.append(z+(z>=w[-1]))
 return tuple(w)
controls=[]
for rep in range(20):
 codebook={};used=collections.defaultdict(set)
 for n,ww in pool.items():
  for w in sorted(set(ww)):
   for attempt in range(10000):
    code=randomword(n)
    if code not in used[n]:break
   else:raise RuntimeError('codebook bounded collision failure')
   codebook[w]=code;used[n].add(code)
 cp=[];chosen=[];missing=0
 for x,ls in ps:
  out=[];sel=[]
  for n in ls:
   n=int(n)
   if n in pool:
    w=pool[n][int(rng.integers(len(pool[n])))];out.extend(codebook[w]);sel.append(list(w))
   else:out.extend(randomword(n));sel.append(None);missing+=1
  cp.append((np.array(out),ls));chosen.append(sel)
 t=trial(cp,100) if rep<4 else {'real':stat(cp)};t.update(rep=rep,codebook=[{'source':list(k),'cipher':list(v)} for k,v in codebook.items()],streams=[x.tolist() for x,l in cp],chosen=chosen,absent_length_units=missing);controls.append(t)
classes=collections.defaultdict(list)
for m,page in zip(M,units(ps)):
 for i,w in enumerate(page):classes[w].append({'page':m['page'],'unit':i,'span':[m['words'][i]['start'],m['words'][i]['end']]})
repeat=[{'unit':list(k),'occurrences':v} for k,v in classes.items() if len(v)>1];res={'real':{k:v for k,v in real.items() if k not in ['null','offsets']},'controls':[{'rep':t['rep'],'real':t['real'],'bonferroni2':t.get('bonferroni2'),'absent_length_units':t['absent_length_units']} for t in controls],'control_ranges':[[min(t['real'][k] for t in controls),max(t['real'][k] for t in controls)] for k in [0,1]],'counts':{'real':1,'real_null':999,'source_model_controls':20,'control_null':400},'seed':2026091719}
with gzip.open(R/'F09-evidence.json.gz','wt') as f:json.dump({'sources':sources,'real':real,'repeat_classes':repeat,'controls':controls},f)
(R/'F09-result.json').write_text(json.dumps(res,indent=2));print(json.dumps(res,indent=2))
