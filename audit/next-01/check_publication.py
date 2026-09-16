"""Read-only NEXT-01 integration/preservation checks; no scientific reruns."""
import hashlib,json,pathlib,subprocess,datetime
R=pathlib.Path.cwd();B=R/'audit/next-01';entry=json.loads((B/'entry.json').read_text());base=entry['working_commit']
for r in entry['unrelated_file_fingerprints']:assert hashlib.sha256((R/r['path']).read_bytes()).hexdigest()==r['sha256'],r['path']
old=[json.loads(l) for l in subprocess.check_output(['git','show',base+':audit/CLAIMS.jsonl'],text=True).splitlines()];new=[json.loads(l) for l in (R/'audit/CLAIMS.jsonl').read_text().splitlines()];assert len(old)==len(new)==47
for a,b in zip(old,new):
 for k in ['id','claim','source','additional_sources','depends_on','assumptions','expected_result','inherited_ledger_ids','status']:assert a[k]==b[k],(a['id'],k)
assert sum('NEXT-01' in r['tested_scope'] for r in new)==7
assert not subprocess.check_output(['git','diff',base,'--','liber-primus','audit/parallel-01','audit/runs','audit/reports/T0.md','audit/reports/T1.md','audit/reports/PARALLEL-01.md','audit/tools'])
rows=[]
for owner in ['experiment-01','alphanumeric-01','f-interruption-01','next-review']:
 for p in sorted((R/'audit'/owner/'runs').glob('*/command.json')):
  r=json.loads(p.read_text());assert r['outcome']!='RUNNING';assert all(k in r for k in ['started_utc','finished_utc','exit_code','duration_seconds','sources_inputs','command','working_commit']);assert r['timeout_seconds']<=300
  for stream in ['stdout.txt','stderr.txt']:assert (p.parent/stream).is_file()
  for f in r['sources_inputs']:
   if f.get('exists') and f['path'].endswith('.py'):
    snap=p.parent/'code'/f['path'];assert hashlib.sha256(snap.read_bytes()).hexdigest()==f['sha256'],str(snap)
  rows.append({'owner':owner,'run':str(p.parent.relative_to(R)),'outcome':r['outcome'],'exit_code':r['exit_code'],'seconds':r['duration_seconds']})
# Verify no task artifact changed its frozen sources or the actual preserved counts.
f=json.loads((R/'audit/experiment-01/FREEZE.json').read_text());prereg=R/'audit/experiment-01/preregistration.json'
assert hashlib.sha256(prereg.read_bytes()).hexdigest()=='ed0fdd288c12a705f3688924a813960d489b20c504116002ef6a811adfced9ea'
for r in json.loads((B/'publication-redactions.json').read_text())['files']:
 assert hashlib.sha256((R/r['path']).read_bytes()).hexdigest()==r['published_sha256'];assert hashlib.sha256((B/'private-originals'/r['path']).read_bytes()).hexdigest()==r['original_sha256']
private=[];large=[]
for name in ['next-01','experiment-01','alphanumeric-01','f-interruption-01','next-review']:
 for p in (R/'audit'/name).rglob('*'):
  if not p.is_file() or 'private-originals' in p.parts:continue
  if p.stat().st_size>10_000_000:large.append(str(p.relative_to(R)))
  try:s=p.read_text()
  except UnicodeError:continue
  if str(R) in s or ('/'+'Users/') in s:private.append(str(p.relative_to(R)))
assert not private,private
assert not large,large
print(json.dumps({'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'outcome':'PASS','claims_preserved':47,'claims_scoped_updates':7,'original_research_and_prior_audits_unchanged':True,'unrelated_local_files_unchanged':True,'frozen_preregistration_unchanged':True,'private_prefixes_published':private,'files_over10MB':large,'worker_review_runs':rows,'seconds_by_owner':{o:sum(r['seconds'] for r in rows if r['owner']==o) for o in sorted({r['owner'] for r in rows})}},indent=2))
