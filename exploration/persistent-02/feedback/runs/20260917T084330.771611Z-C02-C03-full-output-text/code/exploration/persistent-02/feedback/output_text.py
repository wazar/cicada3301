import pathlib,json
from summarize import trans
O=pathlib.Path(__file__).resolve().parent
for dirname in ['C03','C02-actual']:
 p=json.loads((O/dirname/'panel00.json').read_text());groups=p.get('groups',{'prefix':{'global16':p['alternatives']}});ends=set(p.get('ends',json.loads((O/'C03/input.json').read_text())['ends']));lines=[]
 for name,g in groups.items():
  for i,a in enumerate(g['global16']):lines.append(f"{name} alternative{i+1} k={a['k']} seed={a['seed']} full={a['full_score']} continuation={a['continuation_score']}\n"+trans(a['plain'],ends)+'\n')
 (O/dirname/'actual-alternatives.txt').write_text('\n'.join(lines))
 print(dirname,lines[0])
