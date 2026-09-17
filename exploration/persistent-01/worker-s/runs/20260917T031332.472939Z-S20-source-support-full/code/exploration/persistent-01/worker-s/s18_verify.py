from pathlib import Path
import json,gzip,itertools,hashlib
B=Path('exploration/persistent-01/worker-s');src=Path('exploration/persistent-01/worker-f/F06-maps.json');ps={p['page']:p for p in json.loads(src.read_text())};r=json.loads((B/'S18-result.json').read_text());assert r['source_sha256']==hashlib.sha256(src.read_bytes()).hexdigest();checked=[]
for page in r['pages']:
 p=ps[page['page']];assert set(p['indices'])==set(range(29))
 for cert in page['result']['certificates']:
  prime=cert['field'];ids=cert['word_indices'];assert len(ids)==29 and len(set(ids))==29;rows=[]
  for wi,stored in zip(ids,cert['source_words']):
   w=p['words'][wi];word=p['indices'][w['start']:w['end']];assert stored=={'word_index':wi,'runes':word,'map':w};a=[0]*29
   for x in word:a[x]+=1
   rows.append(a)
  inverse=cert['inverse']
  for A,C in [(rows,inverse),(inverse,rows)]:
   for i in range(29):
    for j in range(29):assert sum(A[i][k]*C[k][j] for k in range(29))%prime==int(i==j)
  checked.append({'page':p['page'],'field':prime,'rank_certified':29,'both_inverse_products':True})
assert len(checked)==4
perms=list(itertools.permutations(range(3)));even=[(0,1,2),(1,2,0),(2,0,1)]
for a in perms:
 for b in perms:
  ab=tuple(b[a[i]] for i in range(3));assert (int(a not in even)+int(b not in even))%2==int(ab not in even)
  if a in even and b in even:assert (even.index(a)+even.index(b))%3==even.index(ab)
controls=json.loads(gzip.decompress((B/'S18-controls.json.gz').read_bytes()));products=0
for panel in controls['panels']:
 m=panel['map'];assert set(m)==set(range(6));emitted=set()
 for word,trace in zip(panel['words'],panel['traces']):
  for initial in range(3):
   s=initial;states=[s]
   for label in word:s=perms[m[label]][s];states.append(s);emitted.add(m[label])
   assert s==initial and states==trace['state_paths'][initial];products+=1
 assert emitted==set(range(6))
result={'certificates':checked,'independent_S3_product_cases':36,'controls':len(controls['panels']),'control_initial_state_closures':products,'all_controls_emit_all_six_opcodes':True,'conclusion':'Both pages admit only identity opcodes under the stated S3 word-identity model.'};(B/'S18-proof-check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
