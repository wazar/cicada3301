"""Independent necessary-condition proof for the three empty O02 pages."""
import json,gzip,collections,hashlib
from pathlib import Path
B=Path('exploration/persistent-01');d=json.load(gzip.open(B/'worker-o/O02-evidence.json.gz','rt'));j=json.load(gzip.open(B/'worker-j/j03-windows.json.gz','rt'));t={x['name']:x['source'] for x in j['texts']};dataset=json.loads(Path('audit/parallel-01/inputs/dataset.json').read_text());out=[]
for p in d['real']:
 if p['page'] not in [0,3,17]:continue
 page=next(x for x in dataset['pages'] if x['original_page']==p['page']);items=sorted(collections.Counter(page['indices']).values());assert items==p['items'];witnesses=[]
 for c in p['cases']:
  targets=c['targets'];assert sum(items)==sum(targets)
  deficits=[{'threshold':z,'demand':sum(v for v in targets if v<=z),'available':sum(v for v in items if v<=z)} for z in sorted(set(targets)) if sum(v for v in targets if v<=z)>sum(v for v in items if v<=z)]
  assert deficits,'Necessary test insufficient: would require exact partition verification'
  for w in c['provenance']:
   source=t[w['group']][w['start']:w['start']+len(page['indices'])];cnt=collections.Counter(source);assert [cnt[i] for i in range(26)]==w['letter_counts'];assert sorted(cnt.values())==targets
  witnesses.append({'targets':targets,'windows':c['provenance'],'capacity_contradiction':deficits[0]})
 expected=j['windows'][[0,1,3,7,17].index(p['page'])];actual_pairs=sum(v*(v-1)//2 for v in items);a={(w['group'],w['start']) for w in expected if w['bound']<=actual_pairs};b={(w['group'],w['start']) for c in p['cases'] for w in c['provenance']};assert a==b
 out.append({'page':p['page'],'eligible_windows':len(a),'cases':len(witnesses),'witnesses':witnesses})
result={'proof':'Bins with target<=t require items<=t; total demand cannot exceed total available. Every case on these three pages violates this necessary inequality. Other J03 windows already fail reviewed collision relaxation.','scope':'Finite J03 source windows, no arbitrary language or cipher exclusion. No exact solver imported/executed.','pages':out}
(B/'coordinator/O02-necessary-proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'pages':[{k:v for k,v in p.items() if k!='witnesses'} for p in out],'all_pass':True}))
