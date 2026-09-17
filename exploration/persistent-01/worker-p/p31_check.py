import os
for v in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[v]='1'
from pathlib import Path
import numpy as np,json,random,hashlib,itertools
O=Path('exploration/persistent-01/worker-p/P31');ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def forward(s):
 n=len(s);order=sorted(range(n),key=lambda i:tuple(s[(i+j)%n] for j in range(n)))
 return bytes(s[(i+n-1)%n] for i in order)
def matrix(last):
 rows=[b'']*len(last)
 for _ in last:rows=sorted(bytes([c])+row for c,row in zip(last,rows))
 return rows
panels=0;rowschecked=0;valid=0;results=[];pages={p['page']:p for p in json.loads(Path('exploration/persistent-01/worker-f/F06-maps.json').read_text())}
for i in range(7):
 p=json.loads((O/f'packet-{i}.json').read_text());nullaccepted=0;mainvalid=False
 if i<4:
  src=p['source'];assert hashlib.sha256(Path(src['path']).read_bytes()).hexdigest()==src['sha256'];raw=src['raw'];pos=[j for j,c in enumerate(raw) if c in ABC];truth=bytes(ABC.index(raw[j]) for j in pos);assert pos==src['source_char_positions'] and list(truth)==p['truth'] and list(forward(truth))==p['indices']
 else:assert p['source']==pages[[0,17,55][i-4]] and p['indices']==p['source']['indices']
 for j in [None]+list(range(19)):
  name=f'packet-{i}-main' if j is None else f'packet-{i}-null-{j:02}';meta=json.loads((O/(name+'.json')).read_text());z=np.load(O/(name+'.npz'));last=bytes(z['input']);expected=list(p['indices'])
  if j is not None:rng=random.Random(531100+100*i+j);rng.shuffle(expected);assert meta['seed']==531100+100*i+j
  assert last==bytes(expected);rows=matrix(last);candidates=[bytes(r) for r in z['candidates']];assert sorted(candidates)==rows
  assert sorted(z['lf'].tolist())==list(range(len(last)))
  for row,gid in zip(candidates,z['group_for_primary']):
   g=bytes(z['groups'][gid]);assert g in [row[k:]+row[:k] for k in range(len(row))];assert g==min(row[k:]+row[:k] for k in range(len(row)))
  for g,col,okay in zip(z['groups'],z['forward_columns'],z['valid']):
   got=forward(bytes(g));assert got==bytes(col) and bool(okay)==(got==last)
  validrows=[k for k,g in enumerate(z['group_for_primary']) if z['valid'][g]];assert validrows==meta['valid_primary_rows'] and bool(validrows)==meta['compatible']
  assert np.flatnonzero(z['valid']).tolist()==meta['valid_groups'];rowschecked+=len(rows);panels+=1;valid+=bool(validrows)
  if j is None:
   mainvalid=bool(validrows)
   if i<4:assert truth in candidates and mainvalid
  else:nullaccepted+=bool(validrows)
 summary=json.loads((O/f'packet-{i}-summary.json').read_text());assert summary['inventory_null_compatible']==nullaccepted;results.append(dict(packet=i,compatible=mainvalid,null_compatible=nullaccepted))
# Independently check exhaustive tiny forward image-set cardinalities.
for t in json.loads((O/'tiny.json').read_text()):
 inputs=[bytes(x) for x in itertools.product(range(t['alphabet']),repeat=t['n'])];image={forward(x) for x in inputs};assert len(image)==t['valid'] and len(inputs)==t['inputs']
r=dict(pass_all=True,panels=panels,primary_rows=rowschecked,compatible_panels=valid,results=results,method='independent iterative matrix reconstruction and index-sorted forward rotations; no LF implementation import')
(O/'independent-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
