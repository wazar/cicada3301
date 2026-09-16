import pathlib,json,hashlib,struct,math,sys,zlib,io,random,datetime
import numpy as np
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[3];R=pathlib.Path(__file__).parent/'P10'
ZZ=[0,1,8,16,9,2,3,10,17,24,32,25,18,11,4,5,12,19,26,33,40,48,41,34,27,20,13,6,7,14,21,28,35,42,49,56,57,50,43,36,29,22,15,23,30,37,44,51,58,59,52,45,38,31,39,46,53,60,61,54,47,55,62,63]
class Unsupported(Exception):pass
class Invalid(Exception):pass
def need(x,m):
 if not x:raise Invalid(m)
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(n,x):(R/(n+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def gate():
 assert not(ROOT/'exploration/persistent-01/STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def marker(d,i):
 need(i<len(d) and d[i]==255,'expected marker');a=i
 while i<len(d) and d[i]==255:i+=1
 need(i<len(d) and d[i]!=0,'bad marker');return d[i],i+1,i-a-1
class Bits:
 def __init__(self,d,i):self.d=d;self.i=i;self.byte=0;self.left=0;self.bits=0;self.stuffed=[];self.last_raw=None
 def bit(self):
  if not self.left:
   need(self.i<len(self.d),'truncated entropy');self.last_raw=self.i;self.byte=self.d[self.i];self.i+=1
   if self.byte==255:
    need(self.i<len(self.d) and self.d[self.i]==0,'marker before expected MCU end');self.stuffed.append(self.i);self.i+=1
   self.left=8
  self.left-=1;self.bits+=1;return (self.byte>>self.left)&1
 def get(self,n):
  v=0
  for _ in range(n):v=(v<<1)|self.bit()
  return v
 def symbol(self,table):
  v=0
  for n in range(1,17):
   v=(v<<1)|self.bit()
   if (n,v) in table:return table[n,v]
  raise Invalid('undefined Huffman code')
def extend(v,n):return v if not n or v>=(1<<(n-1)) else v-((1<<n)-1)
def parse(d):
 need(d[:2]==b'\xff\xd8','not JPEG');i=2;tables={};frame=None;headers=[];restart=0
 while True:
  start=i;m,i,fill=marker(d,i);need(i+2<=len(d),'truncated segment');ln=int.from_bytes(d[i:i+2],'big');need(ln>=2 and i+ln<=len(d),'bad segment length');b=d[i+2:i+ln];i+=ln;headers.append(dict(marker=m,offset=start,length=ln,fill=fill))
  if m in set(range(0xc0,0xd0))-{0xc4,0xc8,0xcc} and m!=0xc0:raise Unsupported('non-baseline frame')
  if m==0xc0:
   need(frame is None,'duplicate frame');need(len(b)>=6,'short SOF');prec,h,w,n=struct.unpack('>BHHB',b[:6]);need(len(b)==6+3*n,'SOF length')
   if prec!=8 or n not in [1,3]:raise Unsupported('precision/components')
   comps=[dict(id=b[6+3*k],h=b[7+3*k]>>4,v=b[7+3*k]&15,q=b[8+3*k]) for k in range(n)];need(w>0 and h>0 and len({c['id'] for c in comps})==n,'bad dimensions/ids');need(all(1<=c['h']<=4 and 1<=c['v']<=4 for c in comps),'sampling');frame=dict(width=w,height=h,components=comps)
  elif m==0xc4:
   p=0
   while p<len(b):
    tc=b[p]>>4;tid=b[p]&15;p+=1;need(tc in [0,1] and tid<=3,'Huffman class/id');counts=list(b[p:p+16]);need(len(counts)==16,'DHT counts');p+=16;vals=list(b[p:p+sum(counts)]);need(len(vals)==sum(counts),'DHT values');p+=len(vals);table={};code=0;k=0
    for n,num in enumerate(counts,1):
     need(code+num<=1<<n,'oversubscribed Huffman')
     for _ in range(num):table[n,code]=vals[k];code+=1;k+=1
     code<<=1
    tables[tc,tid]=table
  elif m==0xdd:
   need(len(b)==2,'DRI length');restart=int.from_bytes(b,'big')
   if restart:raise Unsupported('nonzero restart interval')
  elif m==0xda:
   need(frame is not None and len(b)>=4,'SOS before frame');n=b[0];need(len(b)==1+2*n+3,'SOS length')
   if n!=len(frame['components']) or b[-3:]!=bytes([0,63,0]):raise Unsupported('multiscan/non-sequential SOS')
   scans=[dict(id=b[1+2*k],dc=b[2+2*k]>>4,ac=b[2+2*k]&15) for k in range(n)];need([c['id'] for c in scans]==[c['id'] for c in frame['components']],'scan component order');break
  elif m not in [0xdb,0xfe] and not 0xe0<=m<=0xef:raise Unsupported('marker '+hex(m))
 comps=frame['components'];hm=max(c['h'] for c in comps);vm=max(c['v'] for c in comps);w=frame['width'];h=frame['height'];inter=len(comps)>1;mw=math.ceil(w/(8*hm)) if inter else math.ceil(w/8);mh=math.ceil(h/(8*vm)) if inter else math.ceil(h/8)
 arrays={c['id']:np.zeros((math.ceil(h*c['v']/(8*vm)),math.ceil(w*c['h']/(8*hm)),64),dtype='<i2') for c in comps};pred={c['id']:0 for c in comps};br=Bits(d,i);blocks=0;dummy=0;ac_symbols=0
 for my in range(mh):
  for mx in range(mw):
   for c,s in zip(comps,scans):
    need((0,s['dc']) in tables and (1,s['ac']) in tables,'missing Huffman table')
    for yy in range(c['v'] if inter else 1):
     for xx in range(c['h'] if inter else 1):
      t=br.symbol(tables[0,s['dc']]);need(t<=11,'DC category');pred[c['id']]+=extend(br.get(t),t);a=[0]*64;a[0]=pred[c['id']];k=1
      while k<64:
       rs=br.symbol(tables[1,s['ac']]);ac_symbols+=1;run=rs>>4;size=rs&15
       if size==0:
        if run==0:break
        need(run==15,'invalid AC zero size');k+=16;need(k<=64,'ZRL overflow');continue
       need(size<=10,'AC category');k+=run;need(k<64,'AC run overflow');a[ZZ[k]]=extend(br.get(size),size);k+=1
      y=my*(c['v'] if inter else 1)+yy;x=mx*(c['h'] if inter else 1)+xx;ar=arrays[c['id']];blocks+=1
      if y<ar.shape[0] and x<ar.shape[1]:ar[y,x]=a
      else:dummy+=1
 pad=br.byte&((1<<br.left)-1);end=br.i;raw=bytearray();unstuffed=bytearray();j=end;tailstuff=[]
 while j<len(d):
  if d[j]!=255:raw.append(d[j]);unstuffed.append(d[j]);j+=1;continue
  if j+1<len(d) and d[j+1]==0:raw.extend(d[j:j+2]);unstuffed.append(255);tailstuff.append(j+1);j+=2;continue
  break
 eoi,endmarker,fill=marker(d,j)
 if eoi!=0xd9:raise Unsupported('additional scan/marker after expected MCUs '+hex(eoi))
 meta=dict(frame=frame,headers=headers,sos_data_offset=i,mcu_grid=[mw,mh],mcus=mw*mh,blocks=blocks,ac_symbols=ac_symbols,dummy_blocks=dummy,entropy_bits=br.bits,final_data_byte_offset=br.last_raw,consumed_bits_in_final_byte=8-br.left,pad_bits=br.left,pad_value=pad,padding_all_ones=pad==(1<<br.left)-1,entropy_byte_end=end,entropy_stuffed_zero_offsets=br.stuffed,tail_raw_span=[end,j],tail_raw_bytes=len(raw),tail_bytes=len(unstuffed),tail_stuffed_zero_offsets=tailstuff,marker_fill_bytes=fill,eoi_offset=endmarker-2,after_eoi_span=[endmarker,len(d)],after_eoi_bytes=len(d)-endmarker,coefficient_sha256={str(k):sha(v.tobytes()) for k,v in arrays.items()},coefficient_shapes={str(k):list(v.shape) for k,v in arrays.items()})
 return meta,bytes(raw),bytes(unstuffed),arrays
MAGIC=b'LP10TAIL'
def frame(payload):return MAGIC+struct.pack('>I',len(payload))+payload+struct.pack('>I',zlib.crc32(payload))
def unframe(b):
 need(len(b)>=16 and b[:8]==MAGIC,'frame magic/size');n=int.from_bytes(b[8:12],'big');need(len(b)==16+n,'frame length');payload=b[12:12+n];need(zlib.crc32(payload)==int.from_bytes(b[-4:],'big'),'frame CRC');return payload
