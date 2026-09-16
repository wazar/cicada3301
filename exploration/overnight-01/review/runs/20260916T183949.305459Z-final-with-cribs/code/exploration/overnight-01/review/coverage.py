import pathlib,json,gzip,hashlib,collections
R=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).parent;B=R/'exploration/overnight-01';hold={4,9,14,19,24,29,34,39,44,54};rows=[]
def emit(lane,counts,extra=None):
 assert not (set(counts)&hold),(lane,counts);rows.append(dict(lane=lane,completed_rows=sum(counts.values()),pages=sorted(counts),per_page=dict(counts),extra=extra))
for d in (B/'worker-a').glob('r01*'):
 if not d.is_dir():continue
 cnt=collections.Counter()
 for f in d.glob('scores-*.jsonl.gz'):
  with gzip.open(f,'rt') as h:
   for line in h:
    z=json.loads(line);cnt[z['original_page']]+=1
 emit(str(d.relative_to(R)),cnt)
for d in (B/'worker-a/r02').glob('*'):
 if not d.is_dir():continue
 cnt=collections.Counter()
 for f in d.glob('scores-*.jsonl.gz'):
  with gzip.open(f,'rt') as h:
   for line in h:cnt[json.loads(line)['original_page']]+=1
 emit(str(d.relative_to(R)),cnt)
for lane in ['r03','r03-f','r04','r04-wide']:
 cnt=collections.Counter();files=sorted((B/'worker-b'/lane).glob('cell-*'))
 for f in files:
  if f.suffix=='.gz':
   with gzip.open(f,'rt') as h:z=json.load(h)
  else:z=json.loads(f.read_text())
  if lane=='r03':
   for a in z:cnt[int(a[0].split(':')[0])]+=1
  elif lane=='r03-f':cnt[z['page']]+=1
  else:
   for a in z:cnt[a['page']]+=1
 emit(lane,cnt)
for f in (B/'worker-c').glob('*scores.jsonl.gz'):
 if f.name.startswith('R08'):continue
 cnt=collections.Counter()
 with gzip.open(f,'rt') as h:
  for l in h:cnt[json.loads(l)['page']]+=1
 emit(f.name,cnt)
for lane in ['r05','r06']:
 cnt=collections.Counter();relations=cribs=0
 for f in sorted((B/'worker-b'/lane).glob('*.json.gz')):
  with gzip.open(f,'rt') as h:z=json.load(h)
  if lane=='r06':cnt[z['page']]+=len(z['scores'])
  else:
   for row in z:
    bits=row[0].split(':');assert not ({int(bits[0]),int(bits[1])}&hold)
    if bits[-1]=='crib':cribs+=1
    else:relations+=1;cnt[int(bits[0])]+=1;cnt[int(bits[1])]+=1
 emit(lane,cnt,{'relations':relations,'cribs':cribs,'count_note':'R05 endpoint counts count each relation twice'})
(O/'coverage.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps([{k:v for k,v in z.items() if k not in ('per_page','extra')} for z in rows],indent=2))
