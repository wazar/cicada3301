import pathlib,json,hashlib,re,sys,gzip,random,datetime,time
R=pathlib.Path(__file__).parent; ROOT=pathlib.Path.cwd();sys.path.insert(0,str(ROOT/'liber-primus/src'))
from lp.gematria import keyword_to_indices,_TRANS_SORTED
seed=2026091721;rng=random.Random(seed)
def gate():
 assert not (R.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def encode(s,v):
 if not v:return keyword_to_indices(s)
 out=[];i=0
 while i<len(s):
  for t,k in [('ING',21),('IO',27)]+_TRANS_SORTED:
   if s.startswith(t,i):out.append(k);i+=len(t);break
  else:out.extend(keyword_to_indices(s[i]));i+=1
 return out
sources=[];snap=R/'sources';snap.mkdir(exist_ok=True)
for f in sorted((ROOT/'liber-primus/data/keys/armada18').glob('mabinogion_vol*_guest_edwards_ed.txt')):
 b=f.read_bytes();(snap/f.name).write_bytes(b);raw=b.decode();matches=list(re.finditer(r"[A-Za-z]+(?:['’][A-Za-z]+)*",raw))
 for v in range(2):
  words=[encode(re.sub("['’]",'',m.group()).upper(),v) for m in matches]
  sources.append(dict(path=str(f.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),variant=v,raw=raw,spans=[list(m.span()) for m in matches],words=words))
L=[[len(w) for w in s['words']] for s in sources];idx={}
for si,x in enumerate(L):
 for j in range(len(x)-5):idx.setdefault(tuple(x[j:j+6]),[]).append((si,j))
probes=0;extensions=0
def scan(seqs,retain=False):
 global probes,extensions
 best=0;hits=[]
 for pi,x in enumerate(seqs):
  for i in range(len(x)-5):
   probes+=1
   for si,j in idx.get(tuple(x[i:i+6]),[]):
    extensions+=1;n=6
    while i+n<len(x) and j+n<len(L[si]) and x[i+n]==L[si][j+n]:n+=1
    best=max(best,n)
    if retain and n>=8 and not(i and j and x[i-1]==L[si][j-1]):hits.append(dict(page_index=pi,page_start_unit=i,source=si,source_start_unit=j,unit_count=n))
 return best,hits
def shuffled(x):
 pp=[rng.sample(range(len(z)),len(z)) for z in x];return [[z[i] for i in p] for z,p in zip(x,pp)],pp
M=json.load(open(R.parent/'worker-f/F06-maps.json'));seqs=[[w['end']-w['start'] for w in m['words']] for m in M]
controls=[]
for si,x in enumerate(L):
 gate();j=1000;pi=next(i for i,z in enumerate(seqs) if len(z)>=50);planted=[z[:] for z in seqs];planted[pi][5:45]=x[j:j+40];best,hits=scan(planted,True)
 truth=next((h for h in hits if h['source']==si and h['page_index']==pi and h['page_start_unit']<=5 and h['source_start_unit']-h['page_start_unit']==j-5 and h['unit_count']>=40),None);assert truth
 plain=[r for w in sources[si]['words'][j:j+40] for r in w];cipher=[(2*r+3)%29 for r in plain];assert [((c-3)*15)%29 for c in cipher]==plain
 ns=[]
 for rep in range(99):ns.append(scan(shuffled(planted)[0])[0])
 controls.append(dict(source=si,truth=truth,best=best,null=ns,tail=(1+sum(a>=best for a in ns))/100,plain=plain,cipher=cipher))
gate();before=(probes,extensions);real,hits=scan(seqs,True);realcounts=[probes-before[0],extensions-before[1]];null=[];perms=[]
for rep in range(999):
 if rep%50==0:gate()
 sh,pp=shuffled(seqs);perms.append(pp);null.append(scan(sh)[0])
tail=(1+sum(n>=real for n in null))/1000
for h in hits:
 s=sources[h['source']];j=h['source_start_unit'];n=h['unit_count'];a=s['spans'][j][0];b=s['spans'][j+n-1][1];h.update(page=M[h['page_index']]['page'],source_char_span=[a,b],raw_source_span=s['raw'][a:b],admitted=n>=12 and tail<=.01)
result=dict(source_count=2,variants=2,source_units=[len(x) for x in L],source_hashes=[{k:s[k] for k in ['path','variant','sha256']} for s in sources],max_exact_units=real,tail=tail,hits=hits,admitted=sum(h['admitted'] for h in hits),real_dictionary_probes=realcounts[0],real_extensions=realcounts[1],total_probes=probes,total_extensions=extensions,real_page_queries=len(seqs),real_null_searches=999,control_searches=4,control_null_searches=396,controls=[{k:v for k,v in c.items() if k not in ['plain','cipher','null']} for c in controls],seed=seed)
with gzip.open(R/'H01-evidence.json.gz','wt') as f:json.dump(dict(sources=sources,controls=controls,null=null,permutations=perms,real_sequences=seqs),f)
(R/'H01-result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
