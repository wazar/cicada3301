import os
for k in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,gzip,re,random,math,hashlib,collections,subprocess
import numpy as np
O=Path('exploration/persistent-01/review-64');S=O.parent/'worker-s';D=S/'S19';M=O.parent/'coordinator/Q05-latin-clean';F=O.parent/'worker-f/F06-maps.json'
def js(p):return json.loads(p.read_text())
def gz(p):return json.loads(gzip.decompress(p.read_bytes()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[f for f in D.iterdir() if f.is_file()]+[F,M/'train-maps.json.gz',M/'pg218.txt',M/'pg227.txt',M/'model.json',S/'S19-CARD.md'];snapshot={str(f):sha(f) for f in files};(O/'inputs.json').write_text(json.dumps(snapshot,indent=2))
labels='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split();lookup={s:i for i,s in enumerate(labels)};lookup.update(V=1,K=5,Z=15,Q=5)
def parse(word,base):
 word=word.upper();p=[];spans=[];i=0
 while i<len(word):
  length=2 if i+1<len(word) and word[i:i+2] in lookup else 1;p.append(lookup[word[i:i+length]]);spans.append([base+i,base+i+length]);i+=length
 return p,spans
train=gz(M/'train-maps.json.gz');raw=(M/'pg218.txt').read_bytes().decode('utf-8-sig');start,end=train['body'];ex=train['excluded_headings'];matches=[m for m in re.finditer('[A-Za-z]+',raw[start:end]) if not any(a<=start+m.start()<b for a,b in ex)];assert len(matches)==len(train['words'])==20484
flat=[]
for m,w in zip(matches,train['words']):
 a=start+m.start();b=start+m.end();p,sp=parse(m.group(),a);assert (a,b)==(w['start'],w['end']) and m.group()==w['text'] and p==w['runes'] and sp==w['rune_char_spans'];flat.extend(p)
assert len(flat)==120854
counts=[collections.Counter() for _ in range(3)];tot=[collections.Counter() for _ in range(3)];a=b=29
for x in flat:
 for n,key in enumerate([(x,),(b,x),(a,b,x)]):counts[n][key]+=1;tot[n][key[:-1]]+=1
 a,b=b,x
saved=[{tuple(x['key']):x['count'] for x in r} for r in gz(D/'counts.json.gz')];assert counts==saved
lp=np.empty((30,30,29))
for a in range(30):
 for b in range(30):
  for c in range(29):
   q=(counts[0][(c,)]+.5)/(len(flat)+14.5);q=(counts[1][(b,c)]+8*q)/(tot[1][(b,)]+8);q=(counts[2][(a,b,c)]+5*q)/(tot[2][(a,b)]+5);lp[a,b,c]=math.log(q)
table=np.fromfile(D/'model-table.bin',dtype='<f8').reshape(30,30,30);err=float(np.max(abs(lp-table[:,:,:29])));assert err<1e-12 and np.all(np.isnan(table[:,:,29]))
packets=js(D/'packets.json');pages=js(F);sizes=[len(p['words']) for p in pages];lengths=[[w['end']-w['start'] for w in p['words']] for p in pages];assert sum(sizes)==2355 and packets[4]['source_pages']==pages and packets[4]['lengths']==lengths and packets[4]['chunks']==[[n-1 for n in row] for row in lengths]
vr=(M/'pg227.txt').read_bytes().decode('utf-8-sig');rng=random.Random(1709202619);maps=0
for ix,book in enumerate(['I','IV','VII','X']):
 heading=re.search(r'^  LIBER '+book+r'\s*$',vr,re.M);nxt=re.search(r'^  LIBER [IVX]+\s*$',vr[heading.end():],re.M);end=heading.end()+nxt.start() if nxt else vr.index('*** END OF THE PROJECT GUTENBERG');plain=[];src=[]
 for m in re.finditer('[A-Za-z]+',vr[heading.end():end]):
  p,sp=parse(m.group(),heading.end()+m.start());plain+=p;src.extend(dict(word=m.group(),word_start=heading.end()+m.start(),source_char_span=s) for s in sp)
  if len(plain)>=2355:break
 plain=plain[:2355];src=src[:2355];p=packets[ix];assert src==p['source_maps'] and plain==[x for row in p['truth'] for x in row];maps+=len(src)
 enc=list(range(29));rng.shuffle(enc);assert enc==p['encoder_map'] and [enc.index(v) for v in range(29)]==p['truth_map'];assert [[enc[x] for x in row] for row in p['truth']]==p['chunks'];assert [len(row) for row in p['truth']]==sizes;assert [[x+1 for x in row] for row in p['chunks']]==p['encoded_lengths']
 assert sum(x+1 for row in p['chunks'] for x in row)==p['generated_total_filler_runes']
def score(chunks,mp):
 value=0
 for row in chunks:
  a=b=29
  for x in row:c=mp[x];value+=float(lp[a,b,c]);a,b=b,c
 return value
rows=0;worst=0;probes=0;controls=[];nullscores=[];evals=0;accepted=0;prank=sorted(range(29),key=lambda x:(-counts[0][(x,)],x))
for name in [f'control{i}' for i in range(4)]+['actual']+[f'null{j:02}' for j in range(19)]:
 r=js(D/(name+'.json'));i=r['packet'];p=packets[i];chunks=p['chunks']
 if name.startswith('null'):
  j=int(name[4:]);q=js(D/(name+'.input.json'));seed=1709192619+j;assert q['seed']==seed;g=random.Random(seed);out=[];perms=[]
  for row in chunks:
   order=list(range(len(row)));g.shuffle(order);perms.append(order);out.append([row[v] for v in order])
  assert out==q['chunks'] and perms==q['permutations'];chunks=out
 else:j=None
 assert r['cipher_chunks']==chunks and r['complete'] and r['exit']==0 and r['seed']==1709182619+100*i+(0 if j is None else j+1)
 allcipher=[x for row in chunks for x in row];order=sorted(range(29),key=lambda x:(-allcipher.count(x),x));init=[0]*29
 for c,x in zip(order,prank):init[c]=x
 assert r['restarts'][0]['initial']==init
 for row in r['restarts']:
  assert sorted(row['map'])==list(range(29)) and sorted(row['initial'])==list(range(29));decoded=[[row['map'][x] for x in a] for a in chunks];assert decoded==row['plain_chunks'];inv=[row['map'].index(x) for x in range(29)];assert [[inv[x] for x in a] for a in decoded]==chunks
  error=abs(score(chunks,row['map'])-row['score']);worst=max(worst,error);assert error<1e-7;rows+=1;evals+=row['evaluations'];accepted+=row['accepted_sa'];assert row['evaluations']==30000+406*row['hill_sweeps']
 for pr in r['probes']:
  before=score(chunks,pr['map']);mp=pr['map'].copy();a,b=pr['a'],pr['b'];mp[a],mp[b]=mp[b],mp[a];after=score(chunks,mp);assert max(abs(before-pr['before']),abs(after-pr['after']),abs(after-before-pr['delta']))<1e-7;probes+=1
 best=max(r['restarts'],key=lambda x:x['score']);assert best['score']==r['maximum'] and best['restart']==r['best_restart'] and abs(best['score']/2355-r['mean_rune_score'])<1e-12
 if i<4:
  true=[x for row in p['truth'] for x in row];got=[x for row in best['plain_chunks'] for x in row];errors=[k for k,(a,b) in enumerate(zip(true,got)) if a!=b];tm=p['truth_map'];s=score(chunks,tm);c=r['control'];assert errors==c['errors'] and abs(s-c['truth_score'])<1e-7 and c['truth_rank']==1+sum(z['score']>s+1e-8 for z in r['restarts']);used=set(allcipher)
  assert c['observed_map_accuracy']==sum(best['map'][x]==tm[x] for x in used)/len(used) and c['full_map_accuracy']==sum(a==b for a,b in zip(best['map'],tm))/29
  assert c['all_retained_error_counts']==[sum(a!=b for a,b in zip(true,[x for a in z['plain_chunks'] for x in a])) for z in r['restarts']]
  controls.append(dict(errors=len(errors),rank=c['truth_rank'],support=len(used)))
 elif j is None:actual=r['maximum']
 else:nullscores.append(r['maximum'])
assert rows==576;tail=(1+sum(s>=actual for s in nullscores))/20;assert tail==.65
cmd=['c++','-O2','-std=c++17',str(O/'kernel.cpp'),'-o',str(O/'kernel')];p=subprocess.run(cmd,capture_output=True);(O/'compile.stderr').write_bytes(p.stderr);assert p.returncode==0
p=subprocess.run([str(O/'kernel')],capture_output=True,timeout=60);(O/'kernel.stdout').write_bytes(p.stdout);(O/'kernel.stderr').write_bytes(p.stderr);assert p.returncode==0
assert all(sha(Path(f))==h for f,h in snapshot.items())
r=dict(pass_all=True,train_words=20484,train_runes=120854,held_source_maps=maps,table_cells=26100,table_error=err,outputs=rows,score_error=worst,probes=probes,controls=controls,actual_support=len(set(x for a in packets[4]['chunks'] for x in a)),actual=actual,tail=tail,evaluations_recorded=evals,accepted_recorded=accepted,kernel=json.loads(p.stdout),limits='No full SA trajectory or global optimality claim;14actual labels versus27control labels.')
(O/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
