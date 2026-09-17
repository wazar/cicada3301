from pathlib import Path
import sys,json,gzip,hashlib,ast,math
R=Path(__file__).parent;P=R.parent/'worker-p';sys.path.insert(0,str(P));import p18 as s
name=sys.argv[1];load=lambda p:json.load(gzip.open(p,'rt'));key=load(R/'source-replay.json.gz')['runes'];z=load(P/f'P18/{name}-aggregate.json.gz');f=z['packet'];N=2*(len(key)-sum(v!=0 for v in f['cipher'])+1);assert z['cells']==N
ns=globals();tree=ast.parse((R/'precheck.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)],type_ignores=[]),'independent-scalar','exec'),ns)
selected={0,N-1}|{(431+997*i)%N for i in range(32)};count=feasible=paths_checked=0;scores=[];distinct={};inputs={};truthrow=None
files=sorted((P/'P18').glob(name+'-*.jsonl.gz'),key=lambda p:int(p.name.split('-')[-2]))
for path in files:
 inputs[str(path)]={'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 assert path.stat().st_size<90_000_000
 for line in gzip.open(path,'rt'):
  row=json.loads(line);assert row['id']==count and row['job']=={'offset':count//2,'sign':-1 if count%2==0 else 1};count+=1
  assert row['score'] is not None and len(row['alternatives'])==1;feasible+=1;a=row['alternatives'][0];assert row['score']==a['score'];scores.append(a['score']);identity=(bytes(a['plain']),tuple(a['literal_positions']))
  if len(distinct)<16 or a['score']>=min(distinct.values()):
   if identity in distinct:assert distinct[identity]==a['score']
   distinct[identity]=a['score']
   if len(distinct)>16:distinct=dict(sorted(distinct.items(),key=lambda t:t[1],reverse=True)[:16])
  if row['id'] in selected:replay(f,row['job'],a);paths_checked+=1
  if 'truth' in f and row['job']=={'offset':f['truth']['offset'],'sign':f['truth']['sign']}:truthrow=row;replay(f,row['job'],a);paths_checked+=1
assert count==N and feasible==z['feasible'] and z['infeasible']==0
threshold=min(distinct.values()) if len(distinct)==16 else float('-inf');assert threshold==z['threshold'];eligible=[i for i,v in enumerate(scores) if v>=threshold];assert len(eligible)==z['rerun_cells']
assert z['best_score']==max(scores);assert len({(tuple(a['plain']),tuple(a['literal_positions'])) for a in z['top16']})==len(z['top16'])==16;assert [a['score'] for a in z['top16']]==sorted([a['score'] for a in z['top16']],reverse=True)
alias_records=[]
for a in z['top16']:
 assert a['score']>=threshold;literal=set(a['literal_positions']);aliases=[]
 for sign in [-1,1]:
  required=[(sign*(p-v))%29 for i,(p,v) in enumerate(zip(a['plain'],f['cipher'])) if i not in literal]
  for offset in range(len(key)-len(required)+1):
   if all(key[offset+j]==v for j,v in enumerate(required)):aliases.append({'offset':offset,'sign':sign})
 assert aliases==a['aliases'] and all(j in aliases for j in a['retained_grid_aliases'])
 for job in aliases:replay(f,job,a);assert 2*job['offset']+(job['sign']==1) in eligible;paths_checked+=1
 alias_records.append({'score':a['score'],'aliases':aliases,'retained_aliases':a['retained_grid_aliases']})
if 'truth' in f:
 t=f['truth'];assert truthrow is not None and truthrow['score']==z['truth_job_top1_score'];assert 1+sum(v>truthrow['score'] for v in scores)==z['truth_job_score_rank'];assert abs(score(t['plain'],set(f['ends']))-z['truth_plain_score'])<1e-11
 for a in z['truth_cell_top16']['alternatives']:replay(f,truthrow['job'],a);paths_checked+=1
 assert z['best_errors']==sum(a!=b for a,b in zip(z['top16'][0]['plain'],t['plain']));assert z['literal_path_recovered']==(z['top16'][0]['literal_positions']==t['literal_positions']);assert z['key_recovered']==({'offset':t['offset'],'sign':t['sign']} in z['top16'][0]['aliases']);assert z['truth_global_ranks']==[i+1 for i,a in enumerate(z['top16']) if a['plain']==t['plain'] and a['literal_positions']==t['literal_positions']]
else:
 pid=int(name.split('-')[1]);m=f['map'];assert m['page']==pid and pid in [0,17];actual=m['indices']
 if name.startswith('real'):assert actual==f['cipher']
 else:
  import random
  rng=random.Random(331819+pid);cipher=[rng.randrange(29)]
  for a,b in zip(actual,actual[1:]):
   if a==b:cipher.append(cipher[-1])
   else:v=rng.randrange(28);cipher.append(v+(v>=cipher[-1]))
  assert cipher==f['cipher']
summary={'status':'PASS','name':name,'cells':N,'feasible':feasible,'threshold':threshold,'eligible_rerun_cells':len(eligible),'scalar_paths_checked':paths_checked,'best_score':z['best_score'],'aliases':alias_records,'inputs':inputs,'best_errors':z.get('best_errors'),'truth_rank':z.get('truth_job_score_rank'),'truth_global_ranks':z.get('truth_global_ranks')}
(R/(name+'-audit.json')).write_text(json.dumps(summary,indent=2));(R/'snapshots'/(name+'-aggregate.json.gz')).write_bytes((P/f'P18/{name}-aggregate.json.gz').read_bytes());print({k:v for k,v in summary.items() if k not in ['aliases','inputs']})
