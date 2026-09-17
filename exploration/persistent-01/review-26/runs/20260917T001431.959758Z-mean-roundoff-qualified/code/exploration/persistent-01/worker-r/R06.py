import pathlib,json,hashlib,sys,time,datetime
import numpy as np
from PIL import Image
P=pathlib.Path(__file__).resolve().parent;SRC=P.parent/'worker-p/P16/input.bin';PIN='3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290';O=P/'R06';O.mkdir(exist_ok=True)
LOOK=np.unpackbits(np.arange(256,dtype=np.uint8)[:,None],axis=1,bitorder='big')
def guard():
 assert not (P.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def save(n,x):(O/n).write_text(json.dumps(x,indent=2)+'\n')
def unpack(b):return LOOK[np.frombuffer(b,dtype=np.uint8)].reshape(32,64)
def pack(a):return np.packbits(a.reshape(-1),bitorder='big').tobytes()
def stat(a):
 h=int(np.sum(a[:,7:56:8]==a[:,8:57:8]));v=int(np.sum(a[:-1]==a[1:]));return h,v,(h/224+v/1984)/2

def panel(name,b,n,seed):
 guard();a=unpack(b);assert len(b)==256 and pack(a)==b;h,v,s=stat(a);hs=sum(int(a[y,x])==int(a[y,x+1]) for y in range(32) for x in range(7,56,8));vs=sum(int(a[y,x])==int(a[y+1,x]) for y in range(31) for x in range(64));assert (h,v)==(hs,vs)
 rng=np.random.default_rng(seed);perms=np.empty((n,256),dtype=np.uint8);counts=np.empty((n,2),dtype=np.int32);scores=np.empty(n);bs=np.frombuffer(b,dtype=np.uint8)
 for i in range(n):
  if i%500==0:guard()
  ix=rng.permutation(256);perms[i]=ix;aa=LOOK[bs[ix]].reshape(32,64);hh,vv,ss=stat(aa);counts[i]=hh,vv;scores[i]=ss
 tail=(1+int(np.sum(scores>=s)))/(n+1);im=Image.fromarray((255*(1-a)).astype('uint8'),'L');im.save(O/(name+'-native.png'))
 if name=='actual':im.resize((1024,512),Image.Resampling.NEAREST).save(O/'actual-view.png')
 np.savez_compressed(O/(name+'.npz'),input_bytes=bs,bits=a,permutations=perms,null_counts=counts,null_scores=scores);(O/(name+'.bin')).write_bytes(b)
 z=dict(name=name,seed=seed,nulls=n,ones=int(a.sum()),horizontal_agree=h,horizontal_total=224,vertical_agree=v,vertical_total=1984,statistic=s,p_upper=tail,null_mean=float(scores.mean()),null_min=float(scores.min()),null_max=float(scores.max()),input_sha256=hashlib.sha256(b).hexdigest());save(name+'.json',z);print(name,tail,h,v,flush=True);return z

def controls():
 plants=[]
 a=np.zeros((32,64),np.uint8);a[[6,7,16,17,26,27]]=1;plants.append(('horizontal_rows',a.copy()))
 a[:]=0;a[:,13:16]=1;a[:,45:48]=1;plants.append(('vertical_bars',a.copy()))
 a[:]=0;a[8:24,16:48]=1;plants.append(('filled_rectangle',a.copy()))
 yy,xx=np.indices((32,64));a=(abs(xx-32)+abs(yy-16)==12).astype(np.uint8);plants.append(('diamond_outline',a.copy()))
 a[:]=0;glyphs=['10000/10000/10000/10000/10000/10000/11111','11110/10001/10001/11110/10000/10000/10000']
 for k,pat in enumerate(glyphs):
  g=np.array([[int(v) for v in row] for row in pat.split('/')],np.uint8);a[5:26,13+19*k:28+19*k]=np.repeat(np.repeat(g,3,0),3,1)
 plants.append(('LP_glyphs',a.copy()))
 a[:]=0;a[6,10:54]=a[25,10:54]=1;a[6:26,10]=a[6:26,53]=1;a[16,10:54]=1;plants.append(('box_connector',a.copy()))
 limits=[];a[:]=0;limits.append(('blank',a.copy()));a[15,31]=1;limits.append(('single_pixel',a.copy()));a[:]=0;r=np.random.default_rng(476100);positions=r.choice(2048,8,replace=False);a.flat[positions]=1;limits.append(('eight_points',a.copy()));limits.append(('checkerboard',((xx+yy)%2).astype(np.uint8)))
 rows=[]
 for i,(name,a) in enumerate(plants+limits):rows.append(panel(name,pack(a),999,476000+i))
 for i in range(30):
  density=[.05,.5,.95][i//10];r=np.random.default_rng(476200+i);a=(r.random((32,64))<density).astype(np.uint8);z=panel(f'ordinary-{i:02d}',pack(a),999,477000+i);z['density']=density;z['generation_seed']=476200+i;rows.append(z)
 viable=rows[0]['p_upper']<=.01 and rows[2]['p_upper']<=.01;save('controls-summary.json',dict(viable=viable,rows=rows,ordinary_at_01=sum(z['p_upper']<=.01 for z in rows[10:])));print('VIABLE',viable)
def actual():
 assert json.loads((O/'controls-summary.json').read_text())['viable'];b=SRC.read_bytes();assert len(b)==256 and hashlib.sha256(b).hexdigest()==PIN;z=panel('actual',b,9999,478000);a=unpack(b);maps=[dict(x=x,y=y,byte_index=y*8+x//8,msb_first_bit_index=x%8,bit_value=int(a[y,x])) for y in range(32) for x in range(64)];save('actual-pixel-map.json',maps);save('actual-summary.json',z)
if __name__=='__main__':
 t=time.monotonic();guard();{'controls':controls,'actual':actual}[sys.argv[1]]();print('SECONDS',time.monotonic()-t)
