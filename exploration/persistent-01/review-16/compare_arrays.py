import pathlib,json,hashlib
import numpy as np
R=pathlib.Path(__file__).parent;P=R.parent/'worker-p/P10';prior=json.loads((R/'independent-results.json').read_text());zz=[]
for diagonal in range(15):
 rows=list(range(max(0,diagonal-7),min(7,diagonal)+1))
 if diagonal%2==0:rows.reverse()
 zz.extend(row*8+(diagonal-row) for row in rows)
assert zz[:6]==[0,1,8,16,9,2]
out=[]
for page,z in enumerate(prior):
 path=P/f'actual-{page}-coefficients.npz';a=np.load(path);Y=a['1'].reshape(225,2,150,2,64).transpose(0,2,1,3,4).reshape(33750,4,64);Cb=a['2'].reshape(33750,1,64);Cr=a['3'].reshape(33750,1,64);v=np.concatenate([Y,Cb,Cr],axis=1)[:,:,zz].ravel();sel=v[(v!=0)&(v!=1)];bits=(sel&1).astype(np.uint8);packed=np.packbits(bits,bitorder='big').tobytes();assert len(bits)==z['eligible_count'] and hashlib.sha256(packed).hexdigest()==z['eligible_packed_sha256'];assert sel[:64].tolist()==[x['value'] for x in z['eligible_trace_first64']];out.append({'page':page,'array_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'eligible':len(bits),'packed_sha256':hashlib.sha256(packed).hexdigest(),'all_bits_and_first64_values_agree':True})
(R/'array-comparison.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
