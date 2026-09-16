import pathlib,json,zlib,hashlib
from PIL import Image
from independent import inspect
R=pathlib.Path(__file__).parent;P=R.parent/'worker-p/P10';frame=(P/'control-frame.bin').read_bytes();payload=(P/'payload.bin').read_bytes();assert frame[:8]==b'LP10TAIL' and int.from_bytes(frame[8:12],'big')==len(payload) and frame[12:-4]==payload and int.from_bytes(frame[-4:],'big')==zlib.crc32(payload)
out=[]
for idx in range(16):
 clean=P/f'control-{idx}-clean.jpg';plant=P/f'control-{idx}-planted.jpg';a=inspect(clean);b=inspect(plant);assert a['tail_bytes']==0;assert bytes.fromhex(b['tail_unstuffed_hex'])==frame;assert a['consumed_bits']==b['consumed_bits'];assert Image.open(clean).tobytes()==Image.open(plant).tobytes();out.append({'index':idx,'bits':a['consumed_bits'],'blocks':a['dc_symbols'],'pad':a['final_pad_bits'],'frame_sha256':hashlib.sha256(frame).hexdigest(),'payload_crc32':zlib.crc32(payload),'pixel_identity':True})
reject={}
for file in ['invalid-allones-dht.jpg','invalid-truncated.jpg','unsupported-multiscan-header.jpg','unsupported-progressive.jpg','unsupported-restart-header.jpg']:
 try:inspect(P/file)
 except (AssertionError,ValueError,IndexError,KeyError) as e:reject[file]={'rejected':True,'error_type':type(e).__name__,'message':str(e)}
 else:raise AssertionError('accepted invalid '+file)
pad=inspect(P/'noncanonical-padding.jpg');assert '0' in pad['final_pad_bits']
(R/'p-fixture-check.json').write_text(json.dumps({'controls':out,'rejections':reject,'noncanonical_pad':pad['final_pad_bits']},indent=2));print(json.dumps({'independent_control_replays':len(out),'rejections':len(reject),'noncanonical_padding_flagged':True}))
