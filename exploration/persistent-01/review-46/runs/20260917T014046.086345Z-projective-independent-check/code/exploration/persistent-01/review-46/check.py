from pathlib import Path
import json,hashlib
R=Path(__file__).parent;Q=R.parent/'coordinator/Q07-edformat';p=2**255-19;n=2**252+27742317777372353535851937790883648493;d=-121665*pow(121666,p-2,p)%p;O=(0,1,1,0)
def add(P,Q):
 x,y,z,t=P;u,v,w,s=Q;A=(y-x)*(v-u)%p;B=(y+x)*(v+u)%p;C=2*d*t*s%p;D=2*z*w%p;E=(B-A)%p;F=(D-C)%p;G=(D+C)%p;H=(B+A)%p;return E*F%p,G*H%p,F*G%p,E*H%p
def mul(k,P):
 a=O;b=P
 for bit in bin(k)[2:]:
  if bit=='0':b=add(a,b);a=add(a,a)
  else:a=add(a,b);b=add(b,b)
 return a
def affine(P):
 x,y,z,t=P;zi=pow(z,p-2,p);assert z and (x*y-z*t)%p==0;return x*zi%p,y*zi%p
def sqrt(a):
 if a==0:return 0
 if pow(a,(p-1)//2,p)!=1:return None
 q=p-1;s=0
 while q%2==0:q//=2;s+=1
 z=2
 while pow(z,(p-1)//2,p)!=p-1:z+=1
 c=pow(z,q,p);x=pow(a,(q+1)//2,p);t=pow(a,q,p);m=s
 while t!=1:
  j=1;tt=t*t%p
  while tt!=1:tt=tt*tt%p;j+=1
  b=pow(c,1<<(m-j-1),p);x=x*b%p;t=t*b*b%p;c=b*b%p;m=j
 return x
def decode(b):
 raw=int.from_bytes(b,'little');y=raw%(1<<255);sign=raw>>255
 if y>=p:return None,'noncanonical_y'
 denom=(d*y*y+1)%p
 if denom==0:return None,'zero_denominator'
 x=sqrt((y*y-1)*pow(denom,p-2,p)%p)
 if x is None:return None,'nonsquare_x2'
 if x==0 and sign:return None,'noncanonical_zero_x_sign'
 if x%2!=sign:x=(-x)%p
 assert (y*y-x*x-1-d*x*x*y*y)%p==0
 return (x,y,1,x*y%p),'decoded'
def encode(P):
 x,y=affine(P);return (y+((x%2)<<255)).to_bytes(32,'little')
checks=0
def check_point(r):
 global checks
 checks+=1;P,reason=decode(bytes.fromhex(r['hex']));assert reason==r['reason'];assert bool(P is not None)==r['canonical']==r['curve']
 if P is not None:
  x,y=affine(P);L=affine(mul(n,P));assert x==r['x'] and y==r['y'] and list(L)==r['l_times'] and (L==(0,1))==r['prime_subgroup'] and ((x,y)!=(0,1))==r['nonidentity']
 return P
def check_sig(r):
 point=check_point(r['R']);b=bytes.fromhex(r['hex']);s=int.from_bytes(b[32:],'little');assert s==r['S'] and (s<n)==r['scalar_canonical'];assert r['necessary_format']==bool(point is not None and affine(mul(n,point))==(0,1) and s<n)
 return point,s
base,_=decode(bytes.fromhex('5866666666666666666666666666666666666666666666666666666666666666'));assert affine(mul(n,base))==(0,1)
controls=json.loads((Q/'controls.json').read_text());rfc=(Q/'rfc8032.txt').read_bytes();retr=json.loads((Q/'retrieval.json').read_text());assert hashlib.sha256(rfc).hexdigest()==retr['sha256'] and len(rfc)==retr['bytes'];compact=''.join(rfc.decode().split()).lower()
for i,c in enumerate(controls['positive']):
 seed=bytes.fromhex(c['public_test_seed']);msg=bytes.fromhex(c['message_hex']);A=check_point(c['public']);Rp,S=check_sig(c['signature']);pk=bytes.fromhex(c['public']['hex']);sig=bytes.fromhex(c['signature']['hex']);h=bytearray(hashlib.sha512(seed).digest());h[0]&=248;h[31]&=63;h[31]|=64;a=int.from_bytes(h[:32],'little');assert encode(mul(a,base))==pk;r=int.from_bytes(hashlib.sha512(bytes(h[32:])+msg).digest(),'little')%n;rr=encode(mul(r,base));challenge=int.from_bytes(hashlib.sha512(rr+pk+msg).digest(),'little')%n;assert rr+((r+challenge*a)%n).to_bytes(32,'little')==sig;assert affine(mul(S,base))==affine(add(Rp,mul(challenge,A)))
 if i<2:assert c['public_test_seed'] in compact and pk.hex() in compact and sig.hex() in compact
 else:assert seed==hashlib.sha256(f'Q07 PUBLIC TEST SEED {i-2}'.encode()).digest() and msg==f'Q07 public control message {i-2}'.encode()
for c in controls['negative']:
 if 'R' in c:check_sig(c)
 else:check_point(c)
a=json.loads((Q/'actual.json').read_text());source=Path(a['source']);b=source.read_bytes();assert len(b)==256 and hashlib.sha256(b).hexdigest()==a['sha256']=='3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290'
for i,r in enumerate(a['keys']):assert r['offset']==32*i and r['hex']==b[32*i:32*i+32].hex();check_point(r)
for i,r in enumerate(a['signatures']):assert r['offset']==64*i and r['hex']==b[64*i:64*i+64].hex();check_sig(r)
keys=all(r['canonical'] and r['prime_subgroup'] and r['nonidentity'] for r in a['keys']);sigs=all(r['necessary_format'] for r in a['signatures']);assert keys==a['eight_keys']==False and sigs==a['four_signatures']==False
out=dict(status='PASS',point_records=checks,independently_signed_controls=10,negative_cases=4,curve_offsets=[r['offset'] for r in a['keys'] if r['curve']],prime_subgroup_offsets=[r['offset'] for r in a['keys'] if r['prime_subgroup']],canonical_scalar_offsets=[r['offset']+32 for r in a['signatures'] if r['scalar_canonical']],eight_keys=keys,four_signatures=sigs)
(R/'result.json').write_text(json.dumps(out,indent=2));print(out)
