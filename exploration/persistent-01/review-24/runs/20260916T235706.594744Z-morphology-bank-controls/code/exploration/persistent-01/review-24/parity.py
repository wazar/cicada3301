from pathlib import Path
import json,hashlib
R=Path(__file__).parent;P=R.parent/'worker-p/P16/input.bin';b=P.read_bytes();assert len(b)==256
h=hashlib.sha256(b).hexdigest();assert h=='3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290'
counts=[sum((v>>i)&1 for v in b) for i in range(8)];parity=sum((n%2)<<i for i,n in enumerate(counts));assert parity==148
(R/'parity.json').write_text(json.dumps({'status':'PASS','sha256':h,'bytes':len(b),'bit_counts_lsb_first':counts,'xor_from_bit_parities':parity},indent=2));print('PASS',counts,parity)
