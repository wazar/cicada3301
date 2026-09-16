import pathlib,json,gzip,hashlib,math,collections
R=pathlib.Path('exploration/persistent-01');O=R/'review-01';out=json.loads((O/'checked-findings.json').read_text())
def read(p):
 b=p.read_bytes();out['inputs'][str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)};return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
for owner,names in [('worker-e',[f'experiment{i:02d}.py' for i in range(1,7)]),('worker-c',[f'ob_c{i}.py' for i in range(1,5)]+['ob_c4_verify.py','p03_frozen.py'])]:
 for name in names:
  p=R/owner/name;b=p.read_bytes();out['inputs'][str(p)]={'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
S=read(R/'worker-e/experiment01-result.json');m=[S['sources'][0]['values'][j:j+5] for j in range(0,25,5)]
for id in [2,4]:
 e=read(R/f'worker-e/experiment{id:02d}-evidence.json.gz');p=e['control_plain'];p=[p[i:i+5] for i in range(0,len(p),5)] if id==2 else p
 assert [[sum(a*b for a,b in zip(row,block))%29 for row in m] for block in p]==e['control_cipher']
 out['checks'].append(dict(id=f'E{id:02d}-control-forward',status='PASS',blocks=len(p)))
# Count real magic windows independently.
cells=read(R/'worker-e/experiment01-discovery-cells.json');hits=0
for p in cells:
 a=[c['value'] for c in p['cells']]
 for i in range(len(a)-24):
  v=a[i:i+25];sums=[sum(v[j:j+5]) for j in range(0,25,5)]+[sum(v[j::5]) for j in range(5)]+[sum(v[::6]),sum(v[4:21:4])]
  hits+=len(set(sums))==1 and len(set(v))>1
assert hits==0;out['checks'].append(dict(id='E01-full-real-window-check',status='PASS',hits=hits))
out['limitations']=[
 {'id':'L1','severity':'scope','finding':'E02/E04/E06 permutation nulls destroy anti-repeat transitions; their tails are conditional on exchangeability, not general cipher probabilities.'},
 {'id':'L2','severity':'scope','finding':'C1 minimum p=.0398 is one of two endpoints after adaptive model exploration, not globally calibrated significance.'},
 {'id':'L3','severity':'retention','finding':'C3 held control hnull is computed but not persisted; held p not independently re-counted from raw evidence.'},
 {'id':'L4','severity':'wording','finding':'C4 min_error_fraction_any_partition is a same-partition transition lower bound, not minimum rune edit fraction.'},
 {'id':'L5','severity':'scope','finding':'Controls prove sensitivity to their particular biased/Markov or solved-reference input instances; no universal or population power claim.'},
 {'id':'L6','severity':'shared-input','finding':'E and C retain shared transcription ancestry; review reconstructs arithmetic from saved discovery maps, not independent image transcription.'}]
(O/'checked-findings.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'supplement':'PASS','added_checks':3,'hashed_sources':13,'limitations':out['limitations']},indent=2))
