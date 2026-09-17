from pathlib import Path
import json,gzip,itertools,random,hashlib
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'exploration/persistent-01';P=B/'worker-p/P24'
assert not (B/'STOP').exists()
def read(n):
 with gzip.open(P/n,'rt') as f:return json.load(f)
def brute_pattern(r):
 n=r['n'];edges=r['edges'];target=set(map(tuple,r['target']));active=sorted({v for e in edges for v in e})
 return any(all((m[a],m[b]) in target for a,b in edges) for m in (dict(zip(active,vs)) for vs in itertools.permutations(range(n),len(active))))
for r in read('tiny-controls.json.gz'):assert brute_pattern(r)==(r['result']['status']=='SAT')
certificate=json.loads((B/'worker-p/P23/independent-certificate.json').read_text());forbidden=[tuple(x['pair']) for x in certificate['forbidden_pair_certificates']]
for i in range(4):
 r=read('control-'+str(i)+'.json.gz');perm=list(range(29));random.Random(524100+i).shuffle(perm);assert perm==r['planted_permutation']
 observed=set()
 for u in r['units']:
  assert u['runes']==[perm[x] for x in r['words'][u['unit']]]
  observed.update(zip(u['runes'],u['runes'][1:]))
 m=r['full_found_permutation'];assert sorted(m)==list(range(29))
 assert all((m[a],m[b]) not in observed for a,b in forbidden)
 assert {(a,b) for a in range(29) for b in range(29) if a!=b and (a,b) not in observed}==set(map(tuple,r['graph']['absent']))
actual=read('actual.json.gz');pgs=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page']);observed={};counts={};units=0
for p in pgs:
 for ui,w in enumerate(p['words']):
  units+=1;start,end=w['start'],w['end']
  for i in range(start,end-1):
   a,b=p['indices'][i:i+2];counts[(a,b)]=counts.get((a,b),0)+1
   if (a,b) not in observed:
    observed[(a,b)]=dict(page=p['page'],unit=ui,unit_positions=[i-start,i-start+1],source_rune_indices=[i,i+1],source_char_positions=p['source_char_positions'][i:i+2])
for item in actual['graph']['observed']:
 e=tuple(item['pair']);assert item['count']==counts[e] and item['witness']==observed[e]
assert len(actual['graph']['observed'])==len(observed)
allpairs={(a,b) for a in range(29) for b in range(29) if a!=b}
assert allpairs.issubset(observed) and not actual['graph']['absent']
assert all(a!=b for a,b in forbidden) and len(forbidden)==14
assert actual['result']['status']=='UNSAT' and actual['result']['nodes']==1
def components(vertices,edges):
 pending=set(vertices);out=[]
 while pending:
  seen={min(pending)}
  while True:
   larger=seen|{v for a,b in edges if a in seen or b in seen for v in [a,b]}
   if larger==seen:break
   seen=larger
  out.append(sorted(seen));pending-=seen
 return out
out=dict(pass_all=True,pages=len(pgs),units=units,total_withinword_edges=sum(counts.values()),observed_directed_edges=len(observed),observed_distinct_pairs=len(allpairs),observed_self_pairs=len(observed)-len(allpairs),forbidden_edges=len(forbidden),pattern_components=components({v for e in forbidden for v in e},forbidden),absent_graph_components=[[i] for i in range(29)],proof='Every distinct ordered ciphertext pair occurs within an admitted word. A bijection maps every distinct forbidden ordered pair to a distinct ordered ciphertext pair, which therefore cannot be absent. One forbidden pair already suffices.',witnesses=[dict(pair=list(e),count=counts[e],source=observed[e]) for e in sorted(allpairs)])
(P/'independent-certificate.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='witnesses'}))
