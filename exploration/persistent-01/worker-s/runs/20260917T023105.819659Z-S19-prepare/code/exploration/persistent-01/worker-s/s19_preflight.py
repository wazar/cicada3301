from pathlib import Path
import json,hashlib
B=Path('exploration/persistent-01/worker-s');src=Path('exploration/persistent-01/worker-f/F06-maps.json');pages=json.loads(src.read_text());rows=[]
for p in pages:
 lengths=[w['end']-w['start'] for w in p['words']];rows.append({'page':p['page'],'units':len(lengths),'lengths':lengths,'bad':[{'word':i,'length':n,'map':p['words'][i]} for i,n in enumerate(lengths) if not 1<=n<=29]})
r={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'pages':rows,'page_count':len(rows),'units':sum(r['units'] for r in rows),'max_length':max(max(r['lengths']) for r in rows),'bad_count':sum(len(r['bad']) for r in rows)};(B/'S19-preflight.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='pages'}));print(json.dumps([r for r in rows if r['bad']]))
