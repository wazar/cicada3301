from pathlib import Path
import json,gzip,itertools,hashlib
O=Path(__file__).resolve().parent;R=O.parents[2];B=R/'exploration/persistent-01/worker-s';f=R/'exploration/persistent-01/worker-f/F06-maps.json';pages={p['page']:p for p in json.loads(f.read_text())};a=json.loads((B/'S18-result.json').read_text());assert a['source_sha256']==hashlib.sha256(f.read_bytes()).hexdigest();certs=0
for r in a['pages']:
 p=pages[r['page']];words=[p['indices'][w['start']:w['end']] for w in p['words']];A=[[w.count(i) for i in range(29)] for w in words];assert A==r['result']['A'];assert set(v for w in words for v in w)==set(range(29))
 for c in r['result']['certificates']:
  prime=c['field'];M=[A[i] for i in c['word_indices']];V=c['inverse'];assert len(M)==len(V)==29
  for X,Y in [(M,V),(V,M)]:
   for i in range(29):
    for j in range(29):assert sum(X[i][k]*Y[k][j] for k in range(29))%prime==int(i==j)
  for s in c['source_words']:
   i=s['word_index'];assert s['runes']==words[i] and s['map']==p['words'][i]
  certs+=1
c=json.load(gzip.open(B/'S18-controls.json.gz','rt'));perms=list(itertools.permutations(range(3)));assert [list(p) for p in perms]==c['permutations'];closures=0
for panel in c['panels']:
 mapping=panel['map'];assert set(mapping)==set(range(6));p=pages[panel['page']];assert [len(w) for w in panel['words']]==[w['end']-w['start'] for w in p['words']]
 for word,trace in zip(panel['words'],panel['traces']):
  for st in range(3):
   path=[st]
   for r in word:path.append(perms[mapping[r]][path[-1]])
   assert path==trace['state_paths'][st] and path[-1]==st;closures+=1
 assert not panel['result']['obstructed']
for t in c['tiny']:
 count=0
 for mapping in itertools.product(range(6),repeat=3):
  if all(v==0 for v in mapping):continue
  valid=True
  for word in t['words']:
   for st in range(3):
    v=st
    for r in word:v=perms[mapping[r]][v]
    if v!=st:valid=False;break
   if not valid:break
  count+=valid
 assert count==t['nontrivial_solutions'];assert not t['result']['obstructed'] or count==0
# Group argument checked directly: sign is a homomorphism; all even permutations form C3.
signs=[sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))%2 for p in perms];ev=[i for i,s in enumerate(signs) if s==0];assert len(ev)==3
for i,j in itertools.product(range(6),repeat=2):
 k=perms.index(tuple(perms[j][perms[i][v]] for v in range(3)));assert signs[k]==(signs[i]+signs[j])%2
assert all(perms[i][perms[j][v]]==perms[j][perms[i][v]] for i,j in itertools.product(ev,repeat=2) for v in range(3))
result=dict(pass_=True,source_inverse_certificates=certs,control_panels=len(c['panels']),all_state_closures=closures,tiny_cases=len(c['tiny']),tiny_assignments=len(c['tiny'])*216,scope='Fixed S3 opcode maps; every word identity on all three starting states; nontrivial used opcode required.')
(O/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
