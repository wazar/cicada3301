from pathlib import Path
import json,random,math,time,sys,datetime,functools
R=Path(__file__).parent;B=R.parents[1];M=json.loads(Path('exploration/persistent-01/worker-f/F06-maps.json').read_text());BASES=(2,325,9375,28178,450775,9780504,1795265022)
def gate():
 assert not (B/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def prime(n):
 assert 0<=n<2**64
 if n<2:return False
 for p in (2,3,5,7,11,13,17,19,23,29,31,37):
  if n%p==0:return n==p
 d=n-1;s=0
 while d%2==0:d//=2;s+=1
 for a in BASES:
  if a%n==0:continue
  x=pow(a,d,n)
  if x in (1,n-1):continue
  for _ in range(s-1):
   x=x*x%n
   if x==n-1:break
  else:return False
 return True
def integer(x):
 n=0
 for d in x:n=n*29+int(d)
 return n
def arithmetic():
 sieve=bytearray(b'\1')*100001;sieve[0:2]=b'\0\0'
 for p in range(2,317):
  if sieve[p]:sieve[p*p::p]=b'\0'*len(sieve[p*p::p])
 assert all(prime(n)==bool(sieve[n]) for n in range(100001));rng=random.Random(330201)
 for _ in range(1000):
  n=rng.randrange(10**8);assert prime(n)==(n>=2 and all(n%d for d in range(2,math.isqrt(n)+1)))
 for n,v in [(341550071728321,False),(3825123056546413051,False),(18446744073709551557,True),(2**64-1,False)]:assert prime(n)==v
 assert 29**13<2**64<29**14
 (R/'arithmetic.json').write_text(json.dumps(dict(status='PASS',sieve_cases=100001,trial_cases=1000,boundary_cases=4,bases=BASES,source='https://ceur-ws.org/Vol-1326/020-Forisek.pdf'),indent=2)+'\n');print('arithmetic PASS')
def panel(streams,seed,nnull):
 rng=random.Random(seed);records=[];tables=[]
 for m,x in zip(M,streams):
  gate();ls=[w['end']-w['start'] for w in m['words']];n=len(x);xx=x+x;cache={}
  for l in sorted(set(ls)):
   if not 2<=l<=13:continue
   cache[l]=[int(xx[o]!=0 and prime(integer(xx[o:o+l]))) for o in range(n)]
  scores=[]
  for o in range(n):scores.append(sum(cache[l][(w['start']+o)%n] for w,l in zip(m['words'],ls) if l in cache))
  tables.append(scores)
  rec=[]
  for w,l in zip(m['words'],ls):
   digits=x[w['start']:w['end']];v=integer(digits);rec.append(dict(start=w['start'],end=w['end'],value=str(v),eligible=2<=l<=13,canonical=digits[0]!=0,prime=bool(prime(v)) if 2<=l<=13 else None))
  records.append(dict(page=m['page'],units=rec,phase_counts=scores))
 actual=sum(t[0] for t in tables);offsets=[[rng.randrange(len(x)) for x in streams] for _ in range(nnull)];null=[sum(t[o] for t,o in zip(tables,offs)) for offs in offsets];tail=(1+sum(x>=actual for x in null))/(nnull+1)
 return dict(actual=actual,null=null,tail=tail,offsets=offsets,records=records,seed=seed,streams=streams)
def generated(seed,plant):
 rng=random.Random(seed);out=[];tries=0
 for m in M:
  x=[]
  for w in m['words']:
   l=w['end']-w['start']
   for trial in range(1000):
    ds=[rng.randrange(29) for _ in range(l)];tries+=1
    if not plant or not 2<=l<=13 or (ds[0]!=0 and prime(integer(ds))):break
   else:raise RuntimeError('plant cap')
   x+=ds
  out.append(x)
 return out,tries
def run_control(i,plant):
 seed=330202+100*i+(0 if plant else 50);streams,tries=generated(seed,plant);d=panel(streams,seed+1,99);d.update(plant=plant,attempts=tries);(R/f'control-{int(plant)}-{i}.json').write_text(json.dumps(d)+'\n');print('control',plant,i,d['actual'],d['tail'],tries,flush=True)
 if plant:assert d['tail']<=.01 and d['actual']==sum(2<=w['end']-w['start']<=13 for m in M for w in m['words'])
if __name__=='__main__':
 mode=sys.argv[1];gate()
 if mode=='arithmetic':arithmetic()
 elif mode=='pilot':run_control(0,True);run_control(0,False)
 elif mode=='controls':
  for i in range(1,4):run_control(i,True);run_control(i,False)
 elif mode=='real':
  assert all((R/f'control-{int(p)}-{i}.json').exists() for p in (True,False) for i in range(4));d=panel([m['indices'] for m in M],330202,999);(R/'real.json').write_text(json.dumps(d)+'\n');print('real',d['actual'],d['tail'])
