import pathlib,json,hashlib,ast
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2];S=R/'exploration/persistent-02/section';C=R/'exploration/persistent-02/coordinator'
source=(S/'summarize_forest.py').read_text();tree=ast.parse(source);outer=next(x for x in tree.body if isinstance(x,ast.For));guard=outer.body[1]
assert isinstance(guard,ast.If) and isinstance(guard.body[0],ast.Continue)
assert ast.unparse(guard.test)=="d['batch'] not in ['A01', 'A02']"
rows=[json.loads(p.read_text()) for p in (S/'A04').glob('*.json')];rows=[x for x in rows if x['batch'] in ['A01','A02']];summary=json.loads((S/'A04-summary.json').read_text());assert len(rows)==summary['counts']['datasets']==176;assert sum(x['candidate_count'] for x in rows)==summary['counts']['candidates']==629000
hashes=json.loads((C/'forest-summary-original-output-hashes.json').read_text());checks={}
for path,want in hashes.items():
 got=hashlib.sha256((R/path).read_bytes()).hexdigest();assert got==want;checks[path]=got
(O/'summary-fix-check.json').write_text(json.dumps(dict(passed=True,source_sha256=hashlib.sha256(source.encode()).hexdigest(),panels=len(rows),candidates=629000,unchanged_original_outputs=checks),indent=2)+'\n');print('summary fix PASS: explicit batch guard,176/629000,original outputs unchanged')
