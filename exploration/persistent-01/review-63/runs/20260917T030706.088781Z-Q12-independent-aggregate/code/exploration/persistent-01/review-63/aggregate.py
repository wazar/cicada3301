from pathlib import Path
import json, hashlib, datetime
B=Path('exploration/persistent-01'); O=B/'review-63'; Q=B/'coordinator/Q12-sum-autokey'
assert not (B/'STOP').exists()
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
names=['control'+str(i) for i in range(4)]+[s for pg in [0,17,55] for s in ['actual'+str(pg)]+['actual'+str(pg)+f'-null{j:02}' for j in range(19)]]
rows=[json.loads((O/(name+'-review.json')).read_text()) for name in names]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for row in rows:
 for f in row['inputs']:assert sha(Path(f['path']))==f['sha256']
panels=[]
for pg in [0,17,55]:
 name='actual'+str(pg); main=next(r for r in rows if r['name']==name); nulls=[r for r in rows if r['name'].startswith(name+'-null')]; assert len(nulls)==19
 count=sum(r['maximum']>=main['maximum'] for r in nulls); summary=json.loads((Q/(name+'-summary.json')).read_text()); assert summary==dict(main=name,maximum=main['maximum'],nulls=19,tail=(1+count)/20)
 panels.append(dict(page=pg,maximum=main['maximum'],nulls_at_least_actual=count,tail=(1+count)/20))
controls=[]
for r in rows[:4]:
 d=json.loads((Q/(r['name']+'.json')).read_text()); diag=next(x['control']['equal_seed_diagnostics'] for x in d['rows'] if 'control' in x)
 controls.append(dict(name=r['name'],length=r['rune_count'],seed=r['control']['seed'],seed_draws=r['independent_seed_draws'],global_seed_rank=r['control']['global_seed_rank'],selected_errors=r['control']['selected_errors'],best_equal_seed_errors=min(x['errors'] for x in diag),best_scoring_equal_seed_errors=max(diag,key=lambda x:x['score'])['errors']))
files=[Q/'CARD.md',Q/'CONTROL-AMENDMENT.md',Q/'test.py',Q/'model.json',Q/'model.npz',B/'worker-c/p03_frozen.py',B/'worker-f/F06-maps.json',O/'check.py',O/'aggregate.py']
files += [Q/(n+ext) for n in names for ext in ['.json','.npz']]
files += [Path(x['path']) for x in json.loads((Q/'model.json').read_text())['sources']]
files += [Path(json.loads((Q/(n+'.json')).read_text())['source']['path']) for n in names[:4]]
manifest=[dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size) for p in files]
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
out=dict(status='PASS',packets=len(rows),all_seed_scores=sum(c['all_seed_scores'] for r in rows for c in r['checks']),factor_cells=len(rows)*12*29**3,retained_family_paths=len(rows)*3*16,global_paths=len(rows)*16,max_score_error=max(c['max_score_error'] for r in rows for c in r['checks']),max_factor_error=max(c['max_factor_error'] for r in rows for c in r['checks']),summed_review_seconds=sum(r['seconds'] for r in rows),controls=controls,actual=panels)
assert out['all_seed_scores']==46880704
(O/'result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
