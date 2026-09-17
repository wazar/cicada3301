import json,gzip
from pathlib import Path
D=Path(__file__).parent;O=Path('exploration/persistent-01/worker-p/P20');rows=[]
for i in range(2):
 f=json.load(gzip.open(O/f'actual-page-{i}.json.gz','rt'));gap=f['witness'];c=f['pages'][0]['indices'];t=''.join('g' if gap[v] else '.' for v in c);assert 'ggg' not in t;assert all(len(x)<=5 for x in t.split('g'));rows.append({'page':i,'old_P20_gap_map':gap,'extended_trit_map':[2 if x else 0 for x in gap],'trits':t,'old_status':f['status']})
checks=[]
for path in sorted(D.glob('*.json.gz')):
 if path.name=='tiny-exhaustive.json.gz':continue
 r=json.load(gzip.open(path,'rt'))
 if r['status']=='SAT':
  gap=[int(x==2) for x in r['map']];t=''.join('g' if gap[v] else '.' for v in r['cipher']);assert 'ggg' not in t and all(len(x)<=5 for x in t.split('g'));checks.append({'name':path.name,'nongap_to_all_dot_extension_valid':True,'used_trit_classes':sorted(set(r['map'][v] for v in r['cipher']))})
(D/'equivalence-witnesses.json').write_text(json.dumps({'P20_witness_extensions':rows,'all_SAT_extensions':checks,'lemma':'Full fixed Morse grammar feasibility iff no-three-gaps/no-six-marks feasibility when dot/dash classes need not both be nonempty; .^1..5 are all codewords.'},indent=2));print('original_extensions',len(rows),'all_sat_extensions',len(checks))
