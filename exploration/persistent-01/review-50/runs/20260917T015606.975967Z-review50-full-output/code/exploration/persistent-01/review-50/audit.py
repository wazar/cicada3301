import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,gzip,hashlib,re,random,itertools,math,time
R=Path(__file__).resolve().parents[3];B=R/'exploration/persistent-01';S=B/'worker-s';O=B/'review-50';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
def parse(raw):
 seq=[];ends=[]
 for w in re.findall('['+ABC+']+',raw):seq += [ABC.index(c) for c in w];ends.append(len(seq)-1)
 return seq,ends
inputs=sorted(S.glob('S14*'));inputs=[p for p in inputs if p.is_file()];sources=[R/'audit/parallel-01/reference/sources'/('solved_'+s+'.txt') for s in ['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229','0_welcome','jpg107-167','p56_an_end','p57_parable']];keyfile=R/'exploration/overnight-01/worker-a/r02/keys.json';maps=B/'worker-f/F06-maps.json';inputs+=sources+[keyfile,maps]
save('input-snapshot.json',[dict(path=str(p.relative_to(R)),sha256=sha(p),bytes=p.stat().st_size) for p in inputs])
model=load(S/'S14-model.json.gz');assert model['kernel_sha256']==sha(S/'S14_p03_frozen.py')
# Independent dense count tables, reset context for each training source.
uni=np.zeros(30,int);bi=np.zeros((30,30),int);tri=np.zeros((30,30,30),int)
for f,manifest in zip(sources[:5],model['sources']):
 assert manifest['sha256']==sha(f);seq,ends=parse(f.read_text());end=set(ends);tokens=[]
 for i,v in enumerate(seq):tokens.append(v);tokens.extend([29] if i in end else [])
 a=b=29
 for c in tokens:uni[c]+=1;bi[b,c]+=1;tri[a,b,c]+=1;a,b=b,c
p0=(uni+.5)/(uni.sum()+15);p1=(bi+8*p0)/(bi.sum(1)[:,None]+8);P=(tri+5*p1[None,:,:])/(tri.sum(2)[:,:,None]+5);LP=np.log(P);assert np.max(abs(P.sum(2)-1))<1e-14
exp=[e for e in range(1,28) if math.gcd(e,28)==1];tau={};inv={}
for e in exp:
 vals=[]
 for x in range(29):
  z=1
  for j in range(e):z=(z*x)%29
  vals.append(z)
 assert sorted(vals)==list(range(29));tau[e]=np.array(vals);iv=np.empty(29,int);iv[vals]=np.arange(29);inv[e]=iv
keys=json.loads(keyfile.read_text())['keys'][:16];grid=[]
for e in exp:
 for k in keys:
  for phase in range(len(k['key'])):
   for sign in [-1,1]:
    bid=f"{k['id']}:{phase}:{sign}";grid.append(dict(id=f'e{e}|{bid}',base_id=bid,e=e,key_id=k['id'],phase=phase,sign=sign,key=k['key'][phase:]+k['key'][:phase]))
assert grid==model['cells'] and len(grid)==1944
def scores(arr,ends):
 n=arr.shape[1];ends=set(ends);pos=[];t=0
 for i in range(n):pos.append(t);t+=1+(i in ends)
 tok=np.full((len(arr),t+2),29,int);tok[:,np.array(pos)+2]=arr
 return LP[tok[:,:-2],tok[:,1:-1],tok[:,2:]].sum(1)/t
# All scalar arithmetic predicates, rather than trust the stored count.
predicates=0
for e in exp:
 for sign in [-1,1]:
  for c in range(29):
   for k in range(29):
    p=int(inv[e][(tau[e][c]+sign*tau[e][k])%29]);assert int(inv[e][(tau[e][p]-sign*tau[e][k])%29])==c
    for v in range(29):assert (v==p)==(tau[e][v]==(tau[e][c]+sign*tau[e][k])%29);predicates+=1
arith=load(S/'S14-arithmetic.json.gz');assert predicates==arith['scalar_predicates'];tiny=[]
for case in arith['tiny']:
 c=case['cipher'];e=case['e'];key=case['key'];sg=case['sign'];zeros=[i for i,x in enumerate(c) if x==0];paths=[]
 for mask in range(1<<len(zeros)):
  lit={p for k,p in enumerate(zeros) if mask>>k&1};plain=[];u=0
  for i,x in enumerate(c):
   if i in lit:plain.append(0)
   else:plain.append(int(inv[e][(tau[e][x]+sg*tau[e][key[u%len(key)]])%29]));u+=1
  paths.append(plain)
 expected=sorted(scores(np.array(paths),[len(c)-1]),reverse=True)[:16];assert np.max(abs(np.array(expected)-case['scores']))<1e-12;tiny.append(len(paths))
page_map={p['page']:p for p in json.loads(maps.read_text())};results=[];countcells=0;altscount=0;maxerr=0;scalar_positions=0;allmax={};expansions=0
files=sorted(S.glob('S14-packet*-*.json.gz'))
assert len(files)==64
for fi,path in enumerate(files):
 t=time.monotonic();d=load(path);packet=d['packet'];ix=packet['packet'];assert d['complete'];assert len(d['cells'])==1944;assert [c['id'] for c in d['cells']]==[g['id'] for g in grid];c=np.array(d['cipher']);ends=d['ends'];n=len(c)
 if ix<4:
  f=sources[5+ix];truth,te=parse(f.read_text());assert packet['source_sha256']==sha(f) and packet['truth']==truth and packet['ends']==te
  lit=[i for i,p in enumerate(truth) if p==0 and i%3!=1];assert lit==packet['truth_literal'];ki=[0,5,10,15][ix];sg=[-1,1,-1,1][ix];e=[3,5,9,11][ix];expectedid=f'e{e}|{keys[ki]["id"]}:{ix}:{sg}';assert packet['truth_id']==expectedid;g=next(g for g in grid if g['id']==expectedid);u=0;encoded=[]
  for i,p in enumerate(truth):
   if i in lit:encoded.append(0)
   else:encoded.append(int(inv[e][(tau[e][p]-sg*tau[e][g['key'][u%len(g['key'])]])%29]));u+=1
  assert encoded==packet['cipher'] and packet['truth_used']==u
 else:
  pid=[0,17,55][ix-4];p=page_map[pid];assert packet['source']==p and packet['cipher']==p['indices'] and ends==[w['end']-1 for w in p['words']]
 if d['seed'] is None:assert np.array_equal(c,packet['cipher'])
 else:
  j=int(path.name.split('null')[1][:2]);seed=1709302614+100*ix+j;assert seed==d['seed'];rng=random.Random(seed);orig=packet['cipher'];out=[]
  for i,x in enumerate(orig):
   if x==0:out.append(0)
   elif i and x==orig[i-1]:out.append(out[-1])
   else:
    pool=list(range(1,29))
    if i and out[-1]!=0:pool.remove(out[-1])
    out.append(pool[rng.randrange(len(pool))])
  assert out==d['cipher']
 top=[]
 for row,g in zip(d['cells'],grid):
  assert row['cell']==g;aa=row['alternatives'];arr=np.array([a['plain'] for a in aa]);pp=np.array([a['power_plain'] for a in aa]);assert arr.shape==(len(aa),n) and np.array_equal(tau[g['e']][arr],pp);literal=np.zeros(arr.shape,bool)
  for ri,a in enumerate(aa):
   z=a['literal_positions'];assert z==sorted(set(z));literal[ri,z]=True;assert all(c[k]==0 for k in z)
  u=np.cumsum(~literal,axis=1)-(~literal);kr=np.array(g['key'])[u%len(g['key'])];expected=inv[g['e']][(tau[g['e']][c][None,:]+g['sign']*tau[g['e']][kr])%29];expected[literal]=0;assert np.array_equal(arr,expected);assert np.array_equal((~literal).sum(1),[a['used'] for a in aa]);sc=scores(arr,ends);err=float(max(abs(sc-np.array([a['score'] for a in aa]))));maxerr=max(maxerr,err);assert err<2e-12;assert row['score']==aa[0]['score'];assert all(aa[k]['score']>=aa[k+1]['score'] for k in range(len(aa)-1))
  top.extend(dict(id=row['id'],**a) for a in aa);altscount+=len(aa);countcells+=1;expansions+=row['diagnostics']['expanded']
 # Independent grouping of the top distinct outputs using all saved paths.
 ordered=sorted(top,key=lambda a:-a['score']);groups={};order=[]
 for a in ordered:
  identity=(bytes(a['plain']),tuple(a['literal_positions']))
  if identity not in groups:
   if len(order)>=16:continue
   groups[identity]=dict(**a,aliases=[]);order.append(identity)
  if identity in groups:groups[identity]['aliases'].append(a['id'])
 recovered=[groups[k] for k in order];assert recovered==d['global16'];assert d['maximum']==recovered[0]['score']
 # Separate scalar score/re-encryption of each selected first path.
 lead=recovered[0];g=next(g for g in grid if g['id']==lead['id']);a=b=29;total=0.;u=0;lit=set(lead['literal_positions'])
 for i,p in enumerate(lead['plain']):
  if i in lit:assert p==0 and c[i]==0
  else:
   assert int(inv[g['e']][(tau[g['e']][p]-g['sign']*tau[g['e']][g['key'][u%len(g['key'])]])%29])==c[i];u+=1
  total+=float(LP[a,b,p]);a,b=b,p
  if i in set(ends):total+=float(LP[a,b,29]);a,b=b,29
  scalar_positions+=1
 assert abs(total/(n+len(ends))-lead['score'])<2e-12
 if ix<4:
  tr=next(row for row in d['cells'] if row['id']==packet['truth_id']);control=d['control'];assert lead['plain']==packet['truth'] and lead['literal_positions']==packet['truth_literal'] and lead['id']==packet['truth_id'];assert control['selected_rune_errors']==0 and control['correct_cell_rune_errors']==0 and control['truth_key_map_rank']==1+sum(row['score']>tr['score'] for row in d['cells']);assert tr['alternatives'][0]['plain']==packet['truth'] and control['truth_path_top16_rank']==1
 allmax[path.name]=d['maximum'];results.append(dict(file=path.name,cells=1944,paths=sum(len(row['alternatives']) for row in d['cells']),maximum=d['maximum'],seconds=time.monotonic()-t));print(fi,path.name,'PASS',flush=True)
summary=json.loads((S/'S14-summary.json').read_text());tails=[]
for ix in [4,5,6]:
 real=allmax[f'S14-packet{ix}-main.json.gz'];null=[allmax[f'S14-packet{ix}-null{j:02}.json.gz'] for j in range(19)];tail=(1+sum(x>=real for x in null))/20;assert tail==summary['actual'][ix-4]['tail'];tails.append(tail)
assert countcells==summary['nominal_cells']==124416 and expansions==summary['beam_nodes_expanded'];assert all(sha(R/x['path'])==x['sha256'] for x in json.loads((O/'input-snapshot.json').read_text()))
save('result.json',dict(pass_all=True,files=len(files),cells=countcells,retained_paths=altscount,maximum_score_error=maxerr,scalar_selected_positions=scalar_positions,scalar_predicates=predicates,tiny_path_counts=tiny,tails=tails,expansions_accounted=expansions,panels=results,beam_limit='No full search rerun; final retained paths and grid/selection/calibration verified. No exhaustive long-page optimum or independent historical pruning-trace proof.'))
print('AUDIT PASS',countcells,altscount,maxerr,tails)
