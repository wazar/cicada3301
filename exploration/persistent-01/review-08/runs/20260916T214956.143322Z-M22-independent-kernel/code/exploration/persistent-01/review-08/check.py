import pathlib,json,hashlib,subprocess,ctypes,collections,itertools,math,gzip,datetime
import numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];M=O.parent/'worker-m/M22'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readzip(p):
 with gzip.open(p,'rt') as f:return json.load(f)
A='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def parse(raw):
 p=[];ends=set();active=False
 for x in raw:
  if x in A:p.append(A.index(x));active=True
  elif active:ends.add(len(p)-1);active=False
 if active:ends.add(len(p)-1)
 return p,ends

def main():
 assert not(O.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
 summary=load(M/'summary.json');sources=summary['model_sources'];co=[collections.Counter() for _ in range(3)];ct=[collections.Counter() for _ in range(3)]
 for source in sources:
  path=R/source['path'];assert sha(path)==source['sha256'];plain,ends=parse(path.read_text());tokens=[29,29]
  for i,v in enumerate(plain):
   for token in ([v,29] if i in ends else [v]):
    for order in range(3):context=tuple(tokens[-order:]) if order else ();co[order][context+(token,)]+=1;ct[order][context]+=1
    tokens.append(token)
 tab=np.zeros((30,30,30))
 for a,b,c in itertools.product(range(30),repeat=3):
  p=(co[0][(c,)]+.5)/(ct[0][()]+15)
  p=(co[1][(b,c)]+8*p)/(ct[1][(b,)]+8);p=(co[2][(a,b,c)]+5*p)/(ct[2][(a,b)]+5);tab[a,b,c]=math.log(p)
 assert np.allclose(np.exp(tab).sum(2),1);np.save(O/'independent-lm-table.npy',tab)
 (O/'exact.c').write_bytes((M/'exact.c').read_bytes());cmd=['cc','-O3','-std=c99','-dynamiclib',str(O/'exact.c'),'-o',str(O/'exact-local.dylib')];p=subprocess.run(cmd,capture_output=True,text=True);compiler={'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'version':subprocess.run(['cc','--version'],capture_output=True,text=True).stdout,'binary_local_only':True,'source_sha256':sha(O/'exact.c')};(O/'compiler.json').write_text(json.dumps(compiler,indent=2));assert p.returncode==0
 lib=ctypes.CDLL(str(O/'exact-local.dylib'));I=np.ctypeslib.ndpointer(np.int32,flags='C_CONTIGUOUS');D=np.ctypeslib.ndpointer(np.float64,flags='C_CONTIGUOUS');lib.fixed.argtypes=[I,I,ctypes.c_int,I,ctypes.c_int,D];lib.fixed.restype=ctypes.c_double;lib.scan.argtypes=[I,I,ctypes.c_int,ctypes.c_int,D,D]
 def cscore(c,ends,k,T=tab):return lib.fixed(np.array(c,np.int32),np.array([i in ends for i in range(len(c))],np.int32),len(c),np.array(k,np.int32),len(k),np.ascontiguousarray(T.ravel()))
 def pathscore(p,ends,context=(29,29),T=tab):
  score=0.;a,b=context
  for i,v in enumerate(p):
   score+=T[a,b,v];a,b=b,v
   if i in ends:score+=T[a,b,29];a,b=b,29
  return score/(len(p)+len(ends)),(a,b)
 def brute(c,ends,k,T=tab):
  zeros=[i for i,v in enumerate(c) if v==0];best=-math.inf;count=0
  for bits in itertools.product([0,1],repeat=len(zeros)):
   literal={i for i,b in zip(zeros,bits) if b};plain=[];u=0
   for i,v in enumerate(c):
    if i in literal:plain.append(0)
    else:plain.append((v-k[u%len(k)])%29);u+=1
   best=max(best,pathscore(plain,ends,T=T)[0]);count+=1
  return best,count
 def fullused(c,ends,k,context=(29,29),used=0):
  states={(used,*context):0.}
  for i,v in enumerate(c):
   nxt={}
   for (u,a,b),sc in states.items():
    for literal in ([0,1] if v==0 else [0]):
     token=0 if literal else (v-k[u%len(k)])%29;uu=u+(1-literal);ss=sc+tab[a,b,token];ctx=(b,token)
     if i in ends:ss+=tab[b,token,29];ctx=(token,29)
     state=(uu,*ctx);nxt[state]=max(ss,nxt.get(state,-math.inf))
   states=nxt
  return max(states.values())/(len(c)+len(ends))
 rng=np.random.default_rng(33010888);randomtab=rng.normal(size=(30,30,30));tiny=[];masks=0
 for cipher in itertools.product([0,1,28],repeat=3):
  for ebits in range(8):
   ends={j for j in range(3) if (ebits>>j)&1}
   for period in [1,2,3]:
    k=[int(x) for x in rng.integers(29,size=period)]
    for typ,T in [('LM',tab),('arbitrary_objective',randomtab)]:
     expect,num=brute(cipher,ends,k,T);got=cscore(cipher,ends,k,T);assert abs(expect-got)<1e-12;masks+=num;tiny.append({'cipher':cipher,'ends':sorted(ends),'key':k,'table':typ,'score':got,'masks':num})
 (O/'tiny-cases.json').write_text(json.dumps(tiny))
 # scanner indexing independently checked for every period1/2 key on one tiny fixture
 scanner=0
 for period in [1,2]:
  c=[0,28,0,1];ends={1,3};scores=np.empty(29**period);lib.scan(np.array(c,np.int32),np.array([0,1,0,1],np.int32),4,period,tab.ravel(),scores)
  for code,k in enumerate(itertools.product(range(29),repeat=period)):
   expected,_=brute(c,ends,k);assert abs(expected-scores[code])<1e-12;scanner+=1
 controls=load(M/'controls.json');real=load(M/'real.json');witness=None;prefixerrors=[];independent=[]
 def verify_path(c,ends,k,path,context=(29,29),used=0):
  lit=set(path['literal_positions']);u=used;enc=[]
  for i,v in enumerate(path['plain']):
   if i in lit:assert v==0;enc.append(0)
   else:enc.append((v+k[u%len(k)])%29);u+=1
  assert enc==c and u==path['used'];score,ctx=pathscore(path['plain'],ends,context);assert abs(score-path['score'])<1e-12;return ctx,u
 for row in controls+real:
  result=row['result'];cut=result['split'];c=result['cipher'];ends=set(result['ends']);te={i for i in ends if i<cut};se={i-cut for i in ends if i>=cut};k=result['best']['key'];tr=result['training'][0];ctx,u=verify_path(c[:cut],te,k,tr);assert {'context':list(ctx),'used':u}==result['frozen_boundary'];co=result['continuation'][0];verify_path(c[cut:],se,k,co,ctx,u);assert abs(fullused(c[:cut],te,k)-tr['score'])<1e-12;assert abs(fullused(c[cut:],se,k,ctx,u)-co['score'])<1e-12
  scores=np.load(M/'scores'/(result['name']+'.npz'));leaders=[]
  for period in [1,2,3]:
   arr=scores['period'+str(period)];assert arr.shape==(29**period,) and np.isfinite(arr).all();code=int(np.argmax(arr));kk=[];x=code
   for _ in range(period):kk.insert(0,x%29);x//=29
   leaders.append({'period':period,'code':code,'key':kk,'score':float(arr[code])})
  assert leaders==result['period_leaders'] and max(leaders,key=lambda z:z['score'])==result['best']
  if 'fixture' in row:
   f=row['fixture'];assert sha(R/f['source'])==f['source_sha256'];pp,ee=parse((R/f['source']).read_text());assert pp==f['plain'] and ee==set(f['ends']);actualerr=sum(a!=b for a,b in zip(tr['plain'],pp[:cut]));assert actualerr==row['train_errors'];assert sum(a!=b for a,b in zip(co['plain'],pp[cut:]))==row['suffix_errors'];true=pathscore(pp[:cut],te)[0];assert abs(true-row['truepath_score'])<1e-12
   if actualerr:prefixerrors.append({'name':f['name'],'errors':actualerr,'true_score':true,'winner_score':tr['score']})
   if f['name']=='p56_an_end-p3':
    h=row['heuristic']['best'];truthscore,count=brute(c[:cut],te,f['key']);hscore,hcount=brute(c[:cut],te,h['key']);assert abs(hscore-h['score'])<1e-12;assert abs(truthscore-tr['score'])<1e-12
    out=np.empty(29**3);lib.scan(np.array(c[:cut],np.int32),np.array([i in te for i in range(cut)],np.int32),cut,3,tab.ravel(),out);assert np.allclose(out,scores['period3'],atol=1e-12,rtol=0)
    witness={'truth_key':f['key'],'heuristic_key':h['key'],'truth_score':truthscore,'heuristic_exact_score':hscore,'optimization_gap':truthscore-hscore,'brute_masks_each':count,'period3_scores_replayed':len(out)}
  independent.append(result['name'])
 # Stored wholeprocedure null evidence and accounting, no new searches.
 primary=[]
 for row in controls+real:
  result=row['result'];c=result['cipher'];primary.append(result['name']);tail=(1+sum(v['score']>=result['score'] for v in row['null']))/(1+len(row['null']));assert tail==row['tail']
  for nu in row['null']:
   rr=readzip(M/'outputs'/(nu['name']+'.json.gz'));assert rr['score']==nu['score'] and rr['best']==nu['best'];assert rr['ends']==result['ends'];assert [i for i,v in enumerate(rr['cipher']) if v==0]==[i for i,v in enumerate(c) if v==0];assert sorted(rr['cipher'])==sorted(c);assert (M/'scores'/(nu['name']+'.npz')).is_file();primary.append(nu['name'])
 assert len(set(primary))==len(primary)==440
 old=real[0]['result'];mut=readzip(M/'outputs/check-suffix-mutated.json.gz');cut=old['split'];assert old['cipher'][:cut]==mut['cipher'][:cut] and old['cipher'][cut:]!=mut['cipher'][cut:]
 for k in ['best','training','frozen_boundary']:assert old[k]==mut[k]
 a=np.load(M/'scores'/(old['name']+'.npz'));b=np.load(M/'scores/check-suffix-mutated.npz');assert all(np.array_equal(a[k],b[k]) for k in a.files)
 periodic=set()
 for p in [1,2,3]:
  for key in itertools.product(range(29),repeat=p):periodic.add(tuple(key[j%p] for j in range(6)))
 assert len(periodic)==25201;assert 29+29**2+29**3==25259
 result={'sources':sources,'lm_table_sha256':sha(O/'independent-lm-table.npy'),'tiny_cases':len(tiny),'literal_masks_enumerated':masks,'all_period1_2_scanner_keys':scanner,'fullused_DP_records':independent,'p56_witness':witness,'incorrect_prefix_winners':prefixerrors,'retained_primary_searches':len(primary),'periodic_streams':len(periodic),'nominal_keys':25259,'suffix_mutation_isolation':True,'real_tails':[{'page':v['page'],'p':v['tail']} for v in real],'controls_all_tail005':all(v['tail']==.05 for v in controls),'binary_local_only':True}
 (O/'findings.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
