from summarize import trans
import json,pathlib
O=pathlib.Path(__file__).resolve().parent/'C10-actual'
for model in ['p03','complementary']:
 d=json.loads((O/f'{model}-panel00.json').read_text());lines=[]
 for row in d['rows']:
  for name,alts in [('full',row['full']['alternatives']),('continuation',row['continuation'])]:
   for i,a in enumerate(alts):
    text=f'{model} {row["key"]} {name} alternative{i+1}\n'+trans(a['plain'],set(d['ends']))+'\n';lines.append(text)
    if i==0:print(text)
 (O/f'{model}-alternatives.txt').write_text('\n'.join(lines))
