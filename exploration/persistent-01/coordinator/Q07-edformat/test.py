from pathlib import Path
import urllib.request,hashlib,json,datetime,importlib.metadata
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey,Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
O=Path(__file__).resolve().parent;ROOT=O.parents[3]
p=2**255-19;l=2**252+27742317777372353535851937790883648493;d=(-121665*pow(121666,-1,p))%p;I=(0,1)
def add(a,b):
 x,y=a;u,v=b;t=d*x*u*y*v%p
 return ((x*v+y*u)*pow((1+t)%p,-1,p)%p,(y*v+x*u)*pow((1-t)%p,-1,p)%p)
def mul(n,a):
 q=I
 while n:
  if n&1:q=add(q,a)
  a=add(a,a);n>>=1
 return q
def point(b):
 assert len(b)==32
 n=int.from_bytes(b,'little');sign=n>>255;y=n&((1<<255)-1)
 r=dict(hex=b.hex(),y=y,sign=sign,canonical=False,curve=False,prime_subgroup=False,nonidentity=False)
 if y>=p:r['reason']='noncanonical_y';return r
 den=(d*y*y+1)%p
 if den==0:r['reason']='zero_denominator';return r
 xx=(y*y-1)*pow(den,-1,p)%p;x=pow(xx,(p+3)//8,p)
 if x*x%p!=xx:x=x*pow(2,(p-1)//4,p)%p
 if x*x%p!=xx:r['reason']='nonsquare_x2';return r
 if x==0 and sign:r['reason']='noncanonical_zero_x_sign';return r
 if x%2!=sign:x=p-x
 assert (-x*x+y*y-1-d*x*x*y*y)%p==0
 a=(x,y);q=mul(l,a);r.update(canonical=True,curve=True,x=x,l_times=list(q),prime_subgroup=q==I,nonidentity=a!=I,reason='decoded')
 return r
def signature(b):
 assert len(b)==64
 r=point(b[:32]);s=int.from_bytes(b[32:],'little');return dict(hex=b.hex(),R=r,S=s,scalar_canonical=s<l,necessary_format=r['canonical'] and r['prime_subgroup'] and s<l)
def check_fixture(seed,msg,pk=None,sig=None):
 k=Ed25519PrivateKey.from_private_bytes(seed);actualpk=k.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw);actualsig=k.sign(msg)
 if pk is not None:assert actualpk==pk
 if sig is not None:assert actualsig==sig
 Ed25519PublicKey.from_public_bytes(actualpk).verify(actualsig,msg)
 q=point(actualpk);r=signature(actualsig);assert q['prime_subgroup'] and q['nonidentity'] and r['necessary_format']
 return dict(public_test_seed=seed.hex(),message_hex=msg.hex(),public=q,signature=r)
url='https://www.rfc-editor.org/rfc/rfc8032.txt'
with urllib.request.urlopen(url,timeout=30) as response:raw=response.read();final_url=response.url;status=response.status
(O/'rfc8032.txt').write_bytes(raw);(O/'retrieval.json').write_text(json.dumps(dict(url=url,final_url=final_url,status=status,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw)),indent=2)+'\n')
vectors=[('9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60','d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a','','e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b'),('4ccd089b28ff96da9db6c346ec114e0f5b8a319f35aba624da8cf6ed4fb8a6fb','3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c','72','92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00')]
compact=''.join(raw.decode().split()).lower();controls=[]
for sk,pk,msg,sig in vectors:
 for h in [sk,pk,sig]:assert h in compact
 controls.append(check_fixture(bytes.fromhex(sk),bytes.fromhex(msg),bytes.fromhex(pk),bytes.fromhex(sig)))
for i in range(8):controls.append(check_fixture(hashlib.sha256(f'Q07 PUBLIC TEST SEED {i}'.encode()).digest(),f'Q07 public control message {i}'.encode()))
negatives=[point(p.to_bytes(32,'little')),point((1+(1<<255)).to_bytes(32,'little')),point((p-1).to_bytes(32,'little'))]
assert not negatives[0]['canonical'] and not negatives[1]['canonical'] and negatives[2]['curve'] and not negatives[2]['prime_subgroup']
bad=signature(bytes.fromhex(vectors[0][3])[:32]+l.to_bytes(32,'little'));assert not bad['necessary_format'] and not bad['scalar_canonical'];negatives.append(bad)
(O/'controls.json').write_text(json.dumps(dict(positive=controls,negative=negatives,cryptography_version=importlib.metadata.version('cryptography')),indent=2)+'\n');print(json.dumps(dict(controls='PASS',positives=len(controls),negative_cases=len(negatives))),flush=True)
source=ROOT/'exploration/persistent-01/worker-p/P16/input.bin';b=source.read_bytes();assert len(b)==256 and hashlib.sha256(b).hexdigest()=='3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290'
keys=[dict(offset=i,**point(b[i:i+32])) for i in range(0,256,32)];sigs=[dict(offset=i,**signature(b[i:i+64])) for i in range(0,256,64)]
out=dict(source=str(source.relative_to(ROOT)),sha256=hashlib.sha256(b).hexdigest(),eight_keys=all(q['canonical'] and q['prime_subgroup'] and q['nonidentity'] for q in keys),four_signatures=all(q['necessary_format'] for q in sigs),keys=keys,signatures=sigs)
(O/'actual.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(eight_keys=out['eight_keys'],four_signatures=out['four_signatures'],valid_curve_key_offsets=[q['offset'] for q in keys if q['curve']],prime_subgroup_key_offsets=[q['offset'] for q in keys if q['prime_subgroup']],canonical_scalar_offsets=[q['offset']+32 for q in sigs if q['scalar_canonical']])))
