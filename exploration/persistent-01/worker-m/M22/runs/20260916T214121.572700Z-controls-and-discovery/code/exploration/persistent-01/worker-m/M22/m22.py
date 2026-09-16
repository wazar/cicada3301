import sys,pathlib,json,ctypes,numpy as np,random,time,gzip,hashlib,zlib,datetime,importlib
R=pathlib.Path(__file__).parent;ROOT=R.parents[3];sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'));from p03_frozen import LM,parse,beam;from p09_viterbi import viterbi,exhaustive;from p08 import fit
lib=ctypes.CDLL(str(R/'exact.dylib'));I=np.ctypeslib.ndpointer(np.int32,flags='C_CONTIGUOUS');F=np.ctypeslib.ndpointer(np.float64,flags='C_CONTIGUOUS');lib.fixed.argtypes=[I,I,ctypes.c_int,I,ctypes.c_int,F];lib.fixed.restype=ctypes.c_double;lib.scan.argtypes=[I,I,ctypes.c_int,ctypes.c_int,F,F]
lm=LM();tab=np.array([lm.step((a,b),c)[1] for a in range(30) for b in range(30) for c in range(30)],dtype=np.float64)
def gate():
 assert not(R.parent.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(name,x):
 (R/(name+'.json')).write_text(json.dumps(x,indent=2))
def key(code,p):
 out=[0]*p
 for j in range(p-1,-1,-1):out[j]=code%29;code//=29
 return out
def cscore(c,ends,k):return lib.fixed(np.array(c,dtype=np.int32),np.array([i in ends for i in range(len(c))],dtype=np.int32),len(c),np.array(k,dtype=np.int32),len(k),tab)
def summary_stats(p):
 cnt=np.bincount(p,minlength=29);return dict(ioc_times_n=float((cnt*(cnt-1)).sum()/max(1,len(p)-1)),min32distinct=min(len(set(p[j:j+32])) for j in range(max(1,len(p)-31))),zlib_bytes=len(zlib.compress(bytes(p))),runes=len(p),non_english_lm='N/A frozen English rune model only')
def search(c,ends,name):
 gate();start=time.monotonic();split=len(c)//2;te={i for i in ends if i<split};cc=np.array(c[:split],dtype=np.int32);ee=np.array([i in te for i in range(split)],dtype=np.int32);scores={};leaders=[]
 for p in [1,2,3]:
  a=np.empty(29**p,dtype=np.float64);lib.scan(cc,ee,split,p,tab,a);scores['period'+str(p)]=a;ix=int(np.argmax(a));leaders.append(dict(period=p,code=ix,key=key(ix,p),score=float(a[ix])))
 best=max(leaders,key=lambda x:x['score']);k=best['key'];tr,td=viterbi(c[:split],te,k,-1,lm);assert abs(tr[0]['score']-best['score'])<1e-11;s=(29,29)
 for i,v in enumerate(tr[0]['plain']):s,_=lm.extend(s,v,i in te)
 se={i-split for i in ends if i>=split};co,cd=viterbi(c[split:],se,k,-1,lm,start_context=s,start_used=tr[0]['used'])
 np.savez_compressed(R/'scores'/ (name+'.npz'),**scores)
 def reenc(plain,lit,u):
  out=[]
  for i,p in enumerate(plain):
   if i in lit:assert p==0;out.append(0)
   else:out.append((p+k[u%len(k)])%29);u+=1
  return out
 assert reenc(tr[0]['plain'],set(tr[0]['literal_positions']),0)==c[:split];assert reenc(co[0]['plain'],set(co[0]['literal_positions']),tr[0]['used'])==c[split:]
 out=dict(name=name,cipher=c,ends=sorted(ends),split=split,period_leaders=leaders,best=best,training=tr,continuation=co,frozen_boundary=dict(context=list(s),used=tr[0]['used']),score=co[0]['score'],reencryption=True,statistics=summary_stats(tr[0]['plain']+co[0]['plain']),seconds=time.monotonic()-start)
 with gzip.open(R/'outputs'/(name+'.json.gz'),'wt') as f:json.dump(out,f)
 return out,scores

def fixture(name,period,ix):
 f=ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt');plain,ends=parse(f.read_text());rng=random.Random(330822+ix);k=[rng.randrange(1,29) for _ in range(period)];c=[];path=[];u=0
 for i,p in enumerate(plain):
  if p==0 and i%3!=1:c.append(0);path.append(i)
  else:c.append((p+k[u%period])%29);u+=1
 return dict(name=name+'-p'+str(period),source=str(f.relative_to(ROOT)),source_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),plain=plain,ends=sorted(ends),key=k,cipher=c,literal_positions=path)
def permute(c,rng):
 out=c.copy();nz=[i for i,v in enumerate(c) if v];vals=[c[i] for i in nz];rng.shuffle(vals)
 for i,v in zip(nz,vals):out[i]=v
 return out

def pilot():
 gate();(R/'scores').mkdir(exist_ok=True);(R/'outputs').mkdir(exist_ok=True);rng=random.Random(330822);checks=[]
 for ix in range(100):
  n=rng.randrange(5,20);c=[0 if rng.random()<.3 else rng.randrange(29) for _ in range(n)];ends={i for i in range(n) if rng.random()<.2}|{n-1};k=[rng.randrange(29) for _ in range(rng.randrange(1,4))];a=cscore(c,ends,k);v,diag=viterbi(c,ends,k,-1,lm);ex=exhaustive(c,ends,k,-1,lm);assert abs(a-v[0]['score'])<1e-12 and abs(a-ex[0]['score'])<1e-12;checks.append(dict(cipher=c,ends=sorted(ends),key=k,score=a,masks=len(ex)))
 dump('arithmetic-checks',checks);f=fixture('0_welcome',3,0);res,scores=search(f['cipher'],set(f['ends']),'pilot-welcome');dump('pilot',dict(seconds=res['seconds'],projected_452_searches=res['seconds']*452,fixture=f,result=res,model_sources=lm.files));print('PILOT',res['seconds'],res['best'],flush=True)

def run():
 decision=json.load(open(R/'decision.json'));control_n=decision['control_nulls'];real_n=decision['real_nulls'];rng=random.Random(330823);controlrows=[];ix=0
 for name in ['0_welcome','jpg107-167','p56_an_end','p57_parable']:
  for period in [1,2,3]:
   gate();f=fixture(name,period,ix);ix+=1;label='control-'+f['name'];r,scores=search(f['cipher'],set(f['ends']),label);split=r['split'];te={i for i in f['ends'] if i<split};truthcode=0
   for v in f['key']:truthcode=truthcode*29+v
   truthscore=float(scores['period'+str(period)][truthcode]);truthrank=1+int(np.sum(scores['period'+str(period)]>truthscore+1e-12));oracles,diag=viterbi(f['cipher'][:split],te,f['key'],-1,lm);truepath_score=lm.score(f['plain'][:split],te);heur,starts,evals,expanded=fit(f['cipher'][:split],te,period,lm,330108+ix,width=32,restarts=2,sweeps=3);b,bd=beam(f['cipher'][:split],te,f['key'],-1,lm,32,truth=[i for i in f['literal_positions'] if i<split]);null=[]
   for j in range(control_n):
    nr,_=search(permute(f['cipher'],rng),set(f['ends']),label+'-null'+str(j));null.append(dict(name=nr['name'],score=nr['score'],best=nr['best']))
   row=dict(fixture=f,result=r,truth_key_rank_within_period=truthrank,truthkey_best_path_score=truthscore,truepath_score=truepath_score,exact_fixed_truth_key_training_errors=sum(a!=b for a,b in zip(oracles[0]['plain'],f['plain'][:split])),beam_truth_diagnostics=bd,beam_fixed_truth_key_training_errors=sum(a!=b for a,b in zip(b[0]['plain'],f['plain'][:split])),heuristic=dict(best=heur,starts=starts,evaluations=evals,expanded=expanded,settings=dict(width=32,restarts=2,sweeps=3),key_recovered=heur['key']==f['key'],global_objective_gap=max(scores['period'+str(period)])-heur['score']),exact_selected_key_recovered=r['best']['key']==f['key'],train_errors=sum(a!=b for a,b in zip(r['training'][0]['plain'],f['plain'][:split])),suffix_errors=sum(a!=b for a,b in zip(r['continuation'][0]['plain'],f['plain'][split:])),null=null,tail=(1+sum(x['score']>=r['score'] for x in null))/(control_n+1))
   controlrows.append(row);dump('controls',controlrows);print(label,'rank',truthrank,'recover',row['exact_selected_key_recovered'],'tail',row['tail'],flush=True)
 # no reserve reads; use only already-authorized discovery0/17 records
 maps=json.load(open(ROOT/'exploration/persistent-01/worker-f/F06-maps.json'));real=[]
 for m in maps:
  if m['page'] not in [0,17]:continue
  c=m['indices'];parsed,ends=parse(m['raw_joined']);assert parsed==c;label='real-'+str(m['page']);r,_=search(c,ends,label);null=[]
  for j in range(real_n):
   nr,_=search(permute(c,rng),ends,label+'-null'+str(j));null.append(dict(name=nr['name'],score=nr['score'],best=nr['best']))
  row=dict(page=m['page'],source_map=m,result=r,null=null,tail=(1+sum(x['score']>=r['score'] for x in null))/(real_n+1));real.append(row);dump('real',real);print(label,r['score'],row['tail'],flush=True)
 dump('summary',dict(control_count=len(controlrows),controls_detected_05=sum(x['tail']<=.05 for x in controlrows),controls_exact_key_recovered=sum(x['exact_selected_key_recovered'] for x in controlrows),controls_heuristic_key_recovered=sum(x['heuristic']['key_recovered'] for x in controlrows),control_search_key_rank1=sum(x['truth_key_rank_within_period']==1 for x in controlrows),real=[dict(page=x['page'],score=x['result']['score'],tail=x['tail'],key=x['result']['best']['key']) for x in real],control_nulls=control_n,real_nulls=real_n,nominal_keys_persearch=25259,distinct_streams_persearch=25201,total_full_searches=12*(control_n+1)+2*(real_n+1),rng_after=repr(rng.getstate()),model_sources=lm.files))
if __name__=='__main__':pilot() if sys.argv[1]=='pilot' else run()
