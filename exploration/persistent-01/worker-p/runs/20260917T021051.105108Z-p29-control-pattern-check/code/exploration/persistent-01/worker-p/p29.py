import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,gzip,hashlib,random,sys,time,datetime
import numpy as np
R=Path(__file__).resolve().parents[3];B=R/'exploration/persistent-01';W=B/'worker-p';O=W/'P29'
def guard():
 assert not (B/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
SOURCE=read(W/'P17/source.json.gz');RUNES=[x for w in SOURCE['words'] for x in w['runes']];MAP=read(B/'review-25/source-replay.json.gz');assert RUNES==MAP['runes'] and len(RUNES)==18584;assert hashlib.sha256((W/'P17/pg45315.txt').read_bytes()).hexdigest()==MAP['raw_sha256'];PAIRS=[29*a+b for a,b in zip(RUNES,RUNES[1:])];N=131;WINDOWS=len(RUNES)-2*N+1;assert WINDOWS==18323

def check(c,start):
 forward={};reverse={}
 for i,b in enumerate(c):
  a=PAIRS[start+2*i]
  if a in forward:
   old,j=forward[a]
   if old!=b:return i,1,j,None
  if b in reverse:
   old,j=reverse[b]
   if old!=a:return i,2,j,None
  forward[a]=(b,i);reverse[b]=(a,i)
 return N,0,65535,{a:x[0] for a,x in forward.items()}
def search(c):
 arrays=np.empty((WINDOWS,3),dtype=np.uint16);witnesses=[]
 for s in range(WINDOWS):
  l,k,j,m=check(c,s);arrays[s]=[l,k,j]
  if m is not None:
   unusedin=sorted(set(range(841))-set(m));unusedout=sorted(set(range(841))-set(m.values()));complete=dict(m);complete.update(zip(unusedin,unusedout));assert len(set(complete.values()))==841
   witnesses.append(dict(start=s,plain=RUNES[s:s+262],partial_map=[[a,b] for a,b in sorted(m.items())],full_map=[complete[a] for a in range(841)],unidentifiable_assignments=len(unusedin)))
 return arrays,witnesses

def plant(i):
 start=[0,4096,8192,12288][i];mapping=list(range(841));random.Random(529100+i).shuffle(mapping);src=PAIRS[start:start+262:2];assert len(src)==N;c=[mapping[x] for x in src];return c,dict(source_start=start,seed=529100+i,full_map=mapping,plain=RUNES[start:start+262])
def panel(name,c,extra={}):
 guard();p=O/(name+'.json')
 if p.exists():return json.loads(p.read_text())
 t=time.monotonic();arr,wit=search(c);np.savez_compressed(O/(name+'.npz'),cipher_pairs=np.array(c,dtype=np.uint16),obstructions=arr);d=dict(name=name,windows=WINDOWS,maximum_prefix=int(arr[:,0].max()),complete_matches=len(wit),witnesses=wit,seconds=time.monotonic()-t,**extra);save(name+'.json',d);return d

def ensemble(i,n):
 c,truth=plant(i);main=panel(f'control-{i}',c,dict(truth=truth));assert any(w['start']==truth['source_start'] for w in main['witnesses']);ns=[]
 for j in range(n):
  seed=529200+100*i+j;perm=list(range(N));random.Random(seed).shuffle(perm);ns.append(panel(f'control-{i}-null-{j:03}',[c[k] for k in perm],dict(seed=seed,permutation=perm)))
 summary(f'control-{i}-'+('pilot' if n<99 else 'summary')+'.json',main,ns)
def summary(name,r,ns):
 s=dict(maximum_prefix=r['maximum_prefix'],complete_matches=r['complete_matches'],matching_offsets=[x['start'] for x in r['witnesses']],nulls=len(ns),null_full_acceptances=sum(x['complete_matches']>0 for x in ns),null_maxima=[x['maximum_prefix'] for x in ns],prefix_tail=(1+sum(x['maximum_prefix']>=r['maximum_prefix'] for x in ns))/(len(ns)+1));save(name,s);print(name,json.dumps(s),flush=True)
def pilot():
 # Freeze exact source and cipher maps; no main image/cipher fit here.
 page=next(x for x in json.loads((B/'worker-f/F06-maps.json').read_text()) if x['page']==0);assert len(page['indices'])==262
 with gzip.open(O/'source-maps.json.gz','wt') as f:json.dump(dict(source=SOURCE,rune_maps=MAP['rune_maps'],runes=RUNES,cipher_page=page,source_raw_sha256=MAP['raw_sha256'],source_json_sha256=hashlib.sha256((W/'P17/source.json.gz').read_bytes()).hexdigest()),f)
 malformed=[]
 for i in range(4):
  c,tr=plant(i);s=tr['source_start'];p=PAIRS[s:s+262:2];assert check(c,s)[0]==N
  repeat=next(j for j,a in enumerate(p) if a in p[:j]);bad=c.copy();bad[repeat]=next(x for x in range(841) if x not in c);z=check(bad,s);assert z[:2]==(repeat,1);malformed.append(dict(control=i,kind='same_source_two_outputs',cipher=bad,result=list(z[:3]),source_start=s))
  different=next(j for j,a in enumerate(p) if a!=p[0]);bad=c.copy();bad[different]=c[0];z=check(bad,s);assert z[1]==2;malformed.append(dict(control=i,kind='two_sources_one_output',cipher=bad,result=list(z[:3]),source_start=s))
 save('malformed-controls.json',malformed);ensemble(0,3)
def controls():
 for i in range(4):ensemble(i,99)
def actual():
 assert all((O/f'control-{i}-summary.json').exists() for i in range(4));page=next(x for x in json.loads((B/'worker-f/F06-maps.json').read_text()) if x['page']==0);a=page['indices'];c=[29*x+y for x,y in zip(a[::2],a[1::2])];r=panel('actual',c,dict(page=0,source_positions=page['source_char_positions'],ignored_words=page['words']));ns=[]
 for j in range(199):
  seed=530000+j;perm=list(range(N));random.Random(seed).shuffle(perm);ns.append(panel(f'actual-null-{j:03}',[c[k] for k in perm],dict(seed=seed,permutation=perm)))
 summary('summary.json',r,ns)
if __name__=='__main__':
 guard();t=time.monotonic();{'pilot':pilot,'controls':controls,'actual':actual}[sys.argv[1]]();print('SECONDS',time.monotonic()-t)
