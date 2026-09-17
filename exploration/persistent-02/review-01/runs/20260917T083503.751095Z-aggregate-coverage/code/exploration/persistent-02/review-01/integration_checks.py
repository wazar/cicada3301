"""Representative integration review, no new puzzle search grid."""
from independent_checks import R,O,load,exact,st,dump,rng
import sys,json,gzip,hashlib,itertools,math,statistics,numpy as np
sys.path.insert(0,str(R/'exploration/persistent-02/decoder'))
import compare
q=load('review_q12','exploration/persistent-01/coordinator/Q12-sum-autokey/test.py')
ag=load('review_aggregate','exploration/persistent-02/coordinator/aggregate_q12.py')
def references():
 rows=[];lm=compare.LM()
 for case in compare.references():
  name=case['id'][10:];fixture=next(x for x in compare.CASES if x[0]==name)
  # Replay known source rule independently, then run search without interruptions.
  c=case['cipher'];u=0;p=[];fseen=0
  for i,v in enumerate(c):
   fseen+=v==0
   if v==0 and fseen in fixture[3]:p.append(0)
   else:p.append((v-case['key'][u%len(case['key'])])%29);u+=1
  assert p==case['truth']
  got=compare.run(case,lm,retain=256);old=json.loads(gzip.decompress((R/'exploration/persistent-02/decoder/references'/(case['id']+'.json.gz')).read_bytes()))
  assert got['case']==old['case'] and got['exact']==old['exact']
  assert got['truth_metrics']==old['truth_metrics']
  for width in ['64','256','1024']:assert got['beams'][width]['gap']==old['beams'][width]['gap']
  rows.append(got);print('reference passed',case['id'],flush=True)
 # One measured maximal width1024 pruning counterexample; selected to test claim,
 # not a fresh independent discovery evaluation.
 candidates=[]
 for f in (R/'exploration/persistent-02/decoder/section').glob('*.json.gz'):
  data=json.loads(gzip.decompress(f.read_bytes()));candidates.append(data)
 old=max(candidates,key=lambda x:x['beams']['1024']['gap']);got=compare.run(old['case'],lm,retain=16)
 assert got['exact']==old['exact']
 for w in ['64','256','1024']:assert got['beams'][w]['gap']==old['beams'][w]['gap']
 rows.append(got);dump('reference-and-pair-checks.json',dict(passed=True,rows=rows))
 print('section counterexample',got['case']['id'],{w:b['gap'] for w,b in got['beams'].items()},flush=True)
def plants():
 f=R/'exploration/persistent-02/decoder/fresh-controls.json';data=json.loads(f.read_text());sources=[];rows=[]
 for s in data['sources']:
  assert hashlib.sha256((R/s['path']).read_bytes()).hexdigest()==s['sha256'];sources.append(s)
 for name,k in [('fresh-guest-0',5),('fresh-mill-1',6),('fresh-shelley-2',7),('fresh-blake-2',8)]:
  case=next(x for x in data['cases'] if x['id']==name);p=case['truth'];ends=set(case['ends']);seed=[rng.randrange(29) for _ in range(k)]
  c=[(p[i]+(seed[i] if i<k else sum(p[i-k:i])))%29 for i in range(len(p))]
  baseline=[]
  for i,v in enumerate(c):baseline.append((v-(0 if i<k else sum(baseline[i-k:i])))%29)
  e=[(-x)%29 for x in seed];e.append(-sum(e)%29);assert all((baseline[i]+e[i%(k+1)])%29==p[i] for i in range(len(p)))
  W=q.table(baseline,ends,k)
  # Check factor assembly against whole-string local scoring for100 fresh offsets.
  maxerr=0.
  for _ in range(100):
   off=[rng.randrange(29) for _ in range(k)];off.append(-sum(off)%29)
   pp=[(baseline[i]+off[i%(k+1)])%29 for i in range(len(p))]
   direct=q.lm.score(pp,ends)*(len(p)+len(ends));fac=sum(float(W[j,off[j-2],off[j-1],off[j]]) for j in range(k+1));maxerr=max(maxerr,abs(direct-fac))
  assert maxerr<1e-8
  got=st.solve(W);truthscore=q.lm.score(p,ends)*(len(p)+len(ends));assert got['upper_bound']>=truthscore-1e-8
  best=got['alternatives'][0]['offset'];plain=[(baseline[i]+best[i%(k+1)])%29 for i in range(len(p))]
  rows.append(dict(id=name,k=k,seed=seed,cipher=c,truth=p,ends=sorted(ends),factor_max_abs_error=maxerr,result=got,errors=sum(a!=b for a,b in zip(p,plain))))
  print('fresh plant',name,k,rows[-1]['errors'],got['gap'],flush=True)
 dump('fresh-plant-checks.json',dict(passed=True,seed=9170835,source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),sources=sources,rows=rows,scope='Frozen B excerpts reused with new reviewer seeds; not new source population'))
def aggregate():
 root=R/'exploration/persistent-02';cfg=json.loads((root/'config.json').read_text());coverage=json.loads((root/'feedback/C01/coverage.json').read_text())
 data=json.loads((root/'coordinator/C01-aggregate.json').read_text());pages=data['pages'];assert len(pages)==len(set(pages))==42
 assert not set(pages)&set(cfg['reserved_originals']+[0,17,55]);matrix=[];seedset=set();hashes=[]
 expected={x['page'] for x in json.loads((R/'exploration/persistent-01/worker-f/F06-maps.json').read_text())}-set(cfg['reserved_originals']+[0,17,55])
 assert set(pages)==expected=={x['page'] for x in coverage}
 for page in pages:
  row=[]
  for j in range(20):
   path=root/'feedback/C01'/f"actual{page}{'-null%02d'%(j-1) if j else ''}.json";x=json.loads(path.read_text());row.append(x['maximum'])
   assert x['seeds']==sum(29**k for k in [2,3,4]);assert x['maximum']==max(v['top16'][0]['score'] for v in x['rows'])
   if j:
    seed=2026091700+100*page+j-1;assert x['null_seed']==seed and seed not in seedset;seedset.add(seed)
   else:assert x['null_seed'] is None
   hashes.append(dict(path=str(path.relative_to(R)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
  matrix.append(row)
 z=[]
 for row in matrix:
  mu=sum(row)/20;sd=math.sqrt(sum((x-mu)**2 for x in row)/20);z.append([(x-mu)/sd if sd else 0 for x in row])
 maxima=[max(row[i] for row in z) for i in range(20)];rank=sum(x>=maxima[0] for x in maxima)/20
 assert max(abs(a-b) for a,b in zip(maxima,data['panel_maxima']))<1e-12 and rank==data['composite_upper_tail_rank']
 assert hashes==data['sources'] and matrix==data['maxima_by_page_actual_then_19_nulls']
 # All20 labels treated symmetrically before designated observed-label ranking.
 for order in [list(range(19,-1,-1)),list(range(1,20))+[0]]:
  zz,mm,_=ag.aggregate([[row[i] for i in order] for row in matrix]);assert max(abs(mm[i]-maxima[j]) for i,j in enumerate(order))<1e-12
 dump('aggregate-checks.json',dict(passed=True,pages=pages,source_count=len(hashes),unique_null_seeds=len(seedset),panel_maxima=maxima,rank=rank,qualification='Composite comparator rank, no global discovery probability; matrix arithmetic and metadata review, no full-search replay'))
 print('aggregate passed',rank,flush=True)
if __name__=='__main__':references();plants();aggregate()
