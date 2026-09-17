import os
for v in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[v]='1'
from pathlib import Path
import numpy as np,json,hashlib,random,itertools
O=Path('exploration/persistent-01/review-68');B=O.parent;D=B/'worker-n/N18';P=B/'worker-p/P31';ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
def js(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=[f for f in D.iterdir() if f.is_file()];snap={str(f):sha(f) for f in files};(O/'inputs.json').write_text(json.dumps(snap,indent=2))
def forward(s):
 n=len(s);value=0
 for c in s:value=(value<<5)|int(c)
 mask=(1<<(5*n))-1;shift=5*(n-1);rotations=[]
 for _ in range(n):rotations.append(value);value=((value<<5)&mask)|(value>>shift)
 return bytes(v&31 for v in sorted(rotations))
def inverse(last,ins):
 n=len(last);psi=sorted(range(n),key=lambda i:(last[i],i));F=sorted(last);lf=[0]*n
 for j,i in enumerate(psi):lf[i]=j
 # Saved candidate starts at LF^n(primary), even for invalid multicycle columns.
 start=ins
 for _ in range(n):start=lf[start]
 row=start;candidate=[]
 for _ in range(n):candidate.append(F[row]);row=psi[row]
 row=ins;count=0
 while True:
  row=psi[row];count+=1
  if row==ins:break
 return bytes(candidate),lf,count
panels=0;insertions=0;results=[];actualoutputs=[];controls=[]
for i in range(7):
 packet=js(D/f'packet-{i}.json');old=js(P/f'packet-{i}.json');n=len(packet['indices'])
 if i<4:
  src=old['source'];assert sha(Path(src['path']))==src['sha256'];raw=src['raw'];positions=[j for j,c in enumerate(raw) if c in ABC];truth=[ABC.index(raw[j]) for j in positions];assert positions==src['source_char_positions'] and truth==old['truth']==packet['truth'];assert src==packet['source']
  column=forward(bytes(v+1 for v in truth)+b'\0');assert [v-1 for v in column if v]!=[];assert [v-1 for v in column if v]==packet['indices'] and column.index(0)==packet['truth_sentinel_position']
 else:assert packet==old
 accepted=[];main=None
 for j in [None]+list(range(19)):
  name=f'packet-{i}-main' if j is None else f'packet-{i}-null-{j:02}';meta=js(D/(name+'.json'));z=np.load(D/(name+'.npz'));vals=packet['indices'].copy()
  if j is not None:seed=531100+100*i+j;random.Random(seed).shuffle(vals);assert seed==meta['seed']
  else:assert meta['seed'] is None
  assert vals==z['input'].tolist() and meta['n']==n
  if i>=4:assert np.array_equal(z['input'],np.load(P/(name+'.npz'))['input'])
  good=[];outputs=[]
  for ins in range(n+1):
   last=bytes([v+1 for v in vals[:ins]]+[0]+[v+1 for v in vals[ins:]]);s,lf,cycle=inverse(last,ins);col=forward(s);okay=col==last
   assert s==bytes(z['candidates'][ins]) and lf==z['lf'][ins].tolist() and cycle==int(z['sentinel_cycle_length'][ins]);assert col==bytes(z['forward_columns'][ins]) and okay==bool(z['valid'][ins]) and okay==(cycle==n+1)
   if okay:
    assert s[-1]==0 and s.count(0)==1;good.append(ins);outputs.append(dict(sentinel_position=ins,runes=[v-1 for v in s[:-1]]))
   insertions+=1
  assert good==meta['valid_positions'] and outputs==meta['outputs'] and bool(good)==meta['compatible'];panels+=1
  if j is None:
   main=meta
   if i<4:assert dict(sentinel_position=packet['truth_sentinel_position'],runes=packet['truth']) in outputs;controls.append(dict(packet=i,valid=len(good),distinct=len({tuple(o['runes']) for o in outputs})))
   else:actualoutputs.extend(dict(packet=i,**o) for o in outputs)
  else:accepted.append(len(good))
 summary=js(D/f'packet-{i}-summary.json');assert summary['main']==main and accepted==summary['null_valid_positions'] and sum(x>0 for x in accepted)==summary['null_compatible'];results.append(dict(packet=i,valid_main=len(main['valid_positions']),null_compatible=sum(x>0 for x in accepted)))
# Independent complete tiny forward image membership and cycle equivalence.
checks=0
for row in js(D/'tiny.json')['rows']:
 a,n=row['alphabet'],row['n'];words=[bytes(w) for w in itertools.product(range(1,a+1),repeat=n)];image={forward(w+b'\0') for w in words};assert len(words)==row['source_words'] and len(image)==row['image_size']
 for word in words:
  for ins in range(n+1):
   last=word[:ins]+b'\0'+word[ins:];s,lf,cyc=inverse(last,ins);assert (forward(s)==last)==(last in image)==(cyc==n+1);checks+=1
assert checks==js(D/'tiny.json')['columns_checked']==1314
assert all(sha(Path(f))==h for f,h in snap.items())
T=[r['transliteration'] for r in js(Path('KNOWLEDGE.json'))['gematria_primus']['table']];render=[dict(**o,unsegmented_transliteration=''.join(T[x] for x in o['runes'])) for o in actualoutputs];(O/'actual-full-output.json').write_text(json.dumps(render,indent=2))
r=dict(pass_all=True,panels=panels,insertions=insertions,tiny_insertions=checks,controls=controls,results=results,actual_valid_outputs=len(actualoutputs),limits='Exact format compatibility only; omitted sentinel position is unknown and controls have multiple alternatives. Paired index permutations reused, not independent new confirmation.')
(O/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
