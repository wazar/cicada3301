from pathlib import Path
import json,random,hashlib,gzip,itertools,time
R=Path(__file__).parent;B=R.parents[1];source=B/'worker-f/F06-maps.json';allpages=json.loads(source.read_text());pages=[p for p in allpages if p['page'] in [0,1]];assert len(pages)==2;rng=random.Random(1712092026)
def reduce(A,q,n):
 rows=[list(a) for a in A];indices=list(range(len(A)));piv=[];selected=[];at=0
 for j in range(n):
  k=next((i for i in range(at,len(rows)) if rows[i][j]%q),None)
  if k is None:continue
  rows[at],rows[k]=rows[k],rows[at];indices[at],indices[k]=indices[k],indices[at];v=pow(rows[at][j]%q,-1,q);rows[at]=[x*v%q for x in rows[at]]
  for i in range(len(rows)):
   if i!=at:
    v=rows[i][j]%q;rows[i]=[(x-v*y)%q for x,y in zip(rows[i],rows[at])]
  piv.append(j);selected.append(indices[at]);at+=1
  if at==len(rows):break
 free=[i for i in range(n) if i not in piv];basis=[]
 for f in free:
  v=[0]*n;v[f]=1
  for i,j in enumerate(piv):v[j]=-rows[i][f]%q
  basis.append(v)
 return dict(rank=at,pivots=piv,selected=selected,free=free,basis=basis)
def rows(p,xs):
 data=[]
 for wi,w in enumerate(p['words']):
  seq=xs[w['start']:w['end']]
  if len(seq)<3:continue
  a=[0]*30
  for v in seq[:-1]:a[v]+=1
  a[seq[-1]]-=1;a[29]=1;data.append(dict(word=wi,map=w,runes=seq,row=a))
 return data
def det(A):
 a=[r[:] for r in A];n=len(a);old=1;sign=1
 for k in range(n-1):
  if a[k][k]==0:
   j=next((j for j in range(k+1,n) if a[j][k]),None)
   if j is None:return 0
   a[k],a[j]=a[j],a[k];sign=-sign
  pivot=a[k][k]
  for i in range(k+1,n):
   for j in range(k+1,n):
    v=a[i][j]*pivot-a[i][k]*a[k][j];assert v%old==0;a[i][j]=v//old
   a[i][k]=0
  old=pivot
 return sign*a[-1][-1]
def solve(p,xs):
 data=rows(p,xs);A=[x['row'] for x in data];r=reduce(A,29,30);pairs=[(i,j) for i in range(29) for j in range(i+1,29) if all(v[i]==v[j] for v in r['basis'])];r['forced_collisions']=[list(x) for x in pairs]
 if r['rank']==30:
  cert=[data[i] for i in r['selected']];d=det([x['row'] for x in cert]);assert d%29;r.update(disposition='EXACT_EXCLUSION_FULL_RANK',certificate=cert,integer_determinant=d,determinant_mod29=d%29)
 elif pairs:r['disposition']='EXACT_EXCLUSION_FORCED_COLLISION'
 else:r['disposition']='INCONCLUSIVE'
 return dict(page=p['page'],equations=data,excluded_short_words=[i for i,w in enumerate(p['words']) if w['end']-w['start']<3],result=r)
tiny=[]
for i in range(100):
 A=[[rng.randrange(5) for _ in range(3)] for _ in range(rng.randrange(1,7))];r=reduce(A,5,3);brute={v for v in itertools.product(range(5),repeat=3) if all(sum(x*y for x,y in zip(row,v))%5==0 for row in A)};represented={tuple(sum(k*b[j] for k,b in zip(ks,r['basis']))%5 for j in range(3)) for ks in itertools.product(range(5),repeat=len(r['basis']))};assert brute==represented;tiny.append(dict(A=A,result=r,solutions=[list(v) for v in sorted(brute)]))
controls=[]
for i in range(30):
 f=list(range(29));rng.shuffle(f);inv=[f.index(j) for j in range(29)];b=rng.randrange(29);panels=[]
 for p in pages:
  xs=p['indices'][:]
  for w in p['words']:
   if w['end']-w['start']>=3:xs[w['end']-1]=inv[(sum(f[v] for v in xs[w['start']:w['end']-1])+b)%29]
  sol=solve(p,xs);truth=f+[b];assert all(sum(a*v for a,v in zip(e['row'],truth))%29==0 for e in sol['equations']);assert not sol['result']['forced_collisions'] and sol['result']['rank']<30;panels.append(dict(page=p['page'],runes=xs,analysis=sol))
 controls.append(dict(replicate=i,map=f,offset=b,panels=panels))
(R/'controls.json.gz').write_bytes(gzip.compress(json.dumps(dict(seed=1712092026,tiny=tiny,controls=controls)).encode(),mtime=0));print('CONTROLS PASS 60 panels +12500 tiny assignments',flush=True)
actual=[solve(p,p['indices']) for p in pages];out=dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),actual=actual);(R/'actual.json').write_text(json.dumps(out,indent=2));print(json.dumps([dict(page=x['page'],equations=len(x['equations']),rank=x['result']['rank'],disposition=x['result']['disposition'],determinant=x['result'].get('integer_determinant')) for x in actual],indent=2))
