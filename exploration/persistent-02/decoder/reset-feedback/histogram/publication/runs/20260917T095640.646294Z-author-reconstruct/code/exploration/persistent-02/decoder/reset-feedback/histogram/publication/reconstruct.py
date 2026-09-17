"""Lossless W/B/q recipe; no optimizer imports or local archive mutations."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,sys
import numpy as np
O=Path(__file__).resolve().parent;H=O.parent;D=H.parent;R=D.parents[3];MANIFEST=O/'array-manifest.json';PANELS=R/'exploration/persistent-02/coordinator/histogram-reset/panels.json'
def sha(b):return hashlib.sha256(b).hexdigest()
def filehash(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def pins():
 paths=[Path(__file__),PANELS,H/'pins.json',D/'model.py',D/'model-p03.npz',D/'model-complementary.npz',D/'inputs.json']
 return {str(p.relative_to(R)):filehash(p) for p in paths}
def arraymeta(a):return dict(dtype=str(a.dtype),dtype_str=a.dtype.str,shape=list(a.shape),sha256_raw_C=sha(a.tobytes(order='C')))
def manifest():
 assert not MANIFEST.exists();records=[]
 for p in sorted((H/'cells').glob('case*/*.npz')):
  j=p.with_suffix('.json');meta=json.loads(j.read_text());assert 'reused_original_path' not in meta
  with np.load(p,allow_pickle=False) as z:
   assert set(z.files)=={'W','B','q'};arrays={k:arraymeta(z[k]) for k in sorted(z.files)}
  records.append(dict(name=str(p.relative_to(H/'cells').with_suffix('')),local_file=str(p.relative_to(R)),local_npz_sha256=filehash(p),local_npz_bytes=p.stat().st_size,metadata_file=str(j.relative_to(R)),metadata_sha256=filehash(j),case_index=meta['case_index'],panel=meta['panel'],model=meta['model'],mode=meta['mode'],k=meta['k'],arrays=arrays))
 assert len(records)==1584
 data=dict(records=records,source_pins=pins(),numpy_version=np.__version__,python_version=sys.version,policy='Original local archives unchanged. Published JSON results/alternatives unchanged. Recipe reconstructs every W/B/q raw array byte; NPZ container bytes need not match original ZIP timestamps. Archive hashes identify original local artifacts. Reused original actual sixteen cells have no histogram factor archive and are not counted. No optimization rerun.')
 with MANIFEST.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
 print(json.dumps(dict(records=len(records),local_bytes=sum(r['local_npz_bytes'] for r in records),manifest=str(MANIFEST.relative_to(R)))))
def reconstruct(name,out):
 assert not out.exists(),'refuse overwrite';assert out.suffix=='.npz','explicit .npz output required';m=json.loads(MANIFEST.read_text());assert pins()==m['source_pins'],'source mismatch';rec=next(r for r in m['records'] if r['name']==name);assert filehash(R/rec['metadata_file'])==rec['metadata_sha256'];s=json.loads(PANELS.read_text())['cases'][rec['case_index']];c=s['panels'][rec['panel']];n=len(c) if rec['mode']=='full' else s['prefix_length'];ends=[i for i in s['ends'] if i<n];resets=[i for i in s['reset_before'] if i<n]
 spec=importlib.util.spec_from_file_location('p02_reset_factor_recipe',D/'model.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 with np.load(D/f'model-{rec["model"]}.npz',allow_pickle=False) as z:L=z['L']
 W,B,q,_=module.factors(c[:n],ends,rec['k'],resets,L);arrays={'W':W,'B':B,'q':np.asarray(q,dtype=np.dtype(rec['arrays']['q']['dtype_str']))}
 for key,a in arrays.items():assert arraymeta(a)==rec['arrays'][key],(key,arraymeta(a),rec['arrays'][key])
 out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('xb') as f:np.savez_compressed(f,**arrays)
 print(json.dumps(dict(name=name,array_checks={k:True for k in arrays},output=str(out),output_npz_sha256=filehash(out),original_npz_sha256=rec['local_npz_sha256'],container_match=filehash(out)==rec['local_npz_sha256'])))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['manifest','reconstruct']);ap.add_argument('--name');ap.add_argument('--out',type=Path);a=ap.parse_args()
 if a.mode=='manifest':manifest()
 else:
  assert a.name and a.out;reconstruct(a.name,a.out)
