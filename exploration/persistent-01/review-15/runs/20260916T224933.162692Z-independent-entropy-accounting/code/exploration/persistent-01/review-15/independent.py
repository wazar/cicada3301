"""Separate scalar bit/tree baseline JPEG accounting; no worker-P imports."""
import pathlib,json,hashlib,sys

def inspect(path):
 data=pathlib.Path(path).read_bytes();assert data[:2]==b'\xff\xd8';p=2;tables={};components={};dri=0;markers=[]
 while True:
  assert data[p]==255;mark=data[p+1];size=int.from_bytes(data[p+2:p+4],'big');payload=data[p+4:p+2+size];markers.append([p,mark,size]);p+=2+size
  if mark==0xc0:
   assert payload[0]==8;h=int.from_bytes(payload[1:3],'big');w=int.from_bytes(payload[3:5],'big');n=payload[5];assert len(payload)==6+3*n
   components={payload[6+3*j]:(payload[7+3*j]>>4,payload[7+3*j]&15) for j in range(n)}
  elif mark in [0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf]:raise ValueError('unsupported nonbaseline frame')
  elif mark==0xdd:dri=int.from_bytes(payload,'big')
  elif mark==0xc4:
   z=0
   while z<len(payload):
    key=payload[z];counts=payload[z+1:z+17];z+=17;code=0;tree={}
    for width,count in enumerate(counts,1):
     for _ in range(count):
      assert code<(1<<width)-1
      bits=format(code,f'0{width}b');node=tree
      for b in bits[:-1]:node=node.setdefault(b,{})
      assert bits[-1] not in node;node[bits[-1]]=payload[z];z+=1;code+=1
     code*=2
    tables[key]=tree
  elif mark==0xda:
   n=payload[0];assert payload[-3:]==bytes([0,63,0]);scan=[(payload[1+2*j],payload[2+2*j]>>4,payload[2+2*j]&15) for j in range(n)];assert set(x[0] for x in scan)==set(components);break
 assert not dri,'restart unsupported in this independent implementation'
 entropy_start=p;raw=[];positions=[];stuffed=0
 while True:
  if data[p]==255:
   if data[p+1]==0:raw.append(255);positions.append(p);p+=2;stuffed+=1;continue
   assert data[p+1]==0xd9,'unsupported second scan or restart';eoi=p;break
  raw.append(data[p]);positions.append(p);p+=1
 bits=''.join(format(v,'08b') for v in raw);cursor=0;dc=ac=amplitude=0
 def read(tree):
  nonlocal cursor
  node=tree
  while isinstance(node,dict):node=node[bits[cursor]];cursor+=1
  return node
 maxh=max(x[0] for x in components.values());maxv=max(x[1] for x in components.values())
 if len(scan)==1:mcu_cols=(w+7)//8;mcu_rows=(h+7)//8;block_order=[scan[0]]
 else:
  mcu_cols=(w+8*maxh-1)//(8*maxh);mcu_rows=(h+8*maxv-1)//(8*maxv);block_order=[c for c in scan for _ in range(components[c[0]][0]*components[c[0]][1])]
 for _ in range(mcu_rows*mcu_cols):
  for cid,dt,at in block_order:
   s=read(tables[dt]);assert s<=11;cursor+=s;amplitude+=s;dc+=1;k=1
   while k<64:
    sym=read(tables[16+at]);ac+=1;r=sym>>4;s=sym&15
    if not s:
     if not r:break
     assert r==15;k+=16;assert k<=64
    else:
     assert s<=10;k+=r;assert k<64;cursor+=s;amplitude+=s;k+=1
 assert cursor<=len(bits);pad=(-cursor)%8;tail_start=(cursor+pad)//8
 return {'path':str(path),'sha256':hashlib.sha256(data).hexdigest(),'width':w,'height':h,'components':components,'scan':scan,'dri':dri,'mcu_cols':mcu_cols,'mcu_rows':mcu_rows,'mcus':mcu_cols*mcu_rows,'blocks_per_mcu':len(block_order),'dc_symbols':dc,'ac_symbols':ac,'amplitude_bits':amplitude,'entropy_start':entropy_start,'eoi_offset':eoi,'unstuffed_bytes':len(raw),'stuffed_ff_count':stuffed,'consumed_bits':cursor,'final_pad_bits':bits[cursor:cursor+pad],'tail_unstuffed_hex':bytes(raw[tail_start:]).hex(),'tail_bytes':len(raw)-tail_start,'last_required_rawbyte':positions[(cursor-1)//8],'markers':markers}
if __name__=='__main__':
 out=[inspect(p) for p in sys.argv[1:]];root=pathlib.Path(__file__).parent;(root/'independent-results.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
