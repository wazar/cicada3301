import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,gzip,hashlib,collections,math
O=Path('exploration/persistent-01/review-61');B=O.parent;A=B/'worker-n/N14';D=B/'worker-n/N15';F=B/'worker-f/F06-maps.json';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def js(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[F]+[f for d in [A,D] for f in d.iterdir() if f.is_file()];snap={str(p):sha(p) for p in files};(O/'inputs.json').write_text(json.dumps(snap,indent=2))
pages=js(F);savedmaps=js(A/'maps.json');routes=[];edges=[];lengths=[]
# Keep original row coordinates and live left/right endpoints; remove top/bottom by bounds.
def peel(rows):
 active=[(row,0,len(row)-1) for row in rows if row];out=[]
 while active:
  row,l,r=active[0];out.extend(row[l:r+1]);active=active[1:]
  nxt=[]
  for row,l,r in active:
   out.append(row[r]);r-=1
   if l<=r:nxt.append((row,l,r))
  active=nxt
  if active:
   row,l,r=active[-1];out.extend(reversed(row[l:r+1]));active=active[:-1]
  nxt=[]
  for row,l,r in reversed(active):
   out.append(row[l]);l+=1
   if l<=r:nxt.append((row,l,r))
  active=list(reversed(nxt))
 return out
assert peel([[0,1,2],[3,4,5],[6,7,8]])==[0,1,2,5,8,7,6,3,4]
for rows in [[],[[]],[[0]],[[0],[1],[2]],[[0,1,2,3]],[[0],[1,2,3],[4,5],[],[6]]]:assert sorted(peel(rows))==sorted(v for r in rows for v in r)
for p,m in zip(pages,savedmaps):
 idx=[];pos=[];lines=[];rows=[];at=0
 for lineno,line in enumerate(p['raw_joined'].split('\n')):
  row=[]
  for j,c in enumerate(line):
   if c in ABC:row.append(len(idx));idx.append(ABC.index(c));pos.append(at+j);lines.append(lineno)
  rows.append(row);at+=len(line)+1
 assert idx==p['indices'] and lines==p['line_of_rune']
 offset=p['source_char_positions'][0]-pos[0]-lines[0];assert [v+l+offset for v,l in zip(pos,lines)]==p['source_char_positions']
 r=peel(rows);assert sorted(r)==list(range(len(idx))) and r==m['route']
 e=[(u,v) for u,v in zip(r[:-1],r[1:]) if max(u,v)-min(u,v)!=1]
 assert e==[tuple(x) for x in m['novel_edges']]
 assert [pos[i]+lines[i]+offset for i in r]==m['source_char_positions'] and [lines[i] for i in r]==m['source_lines']
 routes.append(r);edges.append(e);lengths.append(len(idx))
assert len(pages)==45 and sum(map(len,edges))==2440
bounds=np.r_[0,np.cumsum(lengths)]
def panel_counts(z):
 totals=np.zeros(len(z),dtype=np.int64)
 for off,es in zip(bounds,edges):
  for x,y in es:totals+=(z[:,off+x]==z[:,off+y])
 return totals
# Full source RNG and acceptance-event replay.
control_events=0
for k in range(12):
 t=json.loads(gzip.decompress((A/f'control-{k}-source.json.gz').read_bytes()));src=Path(t['source']);assert sha(src)==t['sha256'];plain=[ABC.index(x) for x in src.read_text() if x in ABC];g=np.random.default_rng(614100+k);out=[]
 assert t['seed']==614100+k
 for p,r,trace in zip(pages,routes,t['traces']):
  start=int(g.integers(len(plain)));assert start==trace['start'] and trace['page']==p['page'];accepted=[];position=start
  for location,u,okay in trace['events']:
   value=plain[position%len(plain)];assert location==position%len(plain);position+=1
   draw=float(g.random()) if accepted and value==accepted[-1] else None
   assert draw==u and okay==(draw is None or draw>=.83)
   if okay:accepted.append(value)
   control_events+=1
  assert len(accepted)==len(r);page=[None]*len(r)
  for i,v in zip(r,accepted):page[i]=v
  out.extend(page)
 assert out==np.load(A/f'control-{k}.npz')['cipher'].tolist()
actual=np.concatenate([np.asarray(p['indices'],dtype=np.uint8) for p in pages]);assert np.array_equal(actual,np.load(A/'actual.npz')['cipher'])
records=[];variates=0;panels=0;scalar_intervals=0
names=['actual']+[f'control-{k}' for k in range(12)]
for name in names:
 zf=np.load(A/(name+'.npz'));meta=js(A/(name+'.json'));cipher=zf['cipher'];null=zf['nulls'];g=np.random.default_rng(meta['seed']);n=999 if name=='actual' else 199
 assert meta['seed']==(614001 if name=='actual' else 615000+int(name.split('-')[1])) and meta['B']==n and null.shape==(n,len(actual))
 for lo,hi in zip(bounds[:-1],bounds[1:]):
  c=cipher[lo:hi];z=null[:,lo:hi];assert np.all(z[:,0]==c[0]);weights=np.array([np.count_nonzero(c==v)+.5 for v in range(29)],float);weights/=weights.sum()
  transition=np.broadcast_to(weights,(29,29)).copy();np.fill_diagonal(transition,0);transition/=transition.sum(axis=1)[:,None];cdf=transition.cumsum(axis=1);cdf[:,-1]=1
  for i in range(1,len(c)):
   prev=z[:,i-1];dest=z[:,i]
   if c[i]==c[i-1]:assert np.array_equal(prev,dest)
   else:
    u=g.random(n);variates+=n;lower=np.where(dest==0,0,cdf[prev,np.maximum(dest.astype(int)-1,0)]);upper=cdf[prev,dest]
    assert np.all(u>=lower) and np.all(u<=upper) and np.all(prev!=dest)
    # Separate scalar unnormalized sums; sample two panel rows for each draw column.
    for j in range(min(2,n)):
     values=[int(np.count_nonzero(c==v))+.5 for v in range(29)];values[int(prev[j])]=0;den=sum(values);l=sum(values[:int(dest[j])])/den;h=sum(values[:int(dest[j])+1])/den
     assert l-1e-14<=u[j]<=h+1e-14;scalar_intervals+=1
 stat=panel_counts(null);assert np.array_equal(stat,zf['null_stats']);observed=int(panel_counts(cipher[None,:])[0]);tail=(1+int(np.count_nonzero(stat<=observed)))/(n+1)
 assert observed==meta['actual'] and tail==meta['tail'] and stat.mean()==meta['null_mean'] and stat.min()==meta['null_min'];panels+=n;records.append(dict(family='N14',name=name,actual=observed,tail=tail,mean=float(stat.mean())))
for name in names:
 for mode in ['A','B']:
  meta=js(D/f'{name}-{mode}.json');zf=np.load(D/f'{name}-{mode}.npz');cipher=zf['cipher'];null=zf['nulls'];ref=A/(name+'.npz');assert sha(ref)==meta['input_sha256'] and np.array_equal(cipher,np.load(ref)['cipher'])
  seed=(615900 if mode=='A' else 615901) if name=='actual' else 616000+2*int(name.split('-')[1])+(mode=='B');n=999 if name=='actual' else 99
  assert seed==meta['seed'] and n==meta['B'];g=np.random.default_rng(seed)
  for lo,hi in zip(bounds[:-1],bounds[1:]):
   c=cipher[lo:hi];z=null[:,lo:hi]
   if mode=='A':
    assert np.all(z[:,0]==c[0])
    for i in range(1,len(c)):
     prev=z[:,i-1].astype(int);dest=z[:,i].astype(int)
     if c[i]==c[i-1]:assert np.array_equal(prev,dest)
     else:
      draw=g.integers(28,size=n);assert np.all(prev!=dest) and np.array_equal(dest-(dest>prev),draw)
   else:
    for row in z:assert np.array_equal(row,g.permutation(c))
  stat=panel_counts(null);observed=int(panel_counts(cipher[None,:])[0]);tail=(1+int(np.count_nonzero(stat<=observed)))/(n+1)
  assert np.array_equal(stat,zf['null_stats']) and observed==meta['actual'] and tail==meta['tail'] and float(stat.mean())==meta['null_mean'];panels+=n;records.append(dict(family='N15'+mode,name=name,actual=observed,tail=tail,mean=float(stat.mean())))
# A recurrence: equality probability after a forced-change step is (1-p)/28;
# a fixed-repeat step is the identity. B ordered sampling without replacement.
expect=js(D/'exact-expectations.json');ea=eb=0
for p,es,out in zip(pages,edges,expect['pages']):
 c=p['indices'];pa=0
 for a,b in es:
  prob=1.
  for i in range(min(a,b)+1,max(a,b)+1):
   if c[i]!=c[i-1]:prob=(1-prob)/28
  pa+=prob
 cnt=collections.Counter(c);pb=len(es)*sum(v*(v-1) for v in cnt.values())/(len(c)*(len(c)-1));assert abs(pa-out['A_expected'])<1e-12 and abs(pb-out['B_expected'])<1e-12;ea+=pa;eb+=pb
assert abs(ea-expect['A_exact_expectation'])<1e-12 and abs(eb-expect['B_exact_expectation'])<1e-12
assert all(sha(Path(p))==h for p,h in snap.items())
r=dict(pass_all=True,pages=45,novel_edges=2440,control_events=control_events,all_null_panels=panels,N14_random_variates=variates,scalar_interval_checks=scalar_intervals,expectations=dict(A=ea,B=eb),records=records,scope='Complete saved arrays, full RNG replay/law checks; source skips and routes rebuilt. No scientific route search, optimizer or image read.')
(O/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='records'}))
