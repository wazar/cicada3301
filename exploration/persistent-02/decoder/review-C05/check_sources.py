import json,hashlib,sys
from enumerate import ROOT,O
sys.path.insert(0,str(ROOT/'exploration/persistent-01/worker-c'));from p03_frozen import parse
cases=json.loads((ROOT/'exploration/persistent-02/feedback/C05/plants.json').read_text())['cases'];fresh=json.loads((ROOT/'exploration/persistent-02/decoder/fresh-controls.json').read_text());rows=[]
for c in cases:
 s=c['source']
 if 'path' in s:
  f=ROOT/s['path'];assert hashlib.sha256(f.read_bytes()).hexdigest()==s['sha256'];p,ends=parse(''.join(f.read_text().splitlines()));assert p==c['truth'] and sorted(ends)==c['ends'];kind='complete held source'
 else:
  f=ROOT/s['packet'];assert hashlib.sha256(f.read_bytes()).hexdigest()==s['sha256'];x=next(x for x in fresh['cases'] if x['source']==s['source_id'] and x['source_rune_span']==s['rune_span']);assert x['truth']==c['truth'] and x['ends']==c['ends'];kind='frozen B fresh source'
 rows.append(dict(id=c['id'],k=c['k'],kind=kind,passed=True))
(O/'source-check.json').write_text(json.dumps(dict(passed=True,cases=rows,scope='Local bytes/hashes and every plant rune/end match checked; no remote authenticity reassessment.'),indent=2)+'\n');print(json.dumps(dict(passed=True,cases=len(rows))))
