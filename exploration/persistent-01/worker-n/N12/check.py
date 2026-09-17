from pathlib import Path
import json,gzip,random
from fractions import Fraction
R=Path(__file__).parent;B=R.parents[1];pages={p['page']:p for p in json.loads((B/'worker-f/F06-maps.json').read_text())};actual=json.loads((R/'actual.json').read_text());out=[]
for a in actual['actual']:
 p=pages[a['page']];cert=a['result']['certificate'];matrix=[];assert len(cert)==30 and len({e['word'] for e in cert})==30
 for e in cert:
  w=p['words'][e['word']];seq=p['indices'][w['start']:w['end']];assert seq==e['runes'] and w==e['map'];row=[seq[:-1].count(i)-int(seq[-1]==i) for i in range(29)]+[1];assert row==e['row'];matrix.append(list(map(Fraction,row)))
 determinant=Fraction(1)
 for j in range(30):
  k=next(k for k in range(j,30) if matrix[k][j])
  if k!=j:matrix[k],matrix[j]=matrix[j],matrix[k];determinant=-determinant
  v=matrix[j][j];determinant*=v
  for k in range(j+1,30):
   factor=matrix[k][j]/v
   for col in range(j,30):matrix[k][col]-=factor*matrix[j][col]
 assert determinant.denominator==1 and determinant.numerator==a['result']['integer_determinant'] and determinant.numerator%29;out.append(dict(page=a['page'],exact_determinant=int(determinant),mod29=int(determinant)%29,source_rows_checked=30))
ctrl=json.load(gzip.open(R/'controls.json.gz','rt'));rng=random.Random(ctrl['seed'])
for t in ctrl['tiny']:
 A=[[rng.randrange(5) for _ in range(3)] for _ in range(rng.randrange(1,7))];assert A==t['A']
for c in ctrl['controls']:
 f=list(range(29));rng.shuffle(f);b=rng.randrange(29);assert f==c['map'] and b==c['offset']
 for panel in c['panels']:
  p=pages[panel['page']];expected=p['indices'][:]
  for w in p['words']:
   if w['end']-w['start']>=3:
    total=b
    for v in expected[w['start']:w['end']-1]:total+=f[v]
    expected[w['end']-1]=f.index(total%29)
  assert expected==panel['runes']
(R/'check-result.json').write_text(json.dumps(dict(status='PASS',raw_certificates=out,control_rng_panels=60),indent=2));print(out)
