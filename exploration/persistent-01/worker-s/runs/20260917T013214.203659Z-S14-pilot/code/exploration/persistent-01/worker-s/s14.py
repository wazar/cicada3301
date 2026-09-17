import pathlib,json,gzip,random,hashlib,time,sys,importlib.util,itertools,math,datetime
B=pathlib.Path('exploration/persistent-01/worker-s');ROOT=pathlib.Path.cwd();PF=pathlib.Path('exploration/persistent-01/worker-c/p03_frozen.py');spec=importlib.util.spec_from_file_location('s14p03',PF);p03=importlib.util.module_from_spec(spec);spec.loader.exec_module(p03)
EXP=[e for e in range(1,28) if math.gcd(e,28)==1];TAU={e:[pow(x,e,29) for x in range(29)] for e in EXP};INV={e:[pow(x,pow(e,-1,28),29) for x in range(29)] for e in EXP};CS=p03.cells(16,True);assert len(CS)==162;CELLS=[{**c,'base_id':c['id'],'id':f'e{e}|{c["id"]}','e':e} for e in EXP for c in CS];LM=p03.LM()
def save(name,x):(B/name).write_bytes(gzip.compress(json.dumps(x,separators=(',',':')).encode(),mtime=0))
def load(name):return json.loads(gzip.decompress((B/name).read_bytes()))
def guard():
 assert not pathlib.Path('exploration/persistent-01/STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
class Adapter:
 def __init__(self,e):self.inv=INV[e]
 def extend(self,s,r,end):return LM.extend(s,self.inv[r],end)
def encode(p,path,cell):
 path=set(path);u=0;c=[];e=cell['e'];key=cell['key'];sign=cell['sign']
 for i,v in enumerate(p):
  if i in path:assert v==0;c.append(0)
  else:c.append(INV[e][(TAU[e][v]-sign*TAU[e][key[u%len(key)]])%29]);u+=1
 return c,u
def packet(ix):
 if ix<4:
  name=p03.CHECK[ix];source=ROOT/'audit/parallel-01/reference/sources'/f'solved_{name}.txt';plain,ends=p03.parse(source.read_text());ki=[0,5,10,15][ix];sign=[-1,1,-1,1][ix];e=[3,5,9,11][ix];base=f'clue:{ki:03}:{ix}:{sign}';cell=next(c for c in CELLS if c['e']==e and c['base_id']==base);literal=[i for i,v in enumerate(plain) if v==0 and i%3!=1];c,u=encode(plain,literal,cell)
  return {'packet':ix,'name':name,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cipher':c,'ends':sorted(ends),'truth':plain,'truth_literal':literal,'truth_id':cell['id'],'truth_used':u}
 pid=[0,17,55][ix-4];page=next(p for p in json.loads(pathlib.Path('exploration/persistent-01/worker-f/F06-maps.json').read_text()) if p['page']==pid);return {'packet':ix,'name':f'original{pid}','source':page,'cipher':page['indices'],'ends':[w['end']-1 for w in page['words']]}
def conditionalnull(c,seed):
 rng=random.Random(seed);s=[0 if c[0]==0 else rng.randrange(1,29)]
 for i in range(1,len(c)):
  if c[i]==0:s.append(0)
  elif c[i]==c[i-1]:s.append(s[-1])
  else:s.append(rng.choice([v for v in range(1,29) if v!=s[-1]]))
 assert [v==0 for v in s]==[v==0 for v in c] and [a==b for a,b in zip(s[:-1],s[1:])]==[a==b for a,b in zip(c[:-1],c[1:])];return s

def search(ix,null=-1,limit=None):
 guard();data=packet(ix);seed=None if null<0 else 1709302614+100*ix+null;c=data['cipher'] if null<0 else conditionalnull(data['cipher'],seed);ends=set(data['ends']);name=f'S14-packet{ix}-'+('main' if null<0 else f'null{null:02}')+'.json.gz';old=load(name) if (B/name).exists() else None;rows=old['cells'] if old else [];t=time.monotonic();wanted=len(CELLS) if limit is None else limit;expanded=0
 for j in range(len(rows),wanted):
  if j%32==0:guard()
  cell=CELLS[j];e=cell['e'];r,diag=p03.beam([TAU[e][v] for v in c],ends,[TAU[e][v] for v in cell['key']],cell['sign'],Adapter(e),64,truth=data.get('truth_literal') if null<0 and cell['id']==data.get('truth_id') else None)
  for alt in r:
   alt['power_plain']=alt['plain'];alt['plain']=[INV[e][v] for v in alt['power_plain']];assert encode(alt['plain'],alt['literal_positions'],cell)==(c,alt['used'])
  rows.append({'id':cell['id'],'e':e,'cell':cell,'score':r[0]['score'],'alternatives':r,'diagnostics':diag});expanded+=diag['expanded']
  if (j+1)%324==0:save(name,{'packet':data,'cipher':c,'ends':sorted(ends),'seed':seed,'cells':rows,'complete':False,'seconds':(old.get('seconds',0) if old else 0)+time.monotonic()-t})
 allalts=sorted(({'id':row['id'],**alt} for row in rows for alt in row['alternatives']),key=lambda a:a['score'],reverse=True);top=[];seen={}
 for alt in allalts:
  key=(tuple(alt['plain']),tuple(alt['literal_positions']))
  if key not in seen:
   if len(top)==16:continue
   item={**alt,'aliases':[]};seen[key]=item;top.append(item)
  if key in seen:seen[key]['aliases'].append(alt['id'])
 result={'packet':data,'cipher':c,'ends':sorted(ends),'seed':seed,'cells':rows,'complete':len(rows)==len(CELLS),'maximum':top[0]['score'],'global16':top,'seconds':(old.get('seconds',0) if old else 0)+time.monotonic()-t}
 if null<0 and 'truth' in data and any(row['id']==data['truth_id'] for row in rows):
  tr=next(row for row in rows if row['id']==data['truth_id']);ranks=[k+1 for k,a in enumerate(tr['alternatives']) if a['plain']==data['truth'] and a['literal_positions']==data['truth_literal']];result['control']={'truth_id':data['truth_id'],'truth_key_map_rank':1+sum(row['score']>tr['score'] for row in rows),'truth_score':LM.score(data['truth'],ends),'truth_path_top16_rank':ranks[0] if ranks else None,'first_truth_pruned':tr['diagnostics']['first_truth_pruned'],'selected_rune_errors':sum(a!=b for a,b in zip(top[0]['plain'],data['truth'])),'correct_cell_rune_errors':sum(a!=b for a,b in zip(tr['alternatives'][0]['plain'],data['truth'])),'selected_id':top[0]['id']}
 save(name,result);print(json.dumps({'packet':ix,'null':null,'cells':len(rows),'complete':result['complete'],'maximum':result['maximum'],'seconds':result['seconds'],'control':result.get('control')}),flush=True);return result

def arithmetic():
 predicates=0
 for e in EXP:
  assert sorted(TAU[e])==list(range(29)) and all(INV[e][TAU[e][x]]==x for x in range(29))
  for sign in [-1,1]:
   for c in range(29):
    for k in range(29):
     dec=INV[e][(TAU[e][c]+sign*TAU[e][k])%29]
     assert INV[e][(TAU[e][dec]-sign*TAU[e][k])%29]==c
     for p in range(29):assert (p==dec)==(TAU[e][p]==(TAU[e][c]+sign*TAU[e][k])%29);predicates+=1
 rng=random.Random(1709202614);tiny=[]
 for case in range(24):
  e=EXP[case%12];c=[rng.choice([0,0,rng.randrange(29)]) for _ in range(rng.randrange(1,7))];key=[rng.randrange(29) for _ in range(rng.randrange(1,5))];sign=rng.choice([-1,1]);ends={len(c)-1};cell={'e':e,'key':key,'sign':sign};zpos=[i for i,v in enumerate(c) if v==0];alts=[]
  for choice in itertools.product([0,1],repeat=len(zpos)):
   literal={i for i,v in zip(zpos,choice) if v};p=[];u=0
   for i,v in enumerate(c):
    if i in literal:p.append(0)
    else:p.append(INV[e][(TAU[e][v]+sign*TAU[e][key[u%len(key)]])%29]);u+=1
   assert encode(p,literal,cell)==(c,u);alts.append(LM.score(p,ends))
  rows,_=p03.beam([TAU[e][v] for v in c],ends,[TAU[e][v] for v in key],sign,Adapter(e),64);assert all(abs(a['score']-b)<1e-12 for a,b in zip(rows,sorted(alts,reverse=True)[:16]));tiny.append({'e':e,'cipher':c,'key':key,'sign':sign,'scores':[a['score'] for a in rows]})
  if e==1:
   identity,_=p03.beam(c,ends,key,sign,LM,64);assert identity==rows
 save('S14-arithmetic.json.gz',{'scalar_predicates':predicates,'tiny':tiny,'tau':TAU,'inverse':INV});save('S14-model.json.gz',{'cells':CELLS,'lm_train':p03.TRAIN,'lm_check':p03.CHECK,'sources':LM.files,'kernel_path':str(PF),'kernel_sha256':hashlib.sha256(PF.read_bytes()).hexdigest()})
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='pilot':arithmetic();r=search(0,limit=32);(B/'S14-pilot.json').write_text(json.dumps({'cells':32,'seconds':r['seconds'],'forecast_full1944_seconds':r['seconds']/32*1944,'forecast_64_full_search_seconds':r['seconds']/32*1944*64,'cost_only_not_truth_family_search':True},indent=2)+'\n')
 elif mode=='one':search(int(sys.argv[2]),int(sys.argv[3]) if len(sys.argv)>3 else -1)
