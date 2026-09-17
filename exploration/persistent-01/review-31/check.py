from pathlib import Path
import json,gzip,itertools,random,hashlib
R=Path(__file__).parent;B=R.parent;S=B/'worker-s';P=[p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,1]];z=json.load(gzip.open(S/'S04-evidence.json.gz','rt'));(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in [S/'S04-CARD.md',S/'s04.py',S/'S04-evidence.json.gz',B/'worker-f/F06-maps.json']:
 b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 if p.suffix!='.gz':(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
def partition(n,equalities):
 # Boolean transitive closure, independent of union-find/tree walk.
 reach=[[i==j for j in range(n)] for i in range(n)]
 for a,b in equalities:reach[a][b]=reach[b][a]=True
 for k in range(n):
  for i in range(n):
   if reach[i][k]:reach[i]=[x or y for x,y in zip(reach[i],reach[k])]
 return sorted({tuple(j for j in range(n) if reach[i][j]) for i in range(n)})
def verify(xs,words,result,positions=None):
 rows=[]
 for wi,w in enumerate(words):
  for i in range(w['start'],w['end']-1):
   row=dict(word=wi,rune_positions=[i,i+1],rune_labels=xs[i:i+2],endpoint_equality=[2*xs[i]+1,2*xs[i+1]])
   if positions is not None:row['source_char_positions']=positions[i:i+2]
   rows.append(row)
 assert rows==result['constraints'];groups=partition(58,[r['endpoint_equality'] for r in rows]);assert groups==list(map(tuple,result['all_components']))
 witness=result['spanning_witness'];assert all(r in rows for r in witness);assert partition(58,[r['endpoint_equality'] for r in witness])==groups;assert len(witness)==58-len(groups)
 used=set(v for x in xs for v in [2*x,2*x+1]);assert sum(bool(set(c)&used) for c in groups)==result['maximum_used_vertices'];return groups
for p,r in zip(P,z['real']):assert p['page']==r['page'];verify(p['indices'],p['words'],r,p['source_char_positions']);assert r['all_components']==[list(range(58))]
rng=random.Random(1709202604);ncontrols=0
for saved in z['controls']:
 nv=saved['vertices'];graph=[(v,(v+1)%nv) for v in range(nv)]+[(rng.randrange(nv),rng.randrange(nv)) for _ in range(29-nv)];assert [list(e) for e in graph]==saved['graph'];outgoing={v:[i for i,e in enumerate(graph) if e[0]==v] for v in range(nv)}
 for p,ctrl in zip(P,saved['pages']):
  xs=[];walks=[]
  for w in p['words']:
   vertex=rng.randrange(nv);vertices=[vertex];edges=[]
   for i in range(w['start'],w['end']):e=rng.choice(outgoing[vertex]);edges.append(e);xs.append(e);vertex=graph[e][1];vertices.append(vertex)
   walks.append({'interval':[w['start'],w['end']],'vertices':vertices,'edge_labels':edges})
  assert xs==ctrl['runes'] and walks==ctrl['walks'];groups=verify(xs,p['words'],ctrl['inferred']);actual=[v for edge in graph for v in edge];assert all(len({actual[i] for i in c})==1 for c in groups);assert ctrl['inferred']['maximum_used_vertices']>1;ncontrols+=1
for row in z['tiny']:
 seq=row['sequence'];valid=[a for a in itertools.product(range(4),repeat=4) if all(a[2*x+1]==a[2*y] for x,y in zip(seq,seq[1:]))];groups=partition(4,[(2*x+1,2*y) for x,y in zip(seq,seq[1:])]);assert len(valid)==row['valid_assignments'];assert max(map(lambda a:len(set(a)),valid))==row['max_vertices']==len(groups)
result={'status':'PASS','real_constraints':[len(r['constraints']) for r in z['real']],'real_witness_edges':[len(r['spanning_witness']) for r in z['real']],'control_walks':ncontrols,'tiny_cases':len(z['tiny']),'tiny_assignments':len(z['tiny'])*256};(R/'result.json').write_text(json.dumps(result,indent=2));print(result)
