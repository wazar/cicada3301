import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import subprocess,json,hashlib,time,sys,zlib,gzip,struct,datetime,re
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];B=R/'exploration/persistent-01';W=B/'worker-p';O=W/'P28';BIN=W/'private-P28/resurrecting-open-source-projects-outguess-24810e1/src/outguess';KEYS=[None,'3301','33011033','circumference','firfumferenfe','welcome','instar','pilgrim'];MAGIC=b'P28-CONTROL\x00'
def guard():
 assert not (B/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
def run(label,args):
 guard();cmd=[str(BIN)]+[str(a) for a in args];t=time.monotonic()
 try:p=subprocess.run(cmd,capture_output=True,timeout=120);code=p.returncode;out=p.stdout;err=p.stderr;status='EXIT'
 except subprocess.TimeoutExpired as e:code=None;out=e.stdout or b'';err=e.stderr or b'';status='TIMEOUT'
 (O/(label+'.stdout')).write_bytes(out);(O/(label+'.stderr')).write_bytes(err);r=dict(label=label,command=cmd,binary_sha256=sha(BIN),exit_code=code,status=status,seconds=time.monotonic()-t);save(label+'.command.json',r);return r

def validate(b):
 frame=False
 if b.startswith(MAGIC) and len(b)>=len(MAGIC)+4+32:
  n=int.from_bytes(b[len(MAGIC):len(MAGIC)+4],'big');data=b[len(MAGIC)+4:-32];frame=len(data)==n and hashlib.sha256(data).digest()==b[-32:]
 formats={}
 for label,w in [('zlib',15),('gzip',31)]:
  try:
   z=zlib.decompressobj(w);d=z.decompress(b,10000000);d+=z.flush();ok=z.eof and not z.unused_data and not z.unconsumed_tail
   formats[label]=dict(valid_complete=bool(ok),decoded_bytes=len(d),decoded_sha256=hashlib.sha256(d).hexdigest())
  except zlib.error:formats[label]=dict(valid_complete=False)
 armor=bool(b.startswith(b'-----BEGIN PGP ') and re.search(br'-----END PGP (?:SIGNATURE|MESSAGE|PUBLIC KEY BLOCK)-----\s*$',b))
 return dict(checksum_frame=frame,compression=formats,complete_pgp_armor_shape=armor,authenticated=False)
def extract(label,image,key):
 out=O/(label+'.bin');args=(['-k',key] if key is not None else [])+['-r',image,out];r=run(label,args);r.update(input=str(image.relative_to(R)),input_sha256=sha(image),key=key,output_exists=out.exists(),output_bytes=out.stat().st_size if out.exists() else None,output_sha256=sha(out) if out.exists() else None)
 if out.exists():r['format']=validate(out.read_bytes())
 save(label+'.result.json',r);return r
def source(page):
 p=R/f'liber-primus/data/relikd/p{page:02d}.jpg'
 if not p.exists():p=R/f'liber-primus/data/relikd/p{page}.jpg'
 expected=json.loads((W/'P10/actual-0.json').read_text())['sha256'] if page==0 else next(x['sha256'] for x in json.loads((W/'P12/inventory.json').read_text())['rows'] if x['page']==26)
 assert sha(p)==expected;return p

def controls():
 # Independent format fixtures, including damaged/truncated checksums and no concatenation acceptance.
 data=bytes(range(256));frame=MAGIC+len(data).to_bytes(4,'big')+data+hashlib.sha256(data).digest();(O/'known-message.bin').write_bytes(frame)
 assert validate(frame)['checksum_frame'] and not validate(frame[:-1])['checksum_frame'] and not validate(frame[:-1]+bytes([frame[-1]^1]))['checksum_frame']
 assert validate(zlib.compress(data))['compression']['zlib']['valid_complete'];assert not validate(zlib.compress(data)+b'X')['compression']['zlib']['valid_complete'];assert validate(gzip.compress(data,mtime=0))['compression']['gzip']['valid_complete']
 hist=B/'review-48/4gq25.jpg';expected=B/'review-48/4gq25.jpg.outguess';r=extract('historical',hist,None);assert r['exit_code']==0 and (O/'historical.bin').read_bytes()==expected.read_bytes()
 inp=source(0);copy=O/'original0-copy.jpg';copy.write_bytes(inp.read_bytes());rows=[]
 for i,key in enumerate(KEYS):
  carrier=O/f'plant-{i}.jpg';cmd=(['-k',key] if key is not None else [])+['-p','92','-d',O/'known-message.bin',copy,carrier];emb=run(f'plant-{i}-embed',cmd);assert emb['exit_code']==0 and carrier.exists()
  rec=extract(f'plant-{i}-extract',carrier,key);assert rec['exit_code']==0 and (O/f'plant-{i}-extract.bin').read_bytes()==frame and rec['format']['checksum_frame'];rows.append(dict(key=key,carrier_sha256=sha(carrier),embed=emb,extract=rec))
 save('controls-summary.json',dict(historical=r,own_controls=rows,known_message_sha256=sha(O/'known-message.bin'),format_controls_pass=True,original_unchanged=sha(inp)==sha(copy)))
 print('ALL HISTORICAL/EIGHT OWN/FORMAT CONTROLS PASS',flush=True)
def actual():
 assert (O/'controls-summary.json').exists();rows=[]
 for p in [0,26]:
  for i,k in enumerate(KEYS):rows.append(extract(f'actual-{p}-key-{i}',source(p),k))
 icc=Image.open(source(0)).info['icc_profile'];(O/'source.icc').write_bytes(icc)
 sur=[]
 for label in ['blank','line-art']:
  im=Image.new('RGB',(2400,3600),'white')
  if label=='line-art':
   draw=ImageDraw.Draw(im)
   for y in range(600,3000,80):
    for x in range(400,2000,50):
     draw.line([(x,y+50),(x,y),(x+25,y+25),(x,y+50)],fill='black',width=4)
  path=O/(label+'.jpg');im.save(path,quality=92,optimize=True,subsampling=2,dpi=(400,400),icc_profile=icc);sur.append(extract(label,path,None))
 files=[O/'actual-0-key-0.bin',O/'actual-26-key-0.bin',O/'blank.bin',O/'line-art.bin'];comparisons=[]
 for i,p in enumerate(files):
  for q in files[i+1:]:
   if not p.exists() or not q.exists():comparisons.append(dict(a=p.name,b=q.name,status='OUTPUT_MISSING'));continue
   a,b=p.read_bytes(),q.read_bytes();n=next((j for j,(x,y) in enumerate(zip(a,b)) if x!=y),min(len(a),len(b)));comparisons.append(dict(a=p.name,b=q.name,common_prefix=n,bytes_a=len(a),bytes_b=len(b),full_equal=a==b,position_equal=sum(x==y for x,y in zip(a,b))))
 save('summary.json',dict(actual=rows,surrogates=sur,prefix_comparisons=comparisons,original_hashes=[dict(page=p,sha256=sha(source(p))) for p in [0,26]]));print(json.dumps(dict(actual_outputs=[(x['label'],x['exit_code'],x['output_bytes']) for x in rows],surrogates=[(x['label'],x['exit_code'],x['output_bytes']) for x in sur],prefixes=comparisons)),flush=True)
if __name__=='__main__':
 guard();{'controls':controls,'actual':actual}[sys.argv[1]]()
