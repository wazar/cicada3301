import json,pathlib,gzip,hashlib
import numpy as np
D=pathlib.Path(__file__).resolve().parent/'p11';q=json.loads((D/'queue.json').read_text());key=np.load(D/'phi.npz')['mod29'];perpage=[]
for pid in sorted(set(x['page'] for x in q)):
 cells=[(i,x) for i,x in enumerate(q) if x['page']==pid]
 with gzip.open(D/'search'/f'cell-{cells[0][0]:05}.json.gz','rt') as f:r=json.load(f)
 n=len(r['output']['real']['cipher']);groups={}
 for i,c in cells:
  k=bytes(((c['sign']*key[c['offset']:c['offset']+n])%29).tolist());groups.setdefault(hashlib.sha256(k).hexdigest(),[]).append(i)
 perpage.append(dict(page=pid,length=n,cells=len(cells),unique_signed_key_prefixes=len(groups),alias_groups=[v for v in groups.values() if len(v)>1]))
controlcounts={}
for p in sorted((D/'controls').glob('*/*.json.gz')):
 with gzip.open(p,'rt') as f:r=json.load(f)
 name=p.parent.name;counts=controlcounts.setdefault(name,dict(model_key_cells=0,retained_paths=0,reencrypted_paths=0));counts['model_key_cells']+=1;counts['retained_paths']+=len(r['alternatives']);counts['reencrypted_paths']+=sum(a['reencryption'] for a in r['alternatives'])
m=json.loads((D/'publication/raw-retention-manifest.json').read_text());out=dict(real_key_page_cells=11520,null_key_page_cells=11520,model_beam_calls=46080,actual_retained_paths=m['retained_alternative_counts'],actual_retained_paths_total=sum(sum(x.values()) for x in m['retained_alternative_counts'].values()),controls=controlcounts,perpage=perpage,aliases=sum(len(x['alias_groups']) for x in perpage),alias_definition='Identical signed mod29 candidate-key prefix of full ciphertext length within same page. Does not count identical shorter prefixes or duplicate plaintext paths as separate construction equivalence tests.')
(D/'publication/coverage-counts.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k!='perpage'}))
