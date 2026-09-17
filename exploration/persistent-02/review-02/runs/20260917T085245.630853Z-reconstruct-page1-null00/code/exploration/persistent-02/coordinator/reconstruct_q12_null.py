"""Publishable lossless recipe for redundant Q12 null intermediate arrays.
Original local npz files are never changed. Reconstructed array bytes are checked
against recorded hashes; zip-container bytes/timestamps need not be identical.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
import numpy as np
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent;D=O.parent/'feedback/C01'
MANIFEST=O/'C01-null-array-manifest.json'
def digest(b):return hashlib.sha256(b).hexdigest()
def source_pins():
 paths=['exploration/persistent-01/coordinator/Q12-sum-autokey/test.py','exploration/persistent-01/worker-c/p03_frozen.py']
 paths += ['audit/parallel-01/reference/sources/solved_'+x+'.txt' for x in ['0_warning','0_wisdom','0_koan_1','0_loss_of_divinity','jpg229']]
 return {p:digest((R/p).read_bytes()) for p in paths}
def manifest():
 assert not MANIFEST.exists()
 records=[]
 for p in sorted(D.glob('actual*-null*.npz')):
  meta=p.with_suffix('.json');info=json.loads(meta.read_text())
  with np.load(p) as a:
   arrays={key:{'shape':list(a[key].shape),'dtype':str(a[key].dtype),'sha256_raw_C':digest(a[key].tobytes(order='C'))} for key in a.files}
  records.append({'name':p.stem,'local_file':str(p.relative_to(R)),'local_npz_sha256':digest(p.read_bytes()),'local_npz_bytes':p.stat().st_size,'metadata_sha256':digest(meta.read_bytes()),'arrays':arrays,'score_arrays':info['reconstructable_score_arrays']})
 assert len(records)==42*19
 out={'source_pins':source_pins(),'numpy_version':np.__version__,'python_version':sys.version,'records':records,'policy':'Original null npz remain unchanged locally. Git publishes metadata/cipher/ends/top outputs and this exact array reconstruction recipe plus hashes, rather than redundant null factor npz. Actual full score npz are published. Container bytes may differ; reconstructed raw array bytes are verified. No search result is silently relabelled.'}
 MANIFEST.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'records':len(records),'local_bytes':sum(r['local_npz_bytes'] for r in records),'manifest':str(MANIFEST.relative_to(R))}))
def reconstruct(name,out):
 assert not out.exists(),'refuse overwrite'
 m=json.loads(MANIFEST.read_text());assert source_pins()==m['source_pins']
 rec=next(r for r in m['records'] if r['name']==name);p=D/(name+'.json');assert digest(p.read_bytes())==rec['metadata_sha256'];info=json.loads(p.read_text())
 src=R/'exploration/persistent-01/coordinator/Q12-sum-autokey/test.py';sp=importlib.util.spec_from_file_location('q12_reconstruct',src);q=importlib.util.module_from_spec(sp);sp.loader.exec_module(q)
 # Only pure arithmetic is called; no q.search, q.guard, original output write.
 arrays={};c=info['cipher'];ends=set(info['ends']);norm=len(c)+len(ends)
 for k in [2,3,4]:
  zero=q.decode(c,[0]*k);W=q.table(zero,ends,k)
  arrays[f'k{k}_zero_plain']=np.array(zero,dtype=np.uint8);arrays[f'k{k}_factors']=W;arrays[f'k{k}_scores']=q.scores(W,k)/norm
 expected=rec['arrays']|rec['score_arrays'];checks={}
 for key,v in arrays.items():
  e=expected[key];actual={'shape':list(v.shape),'dtype':str(v.dtype),'sha256_raw_C':digest(v.tobytes(order='C'))};assert actual==e,(key,actual,e);checks[key]=True
 out.parent.mkdir(parents=True,exist_ok=True);np.savez_compressed(out,**arrays)
 print(json.dumps({'name':name,'array_checks':checks,'output':str(out),'numpy_version':np.__version__}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['manifest','reconstruct']);ap.add_argument('--name');ap.add_argument('--out',type=Path);a=ap.parse_args()
 if a.mode=='manifest':manifest()
 else:
  assert a.name and a.out;reconstruct(a.name,a.out)
