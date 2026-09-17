import json,pathlib,itertools,random,hashlib
BASE=pathlib.Path('exploration/persistent-01/worker-s'); SOURCE=pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json'); rng=random.Random(1709202604)
pages=[p for p in json.loads(SOURCE.read_text()) if p['page'] in [0,1]]
def infer(xs,words,nlabels=29,positions=None):
 n=2*nlabels; parent=list(range(n)); adjacency=[set() for _ in range(n)]; witnesses=[]; constraints=[]
 def find(a):
  while parent[a]!=a:
   parent[a]=parent[parent[a]];a=parent[a]
  return a
 for wi,w in enumerate(words):
  for i in range(w['start'],w['end']-1):
   a,b=xs[i],xs[i+1]; u,v=2*a+1,2*b
   row={'word':wi,'rune_positions':[i,i+1],'rune_labels':[a,b],'endpoint_equality':[u,v]}
   if positions is not None:row['source_char_positions']=[positions[i],positions[i+1]]
   constraints.append(row); adjacency[u].add(v);adjacency[v].add(u)
   ru,rv=find(u),find(v)
   if ru!=rv: parent[ru]=rv;witnesses.append(row)
 groups={}
 for u in range(n):groups.setdefault(find(u),[]).append(u)
 components=sorted(sorted(c) for c in groups.values())
 seen=set(); dfs=[]
 for start in range(n):
  if start in seen:continue
  stack=[start];cc=[];seen.add(start)
  while stack:
   u=stack.pop();cc.append(u)
   for v in adjacency[u]-seen:seen.add(v);stack.append(v)
  dfs.append(sorted(cc))
 assert sorted(dfs)==components
 used=set(2*x+j for x in xs for j in [0,1]); usedcomponents=[c for c in components if set(c)&used]
 assert len(witnesses)==n-len(components)
 return {'all_components':components,'used_components':usedcomponents,'used_labels':sorted(set(xs)),'maximum_used_vertices':len(usedcomponents),'degenerate_one_vertex':len(usedcomponents)==1,'constraints':constraints,'spanning_witness':witnesses}
# Exhaustive assignments independently test maximum, not only a second partition code.
tiny=[]
for length in range(1,5):
 for seq in itertools.product(range(2),repeat=length):
  r=infer(list(seq),[{'start':0,'end':length}],2); valid=[]
  for assignment in itertools.product(range(4),repeat=4):
   if all(assignment[2*a+1]==assignment[2*b] for a,b in zip(seq[:-1],seq[1:])):valid.append(assignment)
  maximum=max(len(set(a)) for a in valid);assert maximum==len(r['all_components'])
  tiny.append({'sequence':seq,'valid_assignments':len(valid),'max_vertices':maximum})
controls=[]
for nv in [3,5,7]:
 for rep in range(20):
  graph=[(v,(v+1)%nv) for v in range(nv)]+[(rng.randrange(nv),rng.randrange(nv)) for _ in range(29-nv)]
  outgoing={v:[e for e,(a,b) in enumerate(graph) if a==v] for v in range(nv)}; cs=[]
  for p in pages:
   xs=[None]*len(p['indices']);walks=[]
   for w in p['words']:
    vertex=rng.randrange(nv);vertices=[vertex];edges=[]
    for i in range(w['start'],w['end']):
     e=rng.choice(outgoing[vertex]);xs[i]=e;vertex=graph[e][1];vertices.append(vertex);edges.append(e)
    walks.append({'interval':[w['start'],w['end']],'vertices':vertices,'edge_labels':edges})
   r=infer(xs,p['words']);actual=[v for edge in graph for v in edge]
   assert all(len(set(actual[e] for e in c))==1 for c in r['all_components'])
   assert r['maximum_used_vertices']>=len(set(actual[e] for x in xs for e in [2*x,2*x+1]))
   cs.append({'page':p['page'],'runes':xs,'walks':walks,'inferred':r})
  controls.append({'vertices':nv,'rep':rep,'graph':graph,'pages':cs})
real=[]
for p in pages:
 r=infer(p['indices'],p['words'],positions=p['source_char_positions']);r['page']=p['page'];r['words']=p['words'];r['runes']=p['indices'];real.append(r)
summary={'seed':1709202604,'input_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'tiny_cases':len(tiny),'tiny_assignments':len(tiny)*256,'graphs':len(controls),'control_page_walks':sum(len(c['pages']) for c in controls),'controls_nontrivial':sum(not p['inferred']['degenerate_one_vertex'] for c in controls for p in c['pages']),'real':[{'page':r['page'],'used_labels':len(r['used_labels']),'constraints':len(r['constraints']),'spanning_witness_edges':len(r['spanning_witness']),'all_component_sizes':[len(c) for c in r['all_components']],'max_used_vertices':r['maximum_used_vertices']} for r in real]}
(BASE/'S04-result.json').write_text(json.dumps({'summary':summary,'real':real,'tiny':tiny,'controls':controls},indent=2)+'\n');print(json.dumps(summary,indent=2))
