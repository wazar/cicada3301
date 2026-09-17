from pathlib import Path
import json,gzip,hashlib,collections
import numpy as np
R=Path(__file__).parent; B=R.parent/'coordinator'; old=B/'Q05-latin'; new=B/'Q05-latin-clean'
j=lambda p:json.load(gzip.open(p,'rt'))
m=json.loads((new/'model.json').read_text()); a=j(old/'train-maps.json.gz'); b=j(new/'train-maps.json.gz'); expected=np.load(R/'independent-clean-expected.npz')['logp']; actual=np.load(new/'model.npz')['logp']; previous=np.load(old/'model.npz')['logp']
assert b['words']==a['words'][:20484] and len(b['words'])==20484 and b['body']==[1116,150887]
assert j(old/'held-controls.json.gz')==j(new/'held-controls.json.gz')
C=[collections.Counter() for _ in range(3)]; history=[29,29]
for w in b['words']:
 for v in w['runes']+[29]:
  C[0][v,]+=1;C[1][history[-1],v]+=1;C[2][history[-2],history[-1],v]+=1;history.append(v)
saved=j(new/'counts.json.gz')
for k in range(3):assert saved[k]==[{'key':list(t),'count':n} for t,n in sorted(C[k].items())]
assert np.array_equal(actual,expected)
for name,h in m['hashes'].items(): assert hashlib.sha256((new/name).read_bytes()).hexdigest()==h
snap=R/'clean-snapshots';snap.mkdir(exist_ok=True); hashes={}
for p in new.iterdir():
 if p.is_file():
  z=p.read_bytes();hashes[p.name]={'sha256':hashlib.sha256(z).hexdigest(),'bytes':len(z)}
  if p.suffix not in ['.gz','.npz']:(snap/p.name).write_bytes(z)
(R/'clean-inputs.json').write_text(json.dumps(hashes,indent=2))
diff=actual-previous;ix=tuple(map(int,np.unravel_index(np.argmax(abs(diff)),diff.shape)));oldC=j(old/'counts.json.gz');oldtri={tuple(t['key']):t['count'] for t in oldC[2]};canon=['F','U','TH','O','R','C','G','W','H','N','I','J','EO','P','X','S','T','B','E','M','L','NG','OE','D','A','AE','Y','IA','EA','BOUNDARY']
out={'status':'PASS','probabilities':27000,'exact_array_equality':True,'all_counts_equal':True,'unchanged_held_objects':True,'max_delta_cell':ix,'max_delta_labels':[canon[i] for i in ix],'old_logp':float(previous[ix]),'clean_logp':float(actual[ix]),'delta':float(diff[ix]),'old_trigram_count':oldtri.get(ix,0),'clean_trigram_count':C[2][ix],'old_unigram_count':next(x['count'] for x in oldC[0] if x['key']==[ix[-1]]),'clean_unigram_count':C[0][ix[-1],],'normalization_error':float(abs(np.exp(actual).sum(2)-1).max()),'changed_cells':int(np.count_nonzero(diff))}
(R/'clean-result.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
