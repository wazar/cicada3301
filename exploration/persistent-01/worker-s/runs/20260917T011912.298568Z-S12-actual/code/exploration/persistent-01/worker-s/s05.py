import json,pathlib,random,itertools,hashlib
BASE=pathlib.Path('exploration/persistent-01/worker-s');SOURCE=pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json');rng=random.Random(1709202605)
pages=[p for p in json.loads(SOURCE.read_text()) if p['page'] in [0,1]]
def maskof(seq):
 m=0
 for v in seq:m^=1<<v
 return m
def solve(eqs,n=29):
 basis={}
 for i,(a,b) in enumerate(eqs):
  witness=1<<i
  while a:
   bit=a.bit_length()-1
   if bit not in basis:basis[bit]=(a,b,witness);break
   c,d,w=basis[bit];a^=c;b^=d;witness^=w
  else:
   if b:return {'feasible':False,'rank_so_far':len(basis),'witness':[j for j in range(len(eqs)) if witness>>j&1]}
 # ascending pivot triangular solve, arbitrary free coordinates zero.
 def fill(free,homogeneous=False):
  x=free
  for pivot,(a,b,w) in sorted(basis.items()):
   if ((a&x).bit_count()%2) != (0 if homogeneous else b):x^=1<<pivot
  return x
 particular=fill(0); freevars=[i for i in range(n) if i not in basis]
 return {'feasible':True,'rank':len(basis),'particular':particular,'nullspace':[fill(1<<i,True) for i in freevars],'free_variables':freevars}
def rank(eqs):return solve([(a,0) for a,b in eqs])['rank']
def cardinality(eqs):
 cols=[sum((bool(a>>j&1))<<i for i,(a,b) in enumerate(eqs)) for j in range(29)];target=sum(b<<i for i,(a,b) in enumerate(eqs))
 def enum(cs):
  syndromes=[0]*(1<<len(cs));weights=[0]*len(syndromes)
  for mask in range(1,len(syndromes)):
   low=mask&-mask;old=mask^low;syndromes[mask]=syndromes[old]^cs[low.bit_length()-1];weights[mask]=weights[old]+1
  return syndromes,weights
 sa,wa=enum(cols[:14]);sb,wb=enum(cols[14:]);lookup={(v,w):i for i,(v,w) in enumerate(zip(sa,wa))}
 for j,(v,w) in enumerate(zip(sb,wb)):
  i=lookup.get((target^v,14-w))
  if i is not None:return i|(j<<14)
 return None
# Tiny consistency control includes contradictions and underdetermination.
tiny=[]
for rep in range(100):
 eqs=[(rng.randrange(16),rng.randrange(2)) for _ in range(rng.randrange(1,9))];valid=[x for x in range(16) if all((a&x).bit_count()%2==b for a,b in eqs)];r=solve(eqs,4)
 assert r['feasible']==bool(valid)
 if valid:
  assert r['particular'] in valid
  represented={r['particular']}
  for v in r['nullspace']:represented|={x^v for x in list(represented)}
  assert represented==set(valid)
 tiny.append({'equations':eqs,'valid':valid,'solution':r})
controls=[]
for rep in range(100):
 mapping=list(range(29));rng.shuffle(mapping);inv={v:k for k,v in enumerate(mapping)};hidden=sum((d%2)<<i for i,d in enumerate(mapping));assert hidden.bit_count()==14
 cp=[]
 for p in pages:
  xs=[]
  for w in p['words']:
   ds=[rng.randrange(29) for _ in range(w['end']-w['start'])]
   if sum(ds)%2==0:ds[-1]=ds[-1]+1 if ds[-1]<28 else 27
   xs.extend(inv[d] for d in ds)
  eqs=[(maskof(xs[w['start']:w['end']]),1) for w in p['words'] if len(set(xs[w['start']:w['end']]))>=3]
  assert all((a&hidden).bit_count()%2==b for a,b in eqs);r=solve(eqs);assert r['feasible']
  cp.append({'page':p['page'],'runes':xs,'solution':r})
 controls.append({'mapping':mapping,'hidden_parity':hidden,'pages':cp})
fixtures=[]
for prime in [2,3,5,29,31,101,1009,10007,65537]:
 assert all(prime%d for d in range(2,int(prime**.5)+1))
 digits=[];n=prime
 while n:digits.append(n%29);n//=29
 digits=[0,0]+digits[::-1];eligible=len(set(digits))>=3
 assert sum(d*29**i for i,d in enumerate(reversed(digits)))==prime
 if prime==2:assert not eligible and sum(digits)%2==0
 if eligible:assert sum(digits)%2==1
 fixtures.append({'prime':prime,'leading_zero_digits':digits,'eligible':eligible})
real=[]
for p in pages:
 rows=[];excluded=[]
 for wi,w in enumerate(p['words']):
  xs=p['indices'][w['start']:w['end']];row={'word_index':wi,'map':w,'runes':xs,'distinct':len(set(xs)),'mask':maskof(xs),'rhs':1}
  (rows if row['distinct']>=3 else excluded).append(row)
 eqs=[(r['mask'],1) for r in rows];r=solve(eqs);witness=[];card=None
 if not r['feasible']:
  selected=r['witness'][:]
  for j in selected[:]:
   trial=[k for k in selected if k!=j]
   if not solve([eqs[k] for k in trial])['feasible']:selected=trial
  for j in selected:assert solve([eqs[k] for k in selected if k!=j])['feasible']
  witness=[rows[j] for j in selected];xor=0
  # independent checker reconstructs from original symbols, not stored row masks.
  for row in witness:
   w=p['words'][row['word_index']]
   for v in p['indices'][w['start']:w['end']]:xor^=1<<v
  assert xor==0 and len(witness)%2==1
 else:
  card=cardinality(eqs)
  if card is not None:assert card.bit_count()==14 and all((a&card).bit_count()%2==b for a,b in eqs)
 real.append({'page':p['page'],'coefficient_rank':rank(eqs),'eligible':rows,'excluded':excluded,'elimination':r,'inclusion_minimal_contradiction':witness,'odd_cardinality_14_assignment':card,'cardinality_test_run':r['feasible']})
summary={'seed':1709202605,'input_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'tiny_systems':len(tiny),'tiny_assignments':1600,'hidden_bijection_controls':100,'control_pages':200,'fixtures':fixtures,'real':[{'page':r['page'],'eligible_words':len(r['eligible']),'excluded_words':len(r['excluded']),'rank':r['coefficient_rank'],'feasible':r['elimination']['feasible'],'witness_words':[w['word_index'] for w in r['inclusion_minimal_contradiction']],'cardinality_test_run':r['cardinality_test_run']} for r in real]}
(BASE/'S05-result.json').write_text(json.dumps({'summary':summary,'real':real,'controls':controls,'tiny':tiny},indent=2)+'\n');print(json.dumps(summary,indent=2))
