import pathlib,json,hashlib,collections,math
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
R=pathlib.Path(__file__).resolve().parents[3];O=pathlib.Path(__file__).parent;C=R/'exploration/overnight-01/worker-c';sources={}
def load(p):
 b=p.read_bytes();sources[str(p.relative_to(R))]=hashlib.sha256(b).hexdigest();return json.loads(b)
a='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx';blob=bytes(60*a.index(c['token'][0])+a.index(c['token'][1]) for c in load(R/'audit/alphanumeric-01/v1/transcription.json')['cells']);keys=load(C/'R08-keys.json');rows=load(C/'top_candidates.json')['R08'];out=[]
for z in rows:
 raw=keys[z['key_id']]['text'].encode();method=z['method'];key=raw if z['derivation'] in ['raw','raw UTF8'] else hashlib.new(z['derivation'].lower(),raw).digest()
 if method=='XOR-repeat':plain=bytes(x^key[i%len(key)] for i,x in enumerate(blob))
 elif method=='RC4':
  perm=list(range(256));j=0
  for i in range(256):
   j=(j+perm[i]+key[i%len(key)])%256;perm[j],perm[i]=perm[i],perm[j]
  i=j=0;plain=[]
  for x in blob:
   i=(i+1)%256;j=(j+perm[i])%256;perm[j],perm[i]=perm[i],perm[j];plain.append(x^perm[(perm[i]+perm[j])%256])
  plain=bytes(plain)
 else:
  param=z['parameter'];nonce=blob[:16] if param.startswith('prefix') else bytes(16);ciphertext=blob[16:] if param.startswith('prefix') else blob;mode=modes.ECB() if method=='AES-ECB' else modes.CBC(nonce) if method=='AES-CBC' else modes.CTR(nonce);ctx=Cipher(algorithms.AES(key),mode).decryptor();plain=ctx.update(ciphertext)+ctx.finalize()
 assert plain.hex()==z['output_hex'];assert hashlib.sha256(plain).hexdigest()==z['sha256'];pf=sum(x in [9,10,13] or 32<=x<=126 for x in plain)/len(plain);assert pf==z['printable_fraction'];assert not z['structures'];out.append(dict(source_file=str((C/'top_candidates.json').relative_to(R)),id=z['id'],index_kind='R08',independently_reproduced=True,checktype='independent parameter/key construction and byte decryption; shared cryptography AES primitive',status='REPRODUCIBLE_CANDIDATE',method=method,printable_fraction=pf))
(O/'binary_checked.json').write_text(json.dumps(dict(checked=out,sources=sources),indent=2)+'\n');print(json.dumps(out,indent=2))
