import json,math,ast
from pathlib import Path
R=Path(__file__).parent
src=ast.parse((R/'check.py').read_text());ns={}
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'functions','exec'),ns)
z=json.loads((R/'snapshots/real.json').read_text());out=[]
for rec in z['records']:
 for u in rec['units']:
  if not u['eligible'] or u['prime']:continue
  n=int(u['value']);item={'page':rec['page'],'start':u['start'],'value':u['value']}
  if n<2:item['below_two']=True
  else:
   factor=next((d for d in range(2,min(math.isqrt(n),1000)+1) if n%d==0),None)
   if factor:item['factor']=factor
   else:
    s=((n-1)&-(n-1)).bit_length()-1;d=(n-1)>>s
    for a in (2,325,9375,28178,450775,9780504,1795265022):
     x=ns['exp'](a%n,d,n);chain=[x]
     for _ in range(1,s):chain.append(chain[-1]**2%n)
     if a%n and x!=1 and n-1 not in chain:item.update(base=a,odd_exponent=d,squares=chain);break
    assert 'base' in item
  out.append(item)
(R/'real-composite-witnesses.json').write_text(json.dumps(out));print('witnesses',len(out))
