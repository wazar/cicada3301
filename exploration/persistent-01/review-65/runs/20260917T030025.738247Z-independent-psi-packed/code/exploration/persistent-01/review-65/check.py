from pathlib import Path
from collections import Counter
import numpy as np,json,hashlib,random,itertools,time
D=Path(__file__).parent;O=Path('exploration/persistent-01/worker-p/P31');GP='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def packed(s):
 x=0
 for r in s:x=(x<<5)|int(r)
 return x
def rotations(s):
 x=packed(s);n=len(s);mask=(1<<(5*n))-1;shift=5*(n-1);rr=[]
 for _ in range(n):rr.append(x);x=((x<<5)&mask)|(x>>shift)
 return rr
def forward(s):return bytes(v&31 for v in sorted(rotations(s)))
def invert(L):
 # sorted(last symbol, original index) identifies Psi directly
 pairs=sorted((int(v),i) for i,v in enumerate(L));first=np.array([v for v,i in pairs],np.uint8);psi=np.array([i for v,i in pairs]);n=len(L);rows=np.arange(n);table=np.empty((n,n),np.uint8)
 for j in range(n):table[:,j]=first[rows];rows=psi[rows]
 return table,psi
# Explicit periodic cases independently verify complete forward/inverse membership.
periodic=[]
for s in [b'\x00',bytes([0]*8),bytes([0,1]*4),bytes([0,0,1]*3),bytes([0,1,2]*4)]:
 l=forward(s);tab,psi=invert(l);assert any(bytes(r)==s for r in tab);assert all(forward(bytes(r))==l for r in tab);periodic.append({'plain':list(s),'last':list(l),'psi':psi.tolist()})
exhaust=[];total_tiny=0
for alpha,mx in [(2,7),(3,5)]:
 for n in range(1,mx+1):
  allwords=[bytes(x) for x in itertools.product(range(alpha),repeat=n)];image={forward(w) for w in allwords};valid=0
  for l in allwords:
   tab,psi=invert(l);got=any(forward(bytes(row))==l for row in tab);assert got==(l in image);valid+=got;total_tiny+=1
  exhaust.append({'alphabet':alpha,'n':n,'inputs':len(allwords),'valid':valid})
assert exhaust==json.loads((O/'tiny.json').read_text())
files=[O/'CARD.md',O/'REPORT.md',Path('exploration/persistent-01/worker-p/p31.py')]+sorted(O.glob('packet-*'))
(D/'inputs.json').write_text(json.dumps([{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files],indent=2))
F=json.loads(Path('exploration/persistent-01/worker-f/F06-maps.json').read_text());rowsout=[];primary=groups=0;start=time.time()
for ix in range(7):
 p=json.loads((O/f'packet-{ix}.json').read_text())
 if ix<4:
  s=p['source'];path=Path(s['path']);raw=path.read_text();assert raw==s['raw'] and hashlib.sha256(path.read_bytes()).hexdigest()==s['sha256'];positions=[];truth=[]
  for pos,ch in enumerate(raw):
   if ch in GP:positions.append(pos);truth.append(GP.index(ch))
  assert truth==p['truth'] and positions==s['source_char_positions'];assert forward(truth)==bytes(p['indices'])
 else:
  fp=next(q for q in F if q['page']==[0,17,55][ix-4]);assert fp==p['source'] and p['indices']==fp['indices']
 compat=[]
 for f in sorted(O.glob(f'packet-{ix}-*.npz')):
  meta=json.loads(f.with_suffix('.json').read_text());r=dict(np.load(f));L=r['input'];base=list(p['indices'])
  if meta['seed'] is not None:
   assert meta['seed']==531100+100*ix+meta['null'];rng=random.Random(meta['seed']);rng.shuffle(base)
  assert base==L.tolist();tab,psi=invert(L);assert Counter(map(bytes,tab))==Counter(map(bytes,r['candidates']));lf=np.argsort(psi);assert np.array_equal(lf,r['lf'])
  # LF inverse candidates and Psi forward candidates differ by known n-step row permutation for invalid columns.
  rowmap=np.arange(len(L))
  for _ in range(len(L)):rowmap=lf[rowmap]
  assert np.array_equal(tab[rowmap],r['candidates'])
  assert sorted(set(map(int,r['group_for_primary'])))==list(range(len(r['groups'])));primary+=len(L);groups+=len(r['groups']);packedgroups=[packed(g) for g in r['groups']]
  for i,cand in enumerate(r['candidates']):assert min(rotations(cand))==packedgroups[int(r['group_for_primary'][i])]
  actualvalid=[]
  for i,g in enumerate(r['groups']):
   rr=rotations(g);assert min(rr)==packed(g);col=bytes(x&31 for x in sorted(rr));assert col==bytes(r['forward_columns'][i]);yes=col==bytes(L);assert yes==bool(r['valid'][i]);actualvalid.append(yes)
  validrows=[i for i,g in enumerate(r['group_for_primary']) if actualvalid[int(g)]];assert validrows==meta['valid_primary_rows'];assert [i for i,b in enumerate(actualvalid) if b]==meta['valid_groups'];assert bool(validrows)==meta['compatible'];compat.append(meta)
  if ix<4 and meta['seed'] is None:assert any(min(rotations(p['truth']))==packedgroups[i] and actualvalid[i] for i in range(len(actualvalid)))
  rowsout.append({'name':meta['name'],'compatible':bool(validrows),'groups':len(actualvalid),'primary_rows':len(L)})
 summary=json.loads((O/f'packet-{ix}-summary.json').read_text());assert summary['inventory_null_compatible']==sum(x['compatible'] for x in compat if x['seed'] is not None);print(ix,'complete',time.time()-start,flush=True)
result={'PASS':True,'inputs':len(rowsout),'primary_rows':primary,'groups':groups,'tiny_inputs':total_tiny,'periodic':periodic,'rows':rowsout,'seconds':time.time()-start};(D/'result.json').write_text(json.dumps(result,indent=2));print({k:v for k,v in result.items() if k not in ['rows','periodic']})
