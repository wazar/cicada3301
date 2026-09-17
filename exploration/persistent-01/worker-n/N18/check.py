from pathlib import Path
from collections import defaultdict,deque
import numpy as np,json,random,hashlib,itertools
D=Path(__file__).parent;O=Path('exploration/persistent-01/worker-p/P31')
def forward(seq):
 x=0
 for v in seq:x=x*32+int(v)
 n=len(seq);mask=(1<<(5*n))-1;shift=5*(n-1);words=[]
 for _ in seq:words.append(x);x=((x<<5)&mask)|(x>>shift)
 return [w&31 for w in sorted(words)]
def inverse(last):
 buckets=defaultdict(deque)
 for i,v in enumerate(last):buckets[v].append(i)
 first=sorted(last);psi=[buckets[v].popleft() for v in first];lf=[0]*len(last)
 for i,j in enumerate(psi):lf[j]=i
 # independently use forward Psi from sentinel first-column row, measuring its cycle.
 walk=[];pos=0;seen=set()
 while pos not in seen:seen.add(pos);pos=psi[pos];walk.append(first[pos])
 return lf,walk,len(seen)==len(last)
checkedtiny=0;record=[]
for alpha,limit in [(2,6),(3,4)]:
 for n in range(1,limit+1):
  words=list(itertools.product(range(1,alpha+1),repeat=n));image={tuple(forward(w+(0,))) for w in words}
  for w in words:
   for ins in range(n+1):
    last=list(w[:ins]+(0,)+w[ins:]);lf,walk,good=inverse(last);assert good==(tuple(last) in image)
    if good:assert forward(walk)==last and walk[-1]==0
    checkedtiny+=1
  record.append({'alphabet':alpha,'n':n,'source_words':len(words),'image_size':len(image)})
assert record==json.loads((D/'tiny.json').read_text())['rows'];assert checkedtiny==1314
rows=[];positions=0;accepted=0
for ix in range(7):
 p=json.loads((D/f'packet-{ix}.json').read_text());old=json.loads((O/f'packet-{ix}.json').read_text())
 if ix<4:
  assert p['source']==old['source'] and p['truth']==old['truth'];last=forward([v+1 for v in p['truth']]+[0]);assert last.index(0)==p['truth_sentinel_position'];assert [v-1 for v in last if v]==p['indices']
 else:assert p==old
 metas=[]
 for f in sorted(D.glob(f'packet-{ix}-*.npz')):
  a=dict(np.load(f));meta=json.loads(f.with_suffix('.json').read_text());expected=p['indices'].copy()
  if meta['seed'] is not None:assert meta['seed']==531100+100*ix+meta['null'];random.Random(meta['seed']).shuffle(expected)
  assert expected==a['input'].tolist()
  if ix>=4:assert np.array_equal(a['input'],np.load(O/f.name)['input'])
  valid=[];outputs=[]
  for ins in range(len(expected)+1):
   last=[v+1 for v in expected];last.insert(ins,0);lf,walk,good=inverse(last);assert lf==a['lf'][ins].tolist();assert len(walk)==a['sentinel_cycle_length'][ins];assert good==bool(a['valid'][ins]);candidate=a['candidates'][ins].tolist();col=forward(candidate);assert col==a['forward_columns'][ins].tolist();assert (col==last)==good
   # All invalid arrays also follow the complete required reverse rank traversal.
   pos=ins;trace=[]
   for _ in last:trace.append(last[pos]);pos=lf[pos]
   assert trace[::-1]==candidate
   if good:
    assert candidate==walk and walk[-1]==0;valid.append(ins);outputs.append({'sentinel_position':ins,'runes':[v-1 for v in walk[:-1]]})
  assert valid==meta['valid_positions'] and outputs==meta['outputs'] and bool(valid)==meta['compatible'];positions+=len(expected)+1;accepted+=len(valid);metas.append(meta)
 summary=json.loads((D/f'packet-{ix}-summary.json').read_text());assert summary['null_compatible']==sum(m['compatible'] for m in metas if m['null'] is not None)
 if ix<4:
  m=next(m for m in metas if m['null'] is None);assert {'sentinel_position':p['truth_sentinel_position'],'runes':p['truth']} in m['outputs']
 rows.append({'packet':ix,'main_positions':summary['main']['valid_positions'],'null_compatible':summary['null_compatible']});print('packet',ix,flush=True)
(D/'verification.json').write_text(json.dumps({'PASS':True,'inputs':140,'insertion_positions':positions,'admitted_outputs':accepted,'tiny_columns':checkedtiny,'rows':rows},indent=2));print('PASS',positions,accepted)
