import pathlib,json
from independent_jsteg import inspect
from header_controls import header_read
R=pathlib.Path(__file__).parent;P=R.parent/'worker-p/P11';z=inspect(P/'jpeg-control.jpg');packed=(R/'jpeg-control-eligible-bits.bin').read_bytes();bits=''.join(f'{x:08b}' for x in packed)[:z['eligible_count']];h=header_read(bits);assert h['status']=='complete' and bytes.fromhex(h['payload_hex'])==(P/'payload-127.bin').read_bytes();out={'independent_entropy_and_header_recovered_127_bytes':True,'eligible':z['eligible_count'],'payload_header':{k:v for k,v in h.items() if k!='payload_hex'},'image_sha256':z['sha256']};(R/'jpeg-control-check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
