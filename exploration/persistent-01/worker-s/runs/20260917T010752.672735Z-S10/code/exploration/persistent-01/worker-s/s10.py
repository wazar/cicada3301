import pathlib,json,random,itertools,hashlib
BASE=pathlib.Path('exploration/persistent-01/worker-s');SOURCE=pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json');rng=random.Random(1709202610)
pages=[p for p in json.loads(SOURCE.read_text()) if p['page'] in [0,1]]
def eliminate(rows,n=29,p=29):
 basis={};selected=[]
 for ri,row in enumerate(rows):
  a=[v%p for v in row]
  for j in range(n-1,-1,-1):
   if not a[j]:continue
   if j in basis:
    c=a[j];a=[(x-c*y)%p for x,y in zip(a,basis[j])]
   else:
    inv=pow(a[j],-1,p);basis[j]=[(x*inv)%p for x in a];selected.append(ri);break
 null=[]
 for free in [i for i in range(n) if i not in basis]:
  v=[0]*n;v[free]=1
  for j,a in sorted(basis.items()):v[j]=-sum(x*y for x,y in zip(a,v))%p
  assert all(sum(x*y for x,y in zip(a,v))%p==0 for a in rows);null.append(v)
 return {'rank':len(basis),'basis_source_rows':selected,'nullspace':null}
def equations(xs,words,positions=None):
 rows=[];maps=[]
 for wi,w in enumerate(words):
  for i in range(w['start']+2,w['end']):
   a,b,c=xs[i-2:i+1];row=[0]*29;row[a]-=1;row[b]-=1;row[c]+=1;rows.append(row);m={'word':wi,'rune_positions':[i-2,i-1,i],'rune_labels':[a,b,c],'integer_coefficients':row}
   if positions is not None:m['source_char_positions']=[positions[i-2],positions[i-1],positions[i]]
   maps.append(m)
 return rows,maps
def bareiss(matrix):
 a=[r[:] for r in matrix];n=len(a);sign=1;prev=1
 if not n:return 1
 for k in range(n-1):
  pivot=next((i for i in range(k,n) if a[i][k]),None)
  if pivot is None:return 0
  if pivot!=k:a[k],a[pivot]=a[pivot],a[k];sign*=-1
  value=a[k][k]
  for i in range(k+1,n):
   for j in range(k+1,n):
    numerator=a[i][j]*value-a[i][k]*a[k][j];assert numerator%prev==0;a[i][j]=numerator//prev
   a[i][k]=0
  prev=value
 return sign*a[-1][-1]
tiny=[]
for rep in range(100):
 rows=[[rng.randrange(5) for _ in range(3)] for _ in range(rng.randrange(1,7))];r=eliminate(rows,3,5);valid={v for v in itertools.product(range(5),repeat=3) if all(sum(x*y for x,y in zip(a,v))%5==0 for a in rows)};represented={tuple(sum(c*v[j] for c,v in zip(coeff,r['nullspace']))%5 for j in range(3)) for coeff in itertools.product(range(5),repeat=len(r['nullspace']))};assert represented==valid
 if r['rank']==3:assert bareiss([rows[i] for i in r['basis_source_rows']])%5!=0
 tiny.append({'rows':rows,'solution':r,'valid_vectors':sorted(valid)})
controls=[]
for rep in range(30):
 mapping=list(range(29));rng.shuffle(mapping);inv={v:k for k,v in enumerate(mapping)};panels=[]
 for page in pages:
  xs=[];states=[]
  for w in page['words']:
   n=w['end']-w['start'];ys=[rng.randrange(29) for _ in range(min(n,2))]
   while len(ys)<n:ys.append((ys[-1]+ys[-2])%29)
   states.extend(ys);xs.extend(inv[y] for y in ys)
  rows,maps=equations(xs,page['words']);r=eliminate(rows);assert r['rank']<29
  assert all(sum(x*y for x,y in zip(a,mapping))%29==0 for a in rows)
  # Free coordinates determine the fullvector; reconstruct from returnedbasis.
  free=[next(i for i,a in enumerate(v) if a==1 and all(other[i]==0 for other in r['nullspace'] if other is not v)) for v in r['nullspace']] if False else None
  panels.append({'page':page['page'],'runes':xs,'states':states,'solution':r})
 controls.append({'mapping':mapping,'pages':panels})
real=[]
for page in pages:
 rows,maps=equations(page['indices'],page['words'],page['source_char_positions']);r=eliminate(rows);cert=[maps[i] for i in r['basis_source_rows']];det=None;forced=[];injection=None
 if r['rank']==29:
  det=bareiss([m['integer_coefficients'] for m in cert]);assert det%29!=0;verdict='NO_BIJECTION_FULL_RANK'
 else:
  forced=[(a,b) for a in range(29) for b in range(a+1,29) if all(v[a]==v[b] for v in r['nullspace'])]
  injection=next((v for v in r['nullspace'] if len(set(v))==29),None);verdict='NO_BIJECTION_FORCED_EQUALITY' if forced else ('EXPLICIT_COMPATIBLE_MAP' if injection else 'INCONCLUSIVE')
 real.append({'page':page['page'],'equations':maps,'solution':r,'source_certificate':cert,'integer_determinant':det,'determinant_mod29':None if det is None else det%29,'forced_equalities':forced,'injective_map':injection,'verdict':verdict})
summary={'seed':1709202610,'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'tiny_cases':100,'tiny_assignments':12500,'hidden_maps':30,'generated_page_controls':60,'control_ranks':sorted(set(p['solution']['rank'] for c in controls for p in c['pages'])),'real':[{'page':r['page'],'equations':len(r['equations']),'rank':r['solution']['rank'],'certificate_rows':len(r['source_certificate']),'integer_determinant':r['integer_determinant'],'determinant_mod29':r['determinant_mod29'],'verdict':r['verdict']} for r in real]}
(BASE/'S10-result.json').write_text(json.dumps({'summary':summary,'real':real,'controls':controls,'tiny':tiny},indent=2)+'\n');print(json.dumps(summary,indent=2))
