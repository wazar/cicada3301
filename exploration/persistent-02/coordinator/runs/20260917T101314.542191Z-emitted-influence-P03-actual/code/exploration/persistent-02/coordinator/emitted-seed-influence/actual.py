from pathlib import Path
import hashlib,json
from check import trace
root=Path(__file__).resolve().parents[4];out=[];pins={}
for model in ['p03','complementary']:
 path=root/f'exploration/persistent-02/feedback/C11-actual/{model}-panel00.json'
 if not path.exists():continue
 pins[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest();d=json.loads(path.read_text())
 for row in d['rows']:
  if row['outcome']!='COMPLETE':continue
  for kind in ['full','prefix','continuation']:
   alternatives=row[kind]['alternatives'] if kind!='continuation' else row[kind]
   for i,a in enumerate(alternatives):
    c=d['cipher'][:len(a['plain'])];t=trace(c,row['k'],a['literal_positions']);p=[(v[0]+sum(x*y for x,y in zip(v[1:],a['seed'])))%29 for v in t['forms']];assert p==a['plain']
    out.append(dict(model=model,k=row['k'],kind=kind,alternative=i,first_mature_zero=t['first_mature_zero'],final_rank=t['ranks'][-1],rank_path=t['ranks'],seed_phase_path=t['phases'],fixed_mask_full_plaintext_seed_rank=None,scope='Rank describes active history and future continuation only; previous emitted plaintext can still identify the seed.'))
result={'source_pins':pins,'records':out};Path(__file__).with_name('actual.json').write_text(json.dumps(result,separators=(',',':'))+'\n');print(json.dumps({'records':len(out),'leaders':[{k:v for k,v in a.items() if k not in ['rank_path','seed_phase_path']} for a in out if a['alternative']==0]}))
