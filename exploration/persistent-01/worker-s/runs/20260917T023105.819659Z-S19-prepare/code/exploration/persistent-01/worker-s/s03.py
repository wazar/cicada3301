import numpy as np, json, pathlib, time
import s01 as s
rng=np.random.default_rng(1709202603); generated={}; controls={}; nulls={}
words=[[w for w in p['words'] if w['end']-w['start']>=3] for p in s.pages]
def get_vectors(x,ws):
 n=len(x); bykey={}
 for k in sorted(set(w['end']-w['start'] for w in ws)):
  starts=[w['start'] for w in ws if w['end']-w['start']==k]
  signatures=[tuple(sorted(int(x[(a+i)%n]) for i in range(k))) for a in range(n)]
  for a,key in enumerate(signatures):
   if key not in bykey: bykey[key]=np.zeros(n,np.int16)
   for start in starts: bykey[key][(a-start)%n]+=1
 return bykey

def evaluate(xs):
 vs=[get_vectors(x,w) for x,w in zip(xs,words)]
 matrix=np.zeros((len(xs[0]),len(xs[1])),np.int32)
 for key in vs[0].keys()&vs[1].keys(): matrix+=np.outer(vs[0][key],vs[1][key])
 obs=int(matrix[0,0]); return {'observed':obs,'p':float((matrix>=obs).mean()),'null_mean':float(matrix.mean()),'null_max':int(matrix.max()),'null_offsets':int(matrix.size)},matrix

def generate(q):
 xs=[]
 for p in s.pages:
  x=np.empty(len(p['indices']),int); x[0]=rng.integers(29)
  for i in range(1,len(x)):
   v=rng.integers(29)
   if v==x[i-1] and rng.random()<.83:v=(x[i-1]+rng.integers(1,29))%29
   x[i]=v
  xs.append(x)
 # Disjoint random pairs chosen entirely from lengths, no rune observations.
 available=[list(range(len(w))) for w in words]; pairs=[]
 for _ in range(q):
  choices=[(a,b) for a in available[0] for b in available[1] if words[0][a]['end']-words[0][a]['start']==words[1][b]['end']-words[1][b]['start']]
  assert choices
  a,b=choices[int(rng.integers(len(choices)))]; available[0].remove(a); available[1].remove(b)
  w0,w1=words[0][a],words[1][b]; k=w0['end']-w0['start']; bag=rng.choice(29,k,replace=False); y=rng.permutation(bag)
  while np.array_equal(y,bag): y=rng.permutation(bag)
  xs[0][w0['start']:w0['end']]=bag; xs[1][w1['start']:w1['end']]=y
  assert sorted(bag)==sorted(y) and not np.array_equal(bag,y)
  pairs.append({'word_indices_filtered':[a,b],'intervals':[[w0['start'],w0['end']],[w1['start'],w1['end']]],'bag':sorted(int(z) for z in bag)})
 return xs,pairs
start=time.monotonic()
for q in [0,2,4,8]:
 controls[str(q)]=[]
 for rep in range(30):
  xs,pairs=generate(q); result,m=evaluate(xs); result['plants']=pairs; controls[str(q)].append(result)
  for p,x in zip(s.pages,xs): generated[f'q{q}_{rep}_page{p["page"]}']=x
  nulls[f'q{q}_{rep}']=m
xs=[np.array(p['indices']) for p in s.pages]; real,m=evaluate(xs); nulls['real']=m
collisions=[]
for a,w0 in enumerate(words[0]):
 for b,w1 in enumerate(words[1]):
  x0=xs[0][w0['start']:w0['end']]; x1=xs[1][w1['start']:w1['end']]
  if sorted(x0)==sorted(x1):
   collisions.append({'filtered_word_indices':[a,b],'maps':[w0,w1],'runes':[x0.tolist(),x1.tolist()],'exact_order_equal':bool(np.array_equal(x0,x1))})
assert len(collisions)==real['observed']
np.savez_compressed(s.BASE/'S03-generated-controls.npz',**generated); np.savez_compressed(s.BASE/'S03-null-matrices.npz',**nulls)
r={'seed':1709202603,'eligible_words':[len(w) for w in words],'real':real,'real_collisions':collisions,'control_summary':{k:{'n':len(v),'p_le_01':sum(a['p']<=.01 for a in v),'p_le_05':sum(a['p']<=.05 for a in v),'observed_range':[min(a['observed'] for a in v),max(a['observed'] for a in v)]} for k,v in controls.items()},'controls':controls,'elapsed_seconds':time.monotonic()-start}
(s.BASE/'S03-result.json').write_text(json.dumps(r,indent=2)+'\n'); print(json.dumps({k:v for k,v in r.items() if k not in ['controls','real_collisions']},indent=2))
