from pathlib import Path
import hashlib,json,tarfile,gzip
import numpy as np
from PIL import Image
B=Path('exploration/persistent-01/worker-s/S15');P=Path('exploration/persistent-01/worker-p/private-P28');src=P/'resurrecting-open-source-projects-outguess-24810e1/src'
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=[]
with tarfile.open(P/'source.tar.gz') as t:
 for m in t.getmembers():
  if not m.isfile() or '/src/' not in m.name or not m.name.endswith(('.c','.h')):continue
  rel=m.name.split('/src/',1)[1];p=src/rel;q=B/'source'/rel
  raw=t.extractfile(m).read();assert p.read_bytes()==raw,rel
  rows.append({'path':rel,'upstream_sha256':sha(raw),'copy_sha256':sha(q.read_bytes()),'instrumented':raw!=q.read_bytes()})
assert sorted(r['path'] for r in rows if r['instrumented'])==['jpeg-6b-steg/jdcoefct.c','outguess.c']
manifest={'upstream_archive_sha256':sha((P/'source.tar.gz').read_bytes()),'original_binary_sha256':sha((src/'outguess').read_bytes()),'source_files':rows,'configs':[{'path':str(p),'sha256':sha(p.read_bytes())} for p in [src/'config.h',src/'jpeg-6b-steg/jconfig.h']]}
(B/'source-provenance.json').write_text(json.dumps(manifest,indent=2))
summary=[]
for name in ['historical','plant0','actual0','actual26']:
 r=json.loads((B/(name+'.json')).read_text());m=np.frombuffer(gzip.decompress((B/(name+'.map.bin.gz')).read_bytes()),dtype=np.int32).reshape(-1,9);sel=np.frombuffer(gzip.decompress((B/(name+'.selected.bin.gz')).read_bytes()),dtype=np.int32).reshape(-1,2)
 record={k:r[k] for k in ['name','usable_coefficients','selected_bits','payload_bytes','initial_body_ones_bits','first_nonone_coefficient','checks']};record['spans']={k:{kk:vv for kk,vv in v.items() if kk!='frequency_counts'} for k,v in r['spans'].items()}
 record['prefix_coefficient_values']={}
 for label,a,b in [('header',0,32),('shared1417',32,min(len(sel),32+1417*8))]:
  vals,cnts=np.unique(m[sel[a:b,0],4],return_counts=True);record['prefix_coefficient_values'][label]=dict(zip(map(str,vals.tolist()),cnts.tolist()))
 if name.startswith('actual'):
  row=np.array(r['first_nonone_coefficient']);sx=8*row[7]//row[5];sy=8*row[8]//row[6];x=row[1]*sx;y=row[2]*sy;im=np.asarray(Image.open(r['source']).convert('RGB'));patch=im[y:y+sy,x:x+sx];record['first_nonone_footprint']={'xyxy':[int(x),int(y),int(x+sx),int(y+sy)],'minimum_rgb':int(patch.min()),'maximum_rgb':int(patch.max()),'white_at_frozen_threshold':bool(patch.min()>=250)}
 summary.append(record)
(B/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));print('source provenance files',len(rows))
