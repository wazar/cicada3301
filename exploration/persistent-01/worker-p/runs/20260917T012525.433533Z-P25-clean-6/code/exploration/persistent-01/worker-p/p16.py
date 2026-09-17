import pathlib,json,hashlib,random,sys,datetime
R=pathlib.Path(__file__).resolve().parent;ROOT=R.parents[2];O=R/'P16';POLY=0x11d
def gate():
 assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(name,x):(O/(name+'.json')).write_text(json.dumps(x,indent=2)+'\n')
def slow(a,b):
 # Carryless polynomial product then explicit long division.
 v=0
 for i in range(8):
  if b&(1<<i):v^=a<<i
 for bit in range(14,7,-1):
  if v&(1<<bit):v^=POLY<<(bit-8)
 return v
EXP=[];LOG=[None]*256;x=1
for i in range(255):
 assert x not in EXP;EXP.append(x);LOG[x]=i;x=slow(x,2)
assert x==1 and set(EXP)==set(range(1,256))
def mul(a,b):return 0 if not a or not b else EXP[(LOG[a]+LOG[b])%255]
def spow(a,n):
 out=1
 for _ in range(n):out=slow(out,a)
 return out
INV=[0]+[spow(a,254) for a in range(1,256)]
def eval_poly(coef,x,m=mul):
 y=0
 for c in reversed(coef):y=m(y,x)^c
 return y
def encode(coef):return [eval_poly(coef,x) for x in range(256)]
POW=[]
for x in range(256):
 row=[1]
 for k in range(1,256):row.append(mul(row[-1],x))
 POW.append(row)
def syndromes(y,count=32):
 out=[0]*count
 for x,v in enumerate(y):
  for k in range(count):out[k]^=mul(v,POW[x][k])
 return out
def full_moments(y):
 s=syndromes(y,255);a=[0]*256;a[0]=y[0];a[255]=s[0]
 for j in range(1,255):a[j]=s[255-j]
 return a
def newton(y):
 d=list(y)
 for order in range(1,256):
  for i in range(255,order-1,-1):d[i]=slow(d[i]^d[i-1],INV[i^(i-order)])
 a=[d[255]]
 for i in range(254,-1,-1):
  q=[0]*(len(a)+1)
  for j,v in enumerate(a):q[j]^=slow(v,i);q[j+1]^=v
  q[0]^=d[i];a=q
 return a
def rank(rows):
 a=[r[:] for r in rows];piv=0
 for j in range(len(a[0])):
  q=next((i for i in range(piv,len(a)) if a[i][j]),None)
  if q is None:continue
  a[piv],a[q]=a[q],a[piv];z=INV[a[piv][j]];a[piv]=[mul(v,z) for v in a[piv]]
  for i in range(len(a)):
   if i!=piv and a[i][j]:
    z=a[i][j];a[i]=[v^mul(z,w) for v,w in zip(a[i],a[piv])]
  piv+=1
  if piv==len(a):break
 return piv

def controls():
 gate();assert all(mul(a,b)==slow(a,b) for a in range(256) for b in range(256))
 assert all(slow(a,INV[a])==1 for a in range(1,256))
 rows=[[POW[x][k] for x in range(256)] for k in range(32)];assert rank(rows)==32
 msgs=[[0]*224,[1]+[0]*223,[0]*223+[1]]
 for seed in range(331600,331604):
  rng=random.Random(seed);msgs.append([rng.randrange(256) for _ in range(224)])
 good=[]
 for i,m in enumerate(msgs):
  y=encode(m);s=syndromes(y);a=full_moments(y);b=newton(y);assert s==[0]*32 and a==b==m+[0]*32;assert [eval_poly(b,x,slow) for x in range(256)]==y;good.append(dict(index=i,message=m,codeword=y,syndromes=s,coefficients=a))
 bad=[];y=good[3]['codeword']
 for double in [False,True]:
  for i in range(256):
   z=y.copy();z[i]^=1
   if double:z[(i+1)%256]^=2
   s=syndromes(z);assert any(s);bad.append(dict(double=double,positions=[i,(i+1)%256] if double else [i],codeword=z,syndromes=s))
 dump('controls',dict(status='PASS',field_products=65536,nonzero_generator_order=255,parity_rank=32,positive=good,negative=bad))
 print('controls PASS7 positives512 corruptions65536 products',flush=True)
def actual():
 gate();path=ROOT/'audit/alphanumeric-01/v1/transcription.json';cells=json.loads(path.read_text())['cells'];alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx';y=bytes(60*alphabet.index(c['token'][0])+alphabet.index(c['token'][1]) for c in cells)
 assert len(y)==256 and hashlib.sha256(y).hexdigest()=='3b9b07d9a26e6d55c432d94d2661fdff3c2b348daed06821f2bdb23184a4b290'
 (O/'input.bin').write_bytes(y);s=syndromes(y);a=full_moments(y);b=newton(y);assert a==b;assert [eval_poly(a,x,slow) for x in range(256)]==list(y);assert s==list(reversed(a[224:]))
 valid=not any(s);degree=max((i for i,v in enumerate(a) if v),default=-1);(O/'interpolant-coefficients.bin').write_bytes(bytes(a))
 if valid:(O/'message-224.bin').write_bytes(bytes(a[:224]))
 r=dict(source=str(path.relative_to(ROOT)),source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),input_sha256=hashlib.sha256(y).hexdigest(),polynomial=POLY,evaluation_points=list(range(256)),maximum_degree=223,actual_degree=degree,syndromes=s,zero_checks=sum(v==0 for v in s),valid=valid,coefficients=a,independent_newton_equal=True,all256_reevaluations_match=True,message_retained=valid)
 dump('actual',r);print(json.dumps({k:v for k,v in r.items() if k not in ['coefficients','evaluation_points']}),flush=True)
if __name__=='__main__':controls() if sys.argv[1]=='controls' else actual()
