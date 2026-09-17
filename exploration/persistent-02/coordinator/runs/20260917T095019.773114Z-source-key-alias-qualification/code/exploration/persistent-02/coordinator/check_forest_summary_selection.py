"""Execute only the summarizer's read-only aggregation prefix; no result rewrites."""
from pathlib import Path
import ast,json,hashlib,sys
R=Path(__file__).resolve().parents[3];p=R/'exploration/persistent-02/section/summarize_forest.py'
t=ast.parse(p.read_text());nodes=[]
for node in t.body:
 if isinstance(node,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='summary' for x in node.targets):break
 nodes.append(node)
ns={'__file__':str(p)};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(p)+'::aggregation-only','exec'),ns)
record={'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'counts':ns['counts'],'batches':sorted(set(x['batch'] for x in ns['rows'])),'expected_batches':['A01','A02'],'expected_datasets':176,'expected_candidates':629000,'scope':'Reads mixed A04 directory with later A05 outputs present; does not run searches or rewrite original summaries.'}
out=Path(__file__).with_name(sys.argv[1]);assert not out.exists();out.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
assert record['batches']==record['expected_batches'] and record['counts']['datasets']==176 and record['counts']['candidates']==629000,'cross-model aggregation contamination'
