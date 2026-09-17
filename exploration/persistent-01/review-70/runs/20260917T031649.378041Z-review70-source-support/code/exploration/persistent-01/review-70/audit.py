import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,gzip,hashlib,re,random,itertools,collections
import numpy as np
O=Path('exploration/persistent-01/review-70');B=O.parent;D=B/'worker-s/S20';Q=B/'coordinator/Q05-latin-clean'
def gz(p):return json.loads(gzip.decompress(p.read_bytes()))
def js(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[f for f in D.iterdir() if f.is_file()]+[B/'worker-s/S20-CARD.md',B/'worker-p/P04/CARD.md'];snap={str(p):sha(p) for p in files};(O/'inputs.json').write_text(json.dumps(snap,indent=2))
for x in js(D/'inputs.json'):assert sha(Path(x['path']))==x['sha256']
lookup={s:i for i,s in enumerate('F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split())};lookup.update(V=1,K=5,Z=15,Q=5)
def convert(raw,start,end):
 s=raw[start:end].upper();out=[];spans=[];i=0
 while i<len(s):
  width=2 if i+1<len(s) and s[i:i+2] in lookup else 1;out.append(lookup[s[i:i+width]]);spans.append([start+i,start+i+width]);i+=width
 return out,spans
train=gz(Q/'train-maps.json.gz');source=gz(D/'sources.json.gz');packets=js(B/'worker-s/S19/packets.json');wordschecked=0;runeschecked=0;rebuilt=[]
for si,s in enumerate(source):
 path=Path(s['source']);assert sha(path)==s['sha256'];raw=path.read_bytes().decode('utf-8-sig')
 if si==0:assert s['body']==train['body'] and s['excluded_headings']==train['excluded_headings'];assert s['words']==train['words']
 else:
  book=['I','IV','VII','X'][si-1];heading=re.search(r'^  LIBER '+book+r'\s*$',raw,re.M);nxt=re.search(r'^  LIBER [IVX]+\s*$',raw[heading.end():],re.M);stop=heading.end()+nxt.start() if nxt else raw.index('*** END OF THE PROJECT GUTENBERG');assert s['body']==[heading.end(),stop] and not s['excluded_headings']
 start,end=s['body'];matches=[]
 for m in re.finditer('[A-Za-z]+',raw[start:end]):
  a,b=start+m.start(),start+m.end()
  if any(a>=lo and b<=hi for lo,hi in s['excluded_headings']):continue
  matches.append((a,b,m.group()))
 assert len(matches)==len(s['words']);flat=[];sp=[]
 for (a,b,text),w in zip(matches,s['words']):
  seq,coords=convert(raw,a,b);assert w==dict(text=text,start=a,end=b,runes=seq,rune_char_spans=coords);flat+=seq;sp+=coords;wordschecked+=1
 assert flat==s['runes'] and sp==s['rune_char_spans'];runeschecked+=len(flat);rebuilt.append(flat)
 if si:assert flat[:2355]==[x for row in packets[si-1]['truth'] for x in row] and sp[:2355]==[m['source_char_span'] for m in packets[si-1]['source_maps']]
actual=gz(D/'actual.json.gz');pages=js(B/'worker-f/F06-maps.json');seq=[w['end']-w['start']-1 for p in pages for w in p['words']];assert pages==actual['pages'] and seq==actual['sequence']==[x for row in packets[4]['chunks'] for x in row] and len(seq)==actual['unit_count']==2355 and len(set(seq))==actual['support']==14
countsall=[];rows=[];N=2355;minschecked=0
for s,flat in zip(source,rebuilt):
 a=np.asarray(flat);counts=np.zeros(len(a)-N+1,dtype=np.uint8)
 for rune in range(29):
  prefix=np.r_[0,np.cumsum(a==rune,dtype=np.int64)];counts+=(prefix[N:]-prefix[:-N]>0)
 w=gz(D/(s['name']+'-windows.json.gz'));minimum=int(counts.min());maximum=int(counts.max());where=np.flatnonzero(counts==minimum).tolist();passing=np.flatnonzero(counts==14).tolist();hist={str(k):int(np.count_nonzero(counts==k)) for k in sorted(set(counts.tolist()))};rawsp=[[s['rune_char_spans'][i][0],s['rune_char_spans'][i+N-1][1]] for i in where]
 assert counts.tolist()==w['all_support_counts'] and minimum==w['minimum'] and maximum==w['maximum'] and len(counts)==w['windows'] and len(a)==w['runes'];assert where==w['minimizing_offsets'] and rawsp==w['minimizing_raw_spans'] and passing==w['passing_offsets'] and hist==w['support_histogram'];assert not passing
 for i in set([0,len(counts)-1]+where):assert len(set(flat[i:i+N]))==int(counts[i]);minschecked+=1
 rows.append(dict(name=s['name'],runes=len(a),windows=len(counts),minimum=minimum,maximum=maximum,minimizers=len(where),passing=0));countsall.append(len(counts))
controls=gz(D/'controls.json.gz');rng=random.Random(632020);assert controls['seed']==632020
for flat,c in zip(rebuilt,controls['controls'][:5]):
 perm=list(range(29));rng.shuffle(perm);assert perm==c['permutation'] and c['input_support']==len(set(flat[:N]))==len(set(perm[x] for x in flat[:N]))==c['output_support']
for size,c in zip([14,15],controls['controls'][5:]):assert c['sequence']==[i%size for i in range(N)] and len(set(c['sequence']))==c['artificial_support']==size and c['matches_target']==(size==14)
# Independent bit-mask presence calculation against direct sets in every tiny panel.
tiny=0
for alphabet in [2,3]:
 for length in range(1,8):
  for a in itertools.product(range(alphabet),repeat=length):
   for n in range(1,length+1):
    for i in range(length-n+1):
     bits=0
     for x in a[i:i+n]:bits|=1<<x
     assert bits.bit_count()==len(set(a[i:i+n]))
    tiny+=1
assert tiny==controls['tiny_panels']==22862
r=js(D/'result.json');assert sum(countsall)==r['total_windows']==224473 and r['total_passing']==0
for actualrow,stored in zip(rows,r['sources']):assert all(actualrow[k]==stored[k] for k in ['name','runes','windows','minimum','maximum']);assert stored['minimizing_windows']==actualrow['minimizers'] and stored['passing_windows']==0
assert all(sha(Path(p))==h for p,h in snap.items())
out=dict(pass_all=True,words=wordschecked,normalized_runes=runeschecked,actual_units=2355,actual_support=14,total_windows=224473,all_counts_checked=True,minimizing_and_endpoint_set_checks=minschecked,tiny_panels=tiny,sources=rows,limits='Only exact2355rune contiguous windows in fixedfive streams under a bijection; not Latin in general or arbitrary source assembly.')
(O/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
