"""Independent intended 32-bit source format arithmetic, not original C code."""
import pathlib,json,hashlib
R=pathlib.Path(__file__).parent

def header_read(bits):
 if len(bits)<5:return {'status':'truncated_width'}
 width=int(bits[:5],2)
 if len(bits)<5+width:return {'status':'truncated_length','width':width}
 size=int(bits[5:5+width] or '0',2);available=(len(bits)-5-width)//8
 out={'width':width,'size':size,'available':available,'minimal_width':size.bit_length(),'minimal_encoder_compatible':size>0 and width==size.bit_length(),'readme_width_compatible':size>0 and width in [size.bit_length(),size.bit_length()+1]}
 if not size:out['status']='zero_length_sink_edge'
 elif size>available:out['status']='insufficient_capacity'
 else:out.update(status='complete',payload_hex=bytes(int(bits[i:i+8],2) for i in range(5+width,5+width+8*size,8)).hex())
 return out

def getwidth_defined(size,wordbits):
 if not size:return {'width':0,'defined':True}
 shift=1;mask=(1<<wordbits)-1
 while shift<wordbits and (size&(mask>>shift))==size:shift+=1
 if shift>=wordbits:return {'defined':False,'reason':'shift_by_word_width'}
 return {'defined':True,'width':(33-shift)%65536,'shift':shift}

def run():
 controls=[]
 for size in [1,2,7,8,255,256,1023,1024,1025,4096]:
  payload=bytes((j*71+size)%256 for j in range(size))
  for extra in [0,1]:
   width=size.bit_length()+extra;bits=f'{width:05b}'+f'{size:0{width}b}'+''.join(f'{b:08b}' for b in payload)
   coefficients=[]
   for j,b in enumerate(bits):coefficients.extend([0,1,(-2 if b=='0' else -1) if j%2 else (2 if b=='0' else 3)])
   reread=''.join(str(c&1) for c in coefficients if (c&1)!=c);assert reread==bits;got=header_read(reread);assert got['status']=='complete' and bytes.fromhex(got['payload_hex'])==payload
   controls.append({'size':size,'extra_zero':extra,'coefficients':coefficients,'bits':bits,'result':got,'payload_sha256':hashlib.sha256(payload).hexdigest()})
 real=[]
 for z in json.loads((R/'independent-results.json').read_text()):
  path=R/(pathlib.Path(z['path']).stem+'-eligible-bits.bin');bits=''.join(f'{b:08b}' for b in path.read_bytes())[:z['eligible_count']];got=header_read(bits);real.append({'page_path':z['path'],'header':got});assert got['status']=='insufficient_capacity'
 cases=[{'size':n,'intended32':getwidth_defined(n,32),'native64':getwidth_defined(n,64)} for n in [0,1,2,3,255,256,2**30,2**31-1]]
 assert header_read('00000')['status']=='zero_length_sink_edge';assert header_read('00001')['status']=='truncated_length';assert header_read('0')['status']=='truncated_width'
 out={'controls':controls,'real':real,'word_width_cases':cases,'excluded_zero_payload_reason':'original source refresh returns EOF before header; sink checks size only after processing payload bit'};(R/'header-results.json').write_text(json.dumps(out,indent=2));print(json.dumps({'controls':len(controls),'real':real,'word_width_cases':cases}))
if __name__=='__main__':run()
