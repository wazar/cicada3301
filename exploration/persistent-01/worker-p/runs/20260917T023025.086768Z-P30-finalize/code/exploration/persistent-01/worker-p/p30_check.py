import os
for v in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[v]='1'
from pathlib import Path
import json,gzip,math,collections,re,random,itertools,sys,hashlib
B=Path('exploration/persistent-01');O=B/'worker-p/P30';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
cs=[collections.Counter() for _ in range(3)];tt=[collections.Counter() for _ in range(3)]
for name in ['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229']:
 raw=(Path('audit/parallel-01/reference/sources')/('solved_'+name+'.txt')).read_text();a=b=29
 for word in re.findall('['+ABC+']+',raw):
  for v in [ABC.index(x) for x in word]+[29]:
   for n,k in enumerate([(v,),(b,v),(a,b,v)]):cs[n][k]+=1;tt[n][k[:-1]]+=1
   a,b=b,v
cache={}
def lp(a,b,c):
 k=(a,b,c)
 if k not in cache:
  q=(cs[0][(c,)]+.5)/(tt[0][()]+15);q=(cs[1][(b,c)]+8*q)/(tt[1][(b,)]+8);q=(cs[2][k]+5*q)/(tt[2][(a,b)]+5);cache[k]=math.log(q)
 return cache[k]
def score(p,ends):
 a=b=29;s=0
 for i,x in enumerate(p):
  for v in [x,29] if i in ends else [x]:s+=lp(a,b,v);a,b=b,v
 return s/(len(p)+len(ends))
def forward(p,lits,key,sign):
 stream=list(key);pos=0;c=[]
 for i,x in enumerate(p):
  if i in lits:assert x==0;c.append(0)
  else:c.append((x+sign*stream[pos])%29);stream.append(x);pos+=1
 return c,pos,stream[pos:]
keys=json.loads((O/'keys.json').read_text());kd={k['id']:k for k in keys};assert len(keys)==162
old=json.loads(Path('exploration/overnight-01/worker-a/r02/keys.json').read_text())['keys'][:16]
expected=[dict(id=f"{k['id']}:{p}:{s}",key_id=k['id'],phase=p,sign=s,key=k['key'][p:]+k['key'][:p]) for k in old for p in range(len(k['key'])) for s in [-1,1]];assert expected==keys
npaths=0;ncells=0;maxerr=0;controls=[];tails=[];maps=[]
for pf in sorted(O.glob('packet-*.json')):
 if 'summary' in pf.name:continue
 p=json.loads(pf.read_text());ix=p['packet'];ends=set(p['ends'])
 if ix<4:
  source=p['source'];assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256']
  raw=source['raw'];matches=list(re.finditer('['+ABC+']+',raw));indices=[];pos=[];ee=[]
  for m in matches:
   indices.extend(ABC.index(v) for v in m.group());pos.extend(range(m.start(),m.end()));ee.append(len(indices)-1)
  assert indices==p['truth'] and ee==p['ends'];maps.append(dict(packet=ix,source_char_positions=pos))
  k=kd[p['truth_id']];c,u,q=forward(p['truth'],set(p['truth_literal']),k['key'],k['sign']);assert c==p['cipher'] and u==p['truth_used']
  stream=k['key'].copy();cursor=0
  for i,e in enumerate(p['events']):
   assert e['before']==stream[cursor:] and e['cipher']==c[i] and e['plain']==p['truth'][i]
   if i not in p['truth_literal']:stream.append(p['truth'][i]);cursor+=1
   assert e['after']==stream[cursor:] and e['used']==cursor
 rs=[]
 for f in sorted(O.glob(f'packet-{ix}-*.json.gz')):
  r=load(f);cipher=r['cipher'];assert r['ends']==p['ends'];seed=r['null_seed']
  if seed is not None:
   j=int(f.stem.split('-')[-1].split('.')[0]);assert seed==530200+100*ix+j
   rng=random.Random(seed);x=[]
   for i,v in enumerate(p['cipher']):
    if v==0:x.append(0)
    elif i==0:x.append(rng.randrange(1,29))
    elif v==p['cipher'][i-1]:x.append(x[-1])
    else:x.append(rng.choice([t for t in range(1,29) if t!=x[-1]]))
   assert x==cipher
  else:assert cipher==p['cipher']
  assert [row['id'] for row in r['cells']]==list(kd)
  allalts=[]
  for row in r['cells']:
   k=kd[row['id']];ncells+=1
   for z in row['alternatives']:
    enc,u,q=forward(z['plain'],set(z['literal_positions']),k['key'],k['sign']);assert enc==cipher and u==z['used'] and q==z['final_queue']
    err=abs(score(z['plain'],ends)-z['score']);maxerr=max(maxerr,err);assert err<1e-12;npaths+=1
    allalts.append(dict(id=k['id'],**z))
   assert row['top_score']==row['alternatives'][0]['score']
   assert all(a['score']>=b['score'] for a,b in zip(row['alternatives'],row['alternatives'][1:]))
  allalts.sort(key=lambda z:z['score'],reverse=True);seen={};leaders=[]
  for z in allalts:
   sig=(tuple(z['plain']),tuple(z['literal_positions']))
   if sig not in seen and len(leaders)<16:obj=dict(**z,aliases=[]);seen[sig]=obj;leaders.append(obj)
   if sig in seen:seen[sig]['aliases'].append(z['id'])
  assert leaders==r['global16'] and allalts[0]['score']==r['maximum']
  if ix<4:
   k=p['truth_id'];cell=next(z for z in r['cells'] if z['id']==k);z=r['control'];errors=sum(a!=b for a,b in zip(leaders[0]['plain'],p['truth']));assert errors==z['selected_rune_errors']
   assert z['truth_key_rank']==1+sum(c['top_score']>cell['top_score'] for c in r['cells'])
   truthr=[i+1 for i,x in enumerate(cell['alternatives']) if x['plain']==p['truth'] and x['literal_positions']==p['truth_literal']];assert z['truth_path_rank_in_correct_cell']==(truthr[0] if truthr else None)
   controls.append({a:z[a] for a in ['truth_id','truth_key_rank','truth_path_rank_in_correct_cell','first_truth_pruned','selected_rune_errors']})
  rs.append(r)
 if ix>=4 and len(rs)==20:
  main=next(r for r in rs if r['null_seed'] is None);n=sum(r['maximum']>=main['maximum'] for r in rs if r['null_seed'] is not None);summary=json.loads((O/f'packet-{ix}-summary.json').read_text());assert summary['tail']==(1+n)/20;tails.append(dict(packet=ix,tail=summary['tail'],maximum=main['maximum']))
# Separate full-path enumeration for the saved tiny cases, no beam imports.
for t in json.loads((O/'tiny-controls.json').read_text()):
 zero=[i for i,x in enumerate(t['cipher']) if x==0];scores=[]
 for bits in itertools.product([False,True],repeat=len(zero)):
  lits={i for i,b in zip(zero,bits) if b};stream=t['key'].copy();cursor=0;plain=[]
  for i,c in enumerate(t['cipher']):
   if i in lits:plain.append(0)
   else:plain.append((c-t['sign']*stream[cursor])%29);stream.append(plain[-1]);cursor+=1
  assert forward(plain,lits,t['key'],t['sign'])[0]==t['cipher'];scores.append(score(plain,set(t['ends'])))
 assert len(sorted(scores,reverse=True)[:16])==len(t['scores']);assert max(abs(a-b) for a,b in zip(sorted(scores,reverse=True)[:16],t['scores']))<1e-12
result=dict(pass_all=True,cells=ncells,paths=npaths,score_max_error=maxerr,controls=controls,actual=tails,limits='Truth pruning diagnostics require independent beam replay; scalar check does not certify global optimality.')
(O/('check-'+sys.argv[1]+'.json')).write_text(json.dumps(result,indent=2));(O/'control-source-maps.json').write_text(json.dumps(maps));print(json.dumps(result))
