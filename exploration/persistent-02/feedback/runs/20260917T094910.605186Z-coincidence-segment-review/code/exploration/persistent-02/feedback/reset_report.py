import json,pathlib
from summarize import trans
O=pathlib.Path(__file__).resolve().parent
for model in ['p03','complementary']:
 d=json.loads((O/f'C08-actual/{model}-panel00.json').read_text());lines=[]
 for name,alts in [('full',d['full']['alternatives']),('continuation',d['continuation'])]:
  for i,a in enumerate(alts):lines.append(f'{name} alternative{i+1} seed={a["seed"]}\n'+trans(a['plain'],set(d['ends']))+'\n')
 (O/f'C08-actual/{model}-alternatives.txt').write_text('\n'.join(lines));print(model,lines[0],lines[16])
 rows=[]
 for p in sorted((O/'C08').glob(f'{model}-plant*/summary.json')):
  x=json.loads(p.read_text());rows.append({k:v for k,v in x.items() if k!='alternatives'})
 (O/f'C08/{model}-control-summary.json').write_text(json.dumps(rows,indent=2)+'\n')
