import json,pathlib,hashlib
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];IP=R/'exploration/persistent-02/section/coincidence/inputs.json';d=json.loads(IP.read_text());sp=R/d['source'];source=json.loads(sp.read_text());assert hashlib.sha256(sp.read_bytes()).hexdigest()==d['sha256'];assert d['grid']==source['grid'] and d['controls']==source['controls'];rows=[]
for x in d['controls']:
 cell=next(c for c in d['grid'][x['family']] if c['id']==x['plant']['id']);assert cell==x['plant'];key=cell['key'];at=0;cipher=[];resets=set(x['reset_before']);literal=set(x['truth_literal_positions']);starts=sorted({0,len(x['truth'])}|resets);maxseg=max(b-a for a,b in zip(starts,starts[1:]))
 for i,p in enumerate(x['truth']):
  if i in resets:at=0
  if i in literal:assert p==0;cipher.append(0)
  else:cipher.append((p-cell['sign']*key[at%len(key)])%29);at+=1
 assert cipher==x['cipher']
 if x['family']=='finite':assert all(len(c['key'])>=maxseg for c in d['grid']['finite'])
 rows.append(dict(id=x['id'],length=len(cipher),max_segment=maxseg,key_length=len(key),cut=x['spans'][0][1],finite_no_exhaustion_guaranteed=x['family']=='finite'))
(O/'input-review.json').write_text(json.dumps(dict(status='PASS',input_sha256=hashlib.sha256(IP.read_bytes()).hexdigest(),grid_sizes={k:len(v) for k,v in d['grid'].items()},controls=rows),indent=2)+'\n');print('PASS',len(rows),'source/grid/known path; finite streams exceed every segment')
