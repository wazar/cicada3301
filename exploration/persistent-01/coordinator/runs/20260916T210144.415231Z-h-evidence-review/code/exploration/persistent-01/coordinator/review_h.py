from pathlib import Path
import json,gzip,hashlib,zlib,bz2,lzma
R=Path(__file__).resolve().parents[3];P=R/'exploration/persistent-01';H=P/'worker-h/publication-cycle1';O=Path(__file__).resolve().parent
load=lambda n:json.loads((H/n).read_text())
def tail(x,ns):return (1+sum(v>=x for v in ns))/(len(ns)+1)
checks={}
for tag in ['H01','H03']:
 r=load(tag+'-result.json');e=json.loads(gzip.decompress((H/(tag+'-evidence.json.gz')).read_bytes()))
 ns=e['null']
 if tag=='H01':print('H01 null element',ns[0])
 target=r['max_exact_units'] if tag=='H01' else r['score']
 got=tail(target,ns);assert got==r['tail'];checks[tag]={'tail':got,'nulls':len(ns)}
for tag in ['H05','H06','H07']:
 r=load(tag+'-result.json');got=tail(r['score'],r['null']);assert got==r['tail'];checks[tag]={'tail':got,'nulls':len(r['null'])}
# No shared packing or recognition function imported.
M=json.loads((P/'worker-f/F06-maps.json').read_text());counts=dict(nominal=0,overflow=0,too_short=0);seen=set();hits=[]
for m in M:
 lengths=[w['end']-w['start'] for w in m['words']]
 for b in [2,5]:
  possible=b**len(lengths);w=0
  while 256**(w+1)<=possible:w+=1
  for origin in range(b):
   for direction in [1,-1]:
    digits=[(v-origin)%b for v in lengths][::direction]
    n=sum(v*b**(len(digits)-1-i) for i,v in enumerate(digits))
    for endian in ['big','little']:
     counts['nominal']+=1
     if w<5:counts['too_short']+=1;continue
     if n>=256**w:counts['overflow']+=1;continue
     record=n.to_bytes(w,endian);seen.add(record)
for raw in seen:
 for order in ['big','little']:
  if zlib.crc32(raw[:-4])==int.from_bytes(raw[-4:],order):hits.append(['crc32',raw.hex()])
 for fmt in ['zlib','gzip','bz2','xz']:
  try:
   if fmt in ['zlib','gzip']:
    obj=zlib.decompressobj(15 if fmt=='zlib' else 31);decoded=obj.decompress(raw,65537);accepted=obj.eof and not obj.unused_data and not obj.unconsumed_tail
   elif fmt=='bz2':
    obj=bz2.BZ2Decompressor();decoded=obj.decompress(raw,max_length=65537);accepted=obj.eof and not obj.unused_data
   else:
    obj=lzma.LZMADecompressor(format=lzma.FORMAT_XZ,memlimit=64*1024*1024);decoded=obj.decompress(raw,max_length=65537);accepted=obj.eof and not obj.unused_data and obj.check not in [lzma.CHECK_NONE,lzma.CHECK_UNKNOWN]
   if accepted and 0<len(decoded)<=65536:hits.append([fmt,raw.hex()])
  except (ValueError,EOFError,zlib.error,OSError,lzma.LZMAError):pass
r=load('H10-result.json');assert all(counts[k]==r['real_counts'][k] for k in counts);assert len(seen)==r['real_unique_bytes'];assert hits==r['real_hits']==[];assert r['null_hitcounts']==[0]*999
checks['H10']=dict(counts=counts,unique_bytes=len(seen),hits=hits,record_sha256=hashlib.sha256(b''.join(sorted(seen))).hexdigest())
archive=load('MANIFEST.json')
for e in archive['entries']:
 raw=(R/e['publication']).read_bytes();assert hashlib.sha256(raw).hexdigest()==e['publication_sha256']
checks['archive_files']=len(archive['entries']);checks['limits']='Saved-tail recount, independent packing/CRC and same standard-library parser APIs. No null regeneration, no complete source authenticity/transcription audit; not strong independence from common library behavior.'
(O/'H-review.json').write_text(json.dumps(checks,indent=2)+'\n');print(json.dumps(checks,indent=2))
