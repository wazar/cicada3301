"""Seed-independent within-phase rune collision diagnostic for exact Q12 family."""
import extend as ex
import numpy as np,json,random,pathlib,hashlib,sys,time,itertools
O=ex.O/'C04';O.mkdir(exist_ok=True);KS=list(range(2,35))
def simple_baseline(c,k):
 out=[];running=0
 for i,v in enumerate(c):
  p=(v-(0 if i<k else running))%29;out.append(p);running+=p
  if i>=k:running-=out[i-k]
 return out
def hist(p,m):
 h=np.zeros((m,29),dtype=np.int64)
 for i,v in enumerate(p):h[i%m,v]+=1
 return h
def collisions(p,m):
 h=hist(p,m);num=int(np.sum(h*(h-1)));ns=h.sum(axis=1);den=int(np.sum(ns*(ns-1)));return num,den,h
def prepare():
 ex.guard();src=ex.R/'exploration/persistent-02/decoder/fresh-controls.json';data=json.loads(src.read_text());rng=random.Random(2026092000);cases=[]
 for source in ['guest','mill','shelley','blake']:
  case=next(c for c in data['cases'] if c['id']==f'fresh-{source}-2');p=case['truth'];assert len(p)==716
  for k in [3,8,17,34]:
   seed=[rng.randrange(29) for _ in range(k)];cases.append(dict(id=f'{source}-k{k}',kind='language',source_id=case['id'],plain=p,k=k,seed=seed,cipher=ex.q.enc(p,seed)))
 for k in [3,8,17,34]:
  p=[rng.randrange(29) for _ in range(716)];seed=[rng.randrange(29) for _ in range(k)];cases.append(dict(id=f'uniform-k{k}',kind='uniform',plain=p,k=k,seed=seed,cipher=ex.q.enc(p,seed)))
 path=O/'inputs.json';assert not path.exists();path.write_text(json.dumps(dict(source=str(src.relative_to(ex.R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),rng_seed=2026092000,controls=cases),separators=(',',':'))+'\n');print('frozen',len(cases),hashlib.sha256(path.read_bytes()).hexdigest())
def arithmetic():
 rng=random.Random(2026092001);records=[]
 for k in [2,3,4,8,17,34]:
  for n in [k+1,2*(k+1)+3,716]:
   p=[rng.randrange(29) for _ in range(n)];seed=[rng.randrange(29) for _ in range(k)];c=ex.q.enc(p,seed);q=simple_baseline(c,k);assert q==ex.q.decode(c,[0]*k);a,b,h=collisions(q,k+1);aa,bb,hh=collisions(p,k+1);assert (a,b)==(aa,bb)
   if n<100:assert a==sum(q[i]==q[j] for i in range(n) for j in range(n) if i!=j and i%(k+1)==j%(k+1))
   records.append(dict(k=k,n=n,seed=seed,cipher=c,plain=p,numerator=a,denominator=b))
 (O/'arithmetic.json').write_text(json.dumps(dict(passed=True,cases=records),separators=(',',':'))+'\n');print('arithmetic PASS',len(records))
def panel_set(c,label,seedbase,truth=None,plantk=None):
 ex.guard();path=O/(label+'.json')
 if path.exists():return json.loads(path.read_text())
 start=time.monotonic();num=np.zeros((200,len(KS)),dtype=np.int64);den=np.zeros(len(KS),dtype=np.int64);hh=np.zeros((200,len(KS),35,29),dtype=np.int16);cipher=[]
 for panel in range(200):
  ex.guard();cc=c if panel==0 else ex.q.null(c,seedbase+panel-1);cipher.append(cc)
  for col,k in enumerate(KS):
   q=simple_baseline(cc,k);a,b,h=collisions(q,k+1);num[panel,col]=a;den[col]=b;hh[panel,col,:k+1]=h
  if panel%50==0:print(label,panel,flush=True)
 frac=num/den[None,:];mean=frac.mean(axis=0);sd=frac.std(axis=0);assert np.all(sd>0);z=(frac-mean)/sd;mx=z.max(axis=1);winner=int(np.argmax(z[0]));rank=(1+int(np.sum(mx[1:]>=mx[0])))/200
 out=dict(label=label,ks=KS,panels=200,seedbase=seedbase,rank=rank,selected_k=KS[winner],actual_family_maximum=float(mx[0]),actual_collision_fractions=frac[0].tolist(),actual_standardized=z[0].tolist(),seconds=time.monotonic()-start)
 if truth is not None:
  a,b,h=collisions(truth,plantk+1);col=KS.index(plantk);assert a==num[0,col] and b==den[col];out.update(planted_k=plantk,planted_fraction=a/b,planted_period_z=float(z[0,col]))
 np.savez_compressed(O/(label+'.npz'),numerators=num,denominators=den,histograms=hh,cipher=np.array(cipher,dtype=np.uint8),fractions=frac,z=z,family_maximum=mx);path.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True);return out
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='prepare':prepare();arithmetic()
 elif mode=='controls':
  data=json.loads((O/'inputs.json').read_text())
  for ix in map(int,sys.argv[2:]):
   c=data['controls'][ix];panel_set(c['cipher'],f'control{ix:02}',2026100000+1000*ix,c['plain'],c['k'])
 elif mode=='actual':
  src=ex.R/'exploration/persistent-02/section/section-packet.json';p=json.loads(src.read_text());panel_set(p['body']['runes'],'actual',2026200000)
