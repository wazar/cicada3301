import p10 as old
import pathlib,numpy as np,json,subprocess,random,math,gzip,hashlib,sys
R=old.R.parent/'P11';ROOT=old.ROOT

def dump(n,x):(R/(n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def command(label,args):
 r=subprocess.run([str(R/'harness')]+[str(x) for x in args],capture_output=True);(R/(label+'.stdout')).write_bytes(r.stdout);(R/(label+'.stderr')).write_bytes(r.stderr);dump(label+'-command',dict(command=[str(R/'harness')]+[str(x) for x in args],exit_code=r.returncode));assert r.returncode==0,(label,r.returncode,r.stderr);return json.loads(r.stderr)
def bitsnum(n,w):return [(n>>j)&1 for j in range(w-1,-1,-1)]
def sourcebits(payload,width=None):
 if not payload:return []
 n=len(payload);w=width if width is not None else n.bit_length();return bitsnum(w,5)+bitsnum(n,w)+np.unpackbits(np.frombuffer(payload,dtype=np.uint8)).tolist()
def eligible(v):return (v&1)!=v

def sink_sim(bits):
 width=0;n=0;special=0;fi=0;bi=7;buf=bytearray();cur=0;out=bytearray();opened=True;err=[]
 for ix,c in enumerate(bits):
  if not opened:break
  if special<5:special+=1;width|=int(c)<<(5-special)
  elif special<5+width:special+=1;n|=int(c)<<(5+width-special)
  else:
   cur=(cur&~(1<<bi))|(int(c)<<bi);bi-=1
   if bi==-1:bi=7;buf.append(cur);cur=0;fi+=1
   if fi==n:
    if bi!=7:err.append(ix);continue
    out.extend(buf);buf=bytearray();opened=False;break
   if len(buf)==1024:out.extend(buf);buf=bytearray();bi=7
 return bytes(out),dict(rep_width=width,file_size=n,fileindex=fi,header_bits=special,buffer_bytes=len(buf),bitindex=bi,open=int(opened)),err

def header(bits):
 b=list(map(int,bits));total=len(b)
 if total<5:return dict(status='INCOMPLETE_WIDTH',bits=total),b''
 w=int(''.join(map(str,b[:5])),2)
 if total<5+w:return dict(status='INCOMPLETE_LENGTH',width=w,bits=total),b''
 n=int(''.join(map(str,b[5:5+w])),2) if w else 0;capacity=(total-5-w)//8;available=min(n,capacity);a=np.array(b[5+w:5+w+8*available],dtype=np.uint8);payload=np.packbits(a).tobytes();minimal=n.bit_length() if n else 0
 return dict(status='ZERO_LENGTH_NOT_SOURCE_SUCCESS' if n==0 else ('COMPLETE_UNVERIFIED' if n<=capacity else 'DECLARED_LENGTH_EXCEEDS_CAPACITY'),width=w,length=n,capacity_bytes=capacity,bits=total,exact_nonempty_encoder_header=(n>0 and w==minimal),readme_width_compatible=(n>0 and w in [minimal,minimal+1]),complete_available_bytes=available,remaining_payload_partial_bits=(total-5-w)%8),payload

def stream(meta,arrays):
 comps=meta['frame']['components'];mw,mh=meta['mcu_grid'];assert meta['dummy_blocks']==0,'saved arrays lack dummy coefficients; not supported by this adapter';vals=[];positions=[]
 for my in range(mh):
  for mx in range(mw):
   for ci,c in enumerate(comps):
    for y in range(c['v']):
     for x in range(c['h']):
      block=arrays[str(c['id'])][my*c['v']+y,mx*c['h']+x]
      for k,z in enumerate(old.ZZ):
       v=int(block[z]);vals.append(v)
       if eligible(v):positions.append([my,mx,c['id'],y,x,k,z,v])
 return np.array(vals,dtype='<i2'),np.array(positions,dtype='<i4')
def controls():
 old.gate();rng=random.Random(330111);carrier=np.tile(np.arange(-8,9,dtype='<i2'),5000);base=R/'stream-carrier.i16';carrier.tofile(base);rows=[]
 for n in [0,1,2,3,127,128,255,256,1023,1024,1025]:
  payload=rng.randbytes(n);pf=R/f'payload-{n}.bin';pf.write_bytes(payload);cf=R/f'embedded-{n}.i16';cmd=command('inject-'+str(n),['inject',base,cf,pf]);actual=np.fromfile(cf,dtype='<i2');expect=carrier.copy();bs=sourcebits(payload);j=0
  for i,v in enumerate(expect):
   if eligible(int(v)) and j<len(bs):expect[i]=(int(v)&~1)|bs[j];j+=1
  assert j==len(bs) and np.array_equal(expect,actual) and cmd['complete']==1;ab=np.array([int(v)&1 for v in actual if eligible(int(v))],dtype=np.uint8);state=command('sink-'+str(n),['sink',cf,R/f'extracted-{n}.bin']);pred,ps,errs=sink_sim(ab);assert state==ps and pred==(R/f'extracted-{n}.bin').read_bytes();h,ret=header(ab)
  if n:assert ret==payload and pred==payload and state['open']==0
  rows.append(dict(n=n,header=h,sink=state,errors=errs,payload_sha256=old.sha(payload),eligible_bits=len(ab),source_bits=len(bs),exact_coefficient_match=True))
 probes=[]
 cases=[('width0',bitsnum(0,5)+[1,0]*10),('positivewidth-zero',bitsnum(3,5)+[0]*3+[1]*10),('truncatedwidth',[1,0,1]),('truncatedlength',bitsnum(8,5)+[1,1]),('leadingzero',sourcebits(b'AB',3)),('truncatedpayload',sourcebits(b'AB')[:-3])]
 for name,b in cases:
  co=np.array([-2|int(v) for v in b],dtype='<i2');f=R/(name+'.i16');co.tofile(f);st=command('probe-'+name,['sink',f,R/(name+'.bin')]);expected,ss,errs=sink_sim(b);assert st==ss and expected==(R/(name+'.bin')).read_bytes();h,available=header(b);probes.append(dict(name=name,bits=b,header=h,sink=ss,errors=errs,raw_available=available.hex()))
 # Actual baseline JPEG control with source-derived injection and independent P10 decoding.
 inp=old.R/'control-0-clean.jpg';pf=R/'payload-127.bin';jpg=R/'jpeg-control.jpg';command('jpeg-inject',['jpeg',inp,jpg,pf]);meta,_,_,ar=old.parse(jpg.read_bytes());vals,pos=stream(meta,{str(k):v for k,v in ar.items()});vf=R/'jpeg-control.i16';vals.tofile(vf);b=np.array([int(v)&1 for v in vals if eligible(int(v))],dtype=np.uint8);h,payload=header(b);assert payload==pf.read_bytes();st=command('jpeg-sink',['sink',vf,R/'jpeg-control-payload.bin']);assert (R/'jpeg-control-payload.bin').read_bytes()==pf.read_bytes();pred,ss,errs=sink_sim(b);assert ss==st;dump('controls',dict(status='PASS',stream_controls=rows,reader_probes=probes,jpeg=dict(input=str(inp),input_sha256=old.sha(inp.read_bytes()),output_sha256=old.sha(jpg.read_bytes()),header=h,sink=st,meta=meta,payload_sha256=old.sha(payload))));print('CONTROL PASS',len(rows),len(probes),h)
def actual():
 old.gate();assert json.loads((R/'controls.json').read_text())['status']=='PASS';out=[]
 for page in [0,1]:
  old.gate();md=json.loads((old.R/f'actual-{page}.json').read_text());meta=md['metadata'];archive=np.load(old.R/f'actual-{page}-coefficients.npz');ar={k:archive[k] for k in archive.files};archive.close();assert all(old.sha(ar[k].tobytes())==meta['coefficient_sha256'][k] for k in ar);vals,pos=stream(meta,ar);vals.tofile(R/f'actual-{page}-stream.i16');np.savez_compressed(R/f'actual-{page}-eligible-map.npz',positions=pos);bits=np.array([int(v)&1 for v in vals if eligible(int(v))],dtype=np.uint8);bits.tofile(R/f'actual-{page}-bits.u8');packed=np.packbits(bits).tobytes();(R/f'actual-{page}-bits.packed').write_bytes(packed);h,payload=header(bits);(R/f'actual-{page}-available-payload.bin').write_bytes(payload);st=command('actual-sink-'+str(page),['sink',R/f'actual-{page}-stream.i16',R/f'actual-{page}-historical-sink.bin']);pred,ss,errs=sink_sim(bits);assert st==ss and pred==(R/f'actual-{page}-historical-sink.bin').read_bytes()
  # Faircoin header calculation is NOT an ordinary-image null. Exclude N=0 from success.
  cap=len(bits);prob=0;minimalprob=0
  for w in range(32):
   c=max(0,(cap-5-w)//8);valid=max(0,min(c,(1<<w)-1));prob+=valid/(32*(1<<w));lo=1<<(w-1) if w else 1;minimalprob+=max(0,min(c,(1<<w)-1)-lo+1)/(32*(1<<w))
  rng=random.Random(330111+page);null=[]
  for rep in range(999):
   w=rng.getrandbits(5);n=rng.getrandbits(w) if w else 0;c=(cap-5-w)//8;null.append(dict(width=w,length=n,capacity=c,positive_capacity=n>0 and n<=c,minimal=n>0 and w==n.bit_length()))
  row=dict(page=page,image_sha256=md['sha256'],eligible_bits=len(bits),packed_sha256=old.sha(packed),header=h,sink=st,available_payload_sha256=old.sha(payload),historical_output_bytes=len(pred),historical_output_sha256=old.sha(pred),faircoin_probability_positive_capacity=prob,faircoin_probability_minimal_capacity=minimalprob,faircoin_999_positive_capacity=sum(x['positive_capacity'] for x in null),faircoin_999_minimal_capacity=sum(x['positive_capacity'] and x['minimal'] for x in null),null=null);dump('actual-'+str(page),row);out.append({k:v for k,v in row.items() if k!='null'});print(json.dumps(out[-1]),flush=True)
 dump('actual-summary',out)
if __name__=='__main__':{'controls':controls,'actual':actual}[sys.argv[1]]()
