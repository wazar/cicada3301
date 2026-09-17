from pathlib import Path
import json,gzip,random,itertools,collections,hashlib,sys,datetime
B=Path('exploration/persistent-01/worker-s');SRC=Path('exploration/persistent-01/worker-f/F06-maps.json');SEED=1709202616
assert not Path('exploration/persistent-01/STOP').exists()
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
pages=[p for p in json.loads(SRC.read_text()) if p['page'] in [0,1]]
def edges(words):
 out=[]
 for wi,w in enumerate(words):
  for rot in range(1,len(w)):
   for k in range(len(w)):
    if w[k]!=w[(k+rot)%len(w)]:
     out.append({'word_index':wi,'rotation':rot,'mismatch':k,'a':w[k],'b':w[(k+rot)%len(w)]});break
 return out

def graph(words,n=29):
 es=edges(words);adj=[set() for _ in range(n)];degree=[0]*n
 for e in es:adj[e['a']].add(e['b'])
 for a in adj:
  for b in a:degree[b]+=1
 q=collections.deque(i for i in range(n) if degree[i]==0);order=[]
 while q:
  a=q.popleft();order.append(a)
  for b in sorted(adj[a]):
   degree[b]-=1
   if degree[b]==0:q.append(b)
 if len(order)==n:return {'feasible':True,'order':order,'edges':es}
 shortest=None
 for start in range(n):
  q=collections.deque([[start]]);seen={start}
  while q:
   path=q.popleft()
   for v in sorted(adj[path[-1]]):
    if v==start:
     cyc=path+[start]
     if shortest is None or len(cyc)<len(shortest):shortest=cyc
     q.clear();break
    if v not in seen:seen.add(v);q.append(path+[v])
 assert shortest
 witness=[next(e for e in es if e['a']==a and e['b']==b) for a,b in zip(shortest,shortest[1:])]
 return {'feasible':False,'cycle':shortest,'witness':witness,'edges':es}
def minimal(w,rank):return all(tuple(rank[a] for a in w)<=tuple(rank[a] for a in w[r:]+w[:r]) for r in range(len(w)))
def check(words,r,n):
 if r['feasible']:
  rank={a:i for i,a in enumerate(r['order'])};assert len(rank)==n;assert all(minimal(w,rank) for w in words)
 else:
  assert r['cycle'][0]==r['cycle'][-1];assert len(r['witness'])==len(r['cycle'])-1
  for i,e in enumerate(r['witness']):
   w=words[e['word_index']];rot=w[e['rotation']:]+w[:e['rotation']];k=e['mismatch'];assert w[:k]==rot[:k] and w[k]!=rot[k];assert (w[k],rot[k])==(r['cycle'][i],r['cycle'][i+1])
if sys.argv[1]=='controls':
 rng=random.Random(SEED);panels=[]
 for rep in range(20):
  for p in pages:
   order=list(range(29));rng.shuffle(order);rank={a:i for i,a in enumerate(order)};raw=[];canonical=[];rotations=[]
   for w in p['words']:
    a=[rng.randrange(29) for _ in range(w['end']-w['start'])];r=min(range(len(a)),key=lambda r:tuple(rank[x] for x in a[r:]+a[:r]));raw.append(a);canonical.append(a[r:]+a[:r]);rotations.append(r)
   result=graph(canonical);assert result['feasible'];check(canonical,result,29);panels.append({'rep':rep,'page':p['page'],'order':order,'raw_circles':raw,'rotations':rotations,'canonical':canonical,'result':result})
 tiny=[]
 for n,maxlen,pairs in [(3,4,True),(4,3,False)]:
  words=[list(w) for length in range(1,maxlen+1) for w in itertools.product(range(n),repeat=length)];orders=list(itertools.permutations(range(n)));ranks=[{a:i for i,a in enumerate(o)} for o in orders];valid=[[minimal(w,rank) for rank in ranks] for w in words];counts={'n':n,'maxlen':maxlen,'word_count':len(words),'orders':len(orders),'panels':0,'feasible':0}
  groups=itertools.combinations_with_replacement(range(len(words)),2) if pairs else ((i,) for i in range(len(words)))
  for ids in groups:
   ww=[words[i] for i in ids];expected=any(all(valid[i][k] for i in ids) for k in range(len(orders)));actual=graph(ww,n);assert actual['feasible']==expected;check(ww,actual,n);counts['panels']+=1;counts['feasible']+=expected
  tiny.append(counts)
 bad=[]
 for words in [[[0,1],[1,0]],[[0,1],[1,2],[2,0]]]:
  result=graph(words,3);assert not result['feasible'];check(words,result,3);bad.append({'words':words,'result':result})
 (B/'S16-controls.json.gz').write_bytes(gzip.compress(json.dumps({'seed':SEED,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'panels':panels,'tiny':tiny,'bad':bad}).encode(),mtime=0));print(json.dumps({'panels':len(panels),'tiny':tiny,'explicit_bad':len(bad)},indent=2))
else:
 assert sys.argv[1]=='actual' and (B/'S16-controls.json.gz').exists();out=[]
 for p in pages:
  words=[p['indices'][w['start']:w['end']] for w in p['words']];r=graph(words);check(words,r,29)
  for e in r.get('witness',[]):
   w=p['words'][e['word_index']];e['word_map']=w;e['runes']=words[e['word_index']];e['source_a']=p['source_char_positions'][w['start']+e['mismatch']];e['source_b']=p['source_char_positions'][w['start']+(e['mismatch']+e['rotation'])%len(e['runes'])]
  out.append({'page':p['page'],'word_count':len(words),'words':words,'result':r})
 (B/'S16-result.json').write_text(json.dumps({'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'pages':out},indent=2));print(json.dumps([{'page':p['page'],'word_count':p['word_count'],'constraints':len(p['result']['edges']),'feasible':p['result']['feasible'],'cycle':p['result'].get('cycle'),'witness':p['result'].get('witness')} for p in out],indent=2))
