import json,pathlib
O=pathlib.Path(__file__).resolve().parent/'C11'
for name in ['p03','complementary']:
 rows=[json.loads(p.read_text()) for p in sorted(O.glob(name+'-plant??.json'))];assert len(rows)==32 and all(r['outcome']=='COMPLETE' for r in rows)
 s=dict(model=name,cases=len(rows),exact=sum(r['selected_rune_errors']==0 for r in rows),errors=[{k:r[k] for k in ['index','id','k','selected_rune_errors','truth_gap','truth_in_retained']} for r in rows if r['selected_rune_errors']],peak_states=max(r['result']['peak_states'] for r in rows),seconds=sum(r['seconds'] for r in rows),peak_rss=max(r['peak_process_rss_bytes'] for r in rows));(O/(name+'-controls-summary.json')).write_text(json.dumps(s,indent=2)+'\n');print(json.dumps(s))
