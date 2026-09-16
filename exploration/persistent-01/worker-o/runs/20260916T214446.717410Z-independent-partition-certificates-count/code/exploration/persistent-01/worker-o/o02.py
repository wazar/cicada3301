import collections,datetime,gzip,hashlib,itertools,json,pathlib,time,random
R=pathlib.Path(__file__).resolve().parent
def guard():
 assert not (R.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def necessary(items,targets):
 if sum(items)!=sum(targets):return {'kind':'total','items':sum(items),'targets':sum(targets)}
 if len(targets)>len(items):return {'kind':'support','items':len(items),'targets':len(targets)}
 if not targets:return None
 if min(targets)<min(items):return {'kind':'minimum','target':min(targets),'minimum_item':min(items)}
 bits=1
 for v in items:bits|=bits<<v
 for t in targets:
  if not ((bits>>t)&1):return {'kind':'subset_support','target':t,'support_bitset':hex(bits)}
 for t in sorted(set(targets)):
  demand=sum(v for v in targets if v<=t);capacity=sum(v for v in items if v<=t)
  if demand>capacity:return {'kind':'small_capacity','threshold':t,'demand':demand,'capacity':capacity}
 return None
class Limit(Exception):pass
def solve(items,targets,seconds=2,nodecap=200000):
 items=tuple(sorted(v for v in items if v));targets=tuple(sorted(v for v in targets if v));start=time.monotonic();nodes={};calls=0
 def visit(ii,tt):
  nonlocal calls
  calls+=1
  if calls>nodecap or time.monotonic()-start>seconds:raise Limit
  key=str(ii)+'/'+str(tt)
  if key in nodes:return None
  reason=necessary(ii,tt)
  if reason:nodes[key]={'items':ii,'targets':tt,'reason':reason};return None
  if not tt:return []
  t=tt[0];counts=collections.Counter(ii);vs=sorted(counts);choices=[]
  def enum(j,left,take):
   if j==len(vs):
    if left==0:yield tuple(take)
    return
   v=vs[j]
   for k in range(min(counts[v],left//v)+1):
    yield from enum(j+1,left-v*k,take+[k])
  for take in enum(0,t,[]):
   if time.monotonic()-start>seconds:raise Limit
   selected=tuple(v for v,k in zip(vs,take) for _ in range(k));left=tuple(v for v,k in zip(vs,take) for _ in range(counts[v]-k))
   childkey=str(left)+'/'+str(tt[1:]);choices.append({'selected':selected,'child':childkey})
   rest=visit(left,tt[1:])
   if rest is not None:return [selected]+rest
  nodes[key]={'items':ii,'targets':tt,'children':choices};return None
 try:
  groups=visit(items,targets);status='FEASIBLE' if groups is not None else 'INFEASIBLE'
 except Limit:groups=None;status='UNKNOWN'
 return {'status':status,'groups':groups,'proof_dag':nodes,'nodes':calls,'seconds':time.monotonic()-start}
def brute(items,targets):
 # Independent labeled assignment enumeration; no pruning except final totals.
 for assignment in itertools.product(range(len(targets)),repeat=len(items)):
  totals=[0]*len(targets)
  for x,k in zip(items,assignment):totals[k]+=x
  if totals==list(targets):return True
 return False
guard();rng=random.Random(2026091732);tiny=[]
for z in range(200):
 n=rng.randrange(2,7);k=rng.randrange(1,min(n,3)+1);items=[rng.randrange(1,5) for _ in range(n)]
 if z%2:
  cuts=sorted(rng.sample(range(1,sum(items)),k-1));targets=[b-a for a,b in zip([0]+cuts,cuts+[sum(items)])]
 else:
  targets=[0]*k
  for i,x in enumerate(items):targets[i%k]+=x
 result=solve(items,targets);truth=brute(items,targets)
 assert result['status']!='UNKNOWN' and (result['status']=='FEASIBLE')==truth
 tiny.append({'items':items,'targets':targets,'brute':truth,'result':result})
J=R.parent/'worker-j';j=json.loads((J/'j02-results.json').read_text());w=json.load(gzip.open(J/'j03-windows.json.gz','rt'));maps=json.loads((R.parent/'worker-f/F06-maps.json').read_text());mapby={m['page']:m for m in maps};textby={t['name']:t for t in w['texts']};real=[];controls=[];startall=time.monotonic()
for a,windows,expected in zip(j['actual'],w['windows'],[285,424,129,1468,30]):
 guard();page=a['page'];assert page not in {4,9,14,19,24,29,34,39,44,54};observed=collections.Counter(mapby[page]['indices']);items=sorted(observed.values());assert items==sorted(a['sorted_counts']) and sum(items)==a['n']
 planted=[0]*20;perm=items[:];rng.shuffle(perm)
 for i,v in enumerate(perm):planted[i%20]+=v
 c=solve(items,planted);assert c['status']=='FEASIBLE';controls.append({'page':page,'items':items,'targets':planted,'result':c})
 bad=[1]*(items.count(1)+1)+[sum(items)-items.count(1)-1];c=solve(items,bad);assert c['status']=='INFEASIBLE';controls.append({'page':page,'items':items,'targets':bad,'result':c})
 eligible=[x for x in windows if x['bound']<=a['pairs']];assert len(eligible)==expected
 cases={}
 for x in eligible:
  seq=textby[x['group']]['source'][x['start']:x['start']+a['n']];cnt=[seq.count(i) for i in range(26)];assert cnt==x['counts']
  key=tuple(sorted(v for v in cnt if v));cases.setdefault(key,[]).append({'group':x['group'],'start':x['start'],'letter_counts':cnt,'bound':x['bound']})
 results=[]
 for targets,provenance in sorted(cases.items()):
  guard();reason=necessary(items,targets)
  if reason:res={'status':'INFEASIBLE','reason':reason,'nodes':0}
  elif time.monotonic()-startall>240:res={'status':'UNKNOWN','reason':{'kind':'global_budget'}}
  else:res=solve(items,targets)
  if res['status']=='FEASIBLE':
   available=collections.defaultdict(list)
   for rune,num in sorted(observed.items()):available[num].append(rune)
   groups=[[available[num].pop(0) for num in group] for group in res['groups']]
   assert sorted(sum(groups,[]))==sorted(observed)
   res['output_rune_groups']=groups
   for prov in provenance:
    letters=sorted((num,letter) for letter,num in enumerate(prov['letter_counts']) if num)
    prov['letter_to_output_runes']=[{'letter_index':letter,'output_runes':group} for (num,letter),group in zip(letters,groups)]
  results.append({'targets':targets,'provenance':provenance,'result':res})
 real.append({'page':page,'output_counts_by_rune':sorted(observed.items()),'items':items,'eligible_windows':len(eligible),'deduplicated_cases':len(cases),'cases':results})
summary=[]
for page in real:
 count=collections.Counter();reasons=collections.Counter()
 for case in page['cases']:
  res=case['result'];count[res['status']]+=len(case['provenance'])
  if 'reason' in res:reasons[res['reason']['kind']]+=len(case['provenance'])
 summary.append({'page':page['page'],'eligible_windows':page['eligible_windows'],'deduplicated_cases':page['deduplicated_cases'],'statuses_weighted':dict(count),'cheap_reasons_weighted':dict(reasons)})
with gzip.open(R/'O02-evidence.json.gz','wt') as f:json.dump({'real':real,'tiny_controls':tiny,'actual_controls':controls,'seed':2026091732,'source_hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [J/'j02-results.json',J/'j03-windows.json.gz',R.parent/'worker-f/F06-maps.json']}},f)
(R/'O02-result.json').write_text(json.dumps({'pages':summary,'tiny_brute_cases':len(tiny),'actual_controls':len(controls),'solver_elapsed':time.monotonic()-startall},indent=2));print((R/'O02-result.json').read_text())
