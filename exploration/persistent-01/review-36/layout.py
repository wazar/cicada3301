from pathlib import Path
import json
R=Path(__file__).parent;B=R.parent;P=B/'worker-p/P22';D=sorted(json.loads((B/'worker-f/F06-maps.json').read_text()),key=lambda p:p['page']);z=json.loads((P/'index-layout.json').read_text());assert z['decoded_prefix_sentinel']==255 and z['all_range_ends_exclusive'];offset=0;count=0
for p,row in zip(D,z['pages']):
 n=len(p['indices']);assert row['page']==p['page'] and row['flat_offset']==offset and row['length']==n
 for lag,m in enumerate(row['lags'],1):assert m==dict(lag=lag,unresolved_cipher_prefix=[offset,offset+lag],decoded_suffix=[offset+lag,offset+n],feedback_positions=[offset,offset+n-lag]);count+=1
 offset+=n
for plain in range(29):
 for feedback in range(29):assert ((plain+feedback)%29-feedback)%29==plain
(R/'layout-check.json').write_text(json.dumps({'status':'PASS','lag_page_maps':count,'scalar_encoder_inverse_cases':841,'total_cipher_runes':offset},indent=2));print(count)
