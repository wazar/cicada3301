from pathlib import Path
import random,json,gzip,hashlib,itertools
R=Path(__file__).parent;B=R.parents[1];source=B/'worker-f/F06-maps.json';pages=[p for p in json.loads(source.read_text()) if p['page'] in [0,1]];src=[v for p in pages for v in p['indices']];rng=random.Random(1713092026)
def encode(x):
 raw=bin(x)[2:];L=len(raw);header=bin(L)[2:];return '0'*(len(header)-1)+header+raw[1:]
def decode(bits):
 i=0;k=0
 while i<len(bits) and bits[i]=='0':k+=1;i+=1
 assert i<len(bits) and i+k<len(bits);L=0
 for c in bits[i:i+k+1]:L=2*L+int(c)
 i+=k+1;assert L>=1 and i+L-1==len(bits);value=1
 for c in bits[i:]:value=2*value+int(c)
 return value
for x in range(1,65536):assert decode(encode(x))==x and len(encode(x))==x.bit_length()+2*(x.bit_length().bit_length()-1)
T=lambda L:L+2*(L.bit_length()-1)
for L in range(1,321):
 for x in [1<<(L-1),(1<<L)-1]:assert len(encode(x))==T(L) and decode(encode(x))==x
admissible={n:next((L for L in range(1,5*n+1) if T(L)==5*n),None) for n in range(1,33)};labels=list(range(29));rng.shuffle(labels);inverse={label:i for i,label in enumerate(labels)};controls=[]
for n,L in admissible.items():
 if L is None:continue
 for rep in range(30):
  proposals=[]
  while True:
   start=rng.randrange(len(src));salt=rng.getrandbits(max(1,L-1));value=0
   for j in range(max(1,L//4+1)):value=29*value+src[(start+j)%len(src)]
   x=(1<<(L-1))|((value^salt)&((1<<(L-1))-1));bits=encode(x);chunks=[int(bits[i:i+5],2) for i in range(0,len(bits),5)];accepted=max(chunks)<=28;proposals.append(dict(source_start=start,salt=salt,integer=x,chunks=chunks,accepted=accepted))
   assert len(proposals)<10000
   if accepted:break
  runes=[labels[v] for v in chunks];recovered=''.join(format(inverse[r],'05b') for r in runes);assert len(runes)==n and recovered==bits and decode(recovered)==x;controls.append(dict(n=n,L=L,rep=rep,proposals=proposals,runes=runes,bits=bits))
(R/'controls.json.gz').write_bytes(gzip.compress(json.dumps(dict(seed=1713092026,labels=labels,admissible=admissible,integer_roundtrips=65535,controls=controls)).encode(),mtime=0));print('CONTROLS',len(controls),'PASS',flush=True)
results=[]
for p in pages:
 hist={};violations=[];allunits=[]
 for wi,w in enumerate(p['words']):
  n=w['end']-w['start'];hist[n]=hist.get(n,0)+1;L=next((j for j in range(1,5*n+1) if T(j)==5*n),None);row=dict(word=wi,length=n,bits=5*n,map=w,runes=p['indices'][w['start']:w['end']],integer_bitlength=L);allunits.append(row)
  if L is None:
   lo=max(j for j in range(1,5*n+1) if T(j)<5*n);assert T(lo)<5*n<T(lo+1);violations.append(dict(**row,lower_L=lo,lower_T=T(lo),upper_L=lo+1,upper_T=T(lo+1)))
 results.append(dict(page=p['page'],units=len(allunits),histogram=hist,violations=violations,all_units=allunits,disposition='EXACT_FORMAT_EXCLUSION' if violations else 'INCONCLUSIVE_LENGTH_COMPATIBLE'))
(R/'actual.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),pages=results),indent=2));print(json.dumps([dict(page=p['page'],units=p['units'],violations=len(p['violations']),bad_lengths=sorted({x['length'] for x in p['violations']}),disposition=p['disposition']) for p in results],indent=2))
