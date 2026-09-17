import pathlib,json,hashlib,numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
manifest=json.loads((R/'exploration/persistent-02/coordinator/C01-null-array-manifest.json').read_text());rec=next(x for x in manifest['records'] if x['name']=='actual1-null00');local=R/rec['local_file'];before=sha(local.read_bytes());assert before==rec['local_npz_sha256']
with np.load(local) as old,np.load(O/'reconstructed-actual1-null00.npz') as new:
 keys=old.files
 for k in keys:assert old[k].dtype==new[k].dtype and old[k].shape==new[k].shape and old[k].tobytes()==new[k].tobytes()
 for k in rec['score_arrays']:assert sha(new[k].tobytes())==rec['score_arrays'][k]['sha256_raw_C']
assert before==sha(local.read_bytes())
(O/'reconstruction-checks.json').write_text(json.dumps(dict(passed=True,name=rec['name'],local_npz_sha256=before,original_arrays_byte_identical=keys,reconstructed_score_arrays=list(rec['score_arrays']),scope='Raw arrays lossless; zip container identity neither required nor claimed'),indent=2)+'\n')
print('reconstruction PASS:',len(keys),'original arrays byte-identical and3score-array hashes match')
