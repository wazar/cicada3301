import os
for k in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,gzip,hashlib,itertools,numpy as np
O=Path('exploration/persistent-01/review-71');B=O.parent;D=B/'worker-s/S21';S=B/'worker-s/S20';N=2355
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(p):return json.loads(p.read_text())
def gz(p):return json.loads(gzip.decompress(p.read_bytes()))
files=[f for f in D.iterdir() if f.is_file()]+[B/'worker-s/S21-CARD.md',B/'worker-s/S21-REPORT.md'];snap={str(p):sha(p) for p in files};(O/'inputs.json').write_text(json.dumps(snap,indent=2))
for p in js(D/'inputs.json'):assert sha(Path(p['path']))==p['sha256']
# Pin the complete source object to independent review70's source snapshot.
old=js(B/'review-70/inputs.json');assert old[str(S/'sources.json.gz')]==sha(S/'sources.json.gz')
sources=gz(S/'sources.json.gz');rows=[];total=0;entries=0
for s in sources:
 a=np.asarray(s['runes'],dtype=np.int16);start=np.arange(len(a)-N+1);end=start+N;c=np.empty((len(start),29),dtype=np.int64)
 for rune in range(29):
  where=np.flatnonzero(a==rune);c[:,rune]=np.searchsorted(where,end,side='left')-np.searchsorted(where,start,side='left')
 z=np.load(D/(s['name']+'.npz'));meta=js(D/(s['name']+'.json'));assert np.array_equal(c,z['counts']) and np.all(c.sum(axis=1)==N)
 error=np.partition(c,14,axis=1)[:,:15].sum(axis=1);support=np.count_nonzero(c,axis=1);assert np.array_equal(error,z['minimum_errors']) and np.array_equal(support,z['support']);assert support.tolist()==gz(S/(s['name']+'-windows.json.gz'))['all_support_counts']
 least=int(error.min());offsets=np.flatnonzero(error==least).tolist();spans=[[s['rune_char_spans'][i][0],s['rune_char_spans'][i+N-1][1]] for i in offsets]
 assert least==meta['minimum_errors'] and int(error.max())==meta['maximum_lower_bound'] and least/N==meta['minimum_error_fraction'];assert offsets==meta['achieving_offsets'] and spans==meta['achieving_raw_spans'] and c[offsets].tolist()==meta['minimum_counts'] and support[offsets].tolist()==meta['achieving_supports'] and len(start)==meta['windows']
 total+=len(start);entries+=c.size;rows.append(dict(name=s['name'],windows=len(start),minimum=least,fraction=least/N,maximum=int(error.max()),achieving=len(offsets),supports=sorted(set(support[offsets].tolist()))))
controls=gz(D/'controls.json.gz');idx=0
for counts in itertools.product(range(4),repeat=4):
 for cap in [1,2,3]:
  c=controls[idx];idx+=1;assert list(counts)==c['counts'] and cap==c['cap'];allowed=[tuple(i for i in range(4) if mask&(1<<i)) for mask in range(16) if mask.bit_count()<=cap];best=max(sum(counts[i] for i in group) for group in allowed);assert best==c['best_mass'];retained=c['retained'];assert retained==sorted(range(4),key=lambda i:(-counts[i],i))[:cap];seq=[i for i,n in enumerate(counts) for _ in range(n)];output=[x if x in retained else retained[0] for x in seq];assert len(set(output))<=cap and sum(x!=y for x,y in zip(seq,output))==sum(counts)-best==c['minimum_errors']
assert idx==768 and total==224473 and entries==6509717
r=js(D/'result.json');assert r['window_length']==2355 and r['type_cap']==14 and r['controls']==768 and r['total_windows']==total
for a,b in zip(rows,r['source_results']):assert a['minimum']==b['minimum_errors'] and a['maximum']==b['maximum_lower_bound'] and a['achieving']==b['achieving_windows'] and a['supports']==b['achieving_support_set'] and a['fraction']==b['minimum_error_fraction']
assert all(sha(Path(p))==h for p,h in snap.items())
out=dict(pass_all=True,windows=total,counts=entries,tiny_controls=idx,sources=rows,overall_minimum=min(r['minimum'] for r in rows),limit='Relaxed14type Hamming mismatch lower bound, not an attainable substitution alignment or approximate decoded plaintext; sourceprovenance inherited and hash-pinned to review70.')
(O/'result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
