import pathlib,json,random,itertools,time,gzip,hashlib
BASE=pathlib.Path('exploration/persistent-01/worker-s');SOURCE=pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json');rng=random.Random(1709202611);pages=json.loads(SOURCE.read_text());assert len(pages)==45 and not ({4,9,14,19,24,29,34,39,44,54}&{p['page'] for p in pages})
for value in range(32):
 bits=[value>>i&1 for i in [4,3,2,1,0]];assert (value<=25)==(not(bits[0] and bits[1] and bits[2]) and not(bits[0] and bits[1] and bits[3]))
def constraints(seqs):
 allpages=[];maps=[]
 for page,xs in zip(pages,seqs):
  phases=[];pm=[]
  for phase in range(5):
   clauses=[];cm=[]
   for start in range(phase,len(xs)-4,5):
    for offsets in [(0,1,2),(0,1,3)]:
     positions=[start+j for j in offsets];mask=sum(1<<v for v in set(xs[j] for j in positions));clauses.append(mask);cm.append({'mask':mask,'start':start,'offsets':offsets,'rune_positions':positions,'source_char_positions':[page['source_char_positions'][j] for j in positions]})
   phases.append(sorted(set(clauses)));pm.append(cm)
  allpages.append(phases);maps.append({'page':page['page'],'phases':pm})
 return allpages,maps
class Limit(Exception):pass
def solve(problem,n=29,k=14,seconds=120,nodecap=2000000):
 edgephases={};pagemasks=[];phaseid=0
 for phases in problem:
  pm=0
  for masks in phases:
   flag=1<<phaseid;phaseid+=1;pm|=flag
   for mask in masks:edgephases[mask]=edgephases.get(mask,0)|flag
  pagemasks.append(pm)
 incident=[[(mask^(1<<v),flags) for mask,flags in edgephases.items() if mask>>v&1] for v in range(n)];order=sorted(range(n),key=lambda v:(-len(incident[v]),v));nodes=[];start=time.monotonic();count=0;answer=None
 def visit(depth,ones,bad):
  nonlocal count,answer
  count+=1
  if count%1024==0 and (time.monotonic()-start>seconds or count>nodecap or pathlib.Path('exploration/persistent-01/STOP').exists()):raise Limit()
  if ones.bit_count()+n-depth<k:idx=len(nodes);nodes.append(['K']);return idx
  for pi,pm in enumerate(pagemasks):
   if bad&pm==pm:idx=len(nodes);nodes.append(['P',pi]);return idx
  if ones.bit_count()==k:answer=ones;return None
  v=order[depth];new=ones|(1<<v);bad1=bad
  for needed,flags in incident[v]:
   if new&needed==needed:bad1|=flags
  left=visit(depth+1,new,bad1)
  if answer is not None:return None
  right=visit(depth+1,ones,bad)
  if answer is not None:return None
  idx=len(nodes);nodes.append(['D',v,left,right]);return idx
 try:root=visit(0,0,0);status='SAT' if answer is not None else 'UNSAT'
 except Limit:root=None;status='UNKNOWN'
 return {'status':status,'ones':answer,'proof':nodes if status=='UNSAT' else None,'root':root,'nodes':count,'seconds':time.monotonic()-start,'order':order,'limits':{'seconds':seconds,'nodecap':nodecap}}
def verify(problem,result,n=29,k=14):
 if result['status']=='SAT':
  ones=result['ones'];assert ones.bit_count()==k and all(any(all(mask&ones!=mask for mask in phase) for phase in phases) for phases in problem);return
 if result['status']!='UNSAT':return
 nodes=result['proof'];visited=set()
 def walk(idx,ones,assigned):
  assert idx not in visited;visited.add(idx);node=nodes[idx]
  if node[0]=='K':assert ones.bit_count()+n-assigned.bit_count()<k
  elif node[0]=='P':assert all(any(mask&ones==mask for mask in phase) for phase in problem[node[1]])
  else:
   _,v,left,right=node;assert not (assigned>>v&1);walk(left,ones|(1<<v),assigned|(1<<v));walk(right,ones,assigned|(1<<v))
 walk(result['root'],0,0);assert len(visited)==len(nodes)
tiny=[]
for rep in range(100):
 problem=[[[sum(1<<v for v in rng.sample(range(6),rng.randrange(1,4))) for _ in range(5)] for _ in range(2)] for _ in range(3)];valid=[sum(1<<v for v in combo) for combo in itertools.combinations(range(6),3) if all(any(all(not all(v in combo for v in range(6) if mask>>v&1) for mask in phase) for phase in phases) for phases in problem)];r=solve(problem,6,3,seconds=10);assert r['status']==('SAT' if valid else 'UNSAT');verify(problem,r,6,3);tiny.append({'problem':problem,'result':r,'valid':valid})
(BASE/'S11-tiny.json.gz').write_bytes(gzip.compress(json.dumps(tiny).encode(),mtime=0))
def output(seqs,ones,problem):
 result=[]
 for page,xs,phases in zip(pages,seqs,problem):
  phase=next(i for i,masks in enumerate(phases) if all(mask&ones!=mask for mask in masks));groups=[]
  for start in range(phase,len(xs)-4,5):
   bits=[ones>>v&1 for v in xs[start:start+5]];value=sum(b<<(4-i) for i,b in enumerate(bits));assert value<=25;groups.append({'start':start,'source_positions':page['source_char_positions'][start:start+5],'bits':bits,'value':value,'letter':chr(65+value)})
  result.append({'page':page['page'],'phase':phase,'groups':groups,'text':''.join(g['letter'] for g in groups),'discarded_positions':list(range(phase))+list(range(phase+5*len(groups),len(xs)))})
 return result
summaries=[]
for countones in [14,15]:
 labels=list(range(29));rng.shuffle(labels);one=set(labels[:countones]);truth=sum(1<<v for v in one);classes=[[v for v in range(29) if v not in one],sorted(one)];seqs=[];truthpages=[]
 for page in pages:
  n=len(page['indices']);phase=rng.randrange(5);xs=[];groups=[]
  for i in range(phase):xs.append(rng.choice([v for v in range(29) if not xs or v!=xs[-1]]))
  while len(xs)+5<=n:
   value=rng.randrange(26);bits=[value>>i&1 for i in [4,3,2,1,0]];start=len(xs)
   for bit in bits:xs.append(rng.choice([v for v in classes[bit] if not xs or v!=xs[-1]]))
   assert [int(v in one) for v in xs[start:]]==bits;groups.append({'start':start,'value':value,'bits':bits})
  while len(xs)<n:xs.append(rng.choice([v for v in range(29) if v!=xs[-1]]))
  seqs.append(xs);truthpages.append({'page':page['page'],'phase':phase,'groups':groups})
 problem,maps=constraints(seqs);assert all(all(mask&truth!=mask for mask in phases[t['phase']]) for phases,t in zip(problem,truthpages));r=solve(problem);verify(problem,r);record={'ones_truth':truth,'ones_count':countones,'runes':seqs,'truth_pages':truthpages,'problem':problem,'result':r,'decoded':output(seqs,r['ones'],problem) if r['status']=='SAT' else None};(BASE/f'S11-control{countones}.json.gz').write_bytes(gzip.compress(json.dumps(record).encode(),mtime=0));summary={k:v for k,v in r.items() if k not in ['proof','order']};summaries.append({'control':countones,**summary});print(json.dumps(summaries[-1]),flush=True)
seqs=[p['indices'] for p in pages];problem,maps=constraints(seqs);r=solve(problem);verify(problem,r);record={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'pages':[p['page'] for p in pages],'problem':problem,'source_maps':maps,'result':r,'decoded':output(seqs,r['ones'],problem) if r['status']=='SAT' else None};(BASE/'S11-real.json.gz').write_bytes(gzip.compress(json.dumps(record).encode(),mtime=0));summary={k:v for k,v in r.items() if k not in ['proof','order']};report={'controls':summaries,'tiny_cases':100,'tiny_assignments':2000,'real':summary};(BASE/'S11-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
