from pathlib import Path
import importlib.util,re,json,gzip,hashlib,collections,math,numpy as np
O=Path(__file__).resolve().parent;ROOT=O.parents[3]
spec=importlib.util.spec_from_file_location('gp',ROOT/'liber-primus/src/lp/gematria.py');gp=importlib.util.module_from_spec(spec);spec.loader.exec_module(gp)
tokens={t:i for i,r,t,p in gp.GEMATRIA};tokens.update(V=1,K=5,Q=5,Z=15)
lookup=sorted(tokens,key=lambda x:(-len(x),x))
def parse_words(raw,start,end,excluded=[]):
 out=[]
 for m in re.finditer('[A-Za-z]+',raw[start:end]):
  a=start+m.start();z=start+m.end()
  if any(a>=u and z<=v for u,v in excluded):continue
  text=m.group();s=text.upper();ids=[];spans=[];i=0
  while i<len(s):
   t=next(t for t in lookup if s.startswith(t,i));ids.append(tokens[t]);spans.append([a+i,a+i+len(t)]);i+=len(t)
  assert ids==gp.keyword_to_indices(text)
  out.append(dict(text=text,start=a,end=z,runes=ids,rune_char_spans=spans))
 return out
def store(n,x):
 with gzip.open(O/n,'wt',encoding='utf8') as f:json.dump(x,f,separators=(',',':'))
raw=(O/'pg218.txt').read_bytes().decode('utf-8-sig');start=raw.index('GALLIA est omnis');end=raw.index('*** END OF THE PROJECT GUTENBERG')
excluded=[[m.start(),m.end()] for m in re.finditer(r'^C\. IULI CAESARIS DE BELLO GALLICO COMMENTARIUS [A-Z]+\s*$',raw,re.M) if m.start()>=start and m.start()<end]
assert len(excluded)==3
words=parse_words(raw,start,end,excluded); store('train-maps.json.gz',dict(source='pg218.txt',coordinate='Decoded UTF-8-sig string preserving CRLF; half-open character spans',body=[start,end],excluded_headings=excluded,words=words))
raw2=(O/'pg227.txt').read_bytes().decode('utf-8-sig');controls=[]
for book in ['I','IV','VII','X']:
 match=re.search(r'^  LIBER '+book+r'\s*$',raw2,re.M);assert match
 nextmatch=re.search(r'^  LIBER [IVX]+\s*$',raw2[match.end():],re.M)
 bound=match.end()+nextmatch.start() if nextmatch else raw2.index('*** END OF THE PROJECT GUTENBERG')
 ws=parse_words(raw2,match.end(),bound)[:60];assert len(ws)==60
 p=[];ends=[];spans=[]
 for w in ws:p+=w['runes'];spans+=w['rune_char_spans'];ends.append(len(p)-1)
 controls.append(dict(id='virgil-book-'+book,source='pg227.txt',words=ws,indices=p,ends=ends,rune_char_spans=spans))
store('held-controls.json.gz',controls)
c=[collections.Counter() for _ in range(3)];t=[collections.Counter() for _ in range(3)];s=(29,29);nt=0
for w in words:
 for x in w['runes']+[29]:
  for n in range(3):ctx=s[-n:] if n else ();c[n][ctx+(x,)]+=1;t[n][ctx]+=1
  s=(s[-1],x);nt+=1
scores=np.empty((30,30,30),dtype=np.float64)
for a in range(30):
 for b in range(30):
  for x in range(30):
   v=(c[0][(x,)]+.5)/(t[0][()]+15)
   for n,alpha in [(1,8),(2,5)]:ctx=(a,b)[-n:];v=(c[n][ctx+(x,)]+alpha*v)/(t[n][ctx]+alpha)
   scores[a,b,x]=math.log(v)
assert np.max(np.abs(np.exp(scores).sum(axis=2)-1))<1e-12
np.savez_compressed(O/'model.npz',logp=scores)
store('counts.json.gz',[[dict(key=list(k),count=v) for k,v in sorted(cc.items())] for cc in c])
meta=dict(train_source='https://www.gutenberg.org/cache/epub/218/pg218.txt',held_source='https://www.gutenberg.org/cache/epub/227/pg227.txt',train_words=len(words),train_runes=sum(len(w['runes']) for w in words),train_tokens=nt,train_body=[start,end],excluded_headings=excluded,normalization='ASCII words; canonical greedy GP with aliases; punctuation/numbers delimit words; three internal chapter-heading lines omitted; abbreviations/Roman numerals in body retained.',model='P03 interpolated unigram .5, bigram8, trigram5; boundary29; no training on held Virgil',controls=[dict(id=v['id'],words=len(v['words']),runes=len(v['indices']),source_span=[v['words'][0]['start'],v['words'][-1]['end']]) for v in controls],hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [O/'pg218.txt',O/'pg227.txt',O/'model.npz',O/'train-maps.json.gz',O/'held-controls.json.gz']})
(O/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
