from pathlib import Path
import json,gzip,hashlib
O=Path('exploration/persistent-01/worker-p/P30');B=O.parents[1]
T=[r['transliteration'] for r in json.loads(Path('KNOWLEDGE.json').read_text())['gematria_primus']['table']]
def load(p):return json.loads(gzip.decompress(p.read_bytes()))
controls=[];actual=[];texts=[];seconds=0;paths=0;expansions=0
for i in range(7):
 p=json.loads((O/f'packet-{i}.json').read_text());r=load(O/f'packet-{i}-main.json.gz')
 if i<4:
  c={k:v for k,v in r['control'].items() if k not in ['truth','truth_literal']};c.update(name=p['name'],length=len(p['cipher']),doublets=sum(a==b for a,b in zip(p['cipher'],p['cipher'][1:])));controls.append(c)
 else:
  actual.append(json.loads((O/f'packet-{i}-summary.json').read_text()))
  for a in r['global16']:
   strings=[];word='';ends=set(r['ends'])
   for k,v in enumerate(a['plain']):
    word+=T[v]
    if k in ends:strings.append(word);word=''
   assert word==''
   texts.append(dict(packet=i,id=a['id'],score=a['score'],plain=a['plain'],literal_positions=a['literal_positions'],text=' '.join(strings),aliases=a['aliases']))
for f in O.glob('packet-*.json.gz'):
 r=load(f);seconds+=r['seconds'];paths+=sum(len(c['alternatives']) for c in r['cells']);expansions+=sum(c['diagnostics']['expanded'] for c in r['cells'])
s=dict(controls=controls,actual=actual,searches=len(list(O.glob('packet-*.json.gz'))),cells=162*len(list(O.glob('packet-*.json.gz'))),paths=paths,expansions=expansions,search_seconds=seconds,compressed_bytes=sum(f.stat().st_size for f in O.glob('packet-*.json.gz')))
(O/'summary.json').write_text(json.dumps(s,indent=2));(O/'full-actual-alternatives.json').write_text(json.dumps(texts,indent=2));print(json.dumps(s))
