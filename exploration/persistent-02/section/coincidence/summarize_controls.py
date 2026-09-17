from pathlib import Path
import json
O=Path(__file__).resolve().parent;rows=[]
for i in range(16):
 x=json.loads((O/f'control{i:02}-summary.json').read_text())
 if x['outcome']!='COMPLETE':rows.append(dict(index=i,**x));continue
 reps=x['full_representatives'];rows.append(dict(index=i,id=x['id'],family=x['family'],outcome=x['outcome'],true_key_full_rank=x['true_key_full_rank'],true_key_prefix_rank=x['true_key_prefix_rank'],known_key_truth_full_rank=x['known_key_full']['strict_rank'],known_key_truth_prefix_rank=x['known_key_prefix']['strict_rank'],truth_full_best=x['truth_in_globally_best_full'],truth_prefix_best=x['truth_in_prefix_frozen_set'],truth_continuation_best=x['truth_in_prefix_frozen_set'] and x['known_key_full']['truth_total']-x['known_key_prefix']['truth_total']==x['continuation_maximum_over_frozen_set'],prefix_tied_paths=x['prefix_tied_paths'],prefix_future_states=x['prefix_future_states'],full_representatives=[dict(cell=r['cell_id'],errors=r['errors'],F_count=r['F_count'],tie_product=r['tie_product']) for r in reps],truth_F_count=x['truth_F_count'],peak_process_rss_bytes=x.get('peak_process_rss_bytes')))
complete=[r for r in rows if r['outcome']=='COMPLETE'];result=dict(controls=16,complete=len(complete),unresolved=16-len(complete),true_key_full_rank1=sum(r['true_key_full_rank']==1 for r in complete),true_key_prefix_rank1=sum(r['true_key_prefix_rank']==1 for r in complete),truth_full_best=sum(r['truth_full_best'] for r in complete),truth_prefix_best=sum(r['truth_prefix_best'] for r in complete),truth_continuation_best=sum(r['truth_continuation_best'] for r in complete),rows=rows);(O/'capability-summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
for r in rows:print(json.dumps(r))
