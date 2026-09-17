from pathlib import Path
import json,hashlib,itertools,random,math,collections
R=Path(__file__).parent;B=R.parent;S=B/'worker-s';P=[p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,1]];a=json.loads((S/'S05-result.json').read_text());b=json.loads((S/'S06-result.json').read_text());(R/'snapshots').mkdir(exist_ok=True);inputs={}
for path in [B/'worker-f/F06-maps.json']+[S/(stem+ext) for stem in ['S05','S06'] for ext in ['-CARD.md','-result.json']]+[S/'s05.py',S/'s06.py']:
 raw=path.read_bytes();inputs[str(path)]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)};(R/'snapshots'/path.name).write_bytes(raw)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
def eq(seq):
 counts=collections.Counter(seq);return sum(1<<k for k,v in counts.items() if v%2)
def rank(rows,n=29):
 # Low-to-high dense Boolean elimination, unlike production sparse high pivot masks.
 M=[[bool(mask>>j&1) for j in range(n)]+[bool(rhs)] for mask,rhs in rows];r=0
 for j in range(n):
  pivot=next((i for i in range(r,len(M)) if M[i][j]),None)
  if pivot is None:continue
  M[r],M[pivot]=M[pivot],M[r]
  for i in range(len(M)):
   if i!=r and M[i][j]:M[i]=[x!=y for x,y in zip(M[i],M[r])]
  r+=1
 return r,not any(not any(row[:n]) and row[n] for row in M)
def verifies_solution(rows,sol,n=29):
 r,feasible=rank(rows,n);assert sol['feasible']==feasible
 if feasible:
  assert sol['rank']==r and len(sol['nullspace'])==n-r;assert all((mask&sol['particular']).bit_count()%2==rhs for mask,rhs in rows)
  assert all(all((mask&v).bit_count()%2==0 for mask,rhs in rows) for v in sol['nullspace']);assert rank([(v,0) for v in sol['nullspace']],n)[0]==n-r
 else:
  total=0;rhs=0
  for i in sol['witness']:total^=rows[i][0];rhs^=rows[i][1]
  assert total==0 and rhs==1
rng=random.Random(1709202605)
for tiny in a['tiny']:
 rows=[(rng.randrange(16),rng.randrange(2)) for _ in range(rng.randrange(1,9))];assert [list(r) for r in rows]==tiny['equations'];valid=[x for x in range(16) if all((mask&x).bit_count()%2==rhs for mask,rhs in rows)];assert valid==tiny['valid'];verifies_solution(rows,tiny['solution'],4)
for control in a['controls']:
 mapping=list(range(29));rng.shuffle(mapping);assert mapping==control['mapping'];inverse={v:k for k,v in enumerate(mapping)};hidden=sum((v%2)<<k for k,v in enumerate(mapping));assert hidden==control['hidden_parity'] and hidden.bit_count()==14
 for p,c in zip(P,control['pages']):
  xs=[]
  for w in p['words']:
   ds=[rng.randrange(29) for _ in range(w['end']-w['start'])]
   if sum(ds)%2==0:ds[-1]=ds[-1]+1 if ds[-1]<28 else 27
   xs.extend(inverse[d] for d in ds)
  assert xs==c['runes'];rows=[(eq(xs[w['start']:w['end']]),1) for w in p['words'] if len(set(xs[w['start']:w['end']]))>=3];verifies_solution(rows,c['solution']);assert all((m&hidden).bit_count()%2==rhs for m,rhs in rows)
minimal=[]
for p,r in zip(P,a['real']):
 eligible=[];excluded=[]
 for wi,w in enumerate(p['words']):
  seq=p['indices'][w['start']:w['end']];row=dict(word_index=wi,map=w,runes=seq,distinct=len(set(seq)),mask=eq(seq),rhs=1);(eligible if len(set(seq))>=3 else excluded).append(row);assert w['source_char_positions']==p['source_char_positions'][w['start']:w['end']]
 assert eligible==r['eligible'] and excluded==r['excluded'];rows=[(row['mask'],1) for row in eligible];assert rank(rows)[0]==r['coefficient_rank'];verifies_solution(rows,r['elimination']);assert not r['cardinality_test_run']
 witness=r['inclusion_minimal_contradiction'];assert all(row in eligible for row in witness);wr=[(eq(row['runes']),1) for row in witness];assert not rank(wr)[1];assert all(rank(wr[:i]+wr[i+1:])[1] for i in range(len(wr)));xor=0
 for mask,rhs in wr:xor^=mask
 assert xor==0 and len(wr)%2==1;minimal.append(len(wr))
for f in a['summary']['fixtures']:
 n=0
 for digit in f['leading_zero_digits']:n=n*29+digit
 assert n==f['prime'] and all(n%d for d in range(2,math.isqrt(n)+1));assert f['eligible']==(len(set(f['leading_zero_digits']))>=3)
 if n==2:assert not f['eligible']
# Enumerate cuts rather than recursive compositions for every actual/control length.
comps={}
for n in range(2,15):
 out=[]
 for cutset in range(1<<(n-1)):
  points=[0]+[j for j in range(1,n) if cutset>>(j-1)&1]+[n];lengths=tuple(y-x for x,y in zip(points,points[1:]))
  if set(lengths)<=set([2,3]):out.append(lengths)
 comps[n]=sorted(out)

def analyze(xs,words):
 forced={};alltilings={}
 for wi,w in enumerate(words):
  n=w['end']-w['start']
  if n==1:continue
  tilings=[]
  for sizes in comps[n]:
   pos=w['start'];tiles=[]
   for size in sizes:tiles.append(dict(token=xs[pos:pos+size],positions=[pos,pos+size]));pos+=size
   tilings.append(tiles)
  sets=[set(tuple(t['token']) for t in tiles) for tiles in tilings];inter=set.intersection(*sets)
  for token in inter:forced.setdefault(token,[]).append(wi)
  alltilings[wi]=tilings
 return forced,alltilings
rng=random.Random(1709202606)
for control in b['controls']:
 dictionary=[]
 for n,k in [(2,14),(3,15)]:
  chosen=set()
  while len(chosen)<k:chosen.add(tuple(rng.randrange(29) for _ in range(n)))
  dictionary.extend(sorted(chosen))
 assert [list(t) for t in dictionary]==control['dictionary']
 for p,c in zip(P,control['pages']):
  xs=[];paths=[]
  for w in p['words']:
   n=w['end']-w['start']
   if n==1:xs.append(rng.randrange(29));paths.append(dict(literal=xs[-1]));continue
   sizes=rng.choice(comps[n]);tokens=[rng.choice([t for t in dictionary if len(t)==size]) for size in sizes];xs.extend(v for t in tokens for v in t);paths.append(dict(tokens=[list(t) for t in tokens]))
  assert xs==c['runes'] and paths==c['paths'];forced,_=analyze(xs,p['words']);assert len(forced)==c['bound']<=29;assert set(forced)<=set(dictionary);assert {tuple(e['token']):e['supporting_words'] for e in c['forced_entries']}==forced
bounds=[];certificates=[]
for p,r in zip(P,b['real']):
 forced,tilings=analyze(p['indices'],p['words']);assert len(forced)==r['forced_lower_bound'];assert {tuple(e['token']):e['supporting_words'] for e in r['forced_entries']}==forced;assert r['literal_exempt_words']==[i for i,w in enumerate(p['words']) if w['end']-w['start']==1]
 for row in r['words']:
  wi=row['word_index'];w=p['words'][wi];assert row['map']==w and row['runes']==p['indices'][w['start']:w['end']];assert row['all_tilings']==tilings[wi];assert set(map(tuple,row['forced_tokens']))=={token for token,support in forced.items() if wi in support}
 cert=r['certificate30'];assert len(cert)==len(set(tuple(e['token']) for e in cert))==30
 for e in cert:assert e['supporting_word'] in forced[tuple(e['token'])]
 bounds.append(len(forced));certificates.append(len(cert))
out={'status':'PASS','S05_tiny_assignments':1600,'S05_control_pages':200,'S05_inclusion_minimal_words':minimal,'S05_cardinality_search_needed':False,'S06_control_pages':60,'S06_forced_bounds':bounds,'S06_distinct_certificate_tokens':certificates,'S06_all_composition_cutmasks':sum(1<<(n-1) for n in range(2,15))};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
