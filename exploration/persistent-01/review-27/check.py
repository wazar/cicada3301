from pathlib import Path
import json,hashlib,itertools,math,bisect
from fractions import Fraction
import numpy as np
R=Path(__file__).parent;Q=R.parent/'coordinator/Q04-prefix';F=R.parent/'worker-f/F06-maps.json';P=json.loads(F.read_text());assert len(P)==45 and not{4,9,14,19,24,29,34,39,44,50,54}&{p['page'] for p in P};sizes=[len(p['indices']) for p in P];starts=np.cumsum([0]+sizes);(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in [Q/'CARD.md',Q/'test.py',Q/'REPORT.md',F]+sorted(Q.glob('*.json'))+sorted(Q.glob('*.npz')):
 b=p.read_bytes();inputs[str(p)]={'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
 if p.suffix!='.npz':(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
# Capacity of each leaf at depth<=5 is power of2. 29 baselineunits need three excessunits.
profiles=[]
for n1 in range(30):
 for n2 in range(30-n1):
  for n4 in range(30-n1-n2):
   n8=29-n1-n2-n4
   if n1+2*n2+4*n4+8*n8==32:profiles.append({1:n1,2:n2,4:n4,8:n8})
assert profiles==[{1:26,2:3,4:0,8:0},{1:28,2:0,4:1,8:0}]
# Depth<=2 would havecapacity>=8 and excess>=7, impossible with total excess3.
def codebook(m,high):
 lengths=[5-int(math.log2(m)) if i in high else 5 for i in range(29)];order=sorted(range(29),key=lambda i:(lengths[i],i));code=0;previous=0;words={}
 for i in order:code<<=lengths[i]-previous;words[i]=format(code,'0'+str(lengths[i])+'b');code+=1;previous=lengths[i]
 assert all(not a.startswith(b) for i,a in words.items() for j,b in words.items() if i!=j)
 decoded=[]
 for value in range(32):
  bits=format(value,'05b');matches=[i for i,w in words.items() if bits.startswith(w)];assert len(matches)==1;decoded.append(matches[0])
 return words,decoded
rational=[]
for m,high in [(2,[0,7,19]),(4,[13])]:
 words,decoded=codebook(m,high);w=[m if i in high else 1 for i in range(29)];assert [decoded.count(i) for i in range(29)]==w
 conditional=[]
 for prev in range(29):
  accepted=[x for x in decoded if x!=prev];masses=[Fraction(accepted.count(i),len(accepted)) for i in range(29)];assert sum(masses)==1 and masses[prev]==0
  assert all(masses[i]==(Fraction(w[i],32-w[prev]) if i!=prev else 0) for i in range(29))
  # Enumerate each unit mass through the executable cumulative-gap mapping, using exact Fraction midpoints.
  cumulative=list(itertools.accumulate(w));out=[]
  for unit in range(32-w[prev]):
   v=Fraction(2*unit+1,2);lower=cumulative[prev]-w[prev]
   if v>=lower:v+=w[prev]
   out.append(next(i for i,c in enumerate(cumulative) if v<c))
  assert sorted(out)==sorted(accepted);conditional.append([str(x) for x in masses])
 rational.append({'multiplier':m,'high':high,'codewords':words,'initial_masses':[str(Fraction(v,32)) for v in w],'conditional_masses':conditional})

def generate(seed,m,high):
 rng=np.random.default_rng(seed);w=[m if i in high else 1 for i in range(29)];out=[];cdfs={}
 for previous in [None]+list(range(29)):
  denominator=sum(w)-(w[previous] if previous is not None else 0)
  masses=[Fraction(weight,denominator) if i!=previous else Fraction(0) for i,weight in enumerate(w)]
  cdfs[previous]=[float(v) for v in itertools.accumulate(masses)]
 for source in P:
  previous=None
  for j,v in enumerate(source['indices']):
   u=float(rng.random())
   if j and v==source['indices'][j-1]:x=previous
   else:x=bisect.bisect_right(cdfs[previous],u)
   assert x<29
   out.append(x);previous=x
 return out

def stat(x,parity):
 initial=[0]*29;emits=[0]*29;depart=[0]*29
 for page in range(parity,45,2):
  a=x[starts[page]:starts[page+1]];initial[a[0]]+=1
  for prev,next in zip(a,a[1:]):
   if prev!=next:emits[next]+=1;depart[prev]+=1
 return initial,emits,depart

def likelihood(st,m,high):
 initial,emits,depart=st;w=[m if i in high else 1 for i in range(29)];return sum((initial[i]+emits[i])*math.log(w[i])-initial[i]*math.log(32)-depart[i]*math.log(32-w[i]) for i in range(29))
def fit(x):
 train=stat(x,0);held=stat(x,1);rows=[]
 for m,k in [(2,3),(4,1)]:
  initial,emits,depart=train;deltas=[]
  for i in range(29):deltas.append((initial[i]+emits[i])*math.log(m)+depart[i]*(math.log(31)-math.log(32-m)))
  high=sorted(sorted(range(29),key=lambda i:(-deltas[i],i))[:k]);hfirst,hemit,hprev=held;base=-sum(hfirst)*math.log(29)-sum(hemit)*math.log(28);gain=(likelihood(held,m,high)-base)/(sum(hfirst)+sum(hemit));rows.append({'multiplier':m,'high':high,'train_ll':likelihood(train,m,high),'held_gain':gain})
 return {'profiles':rows,'best':max(rows,key=lambda r:r['train_ll'])}

def verify(x,stored):
 assert len(x)==sum(sizes)
 for pi,p in enumerate(P):
  a=x[starts[pi]:starts[pi+1]];assert [u==v for u,v in zip(a,a[1:])]==[u==v for u,v in zip(p['indices'],p['indices'][1:])]
 f=fit(x)
 for a,b in zip(f['profiles'],stored['profiles']):
  assert a['multiplier']==b['multiplier'] and a['high']==b['high'];assert abs(a['train_ll']-b['train_ll'])<1e-9 and abs(a['held_gain']-b['held_gain'])<1e-11
 assert f['best']['multiplier']==stored['best']['multiplier'] and f['best']['high']==stored['best']['high'];return f
panels=[];count=0;exhaustive=[]
for name in ['pilot']+[f'control-{i}' for i in range(8)]+['actual']:
 z=json.loads((Q/(name+'.json')).read_text());d=np.load(Q/(name+'.npz'));x=list(map(int,d['actual']));f=verify(x,z['fit']);count+=1
 if name=='actual':assert x==[v for p in P for v in p['indices']]
 else:assert x==generate(z['seed'],z['source_multiplier'],z['source_high'])
 # Exhaustive assignments only for original panels, not thousands of redundant null enumerations.
 st=stat(x,0)
 for row,k in zip(f['profiles'],[3,1]):
  best=max(likelihood(st,row['multiplier'],high) for high in itertools.combinations(range(29),k));assert abs(best-row['train_ll'])<1e-9;exhaustive.append({'name':name,'m':row['multiplier'],'max_ll':best})
 lower=0
 for i,(xx,stored) in enumerate(zip(d['nulls'],z['nulls'])):
  y=list(map(int,xx));assert y==generate(z['null_seed_start']+i,f['best']['multiplier'],f['best']['high']);nf=verify(y,stored);lower+=nf['best']['held_gain']<=f['best']['held_gain'];count+=1
 # Use saved likelihood ordering to check any floating ties separately.
 savedlower=sum(n['best']['held_gain']<=z['fit']['best']['held_gain'] for n in z['nulls']);assert lower==savedlower and (1+lower)/(1+len(z['nulls']))==z['lower_tail'];assert len(d['nulls'])==len(z['nulls']);den=sum(stat(x,1)[0])+sum(stat(x,1)[1]);assert den==z['actual_emissions']
 panels.append({'name':name,'best':f['best'],'lower_count':lower,'nulls':len(z['nulls']),'tail':z['lower_tail'],'nonforced_held_decisions':den})
out={'status':'PASS','panels_recomputed':count,'rational_profiles':rational,'exhaustive_original_assignments':exhaustive,'panels':panels};(R/'result.json').write_text(json.dumps(out,indent=2));print(count,'panels PASS');print([(p['name'],p['best'],p['tail']) for p in panels])
