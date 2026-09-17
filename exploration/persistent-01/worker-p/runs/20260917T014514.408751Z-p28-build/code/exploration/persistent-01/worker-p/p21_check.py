from pathlib import Path
from collections import Counter
import re,json,gzip,random,math
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'exploration/persistent-01';P=B/'worker-p/P21'
assert not (B/'STOP').exists()
ABC='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ'
c=[Counter(),Counter(),Counter()];tot=[Counter(),Counter(),Counter()]
for name in ['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229']:
 raw=(ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text()
 tokens=[]
 for w in re.findall('['+ABC+']+',raw):tokens.extend([ABC.index(x) for x in w]+[29])
 ctx=[29,29]
 for x in tokens:
  for order in range(3):
   h=tuple(ctx[-order:]) if order else ();c[order][h+(x,)]+=1;tot[order][h]+=1
  ctx=[ctx[-1],x]
def score(units):
 ctx=[29,29];logs=[]
 for w in units:
  for x in w+[29]:
   prob=(c[0][(x,)]+.5)/(tot[0][()]+15)
   for order,alpha in [(1,8),(2,5)]:
    h=tuple(ctx[-order:]);prob=(c[order][h+(x,)]+alpha*prob)/(tot[order][h]+alpha)
   logs.append(math.log(prob));ctx=[ctx[-1],x]
 return sum(logs)/len(logs)
def load(f):
 with gzip.open(f,'rt') as z:return json.load(z)
maxerr=0;cases=0
def check(units,r,origins):
 global maxerr,cases
 assert r['origins']==origins
 out=[];kept=[];discarded=[];empty=[];plain=[];ends=[]
 for i,(w,start) in enumerate(zip(units,origins)):
  rotated=[(j,w[j]) for j in [(start+k)%len(w) for k in range(len(w))]]
  inside=rotated[1:-1] if len(w)>2 else []
  if inside:
   out.append([v for j,v in inside]);plain+=out[-1];ends.append(len(plain)-1)
  else:empty.append(i)
  kept += [dict(unit=i,position=j) for j,v in inside]
  discarded += [dict(unit=i,position=j) for j,v in rotated if (j,v) not in inside]
 assert out==r['units'] and plain==r['plain'] and ends==r['ends']
 assert kept==r['kept'] and discarded==r['discarded'] and empty==r['empty_units']
 err=abs(score(out)-r['score']);assert err<1e-12;maxerr=max(maxerr,err);cases+=1
controls=[]
for i in range(4):
 r=load(P/f'control-{i}.json.gz');raw=(ROOT/r['source']).read_text()
 words=[[ABC.index(x) for x in w] for w in re.findall('['+ABC+']+',raw)]
 rng=random.Random(521100+i);carrier=[[rng.randrange(29)]+w+[rng.randrange(29)] for w in words];assert carrier==r['carrier']
 check(carrier,r['result'],[0]*len(carrier));assert r['result']['units']==words
 rng=random.Random(521200+i)
 for n in r['nulls']:check(carrier,n,[rng.randrange(len(w)) for w in carrier])
 tail=(1+sum(x['score']>=r['result']['score'] for x in r['nulls']))/200;assert tail==r['tail'];controls.append(tail)
r=load(P/'actual.json.gz');pages={p['page']:p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,17]}
for inp,out in zip(r['inputs'],r['outputs']):
 p=pages[inp['page']];units=[p['indices'][w['start']:w['end']] for w in p['words']];assert units==inp['units']
 check(units,out['result'],[0]*len(units))
 for m in out['maps']:
  idx=p['words'][m['unit']]['start']+m['position']
  assert idx==m['source_rune_index'] and m['source_char_position']==p['source_char_positions'][idx] and m['rune']==p['indices'][idx]
 assert sorted(m['source_rune_index'] for m in out['maps'])==list(range(len(p['indices'])))
rng=random.Random(521300)
for panel in r['nulls']:
 for inp,result in zip(r['inputs'],panel['results']):check(inp['units'],result,[rng.randrange(len(w)) for w in inp['units']])
 assert panel['maximum']==max(x['score'] for x in panel['results'])
maximum=max(x['result']['score'] for x in r['outputs']);tail=(1+sum(x['maximum']>=maximum for x in r['nulls']))/1000
assert maximum==r['maximum'] and tail==r['tail']
(P/'independent-check.json').write_text(json.dumps(dict(pass_all=True,complete_outputs=cases,scalar_max_error=maxerr,control_tails=controls,actual_maximum=maximum,actual_fullprocedure_tail=tail),indent=2)+'\n')
print((P/'independent-check.json').read_text())
