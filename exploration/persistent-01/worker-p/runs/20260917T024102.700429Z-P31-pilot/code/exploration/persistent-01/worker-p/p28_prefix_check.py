from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];B=R/'exploration/persistent-01';O=B/'worker-p/P28';key=(B/'review-48/default-encryption-keystream.bin').read_bytes();expect=bytes(x^255 for x in key);rows=[]
for name in ['actual-0-key-0','actual-26-key-0','line-art']:
 b=(O/(name+'.bin')).read_bytes();n=next((j for j,(x,y) in enumerate(zip(b,expect)) if x!=y),min(len(b),len(expect)));rows.append(dict(name=name,prefix_matching_not_keystream=n,compared_length=min(len(b),len(expect)),keystream_sha256=hashlib.sha256(key).hexdigest()))
(O/'constant-bit-prefix-check.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
