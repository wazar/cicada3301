from pathlib import Path
import gzip,json
R=Path(__file__).parent;P=R.parent/'worker-p';counts=[0,0]
for f in sorted((P/'P25').glob('packet-*.json.gz')):
 a=json.load(gzip.open(f,'rt'));b=json.load(gzip.open(P/'P25-clean'/f.name,'rt'))
 for x,y in zip(a['cells'],b['cells']):
  ids=lambda z:{(tuple(t['plain']),tuple(t['literal_positions'])) for t in z['alternatives']}
  counts[0]+=ids(x)!=ids(y);counts[1]+=1
(R/'set-comparison.json').write_text(json.dumps(dict(unordered_pathsets_changed=counts[0],cells=counts[1]),indent=2));print(counts)
