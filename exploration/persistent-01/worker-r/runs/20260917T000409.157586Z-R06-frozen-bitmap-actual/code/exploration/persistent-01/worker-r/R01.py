import pathlib,json,hashlib,random,collections,time,datetime
ROOT=pathlib.Path(__file__).resolve().parents[3]; OUT=pathlib.Path(__file__).parent
SRC=ROOT/'exploration/persistent-01/worker-f/F06-maps.json'; raw=SRC.read_bytes(); D=json.loads(raw)
assert not ({4,9,14,19,24,29,34,39,44,50,54}&{p['page'] for p in D})
STOP=ROOT/'exploration/persistent-01/STOP'
def stop():
 if STOP.exists():raise SystemExit('STOP file')
def points(p):return [w['start'] for w in p['words'] if w['end']-w['start']>=2]
def fit(ds):
 c=collections.Counter(p['indices'][i] for p in ds if p['page'] in [0,1] for i in points(p));return min(range(29),key=lambda x:(c[x],x)),[c[x] for x in range(29)]
def evaluate(ds,z):
 rr=[]
 for p in ds:
  if p['page'] in [0,1]:continue
  a=p['indices'];sp=points(p);ends=[w['end']-1 for w in p['words'] if w['end']-w['start']>=2]
  hits=[i for i in sp if a[i]==z]
  rr.append(dict(page=p['page'],n=len(a),fields=len(sp),starts_count=len(hits),ends_count=sum(a[i]==z for i in ends),all_count=a.count(z),violations=[dict(rune_index=i,source_char_position=p['source_char_positions'][i]) for i in hits]))
 return rr
def randomize(ds,z,B,seed):
 r=random.Random(seed);obs=sum(x['starts_count'] for x in evaluate(ds,z));counts=[]
 for b in range(B):
  if b%100==0:stop()
  c=0
  for p in ds:
   if p['page'] in [0,1]:continue
   a=p['indices'];off=r.randrange(len(a));c+=sum(a[(i+off)%len(a)]==z for i in points(p))
  counts.append(c)
 return dict(observed=obs,counts=counts,p_lower=(1+sum(x<=obs for x in counts))/(B+1))
def control(seed,planted):
 r=random.Random(seed);ds=[]
 for p in D:
  q=dict(p);a=[r.randrange(29) for _ in p['indices']]
  if planted:
   for i in points(p):
    if a[i]==27:
     v=r.randrange(28);a[i]=v+(v>=27)
  q['indices']=a;ds.append(q)
 return ds
# Isolated evaluator arithmetic: simple known selection and output violation location.
fake=[dict(page=0,indices=list(range(27))+[28],words=[dict(start=i,end=i+2) for i in range(27)],source_char_positions=list(range(28))),dict(page=2,indices=[27,1,2],words=[dict(start=0,end=2)],source_char_positions=[5,6,7])]
assert fit(fake)[0]==27
assert evaluate(fake,27)[0]['violations']==[dict(rune_index=0,source_char_position=5)]
start=time.monotonic();z,train=fit(D);result=dict(input_sha256=hashlib.sha256(raw).hexdigest(),training_pages=[0,1],selected_zero=z,training_counts=train,pages=evaluate(D,z),randomization=randomize(D,z,4095,330101),controls=[])
for planted in [False,True]:
 for s in range(100):
  stop();ds=control(330200+s,planted);zz,cc=fit(ds);v=sum(x['starts_count'] for x in evaluate(ds,zz));row=dict(planted=planted,seed=330200+s,selected_zero=zz,train_min=cc[zz],violations=v)
  if s<20:row['randomization']=randomize(ds,zz,255,331000+s)
  result['controls'].append(row)
(OUT/'R01-input.json').write_bytes(raw)
# Complete selection procedure under page shifts; separate from conditional fixed-label test.
r=random.Random(339901);complete=[]
for b in range(4095):
 if b%100==0:stop()
 shifted=[]
 for p in D:
  q=dict(p);a=p['indices'];off=r.randrange(len(a));q['indices']=a[off:]+a[:off];shifted.append(q)
 zz,cc=fit(shifted);complete.append(dict(selected_zero=zz,training_min=cc[zz],violations=sum(x['starts_count'] for x in evaluate(shifted,zz))))
obs=result['randomization']['observed']
result['full_procedure_null']={'seed':339901,'replicates':complete,'p_lower':(1+sum(x['violations']<=obs for x in complete))/4096}
result['seconds']=time.monotonic()-start;result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(OUT/'R01-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['controls','pages','randomization']}));print('REAL',result['randomization']['observed'],result['randomization']['p_lower']);print('CONTROL',[(p,sum(x['selected_zero']==27 for x in result['controls'] if x['planted']==p),sum(x['violations']==0 for x in result['controls'] if x['planted']==p)) for p in [False,True]])
