import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,random,math,hashlib
import numpy as np
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'exploration/persistent-01';P=B/'worker-p/P22'
assert not (B/'STOP').exists()
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
pgs=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page'])
def load(name):
 r=json.loads((P/(name+'.json')).read_text());a=np.load(P/(name+'.npz'));cuts=np.r_[0,np.cumsum(a['lengths'])];seqs=[a['cipher'][cuts[i]:cuts[i+1]].astype(int).tolist() for i in range(45)]
 return r,a,cuts,seqs
bases={}
for name in ['actual']+['control-'+str(i) for i in range(4)]:
 r,a,cuts,seqs=load(name);bases[name]=seqs
 if name=='actual':
  assert seqs==[p['indices'] for p in pgs];continue
 ix=int(name[-1]);L=[1,8,16,32][ix];raw=(ROOT/r['source']).read_text();pos=[i for i,ch in enumerate(raw) if ch in ABC];plain=[ABC.index(raw[i]) for i in pos]
 rng=random.Random(522100+ix)
 for pi,page in enumerate(pgs):
  start=rng.randrange(len(plain));seed=[rng.randrange(29) for _ in range(L)];m=r['maps'][pi]
  assert m['source_start']==start and m['seed']==seed
  source_indices=[(start+i)%len(plain) for i in range(len(seqs[pi]))]
  assert source_indices==m['source_indices'] and [pos[j] for j in source_indices]==m['source_chars']
  truth=[plain[j] for j in source_indices];assert truth==m['plain']
  # Independent inverse from actual ciphertext and declared seed.
  c=seqs[pi]
  rec=[(v-(seed[i] if i<L else c[i-L]))%29 for i,v in enumerate(c)]
  assert rec==truth
maxerr=0;rows=[];draws=0
for f in sorted(P.glob('*.npz')):
 name=f.stem;r,a,cuts,seqs=load(name)
 if '-null-' in name:
  base=name.split('-null-')[0];orig=bases[base];tot=np.bincount(np.concatenate(orig[:23]),minlength=29)+1;w=tot/tot.sum()
  assert np.array_equal(w,np.array(r['weights']))
  rng=random.Random(r['seed'])
  for s,c in zip(orig,seqs):
   out=[s[0]]
   for k in range(1,len(s)):
    if s[k]==s[k-1]:out.append(out[-1]);continue
    prev=out[-1];probs=[float(w[j]) if j!=prev else 0 for j in range(29)];u=rng.random()*sum(probs);draws+=1
    # Scalar inverse CDF without production pool construction.
    acc=0
    for j in range(29):
     acc+=probs[j]
     if u<acc:out.append(j);break
   assert out==c
 C=[];H=[];scores=[]
 for lag in range(1,33):
  tc=[0]*29;hc=[0]*29
  for pi,s in enumerate(seqs):
   assert np.all(a['decoded'][lag-1,cuts[pi]:cuts[pi]+lag]==255)
   # Vector arithmetic independent of saved fit counters.
   x=np.asarray(s,np.int64);d=np.remainder(x[lag:]-x[:-lag],29)
   assert np.array_equal(d,a['decoded'][lag-1,cuts[pi]+lag:cuts[pi+1]])
   cnt=np.bincount(d,minlength=29)
   dest=tc if pi<23 else hc
   for j in range(29):dest[j]+=int(cnt[j])
  assert tc==r['train_counts'][lag-1] and hc==r['held_counts'][lag-1]
  q=[(v+1)/(sum(tc)+29) for v in tc]
  assert max(abs(x-y) for x,y in zip(q,r['q'][lag-1]))<1e-15
  score=sum(hc[j]*math.log(29*q[j]) for j in range(29))/sum(hc);scores.append(score)
  maxerr=max(maxerr,abs(score-r['scores'][lag-1]));assert abs(score-r['scores'][lag-1])<1e-12
 chosen=max(range(32),key=lambda i:scores[i])+1;assert chosen==r['selected_lag']
 rows.append(dict(name=name,selected_lag=chosen,maximum=max(scores)))
lookup={r['name']:r for r in rows};summary=json.loads((P/'summary.json').read_text());real=lookup['actual'];tail=(1+sum(lookup[f'actual-null-{i:03}']['maximum']>=real['maximum'] for i in range(199)))/200
assert tail==summary['tail'];controlchecks=[]
for i in range(4):
 r=lookup['control-'+str(i)];tailc=(1+sum(lookup[f'control-{i}-null-{j:03}']['maximum']>=r['maximum'] for j in range(99)))/100
 saved=json.loads((P/f'control-{i}-summary.json').read_text());assert tailc==saved['tail'];controlchecks.append(dict(control=i,tail=tailc,selected_lag=r['selected_lag']))
(P/'independent-check.json').write_text(json.dumps(dict(pass_all=True,panels=len(rows),lag_fits=len(rows)*32,random_draws=draws,maximum_score_error=maxerr,actual_tail=tail,controls=controlchecks),indent=2)+'\n')
print((P/'independent-check.json').read_text())
