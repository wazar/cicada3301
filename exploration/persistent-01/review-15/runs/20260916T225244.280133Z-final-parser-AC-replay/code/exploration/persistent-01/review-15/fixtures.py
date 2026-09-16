import pathlib,io,json,zlib,struct,hashlib
from PIL import Image
from independent import inspect
R=pathlib.Path(__file__).parent;F=R/'fixtures';F.mkdir(exist_ok=True);results=[]
for mode,sub in [('RGB',2),('RGB',0),('L',0)]:
 im=Image.new(mode,(17,19));im.putdata([((j*37)%256,(j*59)%256,(j*11)%256) if mode=='RGB' else (j*37)%256 for j in range(17*19)]);path=F/f'{mode}-{sub}.jpg';im.save(path,quality=92,subsampling=sub);base=inspect(path);payload=b'review15\x00\xff\x01entropy-tail';frame=b'R15T'+len(payload).to_bytes(2,'big')+payload+zlib.crc32(payload).to_bytes(4,'big');stuffed=frame.replace(b'\xff',b'\xff\x00');raw=path.read_bytes();mut=F/f'{mode}-{sub}-tail.jpg';mut.write_bytes(raw[:base['eoi_offset']]+stuffed+raw[base['eoi_offset']:]);got=inspect(mut);assert bytes.fromhex(got['tail_unstuffed_hex'])==frame;assert got['consumed_bits']==base['consumed_bits'];assert Image.open(path).tobytes()==Image.open(mut).tobytes();results.append({'mode':mode,'subsampling':sub,'original':base,'mutated':got,'frame_hex':frame.hex(),'pixel_identity':True})
# Explicit nonbaseline handling: reject a progressive synthetic image.
prog=F/'progressive.jpg';im.convert('RGB').save(prog,progressive=True)
try:inspect(prog)
except ValueError as e:assert str(e)=='unsupported nonbaseline frame';progressive=True
else:raise AssertionError('progressive accepted')
# Fail explicitly on restart declaration; no pretending restart support.
raw=(F/'RGB-2.jpg').read_bytes();restart=F/'declared-restart.jpg';restart.write_bytes(raw[:2]+b'\xff\xdd\x00\x04\x00\x01'+raw[2:])
try:inspect(restart)
except AssertionError as e:assert str(e)=='restart unsupported in this independent implementation';dri=True
else:raise AssertionError('DRI accepted')
out={'fixtures':results,'progressive_rejected':progressive,'restart_declared_rejected':dri};(R/'fixture-results.json').write_text(json.dumps(out,indent=2));print(json.dumps({'pixel_identical_tail_fixtures':len(results),'progressive_rejected':progressive,'restart_declared_rejected':dri}))
