import pathlib,json,gzip,hashlib,math,collections
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import csc_matrix
R=pathlib.Path(__file__).parent;P=R.parent/'worker-r';D=sorted(json.loads((P/'R01-input.json').read_text()),key=lambda x:x['page']);assert len(D)==45 and not{4,9,14,19,24,29,34,39,44,50,54}&{d['page'] for d in D}
(R/'snapshots').mkdir(exist_ok=True);manifest={}
for p in [P/'R01-input.json',P/'R03.py',P/'R03-card.md',P/'R03-stress.py']+sorted(P.glob('R03-*-results.json'))+sorted(P.glob('R03-*-full.jsonl.gz')):
 b=p.read_bytes();manifest[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(manifest,indent=2))
def generate(weights,seed,inverse=None):
 rng=np.random.default_rng(seed);cdfs=[]
 for a in range(29):
  probs=[w if b!=a and (inverse is None or inverse[a]!=b or a==b) else 0. for b,w in enumerate(weights)];total=sum(probs);acc=0.;cdf=[]
  for p in probs:acc+=p/total;cdf.append(acc)
  cdfs.append(cdf)
 out=[]
 for m in D:
  u=float(rng.random());acc=0.;first=None
  for b,w in enumerate(weights):
   acc+=w
   if u<acc:first=b;break
  assert first is not None
  seq=[first]
  for a,b in zip(m['indices'],m['indices'][1:]):
   u=float(rng.random())
   if a==b:seq.append(seq[-1])
   else:seq.append(next(i for i,v in enumerate(cdfs[seq[-1]]) if u<v))
  out.append(seq)
 return out
edges=[(a,b) for a in range(29) for b in range(a+1,29)]
checks=[];panels=[];chosen=[];maxerror=0.;normerror=0.;nrecords=nnull=0
files=['R03-pilot-full.jsonl.gz','R03-controls-0-12-full.jsonl.gz','R03-stress-full.jsonl.gz','R03-real-full.jsonl.gz']
for fn in files:
 rows=[json.loads(line) for line in gzip.open(P/fn,'rt')];groups=collections.defaultdict(list)
 for row in rows:groups[row['tag']].append(row)
 for tag,group in groups.items():
  original=group[0];assert original['kind']=='panel';parent=original['fit']['weights'];null=[]
  for ri,row in enumerate(group):
   x=row['streams'];fit=row['fit'];assert len(x)==45;counts=[[[0]*29 for _ in range(29)] for j in range(2)];hist=[.5]*29
   for i,seq in enumerate(x):
    assert len(seq)==len(D[i]['indices']);assert [a==b for a,b in zip(seq,seq[1:])]==[a==b for a,b in zip(D[i]['indices'],D[i]['indices'][1:])]
    if i%2==0:
     for a in seq:hist[a]+=1
    for a,b in zip(seq,seq[1:]):
     if a!=b:counts[i%2][a][b]+=1
   w=[h/sum(hist) for h in hist];assert max(abs(a-b) for a,b in zip(w,fit['weights']))<1e-14
   assert counts[0]==fit['train_counts'] and counts[1]==fit['held_counts']
   costs=[]
   for ci,c in enumerate(counts):
    e=[[sum(c[a])*w[b]/(1-w[a]) if a!=b else 0 for b in range(29)] for a in range(29)]
    normerror=max(normerror,max(abs(sum(e[a])-sum(c[a])) for a in range(29)))
    saved=fit['train_expected'] if ci==0 else fit['held_expected'];assert max(abs(e[a][b]-saved[a][b]) for a in range(29) for b in range(29))<1e-12
    costs.append({(a,b):(c[a][b]+c[b][a]-e[a][b]-e[b][a])/math.sqrt(e[a][b]+e[b][a]) for a,b in edges})
   pairs=[tuple(p) for p in fit['pairs']];vertices=[v for p in pairs for v in p];assert len(pairs)==14 and len(set(vertices))==28 and all(p in costs[0] for p in pairs);assert set(range(29))-set(vertices)=={fit['singleton']}
   tr=sum(costs[0][p] for p in pairs);he=sum(costs[1][p] for p in pairs);err=max(abs(tr-fit['solver']['objective']),abs(he-fit['held_stat']));maxerror=max(maxerror,err);assert err<1e-10
   assert fit['solver']['status']==0 and fit['solver']['gap']==0 and fit['held_count']==sum(counts[1][a][b]+counts[1][b][a] for a,b in pairs)
   if ri:
    assert row['kind']=='null';assert generate(parent,row['seed'])==x;null.append(he);nnull+=1
   if (fn=='R03-real-full.jsonl.gz' and ri in [0,1]) or (fn in ['R03-controls-0-12-full.jsonl.gz','R03-stress-full.jsonl.gz'] and tag=='0' and ri==0):chosen.append((fn,tag,ri,costs[0],tr))
   nrecords+=1
  # Panel generation and inverse mapping from original seed recipe.
  if 'real' in fn:assert original['streams']==[d['indices'] for d in D]
  else:
   c=int(tag)
   if 'pilot' in fn:seed=460001+c;ratio=5
   elif 'stress' in fn:seed=484001+c;ratio=100
   else:seed=440000+1000*c;ratio=5
   weights=[ratio**(i/28) for i in range(29)];weights=[v/sum(weights) for v in weights];truth=original['truth']
   if c%2==0:
    perm=list(map(int,np.random.default_rng(seed+9).permutation(29)));iv=list(range(29))
    for a,b in zip(perm[:28:2],perm[1:28:2]):iv[a]=b;iv[b]=a
    assert iv==truth
   assert generate(weights,seed,truth)==original['streams']
  panels.append({'file':fn,'tag':tag,'held':original['fit']['held_stat'],'tail':(1+sum(v<=original['fit']['held_stat'] for v in null))/(len(null)+1),'null':null,'true_pairs_recovered':None if original['truth'] is None else sum(original['truth'][a]==b for a,b in original['fit']['pairs']),'true_singleton_recovered':None if original['truth'] is None else original['truth'][original['fit']['singleton']]==original['fit']['singleton']})
# Four independent formulations: add a dummy vertex; every vertex has degree exactly one.
edges30=[(a,b) for a in range(30) for b in range(a+1,30)];A=np.zeros((30,len(edges30)))
for k,(a,b) in enumerate(edges30):A[a,k]=A[b,k]=1
opt=[]
for fn,tag,ri,cost,expected in chosen:
 obj=[cost[(a,b)] if b!=29 else 0. for a,b in edges30]
 res=milp(obj,integrality=np.ones(len(obj)),bounds=Bounds(0,1),constraints=LinearConstraint(csc_matrix(A),np.ones(30),np.ones(30)),options={'time_limit':5.,'mip_rel_gap':0.,'threads':1})
 assert res.success and res.status==0 and res.mip_gap==0 and abs(res.fun-expected)<1e-7
 pairs=[edges30[k] for k,v in enumerate(res.x) if v>.5];assert len(pairs)==15 and len({v for p in pairs for v in p})==30
 opt.append({'file':fn,'tag':tag,'row':ri,'objective':res.fun,'original_objective':expected,'status':int(res.status),'gap':float(res.mip_gap),'dual_bound':float(res.mip_dual_bound),'nodes':int(res.mip_node_count),'pairs_including_dummy':pairs})
# Published summaries carry identical full-procedure tails; no chosen held mapping.
for filename in ['R03-pilot-results.json','R03-controls-0-12-results.json','R03-stress-results.json','R03-real-results.json']:
 published=json.loads((P/filename).read_text());matches=[p for p in panels if p['file']==filename.replace('-results.json','-full.jsonl.gz')]
 assert len(matches)==len(published['panels'])
 for a,b in zip(matches,published['panels']):
  assert abs(a['tail']-b['p_lower'])<1e-15 and max(abs(x-y) for x,y in zip(a['null'],b['null_stats']))<1e-10
  if a['true_pairs_recovered'] is not None:assert a['true_pairs_recovered']==b['true_pairs_recovered'] and a['true_singleton_recovered']==b['true_singleton_recovered']
out={'status':'PASS','records':nrecords,'null_records':nnull,'max_objective_error':maxerror,'max_conditional_row_sum_error':normerror,'panels':panels,'independent_formulation_optima':opt}
(R/'result.json').write_text(json.dumps(out,indent=2));print({k:v for k,v in out.items() if k not in ['panels','independent_formulation_optima']});print([(p['file'],p['tag'],p['tail'],p['true_pairs_recovered']) for p in panels])
