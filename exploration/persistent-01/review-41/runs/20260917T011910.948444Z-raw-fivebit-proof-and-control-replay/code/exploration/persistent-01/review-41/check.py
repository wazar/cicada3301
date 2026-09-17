from pathlib import Path
import json,gzip,hashlib,itertools,random
R=Path(__file__).parent;B=R.parent;S=B/'worker-s';D=json.loads((B/'worker-f/F06-maps.json').read_text());assert len(D)==45 and not {4,9,14,19,24,29,34,39,44,50,54}&{p['page'] for p in D};(R/'snapshots').mkdir(exist_ok=True);inputs={}
for path in list(S.glob('S11-*.json*'))+[S/'S11-CARD.md',S/'S11-REPORT.md',S/'s11.py',B/'worker-f/F06-maps.json']:
 raw=path.read_bytes();inputs[str(path)]={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}
 if path.suffix!='.gz':(R/'snapshots'/path.name).write_bytes(raw)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
def load(name):return json.load(gzip.open(S/name,'rt'))
for value in range(32):
 bits=[int(c) for c in f'{value:05b}'];assert (value<=25)==not_any if False else True
 assert (value<=25)==(sum(bits[:3])<3 and bits[0]+bits[1]+bits[3]<3)
 # Downward closure checked across every bit-subset of each allowed numeral.
 if value<=25:assert all((value&mask)<=25 for mask in range(32))
def rebuild(seqs):
 problem=[];maps=[];blocks=[]
 for page,seq in zip(D,seqs):
  pp=[];pm=[];bb=[]
  for phase in range(5):
   clauses=[];cm=[];bs=[]
   for start in range(phase,len(seq)-4,5):
    group=seq[start:start+5];bs.append(group)
    for positions in [[start,start+1,start+2],[start,start+1,start+3]]:
     mask=0
     for i in positions:mask|=1<<seq[i]
     clauses.append(mask);cm.append(dict(mask=mask,start=start,offsets=[i-start for i in positions],rune_positions=positions,source_char_positions=[page['source_char_positions'][i] for i in positions]))
   pp.append(sorted(set(clauses)));pm.append(cm);bb.append(bs)
  problem.append(pp);maps.append(dict(page=page['page'],phases=pm));blocks.append(bb)
 return problem,maps,blocks

def verify_proof(problem,result,n,k,rawblocks=None):
 if result['status']=='SAT':
  ones=result['ones'];assert ones.bit_count()==k;assert all(any(all(mask&ones!=mask for mask in phase) for phase in page) for page in problem);return 0
 assert result['status']=='UNSAT';proof=result['proof'];stack=[(result['root'],0,0)];seen=set();leaves=0
 while stack:
  idx,ones,assigned=stack.pop();assert 0<=idx<len(proof) and idx not in seen;seen.add(idx);node=proof[idx]
  if node[0]=='D':
   _,v,onechild,zerochild=node;assert 0<=v<n and not assigned>>v&1;stack.append((zerochild,ones,assigned|1<<v));stack.append((onechild,ones|1<<v,assigned|1<<v))
  elif node[0]=='K':assert ones.bit_count()+(n-assigned.bit_count())<k;leaves+=1
  elif node[0]=='P':
   pi=node[1];assert 0<=pi<len(problem)
   if rawblocks is None:assert all(any(mask&ones==mask for mask in phase) for phase in problem[pi])
   else:
    # Interpret raw complete five-rune code as its minimum possible value under partial assignment.
    # Unassigned bits are zero; any value>=26 cannot become valid when more ones are added.
    for groups in rawblocks[pi]:assert any(sum(((ones>>r)&1)<<(4-j) for j,r in enumerate(group))>=26 for group in groups)
   leaves+=1
  else:raise AssertionError(node)
 assert len(seen)==len(proof)==result['nodes'];return leaves
rng=random.Random(1709202611);tiny=load('S11-tiny.json.gz');tinynodes=0
for t in tiny:
 problem=[[[sum(1<<v for v in rng.sample(range(6),rng.randrange(1,4))) for _ in range(5)] for _ in range(2)] for _ in range(3)];assert problem==t['problem'];valid=[]
 for combo in itertools.combinations(range(6),3):
  mask=sum(1<<v for v in combo)
  if all(any(all(m&mask!=m for m in phase) for phase in page) for page in problem):valid.append(mask)
 assert valid==t['valid'];assert (t['result']['status']=='SAT')==bool(valid);verify_proof(problem,t['result'],6,3)
 if not valid:tinynodes+=len(t['result']['proof'])
controls=[]
for count in [14,15]:
 z=load(f'S11-control{count}.json.gz');labels=list(range(29));rng.shuffle(labels);one=set(labels[:count]);truth=sum(1<<v for v in one);assert truth==z['ones_truth'];classes=[[v for v in range(29) if v not in one],sorted(one)];seqs=[];truthpages=[]
 for page in D:
  n=len(page['indices']);phase=rng.randrange(5);s=[];groups=[]
  for i in range(phase):s.append(rng.choice([v for v in range(29) if not s or v!=s[-1]]))
  while len(s)+5<=n:
   value=rng.randrange(26);bits=[int(c) for c in f'{value:05b}'];start=len(s)
   for bit in bits:s.append(rng.choice([v for v in classes[bit] if not s or v!=s[-1]]))
   groups.append(dict(start=start,value=value,bits=bits))
  while len(s)<n:s.append(rng.choice([v for v in range(29) if v!=s[-1]]))
  assert all(a!=b for a,b in zip(s,s[1:]));seqs.append(s);truthpages.append(dict(page=page['page'],phase=phase,groups=groups))
 assert seqs==z['runes'] and truthpages==z['truth_pages'];problem,maps,blocks=rebuild(seqs);assert problem==z['problem'];verify_proof(problem,z['result'],29,14,blocks);assert z['result']['status']=='SAT';ones=z['result']['ones']
 for page,seq,record in zip(D,seqs,z['decoded']):
  phase=record['phase'];groups=[]
  for start in range(phase,len(seq)-4,5):
   bits=[(ones>>r)&1 for r in seq[start:start+5]];value=sum(b<<(4-i) for i,b in enumerate(bits));assert value<=25;groups.append(dict(start=start,source_positions=page['source_char_positions'][start:start+5],bits=bits,value=value,letter=chr(65+value)))
  assert groups==record['groups'];assert record['text']==''.join(g['letter'] for g in groups);assert record['discarded_positions']==list(range(phase))+list(range(phase+5*len(groups),len(seq)))
 controls.append({'truth_ones':count,'found_ones':ones.bit_count(),'same_partition':truth==ones,'changed_bits':(truth^ones).bit_count(),'nodes':z['result']['nodes']})
actual=load('S11-real.json.gz');assert actual['pages']==[p['page'] for p in D];problem,maps,blocks=rebuild([p['indices'] for p in D]);assert problem==actual['problem'] and maps==actual['source_maps'];leaves=verify_proof(problem,actual['result'],29,14,blocks);assert actual['result']['status']=='UNSAT';assert hashlib.sha256((B/'worker-f/F06-maps.json').read_bytes()).hexdigest()==actual['source_sha256']
out={'status':'PASS','actual_nodes':actual['result']['nodes'],'actual_leaves':leaves,'actual_source_clauses':sum(len(phase) for page in maps for phase in page['phases']),'tiny_cases':100,'tiny_balanced_assignments':2000,'tiny_refutation_nodes':tinynodes,'controls':controls,'format_identity_values':32,'monotone_subset_values':26*32};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
