import pathlib,json,collections,random,math,gzip,hashlib,time,datetime
ROOT=pathlib.Path(__file__).resolve().parents[3];OUT=pathlib.Path(__file__).parent
raw=(OUT/'R01-input.json').read_bytes();D=[p for p in json.loads(raw) if p['page'] in [0,1]]
def pairs(vals):
 c=collections.Counter(vals);return sum(v*(v-1)//2 for v in c.values())
def chunk_score(vals):return sum(pairs(vals[i:i+28]) for i in range(0,len(vals),28))
assert chunk_score(list(range(28))*2)==0
assert chunk_score([0]*28)==378
assert chunk_score(list(range(28))+[0]*2)==1
def inspect(a,p=None):
 dep=[[] for _ in range(29)]; loc=[[] for _ in range(29)]
 for i,(v,w) in enumerate(zip(a,a[1:])):
  if v!=w:dep[v].append(w);loc[v].append(i)
 scores=[chunk_score(x) for x in dep];witness=[]
 for v in range(29):
  for start in range(0,len(dep[v]),28):
   first={}
   for k in range(start,min(start+28,len(dep[v]))):
    w=dep[v][k];i=loc[v][k]
    if w in first:
     j=first[w];row=dict(predecessor=v,successor=w,first_rune_index=j,repeat_rune_index=i)
     if p is not None:row.update(first_source_chars=p['source_char_positions'][j:j+2],repeat_source_chars=p['source_char_positions'][i:i+2])
     witness.append(row)
    else:first[w]=i
 return dict(score=sum(scores),source_scores=scores,visits=[len(x) for x in dep],departures=dep,witnesses=witness)
def gen(p,deck,weighted,r):
 truth=p['indices'];counts=collections.Counter(truth);weights=[counts[i]+.5 for i in range(29)] if weighted else [1]*29
 a=[r.randrange(29)];decks=[[] for _ in range(29)]
 for i in range(1,len(truth)):
  prev=a[-1]
  if truth[i]==truth[i-1]:a.append(prev);continue
  if deck:
   if not decks[prev]:decks[prev]=sorted((v for v in range(29) if v!=prev),key=lambda v:-math.log(max(r.random(),1e-300))/weights[v],reverse=True)
   a.append(decks[prev].pop())
  else:
   vals=[v for v in range(29) if v!=prev];a.append(r.choices(vals,weights=[weights[v] for v in vals])[0])
 assert [x==y for x,y in zip(a,a[1:])]==[x==y for x,y in zip(truth,truth[1:])]
 return a
start=time.monotonic();real=[dict(page=p['page'],**inspect(p['indices'],p)) for p in D];results=dict(input_sha256=hashlib.sha256(raw).hexdigest(),real=real,models=[])
with gzip.open(OUT/'R02-controls.jsonl.gz','wt') as full:
 for panel,(deck,weighted) in enumerate([(True,False),(False,False),(True,True),(False,True)]):
  rows=[]
  for k in range(999):
   if (ROOT/'exploration/persistent-01/STOP').exists():raise SystemExit('STOP')
   seed=402000+panel*10000+k;r=random.Random(seed);streams=[];vals=[]
   for p in D:
    a=gen(p,deck,weighted,r);z=inspect(a);vals.append(z['score']);streams.append(dict(page=p['page'],indices=a,score=z['score'],source_scores=z['source_scores'],visits=z['visits']))
   if deck:assert sum(vals)==0
   full.write(json.dumps(dict(panel=panel,seed=seed,pages=streams))+'\n');rows.append(dict(seed=seed,scores=vals))
  total=sum(z['score'] for z in real);results['models'].append(dict(deck=deck,weighted=weighted,replicates=rows,p_upper=(1+sum(sum(z['scores'])>=total for z in rows))/1000))
results.update(seconds=time.monotonic()-start,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(OUT/'R02-results.json').write_text(json.dumps(results,indent=2)+'\n')
print('REAL',[(x['page'],x['score'],max(x['visits']),len(x['witnesses'])) for x in real]);print('MODELS',[(x['deck'],x['weighted'],x['p_upper']) for x in results['models']])
