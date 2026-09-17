import os
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import numpy as np,json,hashlib,subprocess,gzip,sys,datetime
from PIL import Image
B=Path('exploration/persistent-01/worker-s/S15');P=Path('exploration/persistent-01/worker-p/P28');R=Path('exploration/persistent-01/review-48')
def guard():
 assert not Path('exploration/persistent-01/STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def arc(n):
 s=list(range(256));i=255;j=0;k=hashlib.md5(b'EncryptionDefault key').digest()
 for t in range(256):i=(i+1)%256;j=(j+s[i]+k[t%16])%256;s[i],s[j]=s[j],s[i]
 out=[]
 for t in range(n):i=(i+1)%256;j=(j+s[i])%256;s[i],s[j]=s[j],s[i];out.append(s[(s[i]+s[j])%256])
 return np.array(out,dtype=np.uint8)
def run(name,src,expected):
 guard();prefix=B/name;mp=Path(str(prefix)+'.map.bin');sp=Path(str(prefix)+'.selected.bin');rp=Path(str(prefix)+'.randomaccess.bin');op=Path(str(prefix)+'.payload.bin')
 env={**os.environ,'S15_MAP':str(mp.resolve()),'S15_SELECT':str(sp.resolve())};cmd=[str((B/'source/outguess').resolve()),'-r',str(src.resolve()),str(op.resolve())]
 r=subprocess.run(cmd,env=env,capture_output=True,timeout=120);Path(str(prefix)+'.stderr').write_bytes(r.stderr);assert r.returncode==0
 cmd2=[str((B/'coeff_reader').resolve()),str(src.resolve()),str(rp.resolve())];q=subprocess.run(cmd2,capture_output=True,timeout=120);assert q.returncode==0,q.stderr
 m=np.fromfile(mp,dtype=np.int32).reshape(-1,9);other=np.fromfile(rp,dtype=np.int32).reshape(-1,9);sel=np.fromfile(sp,dtype=np.int32).reshape(-1,2)
 order=lambda a:np.lexsort((a[:,3],a[:,1],a[:,2],a[:,0]))
 assert np.array_equal(m[order(m)],other[order(other)]),'coordinate/value mismatch'
 assert np.all(sel[:,0]>=0) and np.all(sel[:,0]<len(m))
 assert np.array_equal(m[sel[:,0],4]&1,sel[:,1]),'selected bit mismatch'
 payload=op.read_bytes();assert payload==expected.read_bytes(),'instrument changed payload'
 raw=np.packbits(sel[:,1].astype(np.uint8).reshape(-1,8),axis=1,bitorder='little').reshape(-1)
 stream=arc(max(len(payload),4));decoded=bytes(raw[4:]^stream[:len(payload)]);assert decoded==payload
 hdr=bytes(raw[:4]^stream[:4]);assert int.from_bytes(hdr[2:],'little')==len(payload)
 im=np.asarray(Image.open(src).convert('RGB'));h,w=im.shape[:2]
 bad=np.pad(np.cumsum(np.cumsum((im.min(axis=2)<250).astype(np.int32),axis=0),axis=1),((1,0),(1,0)))
 def spatial(rows):
  if len(rows)==0:return {'bits':0}
  sx=8*rows[:,7]//rows[:,5];sy=8*rows[:,8]//rows[:,6];x0=rows[:,1]*sx;y0=rows[:,2]*sy;x1=np.minimum(x0+sx,w);y1=np.minimum(y0+sy,h)
  assert np.all(x0<w) and np.all(y0<h)
  nbad=bad[y1,x1]-bad[y0,x1]-bad[y1,x0]+bad[y0,x0];white=nbad==0;dc=rows[:,3]==0
  return {'bits':len(rows),'ones':int(np.sum(rows[:,4]&1)),'dc':int(dc.sum()),'ac':int((~dc).sum()),'white_footprints':int(white.sum()),'white_dc':int((white&dc).sum()),'white_ac':int((white&~dc).sum()),'not_white_dc':int((~white&dc).sum()),'not_white_ac':int((~white&~dc).sum()),'bbox_xyxy':[int(x0.min()),int(y0.min()),int(x1.max()),int(y1.max())],'components':np.bincount(rows[:,0],minlength=3).tolist(),'frequency_counts':np.bincount(rows[:,3],minlength=64).tolist()}
 body=sel[32:];zeros=np.flatnonzero(body[:,1]==0);initial=int(zeros[0]) if len(zeros) else len(body)
 first=m[body[initial,0]].tolist() if initial<len(body) else None
 spans={'header':spatial(m[sel[:32,0]]),'shared_1417_bytes':spatial(m[body[:min(1417*8,len(body)),0]]),'initial_one_run':spatial(m[body[:initial,0]]),'whole_body':spatial(m[body[:,0]])}
 record={'name':name,'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'expected_sha256':hashlib.sha256(expected.read_bytes()).hexdigest(),'payload_sha256':hashlib.sha256(payload).hexdigest(),'commands':[cmd,cmd2],'exits':[r.returncode,q.returncode],'dimensions':[w,h],'usable_coefficients':len(m),'selected_bits':len(sel),'payload_bytes':len(payload),'header_seed':int.from_bytes(hdr[:2],'little'),'header_length':int.from_bytes(hdr[2:],'little'),'initial_body_ones_bits':initial,'first_nonone_coefficient':first,'first_nonone_bitmap_index':int(body[initial,0]) if initial<len(body) else None,'spans':spans,'checks':{'unchanged_payload':True,'independent_randomaccess_mapping':True,'all_selected_parities':True,'scalar_body_decrypt':True},'map_columns':['component','block_x','block_y','natural_frequency','signed_value','h_sampling','v_sampling','max_h','max_v'],'map_format':'native little-endian int32 nine columns; row index is usable bitmap index','selected_columns':['bitmap_index','bit'],'selected_format':'native little-endian int32 two columns; first32 header then body'}
 for p in [mp,sp,rp]:
  data=p.read_bytes();record[p.name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)};Path(str(p)+'.gz').write_bytes(gzip.compress(data));p.unlink()
 Path(str(prefix)+'.json').write_text(json.dumps(record,indent=2));print(json.dumps({k:v for k,v in record.items() if k not in ['spans','map_columns','commands']},indent=2));return record
if sys.argv[1]=='controls':
 out=[run('historical',R/'4gq25.jpg',P/'historical.bin'),run('plant0',P/'plant-0.jpg',P/'plant-0-extract.bin')];(B/'controls.json').write_text(json.dumps({'passed':True,'names':[r['name'] for r in out]},indent=2))
else:
 assert json.loads((B/'controls.json').read_text())['passed'];ix=int(sys.argv[1]);assert ix in [0,26];run('actual'+str(ix),Path(f'liber-primus/data/relikd/p{ix}.jpg'),P/f'actual-{ix}-key-0.bin')
