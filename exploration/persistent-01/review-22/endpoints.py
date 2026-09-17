from pathlib import Path
import json,gzip,hashlib
R=Path(__file__).parent;P=R.parent/'worker-r';D=sorted(json.loads((P/'R01-input.json').read_text()),key=lambda p:p['page']);F=json.loads((R.parent/'worker-f/F06-maps.json').read_text())
for d in D:
 m=next(x for x in F if x['page']==d['page']);assert d['indices']==m['indices'] and d['source_char_positions']==m['source_char_positions']
checks=[]
for file in sorted(P.glob('R03-*-full.jsonl.gz')):
 groups={}
 for line in gzip.open(file,'rt'):
  row=json.loads(line);groups.setdefault(row['tag'],[]).append(row)
 for tag,rows in groups.items():
  if 'real' in file.name:base=430000;n=199
  elif 'pilot' in file.name:base=470000+1000*int(tag);n=19
  elif 'stress' in file.name:base=4841000+1000*int(tag);n=19
  else:base=450000+1000*int(tag);n=49
  assert len(rows)==n+1 and [r['seed'] for r in rows[1:]]==list(range(base,base+n));checks.append({'file':file.name,'tag':tag,'base':base,'nulls':n})
real=json.loads((P/'R03-real-results.json').read_text())['panels'][0];pairs={tuple(p) for p in real['pairs']};witness=[]
for d in D[1::2]:
 for i,(a,b) in enumerate(zip(d['indices'],d['indices'][1:])):
  if tuple(sorted((a,b))) in pairs:witness.append({'page':d['page'],'rune_indices':[i,i+1],'source_char_positions':d['source_char_positions'][i:i+2],'values':[a,b]})
assert witness==json.loads((P/'R03-real-witnesses.json').read_text()) and len(witness)==real['held_count']
(R/'endpoints.json').write_text(json.dumps({'status':'PASS','seed_checks':checks,'real_held_edge_witnesses':witness},indent=2));print('PASS seeds',len(checks),'held edge witnesses',len(witness))
