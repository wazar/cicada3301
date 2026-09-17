from pathlib import Path
import json,gzip,random,itertools,hashlib
O=Path(__file__).resolve().parent;ROOT=O.parents[3];source=ROOT/'exploration/persistent-01/worker-f/F06-maps.json';pages=json.loads(source.read_text());assert len(pages)==45
assert not any(p['page'] in [4,9,14,19,24,29,34,39,44,50,54] for p in pages)
def records(p,clock):
 d={}
 for wi,w in enumerate(p['units']):
  r=p['indices'][w['start']:w['end']]
  for j in range(2,len(r)):
   k=(j,r[j-2],r[j-1]) if clock else (r[j-2],r[j-1])
   q=dict(word=wi,word_position=j,context=r[j-2:j],next=r[j],page_rune_positions=list(range(w['start']+j-2,w['start']+j+1)),source_char_positions=w['source_char_positions'][j-2:j+1])
   d.setdefault(k,[]).append(q)
 return d
def analyze(p,clock):
 d=records(p,clock);bad=[]
 for k,rows in sorted(d.items()):
  if len({r['next'] for r in rows})>1:
   a=rows[0];b=next(r for r in rows if r['next']!=a['next']);bad.append(dict(context=list(k),witness=[a,b],all_occurrences=rows))
 return dict(page=p['page'],clock=clock,contexts=len(d),transitions=sum(len(r) for r in d.values()),compatible=not bad,conflicts=bad)
rng=random.Random(6061709);controls=[]
for clock in [False,True]:
 for rep in range(4):
  panel=[]
  for p in pages:
   f={};out=[]
   for w in p['units']:
    n=w['end']-w['start'];word=[rng.randrange(29) for _ in range(min(n,2))]
    for j in range(2,n):
     k=(j,word[-2],word[-1]) if clock else (word[-2],word[-1])
     if k not in f:f[k]=rng.randrange(29)
     word.append(f[k])
    out+=word
   q=dict(p,indices=out);r=analyze(q,clock);assert r['compatible'];panel.append(dict(page=p['page'],indices=out,table=[dict(key=list(k),value=v) for k,v in sorted(f.items())],result=r))
  controls.append(dict(clock=clock,rep=rep,pages=panel))
tiny=[]
for _ in range(8):
 seq=[rng.randrange(3) for _ in range(7)];d={};valid=True
 for i in range(2,len(seq)):
  k=tuple(seq[i-2:i]);valid &= k not in d or d[k]==seq[i];d[k]=seq[i]
 count=0
 for f in itertools.product(range(3),repeat=9):
  if all(f[3*seq[i-2]+seq[i-1]]==seq[i] for i in range(2,len(seq))):count+=1
 assert valid==(count>0);tiny.append(dict(sequence=seq,compatible=bool(valid),valid_tables=count))
real=[analyze(p,clock) for clock in [False,True] for p in pages]
for name,obj in [('controls.json.gz',controls),('real.json.gz',real),('tiny.json.gz',tiny)]:
 with gzip.open(O/name,'wt') as f:json.dump(obj,f,separators=(',',':'))
summary=dict(input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),pages=[p['page'] for p in pages],models=[dict(clock=c,incompatible_pages=[r['page'] for r in real if r['clock']==c and not r['compatible']],conflicting_contexts=sum(len(r['conflicts']) for r in real if r['clock']==c)) for c in [False,True]],control_page_cases=360,tiny_tables=8*3**9)
(O/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
