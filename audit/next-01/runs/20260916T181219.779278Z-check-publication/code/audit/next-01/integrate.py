"""Attach reviewed NEXT-01 evidence, retaining every original claim and source."""
import datetime,hashlib,json,pathlib
ROOT=pathlib.Path.cwd();base=ROOT/'audit/next-01'
updates={
 'C-002':('alphanumeric-01','Coordinate-linked p49–51 transcript records32 rows/256 two-character tokens, page cuts and rune context; rune-only export unchanged.','Unblinded reconciliation, not certified full image truth; no new token correction claimed.'),
 'C-003':('alphanumeric-01','Fresh relikd copy matches local bytes; targeted source conflicts and actual images support previously corrected payload.','Same-source agreement is not independent testimony; undisputed shared errors remain possible.'),
 'C-008':('f-interruption-01','Independent rule implementation and reviewer reconstruct all919 runes of three complete keyed references with every key transition.','Supplied interruption labels validate arithmetic, not automatic discovery or image transcription.'),
 'C-009':('f-interruption-01','Literal-F non-consumption reproduces14 labeled interruptions. Unknown-F tests preserve908 compatible paths; some truth paths are pruned or rank below alternatives.','Three simple prose successes do not calibrate real-input search. Literal F differs from deleted F and rejection key-skip.'),
 'C-010':('experiment-01','New structured-key gate BLOCKED_BY_POSITIVE_CONTROL:67 pairs executed,66 pass, one119/120-rune failure;253 skipped. Planted key ranks first; no real decode or calibration ran.','Does not retract old selftest result or reject any recipe on LP2; only the new exact-recovery gate failed.'),
 'C-013':('experiment-01','DIVINITY/+1/rejection case6 fails exact terminal recovery despite requiring no more than one consecutive rejection and planted hypothesis ranking first.','No cap-overflow explanation; no stronger pruning claim. No evidence about separate literal-F model.'),
 'C-015':('experiment-01','Frozen shared-recipe/shared-sign whole-set selection executed on positives; required failure correctly blocks all100 calibration,100 heldout and real choices.','No new false-flag estimate, calibrated maximum or real puzzle verdict exists.')}
p=ROOT/'audit/CLAIMS.jsonl';rows=[json.loads(x) for x in p.read_text().splitlines()]
for r in rows:
 if r['id'] not in updates:continue
 assert 'NEXT-01' not in r['tested_scope']
 group,result,limits=updates[r['id']];report=f'audit/{group}/REPORT.md'
 r.setdefault('audit_history',[]).append({'task':'PARALLEL-01','status':r['status'],'observed_result':r['observed_result'],'not_tested':r['not_tested'],'next_check':r['next_check']})
 r['tested_scope']['NEXT-01']={'result':result,'limits':limits,'report':report,'review':'audit/next-review/REPORT.md','input_commit':'beee1b995e142ba920280736e9e45835abbf650a'}
 r['observed_result']+=' NEXT-01: '+result
 r['evidence_paths']+= [report,'audit/next-review/REPORT.md']
 if r['id'] in ['C-010','C-013','C-015']:r['next_check']='Separately preregistered synthetic terminal-path diagnostic; real Experiment01 remains blocked, no scope expansion.'
 if r['id']=='C-009':r['next_check']='Calibrate the separate literal-F model with actual candidate keys before any later unsolved application; production repairs remain separate.'
p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows))
p=ROOT/'audit/CLAIM-INDEX.md';s=p.read_text().replace('# Audit claim index after PARALLEL-01','# Audit claim index after NEXT-01');p.write_text(s+'\nNEXT-01 adds scoped evidence to C-002/003/008/009/010/013/015 without changing inherited claim text or broad statuses. The new four-recipe control gate failed; no real puzzle result exists. See [NEXT-01](reports/NEXT-01.md).\n')
# Preserve exact original failing stderr locally while publishing only path-redacted copies.
private=base/'private-originals';private.mkdir(exist_ok=True);redactions=[]
for rel in ['audit/f-interruption-01/runs/20260916T180418.984354Z-main/stderr.txt','audit/experiment-01/runs/20260916T180556.208277Z-post-stop-accounting/stderr.txt']:
 q=ROOT/rel;b=q.read_bytes();target=private/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b);new=b.decode().replace(str(ROOT),'<REPO_ROOT>').encode();q.write_bytes(new)
 redactions.append({'path':rel,'original_sha256':hashlib.sha256(b).hexdigest(),'published_sha256':hashlib.sha256(new).hexdigest(),'change':'Private checkout prefix only; original bytes retained locally under ignored private-originals.'})
(base/'.gitignore').write_text('/private-originals/\n')
(base/'publication-redactions.json').write_text(json.dumps({'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':redactions},indent=2)+'\n')
print(json.dumps({'updated_claims':list(updates),'all_claims_retained':len(rows),'inherited_source_fields_unchanged':True,'metadata_redactions':len(redactions),'private_originals_retained_locally':True},indent=2))
