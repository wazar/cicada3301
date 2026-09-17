from pathlib import Path
import json
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/decoder/reset-feedback';rows=[json.loads(p.read_text()) for p in (D/'actual').glob('*.json')];s=json.loads((D/'summary.json').read_text());assert len(rows)==320
for group in s['results']:
 results=[]
 for panel in range(20):
  rs=[r for r in rows if r['model']==group['model'] and r['mode']==group['mode'] and r['panel']==panel];assert sorted(r['k'] for r in rs)==[5,6,7,8];r=min(rs,key=lambda x:(-x['maximum_normalized'],x['k'],x['alternatives'][0]['offset']));a=r['alternatives'][0];p=group['panels'][panel]
  assert p['selected_k']==r['k'] and p['seed']==a['seed'] and p['plaintext']==a['plaintext'] and p['fit']==a['fit_score'] and p['continuation']==a['continuation_score'];results.append((a['fit_score'],max(q['upper_normalized'] for q in rs),a['continuation_score']))
 fit,upper,cont=results[0];assert group['actual_fit_rank_lower']==1+sum(r[0]>upper+1e-12 for r in results[1:]);assert group['actual_fit_rank_upper']==1+sum(r[1]>=fit-1e-12 for r in results[1:]);assert group['actual_fit_rank_count_ge']==1+sum(r[0]>=fit-1e-12 for r in results[1:])
 if group['mode']=='prefix':assert group['actual_continuation_rank_count_ge']==1+sum(r[2]>=cont-1e-12 for r in results[1:])
out=dict(passed=True,cells=320,selected_panels=80,all_certified=all(r['certified_within_1e_10'] for r in rows),selection_uses_only_fit=True);(Path(__file__).parent/'reset-summary-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
