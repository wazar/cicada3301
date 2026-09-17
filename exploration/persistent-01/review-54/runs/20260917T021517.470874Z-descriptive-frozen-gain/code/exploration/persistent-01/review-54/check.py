import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,gzip,hashlib
R=Path(__file__).parent;B=R.parent;Q=B/'coordinator/Q09-reciprocal';F=B/'worker-f/F06-maps.json';pages=sorted(json.loads(F.read_text()),key=lambda p:p['page']);templates=[p['indices'] for p in pages];assert len(pages)==45 and not {4,9,14,19,24,29,34,39,44,50,54}&{p['page'] for p in pages};ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
inv=[0]+[next(y for y in range(1,29) if x*y%29==1) for x in range(1,29)];assert all((inv[inv[(a+b)%29]]-b)%29==a for a in range(29) for b in range(29));hashes={};maxg=maxerr=0.;panels=0;drawcount=0

def mat(theta,model):
 weights=np.exp(np.r_[theta,0.]-max(np.r_[theta,0.]));out=np.zeros((29,29))
 for x in range(29):
  raw=[0 if y==x else weights[y if model==0 else (inv[y]-x)%29] for y in range(29)];out[x]=np.array(raw)/sum(raw)
 return out

def read(name):
 p=Q/(name+'.json.gz');data=p.read_bytes();hashes[p.name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)};return json.loads(gzip.decompress(data))
def audit(r):
 global maxg,maxerr,panels
 panels+=1;seqs=r['cipher'];assert len(seqs)==45;C=[]
 for seq,t,dec in zip(seqs,templates,r['decoded']):
  assert len(seq)==len(t) and seq[0]==t[0] and dec==[255]+[(inv[b]-a)%29 for a,b in zip(seq,seq[1:])];assert [a==b for a,b in zip(seq,seq[1:])]==[a==b for a,b in zip(t,t[1:])]
 for subset in [seqs[:23],seqs[23:]]:
  c=np.zeros((29,29),int)
  for seq in subset:
   for a,b in zip(seq,seq[1:]):
    if a!=b:c[a,b]+=1
  C.append(c)
 assert C[0].tolist()==r['train_counts'] and C[1].tolist()==r['held_counts'];held=[]
 for model,f in enumerate(r['fits']):
  P=mat(f['theta'],model);g=np.zeros(29);obj=0.;h=0
  for x in range(29):
   for y in range(29):
    if y==x:assert f['log_probabilities'][x][y]==0;continue
    lp=np.log(P[x,y]);assert abs(lp-f['log_probabilities'][x][y])<1e-12;obj-=C[0][x,y]*lp;h+=C[1][x,y]*lp;index=y if model==0 else (inv[y]-x)%29;g[index]+=C[0][x].sum()*P[x,y]-C[0][x,y]
  obj/=C[0].sum();g/=C[0].sum();err=max(abs(obj-f['objective']),float(abs(g[:28]-f['gradient']).max()));maxerr=max(maxerr,err);maxg=max(maxg,float(abs(g[:28]).max()));assert err<1e-12;assert f['qualified']==bool(f['success'] and abs(g[:28]).max()<=2e-6);assert abs(h-r['held_ll'][model])<1e-8;held.append(h)
 assert abs(held[1]-held[0]-r['held_gain'])<1e-8 and r['qualified']==all(f['qualified'] for f in r['fits'])

def regenerate(r,P,seed):
 global drawcount
 assert r['seed']==seed;rng=np.random.default_rng(seed);pos=0
 for seq,t in zip(r['cipher'],templates):
  for i in range(1,len(t)):
   if t[i]==t[i-1]:continue
   u=float(rng.random());assert u==r['draws'][pos];pos+=1;acc=0
   for y in range(29):
    acc+=P[seq[i-1],y]
    if u<acc:break
   assert y==seq[i]
 assert pos==len(r['draws']);drawcount+=pos
summaries=[]
for i in range(5):
 stem=f'control{i}' if i<4 else 'actual';main=read(stem)
 if i<4:
  src=main['extra'];p=Path(src['path']);raw=p.read_text();pos=[j for j,v in enumerate(raw) if v in ABC];rs=[ABC.index(raw[j]) for j in pos];assert hashlib.sha256(p.read_bytes()).hexdigest()==src['sha256'] and pos==src['positions'] and rs==src['runes'];q=np.bincount(rs,minlength=29)+.5;q/=q.sum();assert np.array_equal(q,src['q']);regenerate(main,mat(np.log(q[:28]/q[28]),1),609100+i)
 else:assert main['cipher']==templates and main['seed'] is None and main['draws'] is None
 audit(main);ns=[];P=mat(main['fits'][0]['theta'],0)
 for j in range(99 if i<4 else 199):
  n=read(stem+f'-null{j:03}');regenerate(n,P,(610000+100*i+j) if i<4 else 611000+j);audit(n);ns.append(n)
 bad=sum(not n['qualified'] for n in ns);ge=sum(n['qualified'] and n['held_gain']>=main['held_gain'] for n in ns);bounds=[(1+ge)/(1+len(ns)),(1+ge+bad)/(1+len(ns))] if main['qualified'] else None;s=json.loads((Q/(stem+'-summary.json')).read_text());assert s['tail_interval']==bounds and s['unknown_nulls']==bad;assert s['tail']==(bounds[0] if bounds and not bad else None);summaries.append(dict(main=stem,held_gain=main['held_gain'],unknown=bad,interval=bounds));print(stem,bounds,flush=True)
assert panels==600
(R/'inputs.json').write_text(json.dumps(hashes,indent=2));(R/'result.json').write_text(json.dumps(dict(status='PASS',panels=panels,fits=2*panels,draws=drawcount,max_gradient=maxg,max_objective_gradient_error=maxerr,rows=summaries),indent=2))
