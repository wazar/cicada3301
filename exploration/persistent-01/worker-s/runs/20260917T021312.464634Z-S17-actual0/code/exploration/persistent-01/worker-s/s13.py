import pathlib,json,random,math,functools,hashlib,gzip
from fractions import Fraction as F
B=pathlib.Path('exploration/persistent-01/worker-s');SRC=pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json');pages=[p for p in json.loads(SRC.read_text()) if p['page'] in [0,1]];rng=random.Random(1709202613)
def eliminate(A,b):
 n=len(A[0]);m=len(A);basis={}
 for i,(row,rhs) in enumerate(zip(A,b)):
  a=list(map(F,row));z=F(rhs);weights=[F(int(j==i)) for j in range(m)]
  for pivot in range(n):
   if not a[pivot]:continue
   if pivot not in basis:
    scale=a[pivot];basis[pivot]=([x/scale for x in a],z/scale,[x/scale for x in weights]);break
   v,t,w=basis[pivot];scale=a[pivot];a=[x-scale*y for x,y in zip(a,v)];z-=scale*t;weights=[x-scale*y for x,y in zip(weights,w)]
  else:
   if z:
    lcm=math.lcm(*(w.denominator for w in weights));integers=[int(w*lcm) for w in weights];divisor=functools.reduce(math.gcd,integers);integers=[w//abs(divisor) for w in integers]
    if sum(x*y for x,y in zip(integers,b))<0:integers=[-w for w in integers]
    return {'consistent':False,'rank_at_contradiction':len(basis),'contradiction_row':i,'multipliers':integers}
 return {'consistent':True,'rank':len(basis)}
def certificate(A,b,r):
 w=r['multipliers'];assert all(sum(mult*row[j] for mult,row in zip(w,A))==0 for j in range(len(A[0])));assert sum(mult*rhs for mult,rhs in zip(w,b))!=0
small=[]
for i in range(20):
 target=[rng.randrange(-2,3) for _ in range(3)];A=[[rng.randrange(3) for _ in range(3)] for _ in range(5)];rhs=[sum(a*x for a,x in zip(row,target)) for row in A];good=eliminate(A,rhs);assert good['consistent'];bad=eliminate(A+[A[0]],rhs+[rhs[0]+1]);assert not bad['consistent'];certificate(A+[A[0]],rhs+[rhs[0]+1],bad);small.append({'A':A,'rhs':rhs,'target':target,'good':good,'bad_duplicate_first':bad})
def equations(xs,words):
 return [[xs[w['start']:w['end']].count(r) for r in range(29)] for w in words]
def tree(n,classes):
 arity=0 if n==1 else (rng.choice([1,2]) if n>=3 else 1);op=rng.choice(classes[arity])
 if arity==0:return {'operator':op,'children':[]}
 if arity==1:return {'operator':op,'children':[tree(n-1,classes)]}
 size=rng.randrange(1,n-1);return {'operator':op,'children':[tree(size,classes),tree(n-1-size,classes)]}
def emit(t):return [r for child in t['children'] for r in emit(child)]+[t['operator']]
controls=[]
for rep in range(10):
 labels=list(range(29));rng.shuffle(labels);classes={0:labels[:13],1:labels[13:21],2:labels[21:]};arity={r:a for a,vs in classes.items() for r in vs};weights=[1-arity[r] for r in range(29)];cp=[]
 for page in pages:
  xs=[];trees=[];traces=[]
  for w in page['words']:
   t=tree(w['end']-w['start'],classes);seq=emit(t);assert len(seq)==w['end']-w['start'];stack=0;trace=[]
   for op in seq:assert stack>=arity[op];stack+=1-arity[op];trace.append(stack)
   assert stack==1;xs+=seq;trees.append(t);traces.append(trace)
  A=equations(xs,page['words']);assert all(sum(a*x for a,x in zip(row,weights))==1 for row in A);r=eliminate(A,[1]*len(A));assert r['consistent'];cp.append({'page':page['page'],'runes':xs,'trees':trees,'stack_traces':traces,'result':r})
 controls.append({'arity':arity,'weights':weights,'pages':cp})
real=[]
for page in pages:
 A=equations(page['indices'],page['words']);r=eliminate(A,[1]*len(A));cert=[]
 if not r['consistent']:
  certificate(A,[1]*len(A),r)
  # Independent direct raw-rune weighted accumulation, not storedcount rows.
  totals=[0]*29
  for wi,mult in enumerate(r['multipliers']):
   if not mult:continue
   w=page['words'][wi];seq=page['indices'][w['start']:w['end']]
   for rune in seq:totals[rune]+=mult
   cert.append({'word_index':wi,'multiplier':mult,'map':w,'runes':seq})
  assert totals==[0]*29 and sum(v['multiplier'] for v in cert)!=0
 real.append({'page':page['page'],'A':A,'rhs':[1]*len(A),'result':r,'source_certificate':cert,'weighted_rhs':sum(v['multiplier'] for v in cert) if cert else None})
summary={'seed':1709202613,'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'tiny_planted':20,'tiny_contradictions':20,'control_operator_maps':10,'control_page_panels':20,'control_ranks':sorted(set(p['result']['rank'] for c in controls for p in c['pages'])),'real':[{'page':r['page'],'word_equations':len(r['A']),'consistent':r['result']['consistent'],'rank_at_contradiction':r['result'].get('rank_at_contradiction'),'certificate_words':len(r['source_certificate']),'weighted_rhs':r['weighted_rhs']} for r in real]}
(B/'S13-result.json').write_text(json.dumps({'summary':summary,'real':real,'tiny':small},indent=2)+'\n');(B/'S13-controls.json.gz').write_bytes(gzip.compress(json.dumps(controls).encode(),mtime=0));print(json.dumps(summary,indent=2))
