import json,pathlib,collections,hashlib
R=pathlib.Path(__file__).parent;M=json.load(open(R.parent/'worker-f/F06-maps.json'));rows=[];adj=[]
for m in M:
 pos=[i for i,g in enumerate(m['gaps']) if g['type']=='period'];intervals=[b-a for a,b in zip(pos,pos[1:])]
 for a,b in zip(pos,pos[1:]):
  if b-a==1:adj.append(dict(page=m['page'],previous_gap=m['gaps'][a],next_gap=m['gaps'][b],intermediate_unit=m['words'][a+1]))
 rows.append(dict(page=m['page'],period_slots=pos,between_period_intervals=intervals,period_count=len(pos)))
e=R/'H03-evidence.json.gz';r=dict(note='Literal source period classes only, physically distinct marks collapsed; no sentence/paragraph interpretation without images.',rows=rows,adjacent_period_pairs=adj,interval_histogram=dict(collections.Counter(i for r in rows for i in r['between_period_intervals'])),h03_artifact=dict(bytes=e.stat().st_size,sha256=hashlib.sha256(e.read_bytes()).hexdigest()))
(R/'H06-description.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='rows'},indent=2))
