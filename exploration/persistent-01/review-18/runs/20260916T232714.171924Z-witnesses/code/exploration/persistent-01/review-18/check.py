from pathlib import Path
import json, math, random, hashlib, gzip
R=Path(__file__).parent; Q=R.parent/'coordinator/Q02'; F=R.parent/'worker-f/F06-maps.json'
M=json.loads(F.read_text()); assert not set(m['page'] for m in M)&{4,9,14,19,24,29,34,39,44,54}
B=(2,325,9375,28178,450775,9780504,1795265022)
def numeral(ds):return sum(d*29**i for i,d in enumerate(reversed(ds)))
def exp(a,b,n):
 r=1
 for bit in bin(b)[2:]:
  r=r*r%n
  if bit=='1':r=r*a%n
 return r
def prime(n):
 if n<100000:
  return n>=2 and all(n%d for d in range(2,math.isqrt(n)+1))
 assert n<2**64
 if n%2==0:return False
 s=((n-1)&-(n-1)).bit_length()-1; d=(n-1)>>s
 for a in B:
  if a%n==0:continue
  x=exp(a%n,d,n); seq=[x]
  for _ in range(1,s):seq.append(seq[-1]**2%n)
  if x!=1 and n-1 not in seq:return False
 return True
def score(ds):return int(ds[0]!=0 and prime(numeral(ds)))
def phase(x,m,o):
 return sum(score([x[(w['start']+o+j)%len(x)] for j in range(w['end']-w['start'])]) for w in m['words'] if 2<=w['end']-w['start']<=13)
files=sorted(Q.glob('control-*.json'))+list(Q.glob('real.json'))
assert len(files)>=8
snapshot={}
for p in [Q/'CARD.md',Q/'test.py',F]+files:
 b=p.read_bytes();snapshot[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 (R/'snapshots').mkdir(exist_ok=True);(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(snapshot,indent=2))
results=[]; nunit=nphase=nnull=nproposal=0
for p in files:
 z=json.loads(p.read_text()); assert len(z['streams'])==len(M)==len(z['records'])==45
 rng=random.Random(z['seed']); offsets=[[rng.randrange(len(x)) for x in z['streams']] for _ in z['offsets']]; assert offsets==z['offsets']
 if p.name.startswith('control'):
  rng=random.Random(z['seed']-1); tries=0; trace=[]
  for m,x in zip(M,z['streams']):
   out=[]
   for w in m['words']:
    l=w['end']-w['start']; proposals=[]
    for k in range(1000):
     ds=[rng.randrange(29) for _ in range(l)]; proposals.append(ds);tries+=1
     if not z['plant'] or not 2<=l<=13 or score(ds):break
    else:raise AssertionError('cap')
    out.extend(ds);trace.append({'page':m['page'],'start':w['start'],'proposals':proposals})
   assert out==x
  assert tries==z['attempts'];nproposal+=tries
  with gzip.open(R/(p.stem+'-proposals.json.gz'),'wt') as f:json.dump(trace,f)
 actual=0;leading=0;zero_primes=0;phasechecks=[]
 for m,x,rec in zip(M,z['streams'],z['records']):
  assert rec['page']==m['page'] and len(x)==len(m['indices'])
  if p.name=='real.json':assert x==m['indices']
  for w,u in zip(m['words'],rec['units']):
   ds=x[w['start']:w['end']]; eligible=2<=len(ds)<=13
   assert u['start']==w['start'] and u['end']==w['end'] and u['value']==str(numeral(ds)) and u['canonical']==(ds[0]!=0) and u['eligible']==eligible
   assert u['prime']==(prime(numeral(ds)) if eligible else None)
   if eligible:
    actual+=score(ds);leading+=ds[0]==0;zero_primes+=ds[0]==0 and u['prime']
   nunit+=1
  # All page phase-zero counts; boundary phases for every page (including wrap).
  for o in sorted({0,1,len(x)-1}):
   v=phase(x,m,o);assert v==rec['phase_counts'][o];phasechecks.append([m['page'],o,v]);nphase+=1
 assert actual==z['actual']
 null=[sum(rec['phase_counts'][o] for rec,o in zip(z['records'],offs)) for offs in offsets]
 assert null==z['null']; assert z['tail']==(1+sum(v>=actual for v in null))/(1+len(null));nnull+=len(null)
 if z.get('plant'):assert actual==sum(2<=w['end']-w['start']<=13 for m in M for w in m['words']) and z['tail']<=.01
 results.append({'file':p.name,'actual':actual,'tail':z['tail'],'leading_zero_eligible':leading,'leading_zero_arithmetic_primes':zero_primes,'phases_replayed':phasechecks})
lengths={}
for m in M:
 for w in m['words']:l=w['end']-w['start'];lengths[l]=lengths.get(l,0)+1
out={'status':'PASS','unit_records':nunit,'phase_recalculations':nphase,'null_panels':nnull,'control_proposals':nproposal,'length_counts':lengths,'results':results,'algorithm':'positional power sum, trial division <100000, independent binary exponentiation and complete square chain for 64-bit SPRP','theorem_source':'https://ceur-ws.org/Vol-1326/020-Forisek.pdf'}
(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='results'}));print([(v['file'],v['actual'],v['tail']) for v in results])
