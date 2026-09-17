from pathlib import Path
import json
R=Path(__file__).parent;Q=R.parent/'coordinator/Q11-uniform-reference';ours={x['name']:x for x in json.loads((R/'constant-reference.json').read_text())};rows=json.loads((Q/'all-panels.json').read_text());old=json.loads((R.parent/'review-54/inputs.json').read_text());new=json.loads((R/'inputs.json').read_text());err=0.
for r in rows:
 a=ours[r['name']];f,b=a['directions'];assert f['events']==r['forward_events'] and b['events']==r['reverse_events'];assert r['q09_sha256']==old[r['name']+'.json.gz']['sha256'] and r['q10_sha256']==new['reverse/'+r['name']+'.json.gz']['sha256']
 expected=[f['destination_minus_uniform'],f['reciprocal_minus_uniform'],b['destination_minus_uniform'],b['reciprocal_minus_uniform'],a['combined_destination_minus_uniform'],a['combined_reciprocal_minus_uniform']];actual=r['forward_vs_uniform']+r['reverse_vs_uniform']+r['combined_vs_uniform'];err=max(err,max(abs(x-y) for x,y in zip(expected,actual)));assert err<1e-10
assert len(rows)==600 and json.loads((Q/'summary.json').read_text())==[r for r in rows if '-null' not in r['name']]
(R/'q11-result.json').write_text(json.dumps(dict(status='PASS',panels=600,max_difference=err,source_hashes_verified=1200),indent=2));print(err)
