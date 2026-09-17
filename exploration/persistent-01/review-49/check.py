import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,re,zlib,itertools,numpy as np
R=Path(__file__).parent;P=R.parent/'worker-p/P28';summary=json.loads((P/'summary.json').read_text());controls=json.loads((P/'controls-summary.json').read_text());hashes={};prefix=[];records=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class ARC:
 def __init__(self,label,key):
  self.s=list(range(256));self.i=0;self.j=0;self.mix(hashlib.md5(label+key).digest())
 def mix(self,data):
  self.i=(self.i-1)%256
  for n in range(256):self.i=(self.i+1)%256;self.j=(self.j+self.s[self.i]+data[n%len(data)])%256;self.s[self.i],self.s[self.j]=self.s[self.j],self.s[self.i]
 def byte(self):
  self.i=(self.i+1)%256;self.j=(self.j+self.s[self.i])%256;self.s[self.i],self.s[self.j]=self.s[self.j],self.s[self.i];return self.s[(self.s[self.i]+self.s[self.j])%256]
 def word(self):return int.from_bytes(bytes(self.byte() for _ in range(4)),'big')
def check_record(r):
 path=P/(r['label']+'.bin');data=path.read_bytes();assert len(data)==r['output_bytes'] and sha(path)==r['output_sha256'];assert sha(Path(r['input']))==r['input_sha256'];assert sha(Path(r['command'][0]))==r['binary_sha256'];saved=json.loads((P/(r['label']+'.command.json')).read_text());assert saved['exit_code']==r['exit_code'] and saved['command']==r['command'];err=(P/(r['label']+'.stderr')).read_text();bits=int(re.search(r'Extracting usable bits:\s+(\d+) bits',err)[1]);mt=re.search(r'Steg retrieve: seed: (\d+), len: (\d+)',err);seed,length=map(int,mt.groups());return data,bits,seed,length
for row in summary['actual']+summary['surrogates']:
 data,bits,seed,length=check_record(row);key=(row['key'] or 'Default key').encode();a=ARC(b'Encryption',key);stream=bytes(a.byte() for _ in range(max(4096,len(data))));header=bytes(x^255 for x in stream[:4]);assert int.from_bytes(header[:2],'little')==seed and int.from_bytes(header[2:],'little')==length
 if data:
  n=next((i for i,(x,y) in enumerate(zip(data,stream)) if x!=(y^255)),len(data));prefix.append(dict(label=row['label'],ones_prefix_bytes=n));assert len(data)==length
  for w in [15,31]:
   try:
    dec=zlib.decompressobj(w);out=dec.decompress(data);out+=dec.flush();assert not(dec.eof and not dec.unused_data and not dec.unconsumed_tail)
   except zlib.error:pass
  assert not data.startswith(b'-----BEGIN PGP ') and not data.startswith(b'P28-CONTROL\0')
 it=ARC(b'Seeding',key);offset=it.word()%32
 for _ in range(32):offset+=it.word()%32+1
 it.mix(seed.to_bytes(2,'little'));failure=None;minskip=2**32
 if length>(bits+7)//8:failure=dict(kind='initial_capacity_rejection',length=length,capacity=(bits+7)//8)
 else:
  for byte in range(length):
   remain=bits-offset;limit=bits//32;adj=np.float32(2) if remain>limit else np.float32(2)-np.float32(limit-remain)/np.float32(limit);skip=int(np.float32(adj*np.float32(remain))/np.float32(8*(length-byte)));minskip=min(minskip,skip)
   if skip<=0:failure=dict(kind='zero_skip_modulus',body_byte=byte,bit_offset=offset,remaining_bits=remain,remaining_payload_bytes=length-byte,skipmod=skip);break
   for bit in range(8):
    if offset>=bits:failure=dict(kind='out_of_bounds_bit_read',body_byte=byte,bit=bit,bit_offset=offset,bits=bits);break
    offset+=it.word()%skip+1
   if failure:break
 records.append(dict(label=row['label'],exit_code=row['exit_code'],usable_bits=bits,seed=seed,length=length,iterator_first_failure=failure,min_skipmod=minskip))
 print(row['label'],failure,flush=True)
for x in summary['prefix_comparisons']:
 a=(P/x['a']).read_bytes();b=(P/x['b']).read_bytes();n=next((i for i,(u,v) in enumerate(zip(a,b)) if u!=v),min(len(a),len(b)));assert n==x['common_prefix'] and sum(u==v for u,v in zip(a,b))==x['position_equal']
hist,b,s,l=check_record(controls['historical']);assert hist==(R.parent/'review-48/4gq25.jpg.outguess').read_bytes() and (s,l)==(230,1136)
frame=(P/'known-message.bin').read_bytes();magic=b'P28-CONTROL\0';body=frame[len(magic)+4:-32];assert frame.startswith(magic) and len(body)==int.from_bytes(frame[len(magic):len(magic)+4],'big') and body==bytes(range(256)) and hashlib.sha256(body).digest()==frame[-32:]
assert len(controls['own_controls'])==8
for c in controls['own_controls']:
 data,b,s,l=check_record(c['extract']);assert data==frame and c['embed']['exit_code']==0 and c['extract']['exit_code']==0
assert sum(r['exit_code']==-10 for r in records)==4
for path in P.iterdir():
 if path.is_file():hashes[path.name]={'sha256':sha(path),'bytes':path.stat().st_size}
(R/'inputs.json').write_text(json.dumps(hashes,indent=2));(R/'result.json').write_text(json.dumps(dict(status='PASS',actual_queries=16,surrogates=2,historical_controls=1,own_controls=8,records=records,prefixes=prefix,scope='Independent scalar path simulation; no executable rerun and no claim exact faulting PC without runtime trace'),indent=2))
