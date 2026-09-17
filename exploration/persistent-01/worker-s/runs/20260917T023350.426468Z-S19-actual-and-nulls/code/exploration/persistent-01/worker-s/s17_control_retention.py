from pathlib import Path
import json
O=Path('exploration/persistent-01/worker-s/S17');p=json.loads((O/'packets.json').read_text());out=[]
for i in range(4):
 r=json.loads((O/f'packet{i}-main.json').read_text());errs=[sum(a!=b for a,b in zip(p[i]['truth'],x['plain'])) for x in r['restarts']];out.append({'control':i,'name':p[i]['name'],'retained_exact_plaintext_maps':sum(e==0 for e in errs),'retained_error_counts':errs,'intermediate_truth_visit_or_survival':'not tracked; optimizer never receives truth'})
(O/'control-retention.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
