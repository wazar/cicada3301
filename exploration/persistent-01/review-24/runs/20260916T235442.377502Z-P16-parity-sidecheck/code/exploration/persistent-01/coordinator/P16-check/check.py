from pathlib import Path
import json,hashlib,functools,operator
R=Path('exploration/persistent-01/worker-p/P16');O=Path(__file__).parent;b=(R/'input.bin').read_bytes();d=json.loads((R/'actual.json').read_text());assert len(b)==256 and hashlib.sha256(b).hexdigest()=='3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290'
def mul(a,b):
 z=0
 while b:
  if b&1:z^=a
  b>>=1;a<<=1
  if a&256:a^=0x11d
 return z
def power(x,n):
 y=1
 for _ in range(n):y=mul(y,x)
 return y
s=[functools.reduce(operator.xor,(mul(v,power(x,k)) for x,v in enumerate(b)),0) for k in range(32)];assert s==d['syndromes'];parity=functools.reduce(operator.xor,b,0);assert parity==148==s[0] and d['coefficients'][-1]==148
# Every proper monomial (including constant) has zero sum across this whole field.
monomial_sums=[functools.reduce(operator.xor,(power(x,k) for x in range(256)),0) for k in range(256)];assert monomial_sums==[0]*255+[1]
coeff=d['coefficients']
for x,v in enumerate(b):
 z=0
 for a in reversed(coeff):z=mul(z,x)^a
 assert z==v
r=dict(status='PASS',input_sha256=hashlib.sha256(b).hexdigest(),syndromes=s,all256_evaluations=True,all256_monomial_sums=monomial_sums,byte_xor=parity,necessary_bound='Nonzero XOR rules out unweighted complete GF256 evaluation of any polynomial degree<=254, independent of ordering and linear byte basis. Does not cover column multipliers, puncturing, arbitrary nonlinear labels or damaged words.');(O/'results.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS XOR',parity,'all32 checks and256evaluations')
