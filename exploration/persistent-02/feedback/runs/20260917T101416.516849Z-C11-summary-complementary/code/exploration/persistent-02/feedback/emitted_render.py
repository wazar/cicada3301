from summarize import trans
import json,pathlib,sys
O=pathlib.Path(__file__).resolve().parent/'C11-actual'
for model in sys.argv[1:]:
 d=json.loads((O/f'{model}-panel00.json').read_text());lines=[]
 for row in d['rows']:
  if row['outcome']!='COMPLETE':continue
  for name,alts in [('full',row['full']['alternatives']),('continuation',row['continuation'])]:
   for i,a in enumerate(alts):
    t=f'{model} k{row["k"]} {name} alternative{i+1} seed={a["seed"]}\n'+trans(a['plain'],set(d['ends']))+'\n';lines.append(t)
    if i==0:print(t)
 (O/f'{model}-alternatives.txt').write_text('\n'.join(lines))
