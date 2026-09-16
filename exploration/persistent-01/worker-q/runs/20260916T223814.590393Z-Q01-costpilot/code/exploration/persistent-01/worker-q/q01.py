import json,gzip,pathlib,hashlib,datetime,argparse,time
import numpy as np
R=pathlib.Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--pilot',action='store_true');args=p.parse_args()
rng=np.random.default_rng(2026091701)
source=pathlib.Path('exploration/persistent-01/worker-f/F10-evidence.json.gz')
d=json.load(gzip.open(source,'rt')); regions=d['regions']; units=[np.array(x,dtype=np.int64) for r in regions for x in r['units']]
counts=[len(r['units']) for r in regions]; offsets=np.cumsum([0]+counts); train=np.concatenate([np.arange(offsets[j],offsets[j]+2*m//3) for j,m in enumerate(counts)]);held=np.array(sorted(set(range(len(units)))-set(train)))
bodies=np.zeros((28,len(units)),dtype=np.int64)
for j,u in enumerate(units):
 for ai,a in enumerate(range(1,29)):
  s=0
  for x in u[:-1]:s=(a*s+int(x))%29
  bodies[ai,j]=a*s%29
  assert bodies[ai,j]==sum(int(x)*pow(a,len(u)-i-1,29) for i,x in enumerate(u[:-1]))%29
term=np.array([x[-1] for x in units]); assert len(term)==122

def check():
 assert not (R.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)

def fit(t):
 synd=(bodies+t)%29
 hist=np.array([np.bincount(row[train],minlength=29) for row in synd])
 ai,b=np.unravel_index(np.argmax(hist),hist.shape)
 prediction=(b-bodies[ai,held])%29
 return {'a':int(ai+1),'b':int(b),'train_hits':int(hist[ai,b]),'held_hits':int((prediction==t[held]).sum()),'predictions':prediction.tolist(),'truth':t[held].tolist()}

def run(t,n):
 real=fit(t);shifts=[];null=[];params=[]
 for i in range(n):
  check();ss=[int(rng.integers(m)) for m in counts];tt=t.copy()
  for j,s in enumerate(ss):tt[offsets[j]:offsets[j+1]]=np.roll(t[offsets[j]:offsets[j+1]],s)
  v=fit(tt);shifts.append(ss);null.append(v['held_hits']);params.append([v['a'],v['b'],v['train_hits']])
 return {'terminals':t.tolist(),'fit':real,'null_scores':null,'null_parameters':params,'shifts':shifts,'tail':(1+sum(x>=real['held_hits'] for x in null))/(n+1)}
start=time.monotonic();controls=[]
for a in [1,2,7,28]:
 b=(a+3)%29;t=(b-bodies[a-1])%29
 assert np.all((bodies[a-1]+t)%29==b)
 for j in range(len(t)):assert (bodies[a-1,j]+(t[j]+1)%29)%29!=b
 result=run(t,9 if args.pilot else 99);result['plant']={'a':a,'b':b};assert result['fit']['held_hits']==len(held);controls.append(result)
real=run(term,19 if args.pilot else 999);baseline=run(rng.integers(29,size=len(units)),19 if args.pilot else 999)
e={'source':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'regions':regions,'counts':counts,'train':train.tolist(),'held':held.tolist(),'bodies':bodies.tolist(),'real':real,'controls':controls,'baseline':baseline,'seed':2026091701,'seconds':time.monotonic()-start}
name='Q01-pilot' if args.pilot else 'Q01'
with gzip.open(R/(name+'-evidence.json.gz'),'wt') as f:json.dump(e,f)
summary={'real':{k:v for k,v in real.items() if k in ['fit','tail']},'controls':[{'plant':x['plant'],'fit':x['fit'],'tail':x['tail']} for x in controls],'baseline':{'fit':baseline['fit'],'tail':baseline['tail']},'train_n':len(train),'held_n':len(held),'fits':sum(1+len(x['null_scores']) for x in [real,baseline]+controls),'seconds':e['seconds']}
(R/(name+'-result.json')).write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
