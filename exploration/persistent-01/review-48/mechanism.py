from pathlib import Path
import hashlib,json
R=Path(__file__).parent;s=list(range(256));i=255;j=0;key=hashlib.md5(b'EncryptionDefault key').digest()
for t in range(256):
 i=(i+1)%256;j=(j+s[i]+key[t%16])%256;s[i],s[j]=s[j],s[i]
out=[]
for t in range(4096):
 i=(i+1)%256;j=(j+s[i])%256;s[i],s[j]=s[j],s[i];out.append(s[(s[i]+s[j])%256])
stream=bytes(out);(R/'default-encryption-keystream.bin').write_bytes(stream)
headers=[]
for byte in [0,255]:
 b=bytes(x^byte for x in stream[:4]);headers.append(dict(constant_usable_bit=bool(byte),raw_header_hex=(bytes([byte])*4).hex(),decoded_header_hex=b.hex(),seed=int.from_bytes(b[:2],'little'),length=int.from_bytes(b[2:],'little')))
vals=[-2,-1,0,1,2];filtercheck=[dict(coefficient=x,unsigned=x%65536,retained=((x%65536)&1)!=(x%65536),bit=x&1) for x in vals]
assert [x['coefficient'] for x in filtercheck if not x['retained']]==[0,1]
(R/'mechanism.json').write_text(json.dumps(dict(headers=headers,coefficient_filter=filtercheck,default_keystream_sha256=hashlib.sha256(stream).hexdigest(),scope='Scalar replay of inspected0.4 source, not image coefficient trace or complete extractor'),indent=2));print(headers)
