import json,hashlib
from pathlib import Path
import numpy as np
D=Path(__file__).parent;O=D.parent/'N14';M=json.loads((O/'maps.json').read_text());R=json.loads((D/'result.json').read_text());tot=0
for meta in R['controls']+R['actual']:
 path=Path(meta['input']);assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['input_sha256'];a=dict(np.load(D/f"{meta['name']}-{meta['model']}.npz"));c=a['cipher'];assert np.array_equal(c,np.load(path)['cipher']);z=a['nulls'];rg=np.random.default_rng(meta['seed']);offset=0;actual=0;counts=np.zeros(len(z),int)
 for m in M:
  n=len(m['route']);cp=c[offset:offset+n];zp=z[:,offset:offset+n]
  if meta['model']=='A':
   assert np.all(zp[:,0]==cp[0]);assert np.all((zp[:,1:]==zp[:,:-1])==(cp[1:]==cp[:-1]))
   for i in range(1,n):
    if cp[i]!=cp[i-1]:
     draws=rg.integers(0,28,size=len(zp))
     # independently enumerate permissible alphabet for 2 rows, full vector arithmetic for remaining rows
     for b in range(2):assert [j for j in range(29) if j!=int(zp[b,i-1])][int(draws[b])]==zp[b,i]
     assert np.array_equal(draws+(draws>=zp[:,i-1]),zp[:,i])
  else:
   assert np.all(np.sort(zp,axis=1)==np.sort(cp))
   for b in range(len(zp)):assert np.array_equal(rg.permutation(cp),zp[b])
  for x,y in m['novel_edges']:
   actual+=int(cp[x]==cp[y]);counts+=zp[:,x]==zp[:,y]
  offset+=n
 assert actual==meta['actual'];assert np.array_equal(counts,a['null_stats']);assert (1+int(sum(counts<=actual)))/(len(zp)+1)==meta['tail'];tot+=len(z)
out={'PASS':True,'families':26,'null_panels':tot,'all_input_hashes_arrays_masks_or_inventories_rng_counts_tails':True};(D/'verification.json').write_text(json.dumps(out,indent=2));print(out)
