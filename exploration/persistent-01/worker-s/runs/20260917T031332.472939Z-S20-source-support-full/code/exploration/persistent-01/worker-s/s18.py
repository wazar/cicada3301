from pathlib import Path
import json,gzip,itertools,random,collections,hashlib,datetime,sys
B=Path('exploration/persistent-01/worker-s');SRC=Path('exploration/persistent-01/worker-f/F06-maps.json');SEED=1709202618
assert not Path('exploration/persistent-01/STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
pages=[p for p in json.loads(SRC.read_text()) if p['page'] in [0,1]];perms=list(itertools.permutations(range(3)));identity=perms.index((0,1,2))
def compose(a,b):return tuple(b[a[i]] for i in range(3)) # execute a, then b
mul=[[perms.index(compose(a,b)) for b in perms] for a in perms];inv=[next(j for j in range(6) if mul[i][j]==identity) for i in range(6)];sign=[sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))%2 for p in perms];cycle=perms.index((1,2,0));even={identity:0,cycle:1,mul[cycle][cycle]:2}
assert len(even)==3
for a in range(6):
 for b in range(6):
  assert sign[mul[a][b]]==(sign[a]+sign[b])%2
  if a in even and b in even:assert even[mul[a][b]]==(even[a]+even[b])%3

def matrix(words,n):return [[w.count(r) for r in range(n)] for w in words]
def rank(A,p):
 basis={};ids=[]
 for ri,row in enumerate(A):
  a=[x%p for x in row]
  for j in range(len(a)):
   if not a[j]:continue
   if j not in basis:
    scale=pow(a[j],-1,p);basis[j]=[x*scale%p for x in a];ids.append(ri);break
   scale=a[j];a=[(x-scale*y)%p for x,y in zip(a,basis[j])]
 return len(basis),ids

def inverse(A,p):
 n=len(A);rows=[[x%p for x in a]+[int(i==j) for j in range(n)] for i,a in enumerate(A)]
 for j in range(n):
  pivot=next(i for i in range(j,n) if rows[i][j]);rows[j],rows[pivot]=rows[pivot],rows[j];scale=pow(rows[j][j],-1,p);rows[j]=[x*scale%p for x in rows[j]]
  for i in range(n):
   if i!=j:
    scale=rows[i][j];rows[i]=[(a-scale*b)%p for a,b in zip(rows[i],rows[j])]
 assert [r[:n] for r in rows]==[[int(i==j) for j in range(n)] for i in range(n)]
 return [r[n:] for r in rows]
def route(words,n=29):
 A=matrix(words,n);r2,ids2=rank(A,2);r3,ids3=rank(A,3)
 return {'A':A,'rank_mod2':r2,'rank_mod3':r3,'obstructed':r2==n and r3==n,'certificates':[{'field':p,'word_indices':ids,'inverse':inverse([A[i] for i in ids],p)} for p,r,ids in [(2,r2,ids2),(3,r3,ids3)] if r==n]}
def product(w,m):
 x=identity
 for r in w:x=mul[x][m[r]]
 return x
if sys.argv[1]=='controls':
 rng=random.Random(SEED);panels=[]
 for rep in range(20):
  for page in pages:
   m=list(range(6))+[rng.randrange(6) for _ in range(23)];rng.shuffle(m);bins={op:[r for r in range(29) if m[r]==op] for op in range(6)};words=[];traces=[]
   for w in page['words']:
    prefix=[rng.randrange(29) for _ in range(w['end']-w['start']-1)];op=product(prefix,m);last=rng.choice(bins[inv[op]]);full=prefix+[last];assert product(full,m)==identity
    states=[]
    for initial in range(3):
     s=initial;path=[s]
     for r in full:s=perms[m[r]][s];path.append(s)
     assert s==initial;states.append(path)
    words.append(full);traces.append({'prefix_product':op,'required_last_opcode':inv[op],'last_rune':last,'state_paths':states})
   assert set(m)==set(range(6));assert any(m[r]!=identity for w in words for r in w);result=route(words);assert not result['obstructed'];panels.append({'rep':rep,'page':page['page'],'map':m,'words':words,'traces':traces,'result':result})
 tiny=[]
 for case in range(64):
  words=[[rng.randrange(3) for _ in range(rng.randrange(1,7))] for _ in range(rng.randrange(1,8))] if case<63 else [[0],[1],[2]]
  r=route(words,3);used=set(x for w in words for x in w);solutions=[list(m) for m in itertools.product(range(6),repeat=3) if any(m[x]!=identity for x in used) and all(product(w,m)==identity for w in words)];assert not (r['obstructed'] and solutions);tiny.append({'words':words,'result':r,'nontrivial_solutions':solutions})
 data={'seed':SEED,'permutations':perms,'product_table':mul,'inverse_table':inv,'sign':sign,'even_exponents':even,'panels':panels,'tiny':tiny};(B/'S18-controls.json.gz').write_bytes(gzip.compress(json.dumps(data).encode(),mtime=0));print(json.dumps({'positive_panels':len(panels),'tiny_panels':len(tiny),'tiny_assignments':64*216,'tiny_obstructed':sum(t['result']['obstructed'] for t in tiny),'tiny_solution_panels':sum(bool(t['nontrivial_solutions']) for t in tiny)}))
else:
 assert sys.argv[1]=='actual' and (B/'S18-controls.json.gz').exists();out=[]
 for page in pages:
  words=[page['indices'][w['start']:w['end']] for w in page['words']];r=route(words)
  for cert in r['certificates']:cert['source_words']=[{'word_index':i,'runes':words[i],'map':page['words'][i]} for i in cert['word_indices']]
  out.append({'page':page['page'],'rune_count':len(page['indices']),'word_count':len(words),'used_labels':sorted(set(page['indices'])),'result':r})
 (B/'S18-result.json').write_text(json.dumps({'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'pages':out},indent=2));print(json.dumps([{'page':p['page'],'words':p['word_count'],'used_count':len(p['used_labels']),'rank2':p['result']['rank_mod2'],'rank3':p['result']['rank_mod3'],'obstructed':p['result']['obstructed']} for p in out]))
