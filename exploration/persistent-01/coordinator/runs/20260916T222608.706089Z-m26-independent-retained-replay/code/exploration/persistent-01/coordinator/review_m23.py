"""Independent inverse encryption of every M23 cell and retained alternative."""
from pathlib import Path
import json,gzip,hashlib
B=Path('exploration/persistent-01');W=B/'worker-m/M23';keys={r['id']:r for r in json.loads((W/'construction.json').read_text())['cells']};counts={'cells':0,'alternatives':0,'rune_visits':0};files=[]
for f in sorted((W/'cells').glob('*.json.gz')):
 d=json.load(gzip.open(f,'rt'));c=d['cipher']
 for row in d['rows']:
  key=keys[row['id']]
  for kind,p in [('cells',row)]+[('alternatives',v) for v in row.get('alternatives',[])]:
   L=set(p['literal_positions']);assert len(L)==len(p['literal_positions']) and all(0<=i<len(c) for i in L);j=0
   assert len(p['plain'])==len(c)
   for i,x in enumerate(p['plain']):
    if i in L:assert x==c[i]==0
    else:assert (x-key['sign']*key['key'][j%len(key['key'])])%29==c[i];j+=1
   assert j==p['used'];counts[kind]+=1;counts['rune_visits']+=len(c)
 files.append({'path':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
assert counts['cells']==68800 and counts['alternatives']==24760
out={'scope':'Exact inverse encryption and key-consumption consistency for every retained full output. No search rerun or semantic/scorer independence claim.','counts':counts,'files':files}
(B/'coordinator/M23-path-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(counts))
