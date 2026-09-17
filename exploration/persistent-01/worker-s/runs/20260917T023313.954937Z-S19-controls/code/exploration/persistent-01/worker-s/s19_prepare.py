import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,gzip,hashlib,collections,re,random,subprocess,datetime
import numpy as np
B=Path('exploration/persistent-01/worker-s');O=B/'S19';O.mkdir(exist_ok=True);M=Path('exploration/persistent-01/coordinator/Q05-latin-clean');SRC=Path('exploration/persistent-01/worker-f/F06-maps.json');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not Path('exploration/persistent-01/STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
train=json.loads(gzip.decompress((M/'train-maps.json.gz').read_bytes()));flat=[r for w in train['words'] for r in w['runes']];assert len(flat)==120854
c=[collections.Counter() for _ in range(3)];tot=[collections.Counter() for _ in range(3)];ctx=(29,29)
for x in flat:
 for n in range(3):key=ctx[-n:] if n else ();c[n][key+(x,)]+=1;tot[n][key]+=1
 ctx=(ctx[-1],x)
lm=np.full((30,30,30),np.nan)
for a in range(30):
 for b in range(30):
  for x in range(29):
   v=(c[0][(x,)]+.5)/(len(flat)+14.5)
   for n,alpha in [(1,8),(2,5)]:key=(a,b)[-n:];v=(c[n][key+(x,)]+alpha*v)/(tot[n][key]+alpha)
   lm[a,b,x]=np.log(v)
assert np.max(np.abs(np.exp(lm[:,:,:29]).sum(axis=2)-1))<1e-12
(O/'model-table.bin').write_bytes(lm.astype('<f8').tobytes());(O/'counts.json.gz').write_bytes(gzip.compress(json.dumps([[{'key':list(k),'count':v} for k,v in sorted(cc.items())] for cc in c]).encode(),mtime=0))
# Reuse checked search, changing only reset context and zero boundary contribution.
original=(B/'s17_engine.cpp').read_text();code=original.replace('vector<double> lm; vector<int> tokens;','vector<double> lm; vector<int> tokens,pre1,pre2;').replace('return lm[(mapped(i-2,m)*30+mapped(i-1,m))*30+mapped(i,m)];','if(tokens[i]==29)return 0;return lm[(mapped(pre2[i],m)*30+mapped(pre1[i],m))*30+mapped(i,m)];')
old='tokens.resize(n);for(int&i:tokens)in>>i;for(int i=0;i<n;i++)if(tokens[i]!=29)positions[tokens[i]].push_back(i);'
new='tokens.resize(n);for(int&i:tokens)in>>i;pre1.resize(n);pre2.resize(n);int last1=-1,last2=-1;for(int i=0;i<n;i++){pre1[i]=last1;pre2[i]=last2;if(tokens[i]==29){last1=-1;last2=-1;}else{positions[tokens[i]].push_back(i);last2=last1;last1=i;}}'
assert old in code;code=code.replace(old,new);(O/'engine.cpp').write_text(code)
import difflib
(O/'engine.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),code.splitlines(True),fromfile='S17',tofile='S19')))
cmd=['c++','-O3','-std=c++17',str(O/'engine.cpp'),'-o',str(O/'engine')];r=subprocess.run(cmd,capture_output=True,timeout=120);(O/'build.stderr').write_bytes(r.stderr);assert r.returncode==0,r.stderr
pages=json.loads(SRC.read_text());lengths=[[w['end']-w['start'] for w in p['words']] for p in pages];sizes=list(map(len,lengths));assert sum(sizes)==2355 and all(1<=n<=29 for a in lengths for n in a)
raw=(M/'pg227.txt').read_bytes().decode('utf-8-sig');table='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split();lookup={s:i for i,s in enumerate(table)};lookup.update(V=1,K=5,Z=15,Q=5);rng=random.Random(1709202619);packets=[]
for index,book in enumerate(['I','IV','VII','X']):
 heading=re.search(r'^  LIBER '+book+r'\s*$',raw,re.M);after=re.search(r'^  LIBER [IVX]+\s*$',raw[heading.end():],re.M);limit=heading.end()+after.start() if after else raw.index('*** END OF THE PROJECT GUTENBERG');plain=[];maps=[]
 for m in re.finditer('[A-Za-z]+',raw[heading.end():limit]):
  word=m.group().upper();pos=0
  while pos<len(word):
   token=max((s for s in lookup if word.startswith(s,pos)),key=len);plain.append(lookup[token]);maps.append({'word':m.group(),'word_start':heading.end()+m.start(),'source_char_span':[heading.end()+m.start()+pos,heading.end()+m.start()+pos+len(token)]});pos+=len(token)
  if len(plain)>=2355:break
 plain=plain[:2355];maps=maps[:2355];assert len(plain)==2355;enc=list(range(29));rng.shuffle(enc);dec=[enc.index(x) for x in range(29)];chunks=[];truth=[];start=0
 for n in sizes:truth.append(plain[start:start+n]);chunks.append([enc[x] for x in truth[-1]]);start+=n
 packets.append({'id':index,'name':'virgil-'+book,'chunks':chunks,'truth':truth,'truth_map':dec,'encoder_map':enc,'source_maps':maps,'encoded_lengths':[[x+1 for x in a] for a in chunks],'generated_total_filler_runes':sum(x+1 for a in chunks for x in a),'used_labels':sorted(set(x for a in chunks for x in a))})
packets.append({'id':4,'name':'actual-lengths','chunks':[[n-1 for n in a] for a in lengths],'lengths':lengths,'source_pages':pages,'actual_total_filler_runes':sum(sum(a) for a in lengths),'used_labels':sorted(set(n-1 for a in lengths for n in a))})
(O/'packets.json').write_text(json.dumps(packets));meta={'input_hashes':{str(p):sha(p) for p in [M/'train-maps.json.gz',M/'pg218.txt',M/'pg227.txt',M/'model.json',SRC,B/'S19-CARD.md',B/'s17_engine.cpp']},'train_runes':len(flat),'page_ids':[p['page'] for p in pages],'chunk_sizes':sizes,'tokens':2355,'plain_frequency_rank':sorted(range(29),key=lambda r:(-c[0][(r,)],r)),'hashes':{str(p):sha(p) for p in [O/'model-table.bin',O/'counts.json.gz',O/'engine.cpp',O/'engine',O/'packets.json']},'compile':cmd};(O/'manifest.json').write_text(json.dumps(meta,indent=2));print(json.dumps({'train_runes':len(flat),'chunk_sizes':sizes,'controls':[{'name':p['name'],'used_labels':len(p['used_labels']),'generated_total_runes':p['generated_total_filler_runes']} for p in packets[:4]],'actual_used_labels':len(packets[4]['used_labels']),'actual_total_runes':packets[4]['actual_total_filler_runes']}))
