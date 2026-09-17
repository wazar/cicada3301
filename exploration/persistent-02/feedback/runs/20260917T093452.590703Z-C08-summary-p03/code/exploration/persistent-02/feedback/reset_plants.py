"""Frozen C08 plants and resumable exhaustive seed partitions."""
import extend as ex
from reset_literal import Engine,encode
import numpy as np,json,random,hashlib,resource,sys,gzip,itertools
O=ex.O/'C08';O.mkdir(exist_ok=True)
def prepare():
 src=ex.R/'exploration/persistent-02/section/A07-inputs.json';d=json.loads(src.read_text());rng=random.Random(2026092300);cases=[]
 for x in d['controls']:
  if not x['id'].startswith('periodic-'):continue
  seed=[rng.randrange(29) for _ in range(2)];literal=x['truth_literal_positions'];truth=x['truth'];resets=x['reset_before']
  cases.append(dict(id=x['id'],truth=truth,ends=x['ends'],reset_before=resets,seed=seed,literal_positions=literal,cipher=encode(truth,seed,literal,resets),source_id=x['id']))
 assert len(cases)==8
 p=O/'plants.json';assert not p.exists();p.write_text(json.dumps(dict(rng_seed=2026092300,source=str(src.relative_to(ex.R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),cases=cases),separators=(',',':'))+'\n');print('frozen',len(cases),hashlib.sha256(p.read_bytes()).hexdigest())
def model(name):
 if name=='p03':return ex.q.L
 assert name=='complementary';return np.load(ex.O/'C06/model.npz')['logprob']
def total(plain,ends,L):
 a=b=29;s=0.
 for i,p in enumerate(plain):
  s+=float(L[a,b,p]);a,b=b,p
  if i in ends:s+=float(L[a,b,29]);a,b=b,29
 return s
def run(ix,name):
 ex.guard();d=json.loads((O/'plants.json').read_text())['cases'][ix];L=model(name);out=O/f'{name}-plant{ix:02}';out.mkdir(exist_ok=True);seeds=list(itertools.product(range(29),repeat=2));rows=[]
 for part in range(29):
  ex.guard();path=out/f'part{part:02}.json.gz'
  if path.exists():
   with gzip.open(path,'rt') as f:r=json.load(f)
  else:
   r=Engine(seeds[part*29:(part+1)*29],L).solve(d['cipher'],d['ends'],d['reset_before']);r['partition']=part;r['peak_process_rss_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
   for alt in r['alternatives']:
    assert encode(alt['plain'],alt['seed'],alt['literal_positions'],d['reset_before'])==d['cipher'];assert abs(total(alt['plain'],set(d['ends']),L)-alt['total'])<1e-8
   with gzip.open(path,'wt') as f:json.dump(r,f,separators=(',',':'))
   print(name,ix,'partition',part,'seconds',r['seconds'],'states',r['peak_states'],flush=True)
  rows.append(r)
 alts=sorted([a for r in rows for a in r['alternatives']],key=lambda a:(-a['total'],a['seed']))[:16];truthscore=total(d['truth'],set(d['ends']),L);assert alts[0]['total']>=truthscore-1e-8
 report=dict(index=ix,id=d['id'],model=name,seed_count=841,maximum=alts[0]['total'],truth_score=truthscore,truth_gap=alts[0]['total']-truthscore,selected_rune_errors=sum(a!=b for a,b in zip(alts[0]['plain'],d['truth'])),truth_in_retained=any(a['plain']==d['truth'] for a in alts),seconds=sum(r['seconds'] for r in rows),peak_states=max(r['peak_states'] for r in rows),peak_process_rss_bytes=max(r['peak_process_rss_bytes'] for r in rows),alternatives=alts)
 (out/'summary.json').write_text(json.dumps(report,separators=(',',':'))+'\n');print(json.dumps({k:v for k,v in report.items() if k!='alternatives'}),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 else:
  for ix in map(int,sys.argv[2:]):run(ix,sys.argv[1])
