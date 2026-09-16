from search import *
import zlib,bz2,lzma,struct,collections,re
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes

def crypt(key,mode,b):
 d=Cipher(algorithms.AES(key),mode).decryptor();return d.update(b)+d.finalize()
def rc4(k,b):
 s=list(range(256));j=0
 for i in range(256):j=(j+s[i]+k[i%len(k)])%256;s[i],s[j]=s[j],s[i]
 i=j=0;out=[]
 for c in b:
  i=(i+1)%256;j=(j+s[i])%256;s[i],s[j]=s[j],s[i];out.append(c^s[(s[i]+s[j])%256])
 return bytes(out)
def inspect(b):
 hits=[]
 for name,wbits in [('gzip',31),('zlib',15)]:
  try:
   d=zlib.decompressobj(wbits);out=d.decompress(b,65537)
   if len(out)<=65536 and d.eof and not d.unused_data and not d.unconsumed_tail:hits.append(dict(format=name,decoded_hex=out.hex(),size=len(out)))
  except zlib.error:pass
 for name,cls in [('bz2',bz2.BZ2Decompressor),('xz',lzma.LZMADecompressor)]:
  try:
   d=cls();out=d.decompress(b,max_length=65537)
   if len(out)<=65536 and d.eof and not d.unused_data:hits.append(dict(format=name,decoded_hex=out.hex(),size=len(out)))
  except (OSError,EOFError,lzma.LZMAError):pass
 try:
  s=b.decode('utf-8');obj=json.loads(s);hits.append(dict(format='complete-utf8-json',value=obj))
 except (UnicodeDecodeError,ValueError):pass
 return hits

def main():
 # Known answer gates: NIST AES ECB/CBC/CTR first block, published RC4 Key/Plaintext; corrupted ciphertext rejected structurally.
 key=bytes.fromhex('2b7e151628aed2a6abf7158809cf4f3c');pt=bytes.fromhex('6bc1bee22e409f96e93d7e117393172a')
 for ct,mode in [('3ad77bb40d7a3660a89ecaf32466ef97',modes.ECB()),('7649abac8119b246cee98e9b12e9197d',modes.CBC(bytes(range(16)))),('874d6191b620e3261bef6864990db6ce',modes.CTR(bytes.fromhex('f0f1f2f3f4f5f6f7f8f9fafbfcfdfeff')))]:assert crypt(key,mode,bytes.fromhex(ct))==pt
 assert rc4(b'Key',b'Plaintext').hex()=='bbf316e8d940af0ad3'
 cb=zlib.compress(b'A verifiable compression control.');assert inspect(cb);bad=bytearray(cb);bad[-1]^=1;assert not inspect(bytes(bad));assert not inspect(zlib.compress(b'X'*65537))
 specs=[('DIVINITY','03.jpg key'),('FIRFUMFERENFE','14.jpg key'),('THE PRIMES ARE SACRED','05.jpg instruction'),('THE TOTIENT FUNCTION IS SACRED','05.jpg instruction normalized spelling'),('ALL THINGS SHOULD BE ENCRYPTED','05.jpg instruction normalized spelling'),('SOME WISDOM','05.jpg title'),('A WARNING','Runes - 01.jpg title'),('WELCOME','03.jpg title'),('PILGRIM','03.jpg plaintext'),('JOURNEY','03.jpg plaintext'),('INSTAR','03.jpg plaintext'),('EMERGE','03.jpg plaintext'),('AN END','LP2/56.jpg title'),('A PARABLE','LP2/57.jpg title'),('LIBER PRIMUS','book title')]
 keys=[]
 for k,src in specs:
  for spelling in (k,k.lower(),k.replace(' ',''),k.lower().replace(' ','')):
   if not any(x['text']==spelling for x in keys):keys.append(dict(text=spelling,source=src))
 assert len(keys)<=128;save(OUT/'R08-keys.json',keys)
 b=payload();jobs=[dict(method='direct',key=None,output=b)];
 for ki,item in enumerate(keys):
  raw=item['text'].encode();jobs.append(dict(method='XOR-repeat',key_id=ki,derivation='raw UTF8',output=bytes(v^raw[i%len(raw)] for i,v in enumerate(b))))
  for deriv,k in [('raw',raw),('SHA256',hashlib.sha256(raw).digest())]:jobs.append(dict(method='RC4',key_id=ki,derivation=deriv,output=rc4(k,b)))
  for deriv,k in [('MD5',hashlib.md5(raw).digest()),('SHA256',hashlib.sha256(raw).digest())]:
   for mode,param,data in [('ECB','none',b),('CBC','zero-IV',b),('CTR','zero-counter',b),('CBC','prefix16-IV',b[16:]),('CTR','prefix16-counter',b[16:])]:
    nonce=b[:16] if param.startswith('prefix') else bytes(16);m=modes.ECB() if mode=='ECB' else modes.CBC(nonce) if mode=='CBC' else modes.CTR(nonce)
    jobs.append(dict(method='AES-'+mode,key_id=ki,derivation=deriv,iv_nonce_hex=None if mode=='ECB' else nonce.hex(),parameter=param,output=crypt(k,m,data)))
 top=[];leads=[];t=time.monotonic()
 with gzip.open(OUT/'R08-scores.jsonl.gz','wt') as f:
  for i,j in enumerate(jobs):
   out=j.pop('output');counts=collections.Counter(out);entropy=-sum(n/len(out)*math.log2(n/len(out)) for n in counts.values());pf=sum(x in (9,10,13) or 32<=x<127 for x in out)/len(out);structures=inspect(out);row=dict(id=i,**j,printable_fraction=pf,entropy=entropy,structures=structures,length=len(out),sha256=hashlib.sha256(out).hexdigest());f.write(json.dumps(row)+'\n');row['output_hex']=out.hex();row['text_preview']=out.decode('ascii','backslashreplace');row['status']='UNREVIEWED'
   if structures:leads.append(row)
   top.append(row);top.sort(key=lambda x:(bool(x['structures']),x['printable_fraction'],-x['entropy']),reverse=True);top=top[:20]
 save(OUT/'R08-results.json',dict(completed=len(jobs),keys=len(keys),seconds=time.monotonic()-t,top=top,structural_leads=leads,controls='AES ECB/CBC/CTR known answers, RC4 known answer, complete zlib checksum and corrupted/bomb controls passed',coverage='corrected payload; historical-inspired small cipher matrix. Zero and prefix IVs explicit hypotheses, not inferred structure. Capped decompression 65536 bytes, full consumption/eof required; no recovered execution.'));print('R08 DONE',len(jobs),len(keys),'structures',len(leads))
if __name__=='__main__':main()
