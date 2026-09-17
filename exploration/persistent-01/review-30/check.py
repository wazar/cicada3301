from pathlib import Path
import json,hashlib,collections,math
import numpy as np
R=Path(__file__).parent;B=R.parent;S=B/'worker-s';P=[p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,1]];assert [p['page'] for p in P]==[0,1]
(R/'snapshots').mkdir(exist_ok=True);inputs={}
for p in [B/'worker-f/F06-maps.json']+[S/(name+ext) for name in ['S01','S02','S03'] for ext in ['-CARD.md','-result.json','-generated-controls.npz']]+[S/'S01-offset-tables.npz',S/'S03-null-matrices.npz']+[S/f's0{i}.py' for i in [1,2,3]]:
 b=p.read_bytes();inputs[str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
 if p.suffix in ['.json','.md','.py']:(R/'snapshots'/p.name).write_bytes(b)
(R/'inputs.json').write_text(json.dumps(inputs,indent=2))
owners=[];masks=[]
for p in P:
 owner=[None]*len(p['indices'])
 for wi,w in enumerate(p['words']):
  for k in range(w['start'],w['end']):assert owner[k] is None;owner[k]=wi
 assert None not in owner;owners.append(owner);n=len(owner);m=[]
 for d in range(2,9):m.append(np.array([[owner[(i-shift)%n]==owner[(i+d-shift)%n] for i in range(n-d)] for shift in range(n)]))
 masks.append(m)

def tables(xs):
 ts=[];details=[]
 for x,mm in zip(xs,masks):
  cols=[];dd=[]
  for d,m in zip(range(2,9),mm):
   eq=np.array([x[i]==x[i+d] for i in range(len(x)-d)]);same=m.sum(1);diff=(~m).sum(1);we=np.logical_and(m,eq).sum(1);ae=np.logical_and(~m,eq).sum(1);cols.append(we/same-ae/diff);dd.append(dict(distance=d,within_pairs=int(same[0]),across_pairs=int(diff[0]),within_equal=int(we[0]),across_equal=int(ae[0])))
  ts.append(np.array(cols).T);details.append(dd)
 return ts,details

def evaluate(xs,rng,trials,saved):
 ts,details=tables(xs);offsets=[rng.integers(len(t),size=trials) for t in ts];sample=(ts[0][offsets[0]]+ts[1][offsets[1]])/2;center=(ts[0].mean(0)+ts[1].mean(0))/2;sd=np.maximum(sample.std(0),1e-12);observed=(ts[0][0]+ts[1][0])/2;zs=(center-observed)/sd;maximum=max(zs);nullmax=np.max((center-sample)/sd,axis=1);tail=(1+sum(nullmax>=maximum))/(trials+1);assert tail==saved['p'];assert details==saved['details'];assert np.max(abs(zs-saved['distance_z']))<1e-12;return ts

def markov(rng):
 out=[]
 for p in P:
  a=[int(rng.integers(29))]
  for _ in range(1,len(p['indices'])):
   v=int(rng.integers(29))
   if v==a[-1] and rng.random()<.83:v=(a[-1]+int(rng.integers(1,29)))%29
   a.append(v)
  out.append(np.array(a))
 return out
r1=json.loads((S/'S01-result.json').read_text());r2=json.loads((S/'S02-result.json').read_text());rng=np.random.default_rng(1709202601);g1=np.load(S/'S01-generated-controls.npz')
for kind in ['markov','word_urn']:
 for rep in range(100):
  if kind=='markov':xs=markov(rng)
  else:
   xs=[]
   for p in P:
    a=[]
    for w in p['words']:a.extend(rng.choice(29,w['end']-w['start'],replace=False).tolist())
    xs.append(np.array(a))
  for p,x in zip(P,xs):assert np.array_equal(x,g1[f'{kind}_{rep}_page{p["page"]}'])
  evaluate(xs,rng,999,r1['controls'][kind][rep])
ts=evaluate([np.array(p['indices']) for p in P],rng,9999,r1['real']);saved=np.load(S/'S01-offset-tables.npz')
for i,t in enumerate(ts):assert np.array_equal(t,saved[f'page{i}'])
rng=np.random.default_rng(1709202602);g2=np.load(S/'S02-generated-controls.npz');witness=[]
for p in P:
 for wi,w in enumerate(p['words']):
  for a in range(w['start'],w['end']):
   for b in range(a+1,w['end']):
    if p['indices'][a]==p['indices'][b]:witness.append(dict(page=p['page'],word=wi,positions=[a,b],source_char_positions=[p['source_char_positions'][a],p['source_char_positions'][b]],rune_index=p['indices'][a],distance=b-a))
assert witness==r2['strict_witnesses']
for rho in [0,.25,.5,.75,1]:
 for rep in range(100):
  xs=[]
  for p in P:
   a=[]
   for w in p['words']:
    seen=set()
    for i in range(w['start'],w['end']):
     v=int(rng.integers(29))
     if i and v==a[-1] and rng.random()<.83:v=(a[-1]+int(rng.integers(1,29)))%29
     if v in seen and rng.random()<rho:v=int(rng.choice([k for k in range(29) if k not in seen]))
     a.append(v);seen.add(v)
   xs.append(np.array(a))
  for p,x in zip(P,xs):assert np.array_equal(x,g2[f'rho{rho}_{rep}_page{p["page"]}'])
  evaluate(xs,rng,999,r2['controls'][str(rho)][rep])
print('S01/S02 701 panels RNG/offset statistic PASS',flush=True)
# Each circular offset is built directly as a bag Counter over original intervals.
words=[[w for w in p['words'] if w['end']-w['start']>=3] for p in P];assert list(map(len,words))==[49,47]
def bagmatrix(xs):
 indexes=[]
 for x,ws in zip(xs,words):
  index=collections.defaultdict(list);n=len(x)
  for shift in range(n):
   bagcounts=collections.Counter()
   for w in ws:
    bag=tuple(sorted(int(x[(k+shift)%n]) for k in range(w['start'],w['end'])));bagcounts[bag]+=1
   for bag,c in bagcounts.items():index[bag].append((shift,c))
  indexes.append(index)
 matrix=np.zeros((262,266),dtype=int)
 for bag,left in indexes[0].items():
  for i,c in left:
   for j,d in indexes[1].get(bag,[]):matrix[i,j]+=c*d
 return matrix
r3=json.loads((S/'S03-result.json').read_text());g3=np.load(S/'S03-generated-controls.npz');saved=np.load(S/'S03-null-matrices.npz');rng=np.random.default_rng(1709202603);nmat=0
for q in [0,2,4,8]:
 for rep in range(30):
  xs=markov(rng);available=[list(range(len(w))) for w in words];pairs=[]
  for _ in range(q):
   choices=[(a,b) for a in available[0] for b in available[1] if words[0][a]['end']-words[0][a]['start']==words[1][b]['end']-words[1][b]['start']];a,b=choices[int(rng.integers(len(choices)))];available[0].remove(a);available[1].remove(b);w0,w1=words[0][a],words[1][b];bag=rng.choice(29,w0['end']-w0['start'],replace=False);other=rng.permutation(bag)
   while np.array_equal(other,bag):other=rng.permutation(bag)
   xs[0][w0['start']:w0['end']]=bag;xs[1][w1['start']:w1['end']]=other;pairs.append(dict(word_indices_filtered=[a,b],intervals=[[w0['start'],w0['end']],[w1['start'],w1['end']]],bag=sorted(map(int,bag))))
  z=r3['controls'][str(q)][rep];assert pairs==z['plants']
  for p,x in zip(P,xs):assert np.array_equal(x,g3[f'q{q}_{rep}_page{p["page"]}'])
  matrix=bagmatrix(xs);assert np.array_equal(matrix,saved[f'q{q}_{rep}']);assert matrix[0,0]==z['observed'] and float((matrix>=matrix[0,0]).mean())==z['p'];nmat+=1
matrix=bagmatrix([p['indices'] for p in P]);assert np.array_equal(matrix,saved['real']);assert matrix[0,0]==0 and r3['real']['p']==1;nmat+=1
out={'status':'PASS','S01_S02_panels':701,'S01_real':r1['real'],'S01_control_summary':r1['control_summary'],'S02_summary':r2['summary'],'strict_witnesses':len(witness),'strict_violating_words':len(set((w['page'],w['word']) for w in witness)),'S03_matrices':nmat,'S03_cells_recomputed':nmat*262*266,'S03_control_summary':r3['control_summary'],'S03_real':r3['real']};(R/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='S01_real'},indent=2))
