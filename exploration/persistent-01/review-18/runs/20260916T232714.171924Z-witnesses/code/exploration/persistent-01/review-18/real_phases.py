import ast,json,hashlib
from pathlib import Path
R=Path(__file__).parent
source=ast.parse((R/'check.py').read_text())
selected=[n for n in source.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef)) or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='B' for t in n.targets)]
ns={};exec(compile(ast.Module(body=selected,type_ignores=[]),'independent-functions','exec'),ns)
score=ns['score'];M=json.loads((R/'snapshots/F06-maps.json').read_text());z=json.loads((R/'snapshots/real.json').read_text());tables=[];count=0
for m,x,rec in zip(M,z['streams'],z['records']):
 n=len(x);ls=sorted({w['end']-w['start'] for w in m['words'] if 2<=w['end']-w['start']<=13});cache={}
 for l in ls:
  cache[l]=[]
  for start in range(n):cache[l].append(score([x[j%n] for j in range(start,start+l)]));count+=1
 table=[0]*n
 for w in m['words']:
  l=w['end']-w['start']
  if l not in cache:continue
  for offset in range(n):table[offset]+=cache[l][(w['start']+offset)%n]
 assert table==rec['phase_counts'];tables.append(table)
null=[sum(t[o] for t,o in zip(tables,offsets)) for offsets in z['offsets']];assert null==z['null']
out={'status':'PASS','independent_window_scores':count,'all_phase_counts':sum(map(len,tables)),'actual':sum(t[0] for t in tables),'null':null,'tail':(1+sum(v>=z['actual'] for v in null))/1000,'phase_tables':tables}
(R/'real-phases.json').write_text(json.dumps(out));print({k:v for k,v in out.items() if k not in ('null','phase_tables')})
