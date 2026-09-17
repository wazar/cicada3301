import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,gzip,hashlib,re,random,itertools,collections,sys,datetime,time
B=Path('exploration/persistent-01'); O=B/'worker-s/S20';O.mkdir(exist_ok=True);Q=B/'coordinator/Q05-latin-clean';N=2355
def guard():assert not (B/'STOP').exists() and datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,25,tzinfo=datetime.timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):(O/name).write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
def load(name):return json.loads(gzip.decompress((O/name).read_bytes()))
table='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split();lookup={s:i for i,s in enumerate(table)};lookup.update(V=1,K=5,Z=15,Q=5)
def words(raw,start,end):
 out=[]
 for m in re.finditer('[A-Za-z]+',raw[start:end]):
  s=m.group().upper();i=0;r=[];sp=[]
  while i<len(s):
   t=max((t for t in lookup if s.startswith(t,i)),key=len);r.append(lookup[t]);sp.append([start+m.start()+i,start+m.start()+i+len(t)]);i+=len(t)
  out.append(dict(text=m.group(),start=start+m.start(),end=start+m.end(),runes=r,rune_char_spans=sp))
 return out
def scan(seq,n):
 if len(seq)<n:return []
 counts=collections.Counter(seq[:n]);out=[len(counts)]
 for i in range(n,len(seq)):
  old=seq[i-n];counts[old]-=1
  if not counts[old]:del counts[old]
  counts[seq[i]]+=1;out.append(len(counts))
 return out
def verify(seq,n,out):
 last=[-1]*29;got=[]
 for i,x in enumerate(seq):
  last[x]=i
  if i>=n-1:got.append(sum(p>=i-n+1 for p in last))
 assert got==out
def prepare():
 guard();meta=json.loads((B/'worker-s/S19/manifest.json').read_text())
 for f in [Q/'pg218.txt',Q/'pg227.txt',Q/'train-maps.json.gz']:
  assert sha(f)==meta['input_hashes'][str(f)]
 train=json.loads(gzip.decompress((Q/'train-maps.json.gz').read_bytes()));raw=(Q/'pg218.txt').read_bytes().decode('utf-8-sig')
 expected=[w for w in words(raw,*train['body']) if not any(w['start']>=a and w['end']<=b for a,b in train['excluded_headings'])];assert expected==train['words']
 sources=[dict(name='caesar-clean',source=str(Q/'pg218.txt'),sha256=sha(Q/'pg218.txt'),body=train['body'],excluded_headings=train['excluded_headings'],words=expected)]
 raw=(Q/'pg227.txt').read_bytes().decode('utf-8-sig')
 for book in ['I','IV','VII','X']:
  head=re.search(r'^  LIBER '+book+r'\s*$',raw,re.M);after=re.search(r'^  LIBER [IVX]+\s*$',raw[head.end():],re.M);end=head.end()+after.start() if after else raw.index('*** END OF THE PROJECT GUTENBERG');sources.append(dict(name='virgil-'+book,source=str(Q/'pg227.txt'),sha256=sha(Q/'pg227.txt'),body=[head.end(),end],excluded_headings=[],words=words(raw,head.end(),end)))
 for s in sources:
  s['runes']=[r for w in s['words'] for r in w['runes']];s['rune_char_spans']=[p for w in s['words'] for p in w['rune_char_spans']];assert len(s['runes'])>=N
 packet=json.loads((B/'worker-s/S19/packets.json').read_text())
 for s,p in zip(sources[1:],packet[:4]):assert s['runes'][:N]==[x for a in p['truth'] for x in a];assert s['rune_char_spans'][:N]==[x['source_char_span'] for x in p['source_maps']]
 actual=packet[4];pages=json.loads((B/'worker-f/F06-maps.json').read_text());seq=[w['end']-w['start']-1 for p in pages for w in p['words']];assert seq==[x for a in actual['chunks'] for x in a] and len(seq)==N and len(set(seq))==14
 rng=random.Random(632020);controls=[]
 for s in sources:
  p=list(range(29));rng.shuffle(p);a=s['runes'][:N];b=[p[x] for x in a];assert len(set(a))==len(set(b)) and scan(b,N)==[len(set(a))];controls.append(dict(source=s['name'],permutation=p,input_support=len(set(a)),output_support=len(set(b))))
 for support in [14,15]:
  a=[i%support for i in range(N)];assert scan(a,N)==[support];controls.append(dict(artificial_support=support,matches_target=support==14,sequence=a))
 tiny=0
 for alphabet in [2,3]:
  for length in range(1,8):
   for a in itertools.product(range(alphabet),repeat=length):
    for n in range(1,length+1):
     got=scan(a,n);assert got==[len(set(a[i:i+n])) for i in range(length-n+1)];verify(a,n,got);tiny+=1
 save('sources.json.gz',sources);save('controls.json.gz',dict(seed=632020,controls=controls,tiny_panels=tiny));save('actual.json.gz',dict(sequence=seq,pages=pages,unit_count=N,support=14))
 files=[Q/'pg218.txt',Q/'pg227.txt',Q/'train-maps.json.gz',B/'worker-s/S19/packets.json',B/'worker-s/S19/manifest.json',B/'worker-f/F06-maps.json',B/'worker-p/P04/CARD.md',B/'worker-s/S20-CARD.md',Path(__file__)]
 (O/'inputs.json').write_text(json.dumps([dict(path=str(p),sha256=sha(p)) for p in files],indent=2));print(json.dumps(dict(stage='pilot',source_lengths=[len(s['runes']) for s in sources],tiny_panels=tiny,controls='PASS')))
def full():
 guard();t=time.monotonic();rows=[]
 for f in json.loads((O/'inputs.json').read_text()):assert sha(Path(f['path']))==f['sha256']
 for s in load('sources.json.gz'):
  guard();a=s['runes'];counts=scan(a,N);verify(a,N,counts);minimum=min(counts);mins=[i for i,c in enumerate(counts) if c==minimum];passing=[i for i,c in enumerate(counts) if c==14]
  for i in sorted(set([0,len(counts)-1]+mins+passing)):assert len(set(a[i:i+N]))==counts[i]
  row=dict(name=s['name'],runes=len(a),windows=len(counts),minimum=minimum,maximum=max(counts),support_histogram=dict(sorted(collections.Counter(counts).items())),minimizing_offsets=mins,passing_offsets=passing,minimizing_raw_spans=[[s['rune_char_spans'][i][0],s['rune_char_spans'][i+N-1][1]] for i in mins],all_support_counts=counts);save(s['name']+'-windows.json.gz',row);rows.append({k:v for k,v in row.items() if k not in ['all_support_counts','minimizing_offsets','minimizing_raw_spans','passing_offsets']}|dict(minimizing_windows=len(mins),passing_windows=len(passing)))
 result=dict(status='PASS',actual_units=N,actual_support=14,sources=rows,total_windows=sum(r['windows'] for r in rows),total_passing=sum(r['passing_windows'] for r in rows),seconds=time.monotonic()-t)
 (O/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if sys.argv[1]=='pilot':prepare()
elif sys.argv[1]=='full':full()
