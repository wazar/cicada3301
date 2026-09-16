import pathlib,json,numpy as np,gzip,re,hashlib,datetime
R=pathlib.Path(__file__).parent;M=json.load(open(R/'F06-maps.json'));A='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';rng=np.random.default_rng(2026091718);sources=[]
for f in sorted(pathlib.Path('audit/parallel-01/reference/sources').glob('solved_*.txt')):
 raw=f.read_text();chars=[(i,A.index(c)) for i,c in enumerate(raw) if c in A];words=[];start=0
 for j,((i,r),(ii,s)) in enumerate(zip(chars,chars[1:])):
  gap=raw[i+1:ii]
  if gap and not gap.isspace():words.append([r for i,r in chars[start:j+1]]);start=j+1
 if chars:words.append([r for i,r in chars[start:]])
 sources.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'raw':raw,'words':words,'rune_raw_positions':[i for i,r in chars]})
L=[[len(w) for w in s['words']] for s in sources];idx=[{} for _ in range(9)]
for k in range(1,9):
 for si,ls in enumerate(L):
  for j in range(len(ls)-k+1):idx[k].setdefault(tuple(ls[j:j+k]),[]).append((si,j))
probes=0
def scan(seqs,retain=False):
 global probes
 best=0;hits=[]
 for pi,x in enumerate(seqs):
  found=False
  for i in range(len(x)-7):
   probes+=1
   for si,j in idx[8].get(tuple(x[i:i+8]),[]):
    found=True;n=8
    while i+n<len(x) and j+n<len(L[si]) and x[i+n]==L[si][j+n]:n+=1
    best=max(best,n)
    if retain:hits.append({'page_index':pi,'page_start_unit':i,'source':si,'source_start_unit':j,'unit_count':n})
  if best<8:
   for k in range(min(7,len(x)),best,-1):
    yes=False
    for i in range(len(x)-k+1):
     probes+=1
     if tuple(x[i:i+k]) in idx[k]:yes=True;break
    if yes:best=k;break
 return best,hits
seqs=[[w['end']-w['start'] for w in m['words']] for m in M];real,hits=scan(seqs,True);null=[];perm=[]
for rep in range(999):
 if rep%100==0:assert not (R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
 pp=[rng.permutation(len(x)).tolist() for x in seqs];perm.append(pp);null.append(scan([[x[i] for i in p] for x,p in zip(seqs,pp)])[0])
def transforms(c,p):
 c=np.array(c);p=np.array(p);aff=[];tests=0
 for a in range(1,29):
  for b in range(29):
   tests+=1
   if np.array_equal((a*p+b)%29,c):aff.append([a,b])
 mapping={};bij=True
 for a,b in zip(p,c):
  if int(a) in mapping and mapping[int(a)]!=int(b):bij=False
  mapping[int(a)]=int(b)
 bij=bij and len(set(mapping.values()))==len(mapping)
 dif=(c-p)%29;periods=[]
 for k in range(1,17):
  if len(dif)>=2*k:
   tests+=1
   if np.all(dif==np.resize(dif[:k],len(dif))):periods.append({'period':k,'key':dif[:k].tolist()})
 return {'affine':aff,'monoalphabetic_consistent_bijection':bij,'mapping':mapping if bij else None,'periodic':periods,'transform_checks':tests+1}
for h in hits:
 m=M[h['page_index']];i=h['page_start_unit'];n=h['unit_count'];lo=m['words'][i]['start'];hi=m['words'][i+n-1]['end'];p=[r for w in sources[h['source']]['words'][h['source_start_unit']:h['source_start_unit']+n] for r in w];c=m['indices'][lo:hi];h.update(page=m['page'],rune_span=[lo,hi],cipher=c,source_plain=p,transforms=transforms(c,p))
controls=[]
for si,s in enumerate(sources):
 p=[r for w in s['words'] for r in w];c=[(2*r+3)%29 for r in p];tr=transforms(c,p);assert [2,3] in tr['affine'];best,hh=scan([L[si]],True);assert best==len(L[si]);ns=[];pp=[]
 for rep in range(99):
  permu=rng.permutation(len(L[si])).tolist();pp.append(permu);ns.append(scan([[L[si][i] for i in permu]])[0])
 controls.append({'source':si,'plain':p,'cipher':c,'max_units':best,'null':ns,'permutations':pp,'tail':(1+sum(v>=best for v in ns))/100,'transforms':tr})
result={'source_count':len(sources),'source_units':[len(l) for l in L],'max_exact_units':real,'raw_tail':(1+sum(v>=real for v in null))/1000,'real_matches_ge8':hits,'controls':[{k:v for k,v in t.items() if k not in ['plain','cipher','null','permutations']} for t in controls],'counts':{'real':1,'real_null':999,'controls':9,'control_null':891,'dictionary_probes':probes,'retained_transform_checks':sum(h['transforms']['transform_checks'] for h in hits)},'seed':2026091718}
with gzip.open(R/'F08-evidence.json.gz','wt') as f:json.dump({'sources':sources,'null':null,'permutations':perm,'controls':controls,'real_sequences':seqs},f)
(R/'F08-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
