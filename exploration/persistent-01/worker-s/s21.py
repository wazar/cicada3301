import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,gzip,hashlib,itertools,datetime,time
B=Path('exploration/persistent-01');O=B/'worker-s/S21';O.mkdir(exist_ok=True);S=B/'worker-s/S20';N=2355;K=14
def guard():assert not (B/'STOP').exists() and datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,24,tzinfo=datetime.timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
guard();start=time.monotonic();control_rows=[]
for counts in itertools.product(range(4),repeat=4):
 for cap in [1,2,3]:
  masses=[sum(counts[i] for i in subset) for subset in itertools.combinations(range(4),cap)];best=max(masses);assert best==sum(sorted(counts,reverse=True)[:cap]);retained=sorted(range(4),key=lambda i:(-counts[i],i))[:cap];seq=[i for i,n in enumerate(counts) for _ in range(n)];projected=[x if x in retained else retained[0] for x in seq];errors=sum(x!=y for x,y in zip(seq,projected));assert errors==sum(counts)-best;control_rows.append(dict(counts=counts,cap=cap,best_mass=best,minimum_errors=errors,retained=retained))
(O/'controls.json.gz').write_bytes(gzip.compress(json.dumps(control_rows).encode(),mtime=0));print('controls PASS',len(control_rows),flush=True)
inputs=json.loads((S/'inputs.json').read_text())
for f in inputs:assert sha(Path(f['path']))==f['sha256']
sources=load(S/'sources.json.gz');rows=[]
for s in sources:
 guard();seq=np.array(s['runes'],dtype=np.int16);windows=len(seq)-N+1;counts=np.zeros((windows,29),dtype=np.uint16);current=np.bincount(seq[:N],minlength=29).astype(np.int32);counts[0]=current
 for i in range(1,windows):
  current[seq[i-1]]-=1;current[seq[i+N-1]]+=1;counts[i]=current
 for rune in range(29):
  prefix=np.concatenate(([0],np.cumsum(seq==rune)));assert np.array_equal(prefix[N:]-prefix[:-N],counts[:,rune])
 assert np.all(counts.sum(axis=1)==N)
 frozen=load(S/(s['name']+'-windows.json.gz'));support=(counts>0).sum(axis=1);assert support.tolist()==frozen['all_support_counts']
 errors=N-np.sort(counts,axis=1)[:,-K:].sum(axis=1);minimum=int(errors.min());offsets=np.flatnonzero(errors==minimum).tolist();np.savez_compressed(O/(s['name']+'.npz'),counts=counts,minimum_errors=errors.astype(np.uint16),support=support.astype(np.uint8))
 row=dict(name=s['name'],windows=windows,minimum_errors=minimum,minimum_error_fraction=minimum/N,maximum_lower_bound=int(errors.max()),achieving_offsets=offsets,achieving_supports=[int(support[i]) for i in offsets],achieving_raw_spans=[[s['rune_char_spans'][i][0],s['rune_char_spans'][i+N-1][1]] for i in offsets],minimum_counts=counts[offsets].tolist());(O/(s['name']+'.json')).write_text(json.dumps(row,separators=(',',':')));rows.append({k:v for k,v in row.items() if k not in ['achieving_offsets','achieving_supports','achieving_raw_spans','minimum_counts']}|dict(achieving_windows=len(offsets),achieving_support_set=sorted(set(row['achieving_supports']))))
files=[S/'sources.json.gz',S/'inputs.json',B/'worker-s/S21-CARD.md',Path(__file__)]+[S/(s['name']+'-windows.json.gz') for s in sources]
(O/'inputs.json').write_text(json.dumps([dict(path=str(p),sha256=sha(p)) for p in files],indent=2));result=dict(status='PASS',window_length=N,type_cap=K,controls=len(control_rows),total_windows=sum(r['windows'] for r in rows),source_results=rows,seconds=time.monotonic()-start);(O/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
