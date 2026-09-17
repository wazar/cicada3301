from pathlib import Path
import json,gzip,hashlib,itertools,random,collections,ast
from fractions import Fraction
R=Path(__file__).parent;B=R.parent;ROOT=B.parent.parent;S=B/'worker-s';P=B/'worker-p/P24';D=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page']);assert not {4,9,14,19,24,29,34,39,44,50,54}&{p['page'] for p in D};pages=[p for p in D if p['page'] in [0,1]];s=json.loads((S/'S10-result.json').read_text());initial=json.loads((S/'S10-initial-result.json').read_text());(R/'snapshots').mkdir(exist_ok=True);inputs={}
for path in [B/'worker-f/F06-maps.json',S/'s10.py',S/'S10-CARD.md',S/'S10-CONTROL-CHECK.md',S/'S10-result.json',S/'S10-initial-result.json',B/'worker-p/p24.py']+list(P.iterdir()):
 if path.is_file():
  raw=path.read_bytes();inputs[str(path)]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
  if path.suffix!='.gz':(R/'snapshots'/path.name).write_bytes(raw)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
def rref(rows,prime,n):
 a=[[v%prime for v in row] for row in rows];r=0;piv=[]
 for j in range(n):
  k=next((i for i in range(r,len(a)) if a[i][j]),None)
  if k is None:continue
  a[r],a[k]=a[k],a[r];inverse=pow(a[r][j],-1,prime);a[r]=[(v*inverse)%prime for v in a[r]]
  for i in range(len(a)):
   if i!=r:
    v=a[i][j];a[i]=[(x-v*y)%prime for x,y in zip(a[i],a[r])]
  piv.append(j);r+=1
 return r

def verify_null(rows,solution,prime,n):
 rank=rref(rows,prime,n);assert rank==solution['rank'];basis=solution['nullspace'];assert len(basis)==n-rank and rref(basis,prime,n)==len(basis);assert all(sum(x*y for x,y in zip(row,v))%prime==0 for row in rows for v in basis)
def eqs(xs,words,positions=None):
 rows=[];maps=[]
 for wi,w in enumerate(words):
  for i in range(w['start'],w['end']-2):
   triple=xs[i:i+3];row=[int(triple[2]==j)-int(triple[0]==j)-int(triple[1]==j) for j in range(29)];m=dict(word=wi,rune_positions=[i,i+1,i+2],rune_labels=triple,integer_coefficients=row)
   if positions is not None:m['source_char_positions']=positions[i:i+3]
   rows.append(row);maps.append(m)
 return rows,maps
rng=random.Random(1709202610)
for tiny in s['tiny']:
 rows=[[rng.randrange(5) for _ in range(3)] for _ in range(rng.randrange(1,7))];assert rows==tiny['rows'];valid=[list(v) for v in itertools.product(range(5),repeat=3) if all(sum(x*y for x,y in zip(row,v))%5==0 for row in rows)];assert valid==tiny['valid_vectors'];verify_null(rows,tiny['solution'],5,3)
for ctrl in s['controls']:
 mapping=list(range(29));rng.shuffle(mapping);assert mapping==ctrl['mapping'];inverse={v:k for k,v in enumerate(mapping)}
 for p,c in zip(pages,ctrl['pages']):
  states=[]
  for w in p['words']:
   n=w['end']-w['start'];seq=[rng.randrange(29) for _ in range(min(n,2))]
   while len(seq)<n:seq.append(sum(seq[-2:])%29)
   states+=seq
  xs=[inverse[v] for v in states];assert xs==c['runes'] and states==c['states'];rows,_=eqs(xs,p['words']);verify_null(rows,c['solution'],29,29);sol=c['solution'];reconstructed=[sum(mapping[f]*v[j] for f,v in zip(sol['free_variables'],sol['nullspace']))%29 for j in range(29)];assert reconstructed==mapping

def determinant(rows):
 a=[[Fraction(v) for v in row] for row in rows];det=Fraction(1)
 for j in range(len(a)):
  k=next((i for i in range(j,len(a)) if a[i][j]),None)
  if k is None:return 0
  if k!=j:a[k],a[j]=a[j],a[k];det=-det
  pivot=a[j][j];det*=pivot
  for i in range(j+1,len(a)):
   factor=a[i][j]/pivot
   for col in range(j+1,len(a)):a[i][col]-=factor*a[j][col]
   a[i][j]=0
 assert det.denominator==1;return int(det)
dets=[]
for p,r in zip(pages,s['real']):
 rows,maps=eqs(p['indices'],p['words'],p['source_char_positions']);assert maps==r['equations'];verify_null(rows,r['solution'],29,29);cert=r['source_certificate'];assert len(cert)==29 and all(m in maps for m in cert);det=determinant([m['integer_coefficients'] for m in cert]);assert det==r['integer_determinant'] and det%29==r['determinant_mod29']!=0;dets.append(det)
def stripfree(x):
 if isinstance(x,dict):return {k:stripfree(v) for k,v in x.items() if k!='free_variables'}
 if isinstance(x,list):return [stripfree(v) for v in x]
 return x
assert stripfree(initial)==stripfree(s)
# P24: renderer's forbidden pairs were independently proved in review39.
cert=json.loads((B/'review-39/result.json').read_text());forbidden=[tuple(x['pair']) for x in cert['forbidden_pair_certificates']];assert len(forbidden)==14 and all(a!=b for a,b in forbidden)
def graph(units):
 counts=collections.Counter();first={}
 for item in units:
  for k,(a,b) in enumerate(zip(item['runes'],item['runes'][1:])):
   counts[a,b]+=1;first.setdefault((a,b),dict(page=item['page'],unit=item['unit'],unit_positions=[k,k+1],source_rune_indices=item.get('source_rune_indices',[])[k:k+2],source_char_positions=item.get('source_char_positions',[])[k:k+2]))
 rows=[dict(pair=list(edge),count=counts[edge],witness=first[edge]) for edge in sorted(counts)];return counts,rows
actual=json.load(gzip.open(P/'actual.json.gz','rt'));units=[]
for p in D:
 for j,w in enumerate(p['words']):
  a,b=w['start'],w['end'];units.append(dict(page=p['page'],unit=j,runes=p['indices'][a:b],source_rune_indices=list(range(a,b)),source_char_positions=p['source_char_positions'][a:b]))
assert units==actual['units'];counts,rows=graph(units);assert rows==actual['graph']['observed'];allnonself={(i,j) for i in range(29) for j in range(29) if i!=j};assert allnonself<=set(counts) and len(allnonself)==812;assert actual['graph']['absent']==[];assert all(not d for d in actual['result']['initial_domains'].values());assert actual['result']['status']=='UNSAT' and actual['result']['nodes']==1 and actual['result']['proof']['domain']==[]
# Tiny injection checks, without invoking production solver.
for tiny in json.load(gzip.open(P/'tiny-controls.json.gz','rt')):
 e=[tuple(x) for x in tiny['edges']];target=set(map(tuple,tiny['target']));active=sorted({x for pair in e for x in pair});possible=False
 for v in itertools.permutations(range(tiny['n']),len(active)):
  m=dict(zip(active,v))
  if all((m[a],m[b]) in target for a,b in e):possible=True;break
 assert possible==(tiny['result']['status']=='SAT')
# Independent maximal-munch parser to validate found full mappings as format witnesses.
tree=ast.parse((ROOT/'liber-primus/src/lp/gematria.py').read_text());tab=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='GEMATRIA' for t in n.targets));ABC=''.join(r for i,r,t,p in tab);spell=[t for i,r,t,p in tab];lex={t:i for i,t in enumerate(spell)}|{'V':1,'K':5,'Q':5,'Z':15}
def parse(text):
 out=[];i=0
 while i<len(text):
  t=text[i:i+2] if text[i:i+2] in lex else text[i];out.append(lex[t]);i+=len(t)
 return out
import re
controlmismatch=[]
for ix in range(4):
 c=json.load(gzip.open(P/f'control-{ix}.json.gz','rt'));f=ROOT/c['source'];raw=f.read_text();assert hashlib.sha256(f.read_bytes()).hexdigest()==c['source_sha256'];words=[parse(''.join(spell[ABC.index(ch)] for ch in m.group())) for m in re.finditer('['+ABC+']+',raw)];assert words==c['words'];perm=list(range(29));random.Random(524100+ix).shuffle(perm);assert perm==c['planted_permutation'];cu=[dict(page=p['page'],unit=j,runes=[perm[v] for v in word]) for p in D for j,word in enumerate(words)];assert cu==c['units'];ct,rows=graph(cu);assert rows==c['graph']['observed'];missing=allnonself-set(ct);assert missing==set(map(tuple,c['graph']['absent']));full=c['full_found_permutation'];assert sorted(full)==list(range(29));assert all((full[a],full[b]) in missing for a,b in forbidden);inv={v:i for i,v in enumerate(full)}
 for word in words:
  decoded=[inv[perm[v]] for v in word];assert parse(''.join(spell[v] for v in decoded))==decoded
 controlmismatch.append(sum(full[i]!=perm[i] for i in range(29)))
(R/'P24-nonself-source-certificate.json').write_text(json.dumps([r for r in rows] if False else [r for r in actual['graph']['observed'] if r['pair'][0]!=r['pair'][1]],indent=2));out={'status':'PASS','S10':{'equations':[len(r['equations']) for r in s['real']],'integer_determinants':dets,'mod29':[d%29 for d in dets],'controls':60,'tiny_assignments':12500,'initial_final_identical_except_free_variables':True},'P24':{'units':len(units),'within_unit_transitions':sum(counts.values()),'observed_edges_including_self':len(counts),'nonself_edges':len(allnonself),'missing_nonself':0,'tiny_cases':100,'control_full_mapping_mismatches':controlmismatch}};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
