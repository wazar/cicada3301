import json,gzip,pathlib,collections,sys,math
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];A=R/'exploration/persistent-02/section/coincidence';results=[]
for ix in map(int,sys.argv[1:]):
 with gzip.open(A/f'control{ix:02}-all.json.gz','rt') as f:d=json.load(f)
 summary=json.loads((A/f'control{ix:02}-summary.json').read_text());inputs=json.loads((A/'inputs.json').read_text());s=d['control'];assert s==inputs['controls'][ix];cells={c['id']:c for c in inputs['grid'][s['family']]};checked=0
 for row in d['rows']:
  cell=cells[row['cell_id']];key=cell['key']
  for seg in row['full']+row['prefix']:
   a,b=seg['start'],seg['stop'];cipher=s['cipher'][a:b]
   for item in seg['result']['rows']:
    pos=0;plain=[];literal=set(item['literal_positions'])
    for i,c in enumerate(cipher):
     if i in literal:assert c==0;p=0
     else:p=(c+cell['sign']*key[pos%len(key)])%29;pos+=1
     plain.append(p)
    assert item['plain']==plain;score=sum(x==y for i,x in enumerate(plain) for j,y in enumerate(plain) if i!=j);assert score==item['score'];checked+=1
   assert seg['result']['maximum']==max(r['score'] for r in seg['result']['rows'])
  assert row['full_maximum']==sum(g['result']['maximum'] for g in row['full']);assert row['prefix_maximum']==sum(g['result']['maximum'] for g in row['prefix'])
  assert row['prefix_tie_product']==math.prod(len(g['result']['best_masks']) for g in row['prefix']);assert row['full_tie_product']==math.prod(len(g['result']['best_masks']) for g in row['full'])
 true=next(r for r in d['rows'] if r['cell_id']==s['plant']['id'])
 for name in ['full','prefix']:
  freq={0:1};truth=0
  for seg in true[name]:
   a,b=seg['start'],seg['stop'];p=s['truth'][a:b];truth+=sum(x==y for i,x in enumerate(p) for j,y in enumerate(p) if i!=j);new=collections.defaultdict(int)
   for row in seg['result']['rows']:
    for score,count in freq.items():new[score+row['score']]+=count
   freq=dict(new)
  m=summary['known_key_'+name];assert m['truth_total']==truth and m['strict_rank']==1+sum(count for score,count in freq.items() if score>truth) and m['score_ties']==freq[truth] and m['legal_complete_masks']==sum(freq.values())
 fm=max(r['full_maximum'] for r in d['rows']);pm=max(r['prefix_maximum'] for r in d['rows']);pre=[r for r in d['rows'] if r['prefix_maximum']==pm]
 assert summary['full_best_cells']==[r['cell_id'] for r in d['rows'] if r['full_maximum']==fm];assert summary['prefix_best_cells']==[r['cell_id'] for r in pre];assert summary['prefix_tied_paths']==sum(r['prefix_tie_product'] for r in pre);assert summary['continuation_maximum_over_frozen_set']==max(r['continuation_maximum'] for r in pre)
 results.append(dict(index=ix,checked_segment_rows=checked,grid_cells=len(d['rows']),truth_full_rank=summary['known_key_full']['strict_rank'],truth_in_best=summary['truth_in_globally_best_full']))
(O/'output-review.json').write_text(json.dumps(dict(status='PASS',cases=results),indent=2)+'\n');print(json.dumps(results))
