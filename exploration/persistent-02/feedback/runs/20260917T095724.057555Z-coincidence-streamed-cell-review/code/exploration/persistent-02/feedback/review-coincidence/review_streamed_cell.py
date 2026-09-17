import json,gzip,pathlib,hashlib,collections
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];A=R/'exploration/persistent-02/section/coincidence';IP=A/'inputs.json';data=json.loads(IP.read_text());path=A/'control07-cells/cell00.json.gz'
with gzip.open(path,'rt') as f:d=json.load(f)
assert d['pins']==dict(index=7,input_sha256=hashlib.sha256(IP.read_bytes()).hexdigest(),core_sha256=hashlib.sha256((A/'core.py').read_bytes()).hexdigest());s=data['controls'][7];cell=data['grid'][s['family']][0];row=d['row'];assert row['cell_id']==cell['id'];checked=0
for group in row['full']+row['prefix']:
 result=group['result'];m={x['mask']:x for x in result['rows']};assert all(x in m for x in result['best_masks'])
 for state in result['future_states']:
  for mask in state['masks']:
   x=m[mask];assert x['position']==state['position'] and x['counts']==state['counts'] and x['score']==result['maximum']
 # Every row's integer objective and final histogram independently checked.
 for x in result['rows']:
  counts=collections.Counter(x['plain']);assert x['counts']==[counts[i] for i in range(29)];assert x['score']==sum(n*(n-1) for n in counts.values());checked+=1
for co in row['continuations']:
 if co.get('feasible') and co['tail'] is not None:
  before=co['initial_counts'];pr=row['prefix'][-1]['result'];pm={x['mask']:x for x in pr['rows']}
  assert all(pm[m]['counts']==before and pm[m]['position']==co['initial_position'] for m in co['prefix_masks'])
  for x in co['tail']['rows']:
   counts=collections.Counter(x['plain']);assert x['counts']==[before[i]+counts[i] for i in range(29)];assert x['score']==sum(n*(n-1)+2*before[i]*n for i,n in counts.items());checked+=1
(O/'streamed-cell-review.json').write_text(json.dumps(dict(status='PASS',control=7,cell=0,stored_rows_checked=checked,file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),continuation_pointer_groups=len(row['continuations'])),indent=2)+'\n');print('PASS',checked,'rows and every tie/prefix continuation pointer')
