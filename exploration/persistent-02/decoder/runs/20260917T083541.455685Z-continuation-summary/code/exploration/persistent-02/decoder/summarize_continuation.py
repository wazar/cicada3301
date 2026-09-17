import gzip,json
from compare import O
rows=[]
for p in sorted((O/'continuation').glob('*.json.gz')):
 x=json.loads(gzip.decompress(p.read_bytes()));r=dict(model=x['model'],id=x['id'],committed_prefix_errors=x['committed_top']['prefix_errors'],committed_suffix_errors=x['committed_top']['suffix_errors'],retained16_errors=x['best_retained_prefix']['prefix_errors']+x['best_retained_prefix']['suffix_errors'],selected_prefix_rank=x['best_retained_prefix']['prefix_rank'],joint=x['joint_metrics'],genuine=x['genuine_metrics'],seconds=x['seconds']);rows.append(r)
assert len(rows)==24
(O/'continuation-summary.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
