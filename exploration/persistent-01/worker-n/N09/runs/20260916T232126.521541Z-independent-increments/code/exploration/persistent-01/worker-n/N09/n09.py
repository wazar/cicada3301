from pathlib import Path
import json,hashlib,random,math,time,datetime,sys,gzip
import numpy as np
O=Path(__file__).resolve().parent;B=O.parents[1];MP=B/'worker-f/F06-maps.json';maps=json.loads(MP.read_text());pages=[];offsets=[0];runlengths=[]
for m in maps:
 c=m['indices'];base=[];runs=[]
 for i,v in enumerate(c):
  if not base or base[-1]!=v:base.append(v);runs.append([])
  runs[-1].append(i)
 pages.append(dict(page=m['page'],base=base,runs=runs,runlengths=list(map(len,runs)),source_coordinates=[[m['source_char_positions'][i] for i in run] for run in runs]));offsets.append(offsets[-1]+len(base));runlengths.extend(map(len,runs))
assert len(pages)==45 and not set(p['page'] for p in pages)&{4,9,14,19,24,29,34,39,44,54}
def guard():
 assert not (B/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
def symbol(a,b,rank):
 f=(2*b-a)%29
 if rank==27:return f
 lo,hi=sorted((b,f));out=rank
 if out>=lo:out+=1
 if out>=hi:out+=1
 return out
def inverse(a,b,c):
 f=(2*b-a)%29
 if c==f:return 27
 assert c!=b
 return c-int(c>b)-int(c>f)
def generate(epsilon,seed):
 rng=random.Random(seed);flat=[];latent=[]
 for page in pages:
  n=len(page['base']);c=[rng.randrange(29)];r=[c[0]]
  if n>1:
   rank=rng.randrange(28);c.append(rank+(rank>=c[-1]));r.append(rank)
  for i in range(2,n):
   rank=27 if rng.random()<epsilon else rng.randrange(27);c.append(symbol(c[-2],c[-1],rank));r.append(rank)
  assert all(a!=b for a,b in zip(c,c[1:]));flat.extend(c);latent.extend(r)
 return np.array(flat,dtype=np.uint8),np.array(latent,dtype=np.uint8)
def evaluate(flat,retain=False):
 rows=[];positions=[]
 for ordinal,page in enumerate(pages):
  c=flat[offsets[ordinal]:offsets[ordinal+1]].astype(np.int64);event=(c[2:]==(2*c[1:-1]-c[:-2])%29);rows.append(dict(page=page['page'],eligible=len(event),events=int(event.sum())))
  if retain:
   for i,value in enumerate(event,start=2):positions.append(dict(page=page['page'],collapsed_index=i,original_run_indices=page['runs'][i],preceding_run_indices=page['runs'][i-2:i],event=bool(value)))
 train_n=sum(r['eligible'] for r in rows[::2]);train_e=sum(r['events'] for r in rows[::2]);held_n=sum(r['eligible'] for r in rows[1::2]);held_e=sum(r['events'] for r in rows[1::2]);eps=min(1/28,(train_e+.5)/(train_n+1));eventgain=math.log(eps*28);othergain=math.log((1-eps)*28/27)
 for row in rows:row['gain']=row['events']*eventgain+(row['eligible']-row['events'])*othergain
 score=(held_e*eventgain+(held_n-held_e)*othergain)/held_n
 out=dict(train_eligible=train_n,train_events=train_e,held_eligible=held_n,held_events=held_e,epsilon=eps,score=score,perpage=rows,exact_zero_escape_violations=train_e+held_e)
 if retain:
  for r in positions:r['model_probability']=eps if r['event'] else (1-eps)/27;r['baseline_probability']=1/28
  out['positions']=positions
 return out
def finitecheck():
 cases=0
 for a in range(29):
  for b in range(29):
   if a==b:continue
   outputs=[symbol(a,b,r) for r in range(28)];assert set(outputs)==set(range(29))-{b}
   for r,c in enumerate(outputs):assert inverse(a,b,c)==r;cases+=1
   for eps in [0,1/56,1/28]:assert abs(eps+27*((1-eps)/27)-1)<1e-14
 return cases
def pilot():
 guard();checks=finitecheck();start=time.monotonic();records=[]
 for i in range(12):
  eps=[0,1/56,1/28][i%3];c,r=generate(eps,1718000+i);records.append(evaluate(c));expanded=np.repeat(c,runlengths);original=np.concatenate([m['indices'] for m in maps]);bounds=np.cumsum([0]+[len(m['indices']) for m in maps])
  for j in range(45):
   a=expanded[bounds[j]:bounds[j+1]];b=original[bounds[j]:bounds[j+1]];assert np.array_equal(a[1:]==a[:-1],b[1:]==b[:-1])
 elapsed=time.monotonic()-start;out=dict(finite_inverse_cases=checks,pilot_panels=12,seconds=elapsed,projected1199seconds=elapsed/12*1199,collapsed_total=offsets[-1],original_total=sum(runlengths),records=records);(O/'pilot.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='records'},indent=2))
def full():
 guard();finitecheck();actual=np.concatenate([p['base'] for p in pages]).astype(np.uint8);real=evaluate(actual,True);(O/'real.json').write_text(json.dumps(real,indent=2));(O/'input.json').write_text(json.dumps(dict(map_path=str(MP),map_sha256=hashlib.sha256(MP.read_bytes()).hexdigest(),pages=pages,collapsed_offsets=offsets,runlengths=runlengths),indent=2))
 C=np.empty((1199,offsets[-1]),dtype=np.uint8);R=np.empty_like(C);fullc=np.empty((1199,sum(runlengths)),dtype=np.uint8);records=[];spec=[('null',1/28,1719000+i) for i in range(999)]+[('hard',0.,1721000+i) for i in range(100)]+[('half',1/56,1722000+i) for i in range(100)]
 for i,(kind,eps,seed) in enumerate(spec):
  if i%100==0:guard()
  C[i],R[i]=generate(eps,seed);fullc[i]=np.repeat(C[i],runlengths);res=evaluate(C[i]);records.append(dict(kind=kind,generator_epsilon=eps,seed=seed,**res))
 null=[r['score'] for r in records[:999]];real['tail']=(1+sum(v>=real['score'] for v in null))/1000
 for row in records[999:]:row['tail']=(1+sum(v>=row['score'] for v in null))/1000;row['detected']=row['score']>0 and row['tail']<=.01
 np.savez_compressed(O/'generated.npz',collapsed=C,latent_ranks=R,expanded=fullc)
 with gzip.open(O/'replicates.json.gz','wt') as f:json.dump(records,f)
 out=dict(real={k:v for k,v in real.items() if k not in ['positions','perpage']},null_count=999,control_results={kind:dict(count=100,detected=sum(r['detected'] for r in records if r['kind']==kind),score_min=min(r['score'] for r in records if r['kind']==kind),score_max=max(r['score'] for r in records if r['kind']==kind)) for kind in ['hard','half']},total_panels=1200)
 (O/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
if __name__=='__main__':pilot() if sys.argv[1]=='pilot' else full()
