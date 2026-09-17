import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,hashlib,gzip,importlib.util,math
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[3];B=R/'exploration/persistent-01';S=B/'worker-s/S15';O=B/'review-51';spec=importlib.util.spec_from_file_location('independent_p10',B/'worker-p/p10.py');p10=importlib.util.module_from_spec(spec);spec.loader.exec_module(p10)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
files=[p for p in S.iterdir() if p.is_file() and p.suffix not in ['.c'] and p.name not in ['coeff_reader']];records={};images=[]
for n in ['historical','plant0','actual0','actual26']:
 d=json.loads((S/(n+'.json')).read_text());records[n]=d;images.append(R/d['source'])
files+=images+[B/'worker-s/S15-CARD.md',B/'worker-s/S15-REPORT.md',B/'worker-s/s15_trace.py',B/'worker-p/p10.py'];snap=[dict(path=str(p.relative_to(R)),sha256=sha(p)) for p in files];save('input-snapshot.json',snap)
# Standalone ARC4 with MD5 domain seed, no OutGuess imports.
def stream(n):
 state=list(range(256));a=255;b=0;seed=hashlib.md5(b'EncryptionDefault key').digest()
 for i in range(256):
  a=(a+1)&255;b=(b+state[a]+seed[i%16])&255;state[a],state[b]=state[b],state[a]
 out=bytearray()
 for i in range(n):
  a=(a+1)&255;b=(b+state[a])&255;state[a],state[b]=state[b],state[a];out.append(state[(state[a]+state[b])&255])
 return bytes(out)
results=[]
for name,d in records.items():
 src=R/d['source'];assert sha(src)==d['source_sha256'];meta,_,_,arr=p10.parse(src.read_bytes());comps=meta['frame']['components'];hm=max(c['h'] for c in comps);vm=max(c['v'] for c in comps);m=np.frombuffer(gzip.decompress((S/(name+'.map.bin.gz')).read_bytes()),dtype='<i4').reshape(-1,9);sel=np.frombuffer(gzip.decompress((S/(name+'.selected.bin.gz')).read_bytes()),dtype='<i4').reshape(-1,2);ra=np.frombuffer(gzip.decompress((S/(name+'.randomaccess.bin.gz')).read_bytes()),dtype='<i4').reshape(-1,9)
 assert len(m)==d['usable_coefficients'] and len(sel)==d['selected_bits'];assert np.all((m[:,4]!=0)&(m[:,4]!=1))
 for ci,c in enumerate(comps):
  rows=m[m[:,0]==ci];a=arr[c['id']];assert np.array_equal(a[rows[:,2],rows[:,1],rows[:,3]],rows[:,4]);assert np.all(rows[:,5:]==np.array([c['h'],c['v'],hm,vm]))
 # Build whole ordered usable stream from independent natural-index coefficient arrays.
 expected=[];mw,mh=meta['mcu_grid'];inter=len(comps)>1
 for my in range(mh):
  for mx in range(mw):
   for ci,c in enumerate(comps):
    a=arr[c['id']]
    for yy in range(c['v'] if inter else 1):
     for xx in range(c['h'] if inter else 1):
      y=my*(c['v'] if inter else 1)+yy;x=mx*(c['h'] if inter else 1)+xx
      if y>=a.shape[0] or x>=a.shape[1]:continue
      for k in np.flatnonzero((a[y,x]!=0)&(a[y,x]!=1)):expected.append([ci,x,y,int(k),int(a[y,x,k]),c['h'],c['v'],hm,vm])
 expected=np.array(expected,dtype=np.int32);assert np.array_equal(m,expected),'whole usable map/order differs'
 order=lambda z:np.lexsort((z[:,3],z[:,1],z[:,2],z[:,0]));assert np.array_equal(m[order(m)],ra[order(ra)]);assert np.all(sel[:,0]>=0) and np.all(sel[:,0]<len(m));assert np.array_equal(m[sel[:,0],4]&1,sel[:,1]);raw=np.packbits(sel[:,1].astype(np.uint8).reshape(-1,8),axis=1,bitorder='little').ravel();key=stream(max(4,len(raw)-4));header=bytes(int(x)^y for x,y in zip(raw[:4],key[:4]));payload=bytes(int(x)^y for x,y in zip(raw[4:],key));assert payload==(S/(name+'.payload.bin')).read_bytes() and hashlib.sha256(payload).hexdigest()==d['expected_sha256'];assert int.from_bytes(header[:2],'little')==d['header_seed'] and int.from_bytes(header[2:],'little')==d['header_length']==len(payload)
 # Direct min of every component-block RGB support footprint, cached by coordinates.
 im=np.asarray(Image.open(src).convert('RGB'));height,width=im.shape[:2];cache={}
 def details(rows):
  if not len(rows):return dict(bits=0)
  white=[];boxes=[]
  for ci,x,y,k,value,h,v,mh,mv in rows:
   z=(int(ci),int(x),int(y))
   if z not in cache:
    x0=int(x)*8*int(mh)//int(h);x1=min(width,(int(x)+1)*8*int(mh)//int(h));y0=int(y)*8*int(mv)//int(v);y1=min(height,(int(y)+1)*8*int(mv)//int(v));patch=im[y0:y1,x0:x1];assert patch.size;cache[z]=(bool(np.min(patch)>=250),(x0,y0,x1,y1),int(patch.min()),int(patch.max()))
   white.append(cache[z][0]);boxes.append(cache[z][1])
  white=np.array(white);dc=rows[:,3]==0;boxes=np.array(boxes)
  return dict(bits=len(rows),ones=int(sum(rows[:,4]&1)),dc=int(dc.sum()),ac=int((~dc).sum()),white_footprints=int(white.sum()),white_dc=int(sum(white&dc)),white_ac=int(sum(white&~dc)),not_white_dc=int(sum(~white&dc)),not_white_ac=int(sum(~white&~dc)),bbox_xyxy=[int(min(boxes[:,0])),int(min(boxes[:,1])),int(max(boxes[:,2])),int(max(boxes[:,3]))],components=np.bincount(rows[:,0],minlength=3).tolist(),frequency_counts=np.bincount(rows[:,3],minlength=64).tolist())
 body=sel[32:];zeros=np.flatnonzero(body[:,1]==0);initial=int(zeros[0]) if len(zeros) else len(body);assert initial==d['initial_body_ones_bits'];spans={'header':m[sel[:32,0]],'shared_1417_bytes':m[body[:1417*8,0]],'initial_one_run':m[body[:initial,0]],'whole_body':m[body[:,0]]};checks={}
 for label,rows in spans.items():checks[label]=details(rows);assert checks[label]==d['spans'][label],label
 first=m[body[initial,0]] if initial<len(body) else None;assert (first.tolist() if first is not None else None)==d['first_nonone_coefficient'];r=dict(name=name,whole_map_rows=len(m),selected_bits=len(sel),whole_map_order_match=True,independent_entropy_decoder=True,complete_payload_match=True,all_spatial_summaries_match=True,initial_ones=initial,first_zero=first.tolist() if first is not None else None,spans=checks,quantization=Image.open(src).quantization)
 if first is not None:r['first_zero_pixel_range']=list(cache[tuple(map(int,first[:3]))][2:])
 if name.startswith('actual'):
  prefix=spans['shared_1417_bytes'];assert np.all(prefix[:,0]==0) and np.all(prefix[:,3]==0) and np.all(prefix[:,4]==339);assert checks['shared_1417_bytes']['white_dc']==11336;r['shared_prefix_white_Y_DC339']=True
 results.append(r);print(name,'PASS',len(m),len(sel),flush=True)
assert all(sha(R/r['path'])==r['sha256'] for r in snap);save('result.json',dict(pass_all=True,images=results,probability_inference='None; deterministic observed arithmetic, not a statistical significance claim.'))
