from pathlib import Path
import json,gzip,itertools,hashlib
O=Path(__file__).resolve().parent;R=O.parents[2];B=R/'exploration/persistent-01/worker-n/N12';F=R/'exploration/persistent-01/worker-f/F06-maps.json';pages={p['page']:p for p in json.loads(F.read_text())};x=json.loads((B/'actual.json').read_text());assert hashlib.sha256(F.read_bytes()).hexdigest()==x['source_sha256']
def row(seq):
 r=[0]*30;r[29]=1
 for v in seq[:-1]:r[v]+=1
 r[seq[-1]]-=1
 return r
def det(A,p):
 a=[[v%p for v in r] for r in A];n=len(a);d=1
 for col in range(n):
  piv=next((i for i in range(col,n) if a[i][col]),None)
  if piv is None:return 0
  if piv!=col:a[col],a[piv]=a[piv],a[col];d=-d
  t=a[col][col];d=d*t%p;inv=pow(t,-1,p)
  for i in range(col+1,n):
   f=a[i][col]*inv%p;a[i]=[(v-f*w)%p for v,w in zip(a[i],a[col])]
 return d%p
cert=[]
for item in x['actual']:
 p=pages[item['page']];expected=[]
 for wi,w in enumerate(p['words']):
  seq=p['indices'][w['start']:w['end']]
  if len(seq)>=3:expected.append(dict(word=wi,map=w,runes=seq,row=row(seq)))
 assert expected==item['equations']
 rr=item['result'];a=[]
 for e in rr['certificate']:
  assert e in expected;a.append(row(e['runes']))
 d=det(a,29);assert d and d==rr['determinant_mod29']==rr['integer_determinant']%29
 cert.append(dict(page=p['page'],equations=len(expected),certificate_rows=len(a),determinant_mod29=d))
c=json.load(gzip.open(B/'controls.json.gz','rt'));count=0
for rep in c['controls']:
 f=rep['map'];b=rep['offset'];assert sorted(f)==list(range(29))
 for panel in rep['panels']:
  p=pages[panel['page']];seq=panel['runes'];assert len(seq)==len(p['indices'])
  for w in p['words']:
   a,z=w['start'],w['end']
   if z-a<3:assert seq[a:z]==p['indices'][a:z]
   else:
    assert seq[a:z-1]==p['indices'][a:z-1]
    assert f[seq[z-1]]==(sum(f[v] for v in seq[a:z-1])+b)%29
  assert panel['analysis']['result']['disposition']=='INCONCLUSIVE';count+=1
for t in c['tiny']:
 actual=[list(v) for v in itertools.product(range(5),repeat=3) if all(sum(a*b for a,b in zip(r,v))%5==0 for r in t['A'])];assert actual==t['solutions']
result=dict(pass_=True,actual=cert,positive_panels=count,tiny_systems=len(c['tiny']),source_sha256=x['source_sha256'],limits='No author imports; modular certificate sufficient for exact impossibility. Did not independently regenerate RNG or integer determinant; author separate checker covers those.')
(O/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
