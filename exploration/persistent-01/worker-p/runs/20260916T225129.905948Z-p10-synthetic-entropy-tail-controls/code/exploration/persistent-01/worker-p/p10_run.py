import p10 as p
import json,random,io,zlib,numpy as np,sys
from PIL import Image
R=p.R

def pixels(b):
 with Image.open(io.BytesIO(b)) as im:return im.mode,im.size,im.tobytes()
def controls():
 p.gate();rng=random.Random(330110);rows=[];payload=bytes(range(256))+b'P10 complete synthetic binary payload; not a discovery.';blob=p.frame(payload);assert p.unframe(blob)==payload;encoded=blob.replace(b'\xff',b'\xff\x00');(R/'payload.bin').write_bytes(payload);(R/'control-frame.bin').write_bytes(blob)
 specs=[(mode,size,sub,q) for mode in ['L','RGB'] for size in [(128,96),(123,91)] for sub in ([0] if mode=='L' else [0,1,2]) for q in [75,92]]
 for ix,(mode,size,sub,quality) in enumerate(specs):
  im=Image.frombytes(mode,size,rng.randbytes(size[0]*size[1]*(1 if mode=='L' else 3)));buf=io.BytesIO();im.save(buf,format='JPEG',quality=quality,subsampling=sub);clean=buf.getvalue();meta,raw,tail,arrays=p.parse(clean);assert not raw and not tail and meta['padding_all_ones'];planted=clean[:meta['eoi_offset']]+encoded+clean[meta['eoi_offset']:];pm,pr,pt,pa=p.parse(planted);assert p.unframe(pt)==payload;assert pixels(clean)==pixels(planted);assert all(np.array_equal(arrays[k],pa[k]) for k in arrays);assert pm['entropy_bits']==meta['entropy_bits'];label='control-'+str(ix);(R/(label+'-clean.jpg')).write_bytes(clean);(R/(label+'-planted.jpg')).write_bytes(planted);(R/(label+'-extracted.bin')).write_bytes(pt);p.dump(label,dict(mode=mode,size=size,subsampling=sub,quality=quality,clean=meta,planted=pm,clean_sha256=p.sha(clean),planted_sha256=p.sha(planted),pixel_sha256=p.sha(pixels(clean)[2]),payload_sha256=p.sha(payload)));rows.append(dict(index=ix,mode=mode,size=size,subsampling=sub,quality=quality,mcus=meta['mcus'],blocks=meta['blocks'],dummy=meta['dummy_blocks'],stuffed=len(meta['entropy_stuffed_zero_offsets']),padding=meta['pad_bits'],payload_bytes=len(payload),pixel_identical=True))
 failures=[]
 for name,mut in [('bad-crc',blob[:-1]+bytes([blob[-1]^1])),('bad-length',blob[:11]+bytes([blob[11]^1])+blob[12:])]:
  try:p.unframe(mut);raise AssertionError('malformed frame accepted')
  except p.Invalid as e:failures.append(dict(case=name,result=str(e)))
 # Unsupported mode checks are run on progressive encoder output and explicit header probes.
 buf=io.BytesIO();im.save(buf,format='JPEG',progressive=True);progressive=buf.getvalue();(R/'unsupported-progressive.jpg').write_bytes(progressive)
 probes=[('progressive',progressive),('restart-header',clean[:2]+b'\xff\xdd\x00\x04\x00\x01'+clean[2:])]
 sos=next(x for x in meta['headers'] if x['marker']==218);off=sos['offset'];b=clean[off+4:off+2+sos['length']];newsos=bytes([2])+b[1:5]+b[-3:];multi=clean[:off]+b'\xff\xda'+(len(newsos)+2).to_bytes(2,'big')+newsos+clean[off+2+sos['length']:];probes.append(('multiscan-header',multi))
 for name,b in probes:
  (R/('unsupported-'+name+'.jpg')).write_bytes(b)
  try:p.parse(b);raise AssertionError('unsupported accepted')
  except p.Unsupported as e:failures.append(dict(case=name,result=str(e)))
 # Truncating entropy cannot be silently padded to the expected MCU count.
 trunc=clean[:meta['entropy_byte_end']-500]+b'\xff\xd9';(R/'invalid-truncated.jpg').write_bytes(trunc)
 try:p.parse(trunc);raise AssertionError('truncation accepted')
 except p.Invalid as e:failures.append(dict(case='truncated',result=str(e)))
 padprobe=None
 for row in rows:
  b=(R/('control-'+str(row['index'])+'-clean.jpg')).read_bytes();m,_,_,_=p.parse(b)
  if m['pad_bits'] and b[m['final_data_byte_offset']]!=255:
   a=bytearray(b);a[m['final_data_byte_offset']]^=1;mm,_,_,_=p.parse(bytes(a));assert not mm['padding_all_ones'];assert pixels(b)==pixels(bytes(a));(R/'noncanonical-padding.jpg').write_bytes(a);padprobe=dict(index=row['index'],meta=mm,pixel_identical=True);break
 assert padprobe is not None
 p.dump('controls',dict(status='PASS',controls=rows,malformed=failures,padprobe=padprobe,payload_sha256=p.sha(payload),specs=len(specs)));print('CONTROLS PASS',len(rows),sum(r['stuffed'] for r in rows))
def actual():
 p.gate();assert json.loads((R/'controls.json').read_text())['status']=='PASS';rows=[]
 for page in [0,1]:
  p.gate();f=p.ROOT/f'liber-primus/data/relikd/p{page}.jpg';d=f.read_bytes();m,raw,tail,arrays=p.parse(d);np.savez_compressed(R/('actual-'+str(page)+'-coefficients.npz'),**{str(k):v for k,v in arrays.items()});(R/f'actual-{page}-tail-raw.bin').write_bytes(raw);(R/f'actual-{page}-tail.bin').write_bytes(tail)
  try:payload=p.unframe(tail);status='VALID_TEST_FRAME';(R/f'actual-{page}-payload.bin').write_bytes(payload)
  except p.Invalid as e:status=str(e)
  p.dump('actual-'+str(page),dict(path=str(f.relative_to(p.ROOT)),sha256=p.sha(d),bytes=len(d),metadata=m,frame_status=status));row=dict(page=page,sha256=p.sha(d),bytes=len(d),mcus=m['mcus'],blocks=m['blocks'],ac_symbols=m['ac_symbols'],entropy_bits=m['entropy_bits'],stuffed=len(m['entropy_stuffed_zero_offsets']),pad_bits=m['pad_bits'],pad_value=m['pad_value'],tail_bytes=len(tail),marker_fill=m['marker_fill_bytes'],after_eoi=m['after_eoi_bytes'],eoi_offset=m['eoi_offset']);rows.append(row);print(json.dumps(row),flush=True)
 p.dump('actual-summary',rows)
if __name__=='__main__':{'controls':controls,'actual':actual}[sys.argv[1]]()
