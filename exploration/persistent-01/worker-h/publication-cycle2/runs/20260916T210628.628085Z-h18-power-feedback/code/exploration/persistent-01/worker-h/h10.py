import pathlib,json,zlib,bz2,lzma,hashlib,random,datetime,base64
R=pathlib.Path(__file__).parent;M=json.load(open(R.parent/'worker-f/F06-maps.json'));L=[[w['end']-w['start'] for w in m['words']] for m in M];rng=random.Random(2026091730);cap=65536
counts={'nominal':0,'overflow':0,'too_short':0,'unique_parser_calls':0};digest=hashlib.sha256()
def gate():
 assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def recognize(b):
 hits=[]
 if len(b)>=5:
  crc=zlib.crc32(b[:-4])
  for order in ['big','little']:
   if int.from_bytes(b[-4:],order)==crc:hits.append(dict(format='crc32-'+order,payload_hex=b[:-4].hex()))
 for fmt in ['zlib','gzip','bz2','xz']:
  try:
   if fmt in ['zlib','gzip']:
    d=zlib.decompressobj(15 if fmt=='zlib' else 31);p=d.decompress(b,cap+1)
    ok=d.eof and not d.unused_data and not d.unconsumed_tail
   elif fmt=='bz2':
    d=bz2.BZ2Decompressor();p=d.decompress(b,max_length=cap+1);ok=d.eof and not d.unused_data
   else:
    d=lzma.LZMADecompressor(format=lzma.FORMAT_XZ,memlimit=64*1024*1024);p=d.decompress(b,max_length=cap+1);ok=d.eof and not d.unused_data and d.check not in [lzma.CHECK_NONE,lzma.CHECK_UNKNOWN]
   if ok and 0<len(p)<=cap:hits.append(dict(format=fmt,payload_hex=p.hex()))
  except (ValueError,EOFError,zlib.error,OSError,lzma.LZMAError):pass
 return hits
def width(n,b):return (b**n).bit_length()//8 if b!=2 else n//8
# floor(log256(base**n)); power-of-256 exactboundary handled explicitly.
def width(n,b):
 v=b**n;w=0
 while 256**(w+1)<=v:w+=1
 return w
def scan(seqs):
 found=[];seen={}
 for pi,x in enumerate(seqs):
  for b in [2,5]:
   w=width(len(x),b)
   for origin in range(b):
    digits=[(v-origin)%b for v in x]
    for reverse in [False,True]:
     ds=digits[::-1] if reverse else digits;n=0
     for d in ds:n=n*b+d
     for endian in ['big','little']:
      counts['nominal']+=1
      if w<5:counts['too_short']+=1;continue
      if n>=256**w:counts['overflow']+=1;continue
      raw=n.to_bytes(w,endian);digest.update(raw)
      if raw not in seen:counts['unique_parser_calls']+=1;seen[raw]=recognize(raw)
      if seen[raw]:found.append(dict(page_index=pi,base=b,origin=origin,reverse=reverse,endian=endian,record_hex=raw.hex(),recognizers=seen[raw]))
 return found,len(seen)
# Strict parsercontrols include actualcompleteformats and badvariants.
parser=[]
for fmt,b in [('zlib',zlib.compress(b'LIBER')),('gzip',zlib.compress(b'LIBER',wbits=31)),('bz2',bz2.compress(b'LIBER')),('xz',lzma.compress(b'LIBER',format=lzma.FORMAT_XZ,check=lzma.CHECK_CRC64))]:
 assert any(h['format']==fmt for h in recognize(b))
 bad=b[:-5]+bytes([b[-5]^1])+b[-4:]
 for label,raw in [('corrupt',bad),('truncated',b[:-1]),('trailing',b+b'x')]:assert not any(h['format']==fmt for h in recognize(raw)),(fmt,label)
 parser.append(dict(format=fmt,valid_hex=b.hex(),corrupt_hex=bad.hex(),passed=True))
for raw in [lzma.compress(b'LIBER',format=lzma.FORMAT_XZ,check=lzma.CHECK_NONE),lzma.compress(b'LIBER',format=lzma.FORMAT_ALONE),zlib.compress(b'A'*(cap+1))]:assert not recognize(raw)
controls=[]
def plant(raw,b,origin,reverse):
 pi=next(i for i,x in enumerate(L) if width(len(x),b)==len(raw));n=int.from_bytes(raw,'big');ds=[]
 for _ in L[pi]:ds.append(n%b);n//=b
 assert n==0;ds=ds[::-1]
 if reverse:ds=ds[::-1]
 x=[v+((d+origin-v)%b) for v,d in zip(L[pi],ds)];got,unique=scan([x]);assert any(h['record_hex']==raw.hex() for h in got)
 controls.append(dict(original_page=M[pi]['page'],base=b,origin=origin,reverse=reverse,lengths=x,record_hex=raw.hex(),recovered=True,hits=got))
for b in [2,5]:
 w=next(width(len(x),b) for x in L if width(len(x),b)>=5);payload=bytes(range(w-4));raw=payload+zlib.crc32(payload).to_bytes(4,'big')
 for origin in ([0,1] if b==2 else [1,3]):
  for reverse in [False,True]:plant(raw,b,origin,reverse)
for origin in [1,3]:
 w=next(width(len(x),5) for x in L if width(len(x),5)>=9);raw=zlib.compress(bytes(range(w-8)));assert len(raw)==w;plant(raw,5,origin,False)
gate();before=counts.copy();real,unique=scan(L);realcounts={k:counts[k]-before[k] for k in counts};null=[];nullhits=[]
for rep in range(999):
 if rep%50==0:gate()
 sh=[rng.sample(x,len(x)) for x in L];hits,u=scan(sh);null.append(len(hits))
 if hits:nullhits.append(dict(rep=rep,hits=hits))
r=dict(real_hits=real,real_unique_bytes=unique,real_counts=realcounts,control_count=len(controls),controls=controls,parser_controls=parser,null_hitcounts=null,null_hits=nullhits,tail=(1+sum(n>=len(real) for n in null))/1000,counts_all=counts,byte_stream_sha256=digest.hexdigest(),seed=2026091730,capacity=[dict(page=m['page'],units=len(x),parity_bytes=width(len(x),2),quinary_bytes=width(len(x),5)) for m,x in zip(M,L)])
(R/'H10-result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['controls','parser_controls','null_hitcounts','capacity']},indent=2))
