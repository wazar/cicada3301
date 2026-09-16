"""Read-only integration integrity checks; not scientific tests."""
import ast,hashlib,json,pathlib,subprocess,datetime
root=pathlib.Path.cwd();old=[json.loads(x) for x in subprocess.check_output(['git','show','95e11e918ace77a51de4b612a48e74c298e67e58:audit/CLAIMS.jsonl'],text=True).splitlines()];new=[json.loads(x) for x in pathlib.Path('audit/CLAIMS.jsonl').read_text().splitlines()]
assert len(new)==len(old)==47
for a,b in zip(old,new):
 for k in ['id','claim','source','additional_sources','depends_on','assumptions','expected_result','inherited_ledger_ids']:
  assert a[k]==b[k],(a['id'],k)
 for e in b['evidence_paths']:
  if e not in a['evidence_paths']: assert pathlib.Path(e).exists(),(b['id'],e)
assert len({x['id'] for x in new})==47
assert len(pathlib.Path('audit/LEDGER-WARNINGS.jsonl').read_text().splitlines())==18
for name,h in [('dataset.json','e3d8a8b7a81f00e17d54209772eee7bedb5b922e6176ca722be31f952eaea895'),('page-map.json','f59bf8d94c86a06cf620b5368eabb27dfebc62fbf39b38e467636785762f4cba')]:
 assert hashlib.sha256((pathlib.Path('audit/parallel-01/inputs')/name).read_bytes()).hexdigest()==h
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],text=True).splitlines();allowed={'.gitignore','audit/tools/run_t0.py','audit/CLAIMS.jsonl','audit/CLAIM-INDEX.md','audit/DEPENDENCIES.md','audit/FINDINGS.md','audit/STATUS.md'};assert set(changed)<=allowed,changed
assert not subprocess.check_output(['git','diff','HEAD','--','liber-primus','audit/runs/T0','audit/reports/T0.md','audit/BASELINE.md','audit/environment.json'])
parsed=[];private=[];large=[]
for p in pathlib.Path('audit/parallel-01').rglob('*'):
 if not p.is_file():continue
 if p.stat().st_size>5_000_000:large.append(str(p))
 if p.suffix=='.py' and 'sources' not in p.parts:ast.parse(p.read_text());parsed.append(str(p))
 try:s=p.read_text()
 except UnicodeError:continue
 if str(root) in s or ('/'+'Users/') in s:private.append(str(p))
assert not private,private
assert not large,large
c=pathlib.Path('audit/parallel-01/coordination');assert hashlib.sha256((c/'blind-answer.json').read_bytes()).hexdigest()==json.loads((c/'blind-commitment.json').read_text())['answer_sha256']
assert hashlib.sha256(pathlib.Path('audit/parallel-01/detectors/blind-ranking.json').read_bytes()).hexdigest()==json.loads((c/'blind-reveal.json').read_text())['ranking_sha256']
# Metadata redaction did not change downloaded bytes.
for r in json.loads(pathlib.Path('audit/parallel-01/reference/sources/retrieval.json').read_text()):
 if 'sha256' in r:
  p=pathlib.Path(r['path'].replace('<REPO_ROOT>/',''));assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':'.venv/bin/python -B audit/parallel-01/coordination/check_integration.py','outcome':'PASS','claims':47,'updated':sum('PARALLEL-01' in r['tested_scope'] for r in new),'warnings':18,'audit_scripts_parsed':len(parsed),'frozen_v1_unchanged':True,'original_claim_source_fields_unchanged':True,'inherited_research_and_T0_unchanged':True,'private_prefixes':private,'files_over_5MB':large,'blind_commitment_and_ranking_unchanged':True},indent=2))
