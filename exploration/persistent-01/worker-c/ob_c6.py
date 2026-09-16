"""Repeated-rune delimiters around base28 binary transport frames."""
import json,gzip,zlib,bz2,lzma,hashlib,time,random,itertools
import numpy as np
from p03_frozen import O,ROOT,parse,CHECK,dump
from ob_c1 import decode,ORDERS
PARAMS=[(r,d,rev,endian) for r,d in ORDERS for rev in [False,True] for endian in ['big','little']]
def transport(digits,r,d,seed=0):
 alpha=[(r+d*i)%29 for i in range(29)];c=[seed,seed]
 for x in digits:c.append([v for v in alpha if v!=c[-1]][x])
 c.append(c[-1]);return c
def digits_for(b):
 w=len(b);n=0
 while 28**n<256**w:n+=1
 v=int.from_bytes(b,'big');ds=[0]*n
 for j in range(n-1,-1,-1):ds[j]=v%28;v//=28
 assert v==0;return ds
def inspect(b):
 hits=[]
 if len(b)>=5:
  crc=zlib.crc32(b[:-4])
  for endian in ['big','little']:
   if int.from_bytes(b[-4:],endian)==crc:hits.append(dict(format='CRC32-suffix-'+endian,payload_hex=b[:-4].hex()))
 for name,bits in [('zlib',15),('gzip',31)]:
  try:
   de=zlib.decompressobj(bits);x=de.decompress(b,65537)
   if len(x)<=65536 and de.eof and not de.unused_data and not de.unconsumed_tail:hits.append(dict(format=name,decoded_hex=x.hex()))
  except zlib.error:pass
 for name,cls in [('bz2',bz2.BZ2Decompressor),('xz',lzma.LZMADecompressor)]:
  try:
   de=cls();x=de.decompress(b,max_length=65537)
   if len(x)<=65536 and de.eof and not de.unused_data:hits.append(dict(format=name,decoded_hex=x.hex()))
  except (OSError,EOFError,lzma.LZMAError):pass
 return hits
def scan(frames,writer=None,keepbytes=False):
 hits=[];trials=admissible=lengthgood=0
 for fi,frame in enumerate(frames):
  c=np.array(frame['cipher']);n=len(c)-3;capacity=28**n;w=(capacity.bit_length()-1)//8;canonical=n>0 and w>0 and 28**(n-1)<256**w
  if canonical:lengthgood+=1
  for pi,(r,d,rev,endian) in enumerate(PARAMS):
   trials+=1;row=dict(frame=frame['id'],parameter=pi,canonical_length=canonical,byte_width=w)
   if canonical:
    ds=decode(c,r,d)[2:-1].tolist()
    if rev:ds=ds[::-1]
    v=0
    for digit in ds:v=28*v+digit
    row['integer_fits']=v<256**w
    if row['integer_fits']:
     admissible+=1;b=v.to_bytes(w,endian);matched=inspect(b);row.update(formats=[x['format'] for x in matched],sha256=hashlib.sha256(b).hexdigest())
     if keepbytes:row['bytes_hex']=b.hex()
     if matched:hits.append({**row,'bytes_hex':b.hex(),'matches':matched})
   if writer:writer.write(json.dumps(row)+'\n')
 return dict(frames=len(frames),canonical_frames=lengthgood,trials=trials,byte_admissible=admissible,hits=hits)
def main():
 out=O/'ob-c6';out.mkdir(exist_ok=True);start=time.monotonic();rng=random.Random(330123);dump(out/'parameters.json',[dict(rotation=r,direction=d,reverse_digits=rev,byte_endian=endian) for r,d,rev,endian in PARAMS]);controls=[]
 for ix,name in enumerate(CHECK):
  p=bytes(parse((ROOT/'audit/parallel-01/reference/sources'/('solved_'+name+'.txt')).read_text())[0]);body=zlib.compress(p);blob=body if ix%2==0 else body+zlib.crc32(body).to_bytes(4,'big');ds=digits_for(blob);c=transport(ds,7,-1,ix);frame=dict(id=name,cipher=c);res=scan([frame]);assert any(x['bytes_hex']==blob.hex() for x in res['hits']);corrupt=bytearray(blob);corrupt[-1]^=1;assert not inspect(bytes(corrupt));controls.append(dict(name=name,source_hex=p.hex(),target_hex=blob.hex(),cipher=c,search=res))
 # Parsercapacity controls, all complete and noexecution.
 assert not inspect(zlib.compress(b'X'*65537));dump(out/'controls.json',controls)
 cfg=json.loads((ROOT/'exploration/persistent-01/config.json').read_text());ps=[p for p in json.loads((ROOT/'audit/parallel-01/inputs/dataset.json').read_text())['pages'] if p['original_page']<=55 and p['original_page']!=50 and p['original_page'] not in cfg['reserved_original_pages']];frames=[]
 for p in ps:
  c=p['indices'];marks=[i for i in range(1,len(c)) if c[i]==c[i-1]]
  for a,b in zip(marks,marks[1:]):frames.append(dict(id=f"{p['original_page']}:{a}:{b}",page=p['original_page'],start_marker=a,end_marker=b,cipher=[c[a-1]]+c[a:b+1],digits=b-a-1))
 dump(out/'frames.json',frames)
 with gzip.open(out/'real-cells.jsonl.gz','wt') as f:real=scan(frames,f,True)
 nulls=[]
 with gzip.open(out/'null-cells.jsonl.gz','wt') as f:
  for ni in range(100):
   nf=[]
   for frame in frames:
    ds=decode(np.array(frame['cipher']),0,1)[2:-1].tolist();rng.shuffle(ds);nf.append(dict(id=f"{ni}:{frame['id']}",cipher=transport(ds,0,1,frame['cipher'][0])))
   nulls.append(dict(id=ni,**scan(nf,f)))
 dump(out/'nulls.json',nulls);summary=dict(strategy='outside-box-v1',model='repeat-delimited minimalbase28 binaryframes,58alphabetorders x2digitorders x2byteorders;CRC32suffix orcompletecompressionchecks',real=real,controls=[dict(name=x['name'],hits=len(x['search']['hits']),truth_bytes_recovered=any(h['bytes_hex']==x['target_hex'] for h in x['search']['hits'])) for x in controls],null_trials=sum(x['trials'] for x in nulls),null_hits=sum(len(x['hits']) for x in nulls),seconds=time.monotonic()-start,limits='Internalrepeat-delimitedframes only,unknownedgefragments excluded;bytewidth minimalcapacity convention,otherpadding/transportformats untested. Null shufflesrankdigitswithinframes undercanonicalorder thenreencodes, preservinglengths/markerpositions. Formatschosenbeforetest;no permissiveprintability criterion.')
 dump(out/'summary.json',summary);print(json.dumps(summary))
if __name__=='__main__':main()
