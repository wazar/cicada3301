import json,hashlib
from pathlib import Path
from check import trace
root=Path(__file__).resolve().parents[4];source=root/'exploration/persistent-02/feedback/C11/plants.json';cases=json.loads(source.read_text())['cases'];out=[]
for d in cases:
 row={'id':d['id'],'k':d['k'],'length':len(d['truth']),'literal_count':len(d['literal_positions'])}
 for convention,emitted,c in [('emitted',True,d['cipher']),('normal_only',False,d['old_cipher'])]:
  t=trace(c,d['k'],d['literal_positions'],emitted=emitted)
  pred=[(v[0]+sum(a*b for a,b in zip(v[1:],d['seed'])))%29 for v in t['forms']];assert pred==d['truth']
  row[convention]={'final_rank':t['ranks'][-1],'first_mature_zero':t['first_mature_zero'],'rank_path':t['ranks'],'seed_phase_path':t['phases']}
 out.append(row)
result={'source':str(source.relative_to(root)),'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':out,'seed_independent_tail_count':sum(d['emitted']['first_mature_zero'] is not None for d in out)}
Path(__file__).with_name('plants.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print(json.dumps({'cases':len(out),'seed_independent_tail_count':result['seed_independent_tail_count'],'final_ranks':[d['emitted']['final_rank'] for d in out]}))
