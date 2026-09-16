import pathlib,json,random,ast
O=pathlib.Path(__file__).parent;ROOT=O.parents[2];D=json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text());P={p['original_page']:p for p in D['pages']if p['original_page']in[3,7,17]};rng=random.Random(31010)
# Reuse exact checked BM function only; no top-level G09 execution/data reread.
module=ast.parse((O/'g09.py').read_text());node=next(x for x in module.body if isinstance(x,ast.FunctionDef) and x.name=='bm');exec(compile(ast.Module(body=[node],type_ignores=[]),'g09.py::bm','exec'))
def scan(s,detail=False):
 records=[];hits=[]
 for start in range(len(s)-23):
  train=s[start:start+16];c=bm(train);out=train.copy()
  for i in range(16,24):out.append(-sum(c[j]*out[i-j]for j in range(1,len(c)))%29)
  correct=sum(a==b for a,b in zip(out[16:],s[start+16:start+24]));r={'start':start,'degree':len(c)-1,'matches':correct}
  if detail:records.append(r)
  if len(c)-1<=8 and correct==8:hits.append({**r,'coefficients':c,'truth':s[start:start+24],'forecast':out[16:]})
 return {'n_windows':len(s)-23,'exact_windows':len(hits),'hits':hits,'windows':records}
def gen(n,degree):
 coef=[rng.randrange(29)for _ in range(degree)];coef[-1]=rng.randrange(1,29);raw=[rng.randrange(29)for _ in range(degree)]
 for i in range(degree,n+100):raw.append(sum(coef[j]*raw[i-j-1]for j in range(degree))%29)
 accepted=[];reject=[]
 for i,v in enumerate(raw):
  if accepted and v==accepted[-1] and rng.random()<.83:reject.append(i);continue
  accepted.append(v)
  if len(accepted)==n:break
 assert len(accepted)==n
 return {'coefficients':coef,'raw':raw,'accepted':accepted,'rejected_offsets':reject}
units=[]
for p,lo,hi in [(3,16,119),(3,122,217),(7,0,194),(17,0,len(P[17]['indices'])),(3,0,217),(7,0,208)]:
 s=P[p]['indices'][lo:hi];r=scan(s,True)
 for h in r['hits']:h['source_positions']=P[p]['source_char_positions'][lo+h['start']:lo+h['start']+24]
 units.append({'page':p,'range':[lo,hi],'indices':s,'result':r})
controls=[]
for unit in units:
 for degree in [4,8]:
  for replicate in range(20):
   c=gen(len(unit['indices']),degree);c.update(degree=degree,replicate=replicate,length=len(unit['indices']),result=scan(c['accepted']));
   if replicate==0:c['raw_result']=scan(c['raw'][:c['length']]);assert c['raw_result']['exact_windows']>0
   controls.append(c)
null={}
for kind in ['permutation','no_adjacent_repeat']:
 records=[]
 for _ in range(100):
  scores=[]
  for u in units:
   s=u['indices'].copy()
   if kind=='permutation':rng.shuffle(s)
   else:
    s=[rng.randrange(29)]
    for i in range(1,len(u['indices'])):
     v=rng.randrange(28);s.append(v+(v>=s[-1]))
   scores.append(scan(s)['exact_windows'])
  records.append(scores)
 null[kind]=records
result={'seed':31010,'units':units,'controls':controls,'null':null};(O/'g10-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'real':[{k:v for k,v in u.items()if k!='indices' and k!='result'}|{k:v for k,v in u['result'].items()if k!='windows' and k!='hits'}for u in units],'control_detected':sum(c['result']['exact_windows']>0 for c in controls),'control_total':len(controls),'control_min_hits':min(c['result']['exact_windows']for c in controls),'null_total_hits':{k:sum(sum(v)for v in x)for k,x in null.items()}},indent=2))
