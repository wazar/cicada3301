import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,subprocess,time,datetime,random,sys
import numpy as np
B=Path('exploration/persistent-01/worker-s');O=B/'S19';STOP=Path('exploration/persistent-01/STOP');DEAD=int(datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc).timestamp());meta=json.loads((O/'manifest.json').read_text());packets=json.loads((O/'packets.json').read_text());lm=np.fromfile(O/'model-table.bin',dtype='<f8').reshape(30,30,30)
def guard():
 assert not STOP.exists() and time.time()<DEAD
 for p,h in {**meta['input_hashes'],**meta['hashes']}.items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p

def scalar(chunks,m):
 result=0.
 for chunk in chunks:
  a=b=29
  for x in chunk:
   p=m[x];result+=float(lm[a,b,p]);a,b=b,p
 return result

def null(j):
 path=O/f'null{j:02}.input.json'
 if path.exists():return json.loads(path.read_text())
 seed=1709192619+j;rng=random.Random(seed);perms=[];chunks=[]
 for a in packets[4]['chunks']:
  p=list(range(len(a)));rng.shuffle(p);perms.append(p);chunks.append([a[i] for i in p])
 out={'seed':seed,'permutations':perms,'chunks':chunks};path.write_text(json.dumps(out));return out

def search(i,j=None):
 guard();path=O/(f'control{i}.json' if i<4 else ('actual.json' if j is None else f'null{j:02}.json'))
 if path.exists():return json.loads(path.read_text())
 p=packets[i];chunks=p['chunks'] if j is None else null(j)['chunks'];flat=[x for a in chunks for x in a];ts=[]
 for k,a in enumerate(chunks):
  if k:ts.append(29)
  ts.extend(a)
 assert len(flat)==2355;freq=sorted(range(29),key=lambda r:(-flat.count(r),r));init=[0]*29
 for c,x in zip(freq,meta['plain_frequency_rank']):init[c]=x
 seed=1709182619+100*i+(0 if j is None else j+1);inp=path.with_suffix('.input.txt');inp.write_text(' '.join(map(str,[len(ts),seed,DEAD]+init+ts))+'\n');cmd=[str((O/'engine').resolve()),str((O/'model-table.bin').resolve()),str(inp.resolve()),str(STOP.resolve())];start=time.monotonic();r=subprocess.run(cmd,capture_output=True,timeout=min(850,max(1,int(DEAD-time.time()))));seconds=time.monotonic()-start;path.with_suffix('.stdout').write_bytes(r.stdout);path.with_suffix('.stderr').write_bytes(r.stderr);assert r.returncode==0,('engine exit',r.returncode)
 data=json.loads(r.stdout);assert len(data['restarts'])==24
 for pr in data['probes']:
  before=scalar(chunks,pr['map']);m=pr['map'].copy();m[pr['a']],m[pr['b']]=m[pr['b']],m[pr['a']];after=scalar(chunks,m);assert abs(pr['before']-before)<1e-7 and abs(pr['after']-after)<1e-7 and abs(after-before-pr['delta'])<1e-7
 for row in data['restarts']:
  assert sorted(row['map'])==list(range(29));assert abs(scalar(chunks,row['map'])-row['score'])<1e-7;row['plain_chunks']=[[row['map'][x] for x in a] for a in chunks]
 best=max(data['restarts'],key=lambda r:r['score']);data.update({'name':p['name'],'packet':i,'j':j,'cipher_chunks':chunks,'seconds':seconds,'command':cmd,'exit':r.returncode,'maximum':best['score'],'mean_rune_score':best['score']/len(flat),'best_restart':best['restart'],'complete':True})
 if i<4:
  truth=[x for a in p['truth'] for x in a];got=[x for a in best['plain_chunks'] for x in a];used=sorted(set(flat));tm=p['truth_map'];truthscore=scalar(chunks,tm);errs=[sum(x!=y for x,y in zip(truth,[v for a in row['plain_chunks'] for v in a])) for row in data['restarts']]
  data['control']={'truth_score':truthscore,'truth_rank':1+sum(row['score']>truthscore+1e-8 for row in data['restarts']),'plaintext_accuracy':sum(x==y for x,y in zip(truth,got))/len(truth),'errors':[k for k,(x,y) in enumerate(zip(truth,got)) if x!=y],'observed_map_accuracy':sum(best['map'][x]==tm[x] for x in used)/len(used),'full_map_accuracy':sum(x==y for x,y in zip(best['map'],tm))/29,'equivalent_on_observed':all(best['map'][x]==tm[x] for x in used),'unused_labels':sorted(set(range(29))-set(used)),'retained_exact_plaintexts':sum(e==0 for e in errs),'all_retained_error_counts':errs}
 path.write_text(json.dumps(data));print(json.dumps({'packet':i,'null':j,'seconds':seconds,'maximum':best['score'],'mean_rune_score':data['mean_rune_score'],'control':data.get('control')}),flush=True);return data
mode=sys.argv[1]
if mode=='pilot':
 r=search(0);print('full24search_forecast_seconds',r['seconds']*24)
elif mode=='controls':
 rs=[search(i) for i in range(4)];gate=sum(r['control']['plaintext_accuracy']>=.8 for r in rs)>=2;out={'gate':gate,'controls':[r['control'] for r in rs]};(O/'controls-summary.json').write_text(json.dumps(out,indent=2));print('GATE',gate)
elif mode=='actual':
 assert json.loads((O/'controls-summary.json').read_text())['gate'];search(4)
 for j in range(19):search(4,j)
