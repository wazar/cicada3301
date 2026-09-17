from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[4];D=R/'exploration/persistent-02/decoder/reset-feedback';H=D/'histogram';count=0;reused=0
for case in range(5):
 rows=[json.loads(p.read_text()) for p in (H/f'cells/case{case}').glob('*.json')];s=json.loads((H/f'summary-case{case}.json').read_text());assert len(rows)==320;count+=len(rows)
 for r in rows:
  if 'reused_original_path' in r:
   old=R/r['reused_original_path'];assert hashlib.sha256(old.read_bytes()).hexdigest()==r['reused_original_sha256'];o=json.loads(old.read_text());assert all(r[k]==v for k,v in o.items());assert case==0 and r['panel']==0;reused+=1
 for g in s['results']:
  out=[]
  for panel in range(20):
   rr=[r for r in rows if r['model']==g['model'] and r['mode']==g['mode'] and r['panel']==panel];r=min(rr,key=lambda x:(-x['maximum_normalized'],x['k'],x['alternatives'][0]['offset']));a=r['alternatives'][0];p=g['panels'][panel];assert p['seed']==a['seed'] and p['plaintext']==a['plaintext'] and p['selected_k']==r['k'];out.append((a['fit_score'],max(v['upper_normalized'] for v in rr),a['continuation_score']))
  f,u,c=out[0];assert g['fit_rank_lower']==1+sum(v[0]>u+1e-12 for v in out[1:]);assert g['fit_rank_upper']==1+sum(v[1]>=f-1e-12 for v in out[1:]);assert g['fit_rank_count_ge']==1+sum(v[0]>=f-1e-12 for v in out[1:])
  if g['mode']=='prefix':assert g['continuation_rank_count_ge']==1+sum(v[2]>=c-1e-12 for v in out[1:])
assert count==1600 and reused==16
out=dict(passed=True,cells=count,original_cells_exactly_reused=reused,new_cells=count-reused,selection_panels=400);(Path(__file__).parent/'histogram-summary-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
