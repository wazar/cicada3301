import json,gzip,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).parent;P=json.loads(Path('exploration/persistent-01/worker-f/F06-maps.json').read_text());M=json.loads((D/'maps.json').read_text());GP='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
# Different route implementation: mutable indexed rows; emit index once.
for p,m in zip(P,M):
 rows={l:[i for i,x in enumerate(p['line_of_rune']) if x==l] for l in sorted(set(p['line_of_rune']))};out=[]
 while rows:
  keys=sorted(rows);out.extend(rows.pop(keys[0]));keys=sorted(rows)
  for l in keys:out.append(rows[l].pop(-1))
  rows={l:r for l,r in rows.items() if r}
  if rows:out.extend(reversed(rows.pop(max(rows))))
  for l in sorted(rows,reverse=True):out.append(rows[l].pop(0))
  rows={l:r for l,r in rows.items() if r}
 assert out==m['route'];assert [p['source_char_positions'][i] for i in out]==m['source_char_positions'];assert [[a,b] for a,b in zip(out,out[1:]) if abs(a-b)>1]==m['novel_edges']
checked=0;draws=0
for k in range(13):
 name='actual' if k==12 else f'control-{k}';meta=json.loads((D/(name+'.json')).read_text());a=dict(np.load(D/(name+'.npz')));c=a['cipher'];z=a['nulls'];score=0;stats=np.zeros(len(z),int);offset=0
 if k<12:
  t=json.load(gzip.open(D/f'control-{k}-source.json.gz','rt'));path=Path(t['source']);assert hashlib.sha256(path.read_bytes()).hexdigest()==t['sha256'];s=[GP.index(x) for x in path.read_text() if x in GP];rg=np.random.default_rng(t['seed'])
 rng=np.random.default_rng(meta['seed'])
 for pi,(p,m) in enumerate(zip(P,M)):
  n=len(p['indices']);cp=c[offset:offset+n];zp=z[:,offset:offset+n]
  if k==12:assert cp.tolist()==p['indices']
  else:
   tr=t['traces'][pi];j=int(rg.integers(len(s)));assert tr['start']==j;seq=[]
   for pos,u,accept in tr['events']:
    assert pos==j%len(s);v=s[pos];j+=1;expected=float(rg.random()) if seq and v==seq[-1] else None;assert u==expected;assert accept==(u is None or u>=.83)
    if accept:seq.append(v)
   assert len(seq)==n;assert cp[m['route']].tolist()==seq
  assert np.all(zp[:,0]==cp[0]);assert np.all((zp[:,1:]==zp[:,:-1])==(cp[1:]==cp[:-1]))
  # Reconstruct all RNG variates, independently check categorical inequalities for first two rows.
  w=np.bincount(cp,minlength=29)+.5;w=w/w.sum()
  for i in range(1,n):
   if cp[i]!=cp[i-1]:
    u=rng.random(len(zp));draws+=len(u)
    for b in range(2):
     prev=int(zp[b,i-1]);v=int(zp[b,i]);q=[float(w[y]) if y!=prev else 0 for y in range(29)];norm=sum(q);lo=sum(q[:v])/norm;hi=sum(q[:v+1])/norm;assert lo<=u[b]<hi
  for x,y in m['novel_edges']:
   score+=int(cp[x]==cp[y]);stats+=zp[:,x]==zp[:,y]
  offset+=n
 assert score==meta['actual'];assert np.array_equal(stats,a['null_stats']);assert (1+sum(stats<=score))/(len(stats)+1)==meta['tail'];checked+=len(stats)
out={'pass':True,'panels':13,'full_null_counts_and_masks':checked,'RNG_variates_reconstructed':draws,'categorical_rows_checked_per_null_family':2,'maps':45};(D/'verification.json').write_text(json.dumps(out,indent=2));print(out)
