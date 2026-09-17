from pathlib import Path
import ast,json,hashlib,numpy as np
R=Path(__file__).parent;tree=ast.parse((R/'check.py').read_text());node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='ARC');exec(compile(ast.Module(body=[node],type_ignores=[]),'own_review_ARC','exec'));out=[]
for rec in json.loads((R/'result.json').read_text())['records']:
 fail=rec['iterator_first_failure']
 if not fail or fail['kind']!='zero_skip_modulus':continue
 key=b'circumference' if rec['label'].endswith('-3') else b'pilgrim';a=ARC(b'Seeding',key);pos=a.word()%32
 for _ in range(32):pos+=a.word()%32+1
 a.mix(rec['seed'].to_bytes(2,'little'));bits=rec['usable_bits']
 for j in range(fail['body_byte']):
  rem=bits-pos;lim=bits//32;adj=np.float32(2) if rem>lim else np.float32(2)-np.float32(lim-rem)/np.float32(lim);skip=int(np.float32(adj*np.float32(rem))/np.float32(8*(rec['length']-j)));assert skip>0
  for k in range(8):pos+=a.word()%skip+1
 assert pos==fail['bit_offset'];word=a.word();nextpos=(pos+word+1)%(1<<32);byteaddr=nextpos//8;assert byteaddr>=(bits+7)//8;out.append(dict(label=rec['label'],random_word=word,next_unsigned_bit_index=nextpos,next_read_byte_offset=byteaddr,bitmap_bytes=(bits+7)//8,mechanism='UDIV zero gives0; MSUB returns randomword; ADD wraps32bits; next unchecked LDRB far outsidebitmap'))
(R/'arm-next-result.json').write_text(json.dumps(out,indent=2));print(out)
