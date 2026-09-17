from pathlib import Path
import json,gzip,math,hashlib
O=Path(__file__).resolve().parent;A=O.parent/'Q09-reciprocal';B=O.parent/'Q10-reciprocal-stability';rows=[]
for p in sorted(A.glob('*.json.gz')):
 a=json.load(gzip.open(p,'rt'));q=B/p.name;b=json.load(gzip.open(q,'rt'));n=sum(map(sum,a['held_counts']));nr=sum(map(sum,a['train_counts']));f=[v+n*math.log(28) for v in a['held_ll']];r=[v+nr*math.log(28) for v in b['reverse_held_ll']];rows.append(dict(name=a['name'],q09_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),q10_sha256=hashlib.sha256(q.read_bytes()).hexdigest(),forward_events=n,reverse_events=nr,forward_vs_uniform=f,reverse_vs_uniform=r,combined_vs_uniform=[x+y for x,y in zip(f,r)],qualified=b['qualified']))
assert len(rows)==600
(O/'all-panels.json').write_text(json.dumps(rows,indent=2)+'\n');main=[r for r in rows if '-null' not in r['name']];(O/'summary.json').write_text(json.dumps(main,indent=2)+'\n');print(json.dumps(main))
