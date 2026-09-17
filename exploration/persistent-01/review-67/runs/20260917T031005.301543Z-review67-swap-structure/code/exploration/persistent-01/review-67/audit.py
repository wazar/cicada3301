import os
for v in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[v]='1'
from pathlib import Path
import json,hashlib,collections,math,functools,itertools
import numpy as np
O=Path('exploration/persistent-01/review-67');B=O.parent;D=B/'worker-n/N17';P=B/'worker-p/P31'
def js(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[f for f in D.iterdir() if f.is_file()];snap={str(p):sha(p) for p in files};(O/'inputs.json').write_text(json.dumps(snap,indent=2));inp=js(D/'inputs.json');structure=js(D/'structural.json');result=js(D/'result.json')
def lf(last):
 order=sorted(range(len(last)),key=lambda j:(last[j],j));p=[0]*len(last)
 for rank,j in enumerate(order):p[j]=rank
 return p

def cycle_lengths(p):
 visited=[False]*len(p);lengths=[]
 for start in range(len(p)):
  if visited[start]:continue
  i=start;n=0
  while not visited[i]:visited[i]=True;n+=1;i=p[i]
  assert i==start;lengths.append(n)
 return lengths

def forward(s):
 d=s+s;n=len(s);return bytes(t[-1] for t in sorted(d[i:i+n] for i in range(n)))
expectedjobs=[];baselines=[]
for ix,c in enumerate(inp['controls']):
 p=js(P/f'packet-{ix}.json');assert sha(P/f'packet-{ix}.json')==c['packet_sha256'] and c['truth']==p['truth'] and c['carrier']==p['indices'] and c['source']==p['source'];s=bytes(c['truth']);L=bytes(c['carrier']);assert forward(s)==L
 order=sorted(range(len(s)),key=lambda i:(s+s)[i:i+len(s)]);src=[(i-1)%len(s) for i in order];chars=[p['source']['source_char_positions'][j] for j in src];assert src==c['carrier_to_source_rune'] and chars==c['carrier_to_source_char'] and bytes(s[j] for j in src)==L
 g=functools.reduce(math.gcd,collections.Counter(L).values());perm=lf(L);assert g==1 and cycle_lengths(perm)==[len(L)];baselines.append(perm);assert structure['controls'][ix]==dict(control=ix,inventory_count_gcd=1,LF_cycle_lengths=[len(L)])
 for j in range(len(L)-1):
  if L[j]!=L[j+1]:expectedjobs.append(dict(job=len(expectedjobs),control=ix,positions=[j,j+1],source_rune_positions=[src[j],src[j+1]],source_char_positions=[chars[j],chars[j+1]],before=[L[j],L[j+1]]))
assert expectedjobs==inp['jobs'] and len(expectedjobs)==769
primary=0;groups=0;columns=0;bycontrol=collections.Counter();samples=[]
for job in expectedjobs:
 name=f"swap-{job['job']:04d}";meta=js(D/(name+'.json'));z=np.load(D/(name+'.npz'));ix=job['control'];orig=inp['controls'][ix]['carrier'];x=orig.copy();i,j=job['positions'];x[i],x[j]=x[j],x[i]
 assert z['input'].tolist()==x and sum(a!=b for a,b in zip(x,orig))==2 and collections.Counter(x)==collections.Counter(orig)
 assert all(meta[k]==v for k,v in job.items());perm=lf(x);base=baselines[ix].copy();base[i],base[j]=base[j],base[i];assert perm==base==z['lf'].tolist();lengths=cycle_lengths(perm);assert len(lengths)==2 and lengths==structure['swaps'][job['job']]['cycle_lengths']
 # Independently fill all reconstruction rows simultaneously from the permutation.
 n=len(x);indices=np.arange(n);expected=np.empty((n,n),dtype=np.uint8);values=np.array(x,dtype=np.uint8);f=np.array(perm)
 for column in range(n-1,-1,-1):expected[:,column]=values[indices];indices=f[indices]
 assert np.array_equal(expected,z['candidates']);primary+=n
 gdata=[bytes(g) for g in z['groups']];assert len(gdata)==meta['candidate_groups'] and len(set(gdata))==len(gdata)
 for row,gid in zip(expected,z['group_for_primary']):
  g=gdata[int(gid)];assert bytes(row) in (g+g)[:-1]
 assert set(z['group_for_primary'].tolist())==set(range(len(gdata)))
 assert not np.any(z['valid']) and not meta['compatible'] and not meta['valid_groups'] and not meta['original_necklace_retained'];assert meta['primary_rows']==n
 # All flags additionally certified by gcd1+two cycles, independently of columns.
 for gid in sorted({0,len(gdata)-1}):
  col=forward(gdata[gid]);assert col==bytes(z['forward_columns'][gid]) and col!=bytes(x);columns+=1
 groups+=len(gdata);bycontrol[ix]+=1;samples.append(dict(job=job['job'],cycles=lengths,checked_column_groups=sorted({0,len(gdata)-1})))
assert primary==284377 and groups==266751 and [bycontrol[i] for i in range(4)]==[386,223,75,85]
assert result['jobs']==769 and result['compatible']==0 and result['npz_bytes']==sum((D/f"swap-{j['job']:04d}.npz").stat().st_size for j in expectedjobs)
for i,row in enumerate(result['rows']):assert row['swaps']==bycontrol[i] and row['compatible']==row['source_necklace_retained']==0
# Finite corroboration on complete small forward codewords, not actual repairs.
words=0;primitive=0;swaps=0
for alphabet,maxn in [(2,8),(3,6)]:
 for n in range(1,maxn+1):
  for vals in itertools.product(range(alphabet),repeat=n):
   s=bytes(vals);last=forward(s);words+=1
   if functools.reduce(math.gcd,collections.Counter(s).values())!=1:continue
   primitive+=1;perm=lf(last);assert cycle_lengths(perm)==[n]
   for j in range(n-1):
    if last[j]==last[j+1]:continue
    changed=list(last);changed[j],changed[j+1]=changed[j+1],changed[j];q=lf(changed);expected=perm.copy();expected[j],expected[j+1]=expected[j+1],expected[j];assert q==expected and len(cycle_lengths(q))==2;swaps+=1
assert all(sha(Path(p))==h for p,h in snap.items())
r=dict(pass_all=True,jobs=769,primary_candidates=primary,group_aliases=groups,forward_columns_sampled=columns,bycontrol=dict(bycontrol),tiny_words=words,tiny_gcd1=primitive,tiny_swaps=swaps,limits='All format outcomes certified structurally; only first/last forward columns per job recomputed, not every stored column; no actual changes/search.')
(O/'result.json').write_text(json.dumps(r,indent=2));(O/'cycle-certificates.json').write_text(json.dumps(samples));print(json.dumps(r))
