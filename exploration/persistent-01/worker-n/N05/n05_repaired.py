import pathlib,json,hashlib,collections,datetime,gzip
import numpy as np
from PIL import Image
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3];I=R/'exploration/persistent-01/worker-i';rng=np.random.default_rng(33011501)
def check():
 assert not (O.parents[1]/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):
 with gzip.open(O/n,'wt') as f:json.dump(x,f)
def main():
 check();raw=json.loads((I/'route-mapping.json').read_text())['records'];assert {r['page'] for r in raw}=={0,1};records=sorted(raw,key=lambda r:(r['page'],r['row'],r['index']));groups=collections.defaultdict(list)
 for i,r in enumerate(records):groups[r['page'],r['row']].append(i)
 rows=[np.array(v) for _,v in sorted(groups.items())];train=np.array([i for j,row in enumerate(rows) if j%2==0 for i in row]);held=np.array([i for j,row in enumerate(rows) if j%2 for i in row[len(row)//2:]]);prefix=np.array([i for j,row in enumerate(rows) if j%2 for i in row[:len(row)//2]])
 classes=sorted({r['shape_class'] for r in records});ci={v:i for i,v in enumerate(classes)};K=len(classes);med={c:float(np.median([records[i]['width'] for i in train if records[i]['shape_class']==c])) for c in classes};assert all(np.isfinite(list(med.values())))
 sep={v['after_record']:v['component_count'] for v in json.loads((O/'separator-types.json').read_text())};n=len(records);x=np.array([r['x'] for r in records],float);X=np.zeros((n,(2*K+1)));base=np.zeros(n);Z=np.zeros((n,3*len(rows)));rowZ=[]
 for j,ix in enumerate(rows):
  accum=0.;cnt=np.zeros(K);seps=0;marks=0;local=[]
  for pos,i in enumerate(ix):
   c=ci[records[i]['shape_class']];base[i]=accum;X[i,:K]=cnt;X[i,K+c]=1;X[i,-1]=marks;Z[i,3*j:3*j+3]=[1,pos,seps];local.append([1,pos,seps]);accum+=med[records[i]['shape_class']];cnt[c]+=1
   marks+=sep.get(int(i),0)==4
   if pos+1<len(ix):seps+=records[ix[pos+1]]['source_char_position']-records[i]['source_char_position']>1
  rowZ.append(np.array(local,float))
 traincols=[3*j+k for j in range(len(rows)) if j%2==0 for k in range(3)];design=np.column_stack([X,Z[:,traincols]]);pen=np.zeros(((2*K+1),design.shape[1]));pen[:,:(2*K+1)]=np.eye((2*K+1));aug=np.vstack([design[train],pen]);pinv=np.linalg.pinv(aug)
 def fit(xx,fonts=True,details=False):
  coef=pinv@np.r_[xx[train]-base[train],np.zeros((2*K+1))] if fonts else np.zeros(design.shape[1]);font=X@coef[:(2*K+1)];pred=base+font;pars=[]
  for j,ix in enumerate(rows):
   use=np.arange(len(ix)) if j%2==0 else np.arange(len(ix)//2);p=np.linalg.lstsq(rowZ[j][use],(xx-base-font)[ix[use]],rcond=None)[0];pred[ix]+=rowZ[j]@p;pars.append(p.tolist())
  res=xx-pred;v=res[train];a,b=np.quantile(v,[.25,.75])
  for _ in range(20):
   bit=np.abs(v-b)<np.abs(v-a)
   if not any(bit) or all(bit):break
   a=float(v[~bit].mean());b=float(v[bit].mean())
  if a>b:a,b=b,a
  bits=np.abs(res-b)<np.abs(res-a);m1=float(np.mean((res[held]-v.mean())**2));m2=float(np.mean(np.minimum((res[held]-a)**2,(res[held]-b)**2)));sep=float(b-a);minor=float(min(bits[train].mean(),1-bits[train].mean()));gain=1-m2/max(m1,1e-15)
  out={'centers':[a,b],'separation':sep,'train_minority':minor,'held_single_MSE':m1,'held_two_MSE':m2,'improvement':gain,'geometric_gate':bool(sep>=4 and minor>=.2 and m2<=.5*m1),'held_residual_range':[float(res[held].min()),float(res[held].max())],'held_abs_gt2_fraction':float(np.mean(abs(res[held])>2))}
  if details:out.update(prediction=pred.tolist(),residual=res.tolist(),bits=bits.astype(int).tolist(),font_corrections=coef[:(2*K+1)].tolist(),row_parameters=pars)
  return out
 controls=[]
 for displacement in [4,8]:
  for rep in range(10):
   check();bits=rng.integers(0,2,n);xx=x+displacement*bits;r=fit(xx,True,True);accuracy=float(np.mean(np.array(r['bits'])[held]==bits[held]));r['held_bit_accuracy']=max(accuracy,1-accuracy);controls.append({'displacement':displacement,'replicate':rep,'bits':bits.tolist(),'positions':xx.tolist(),'result':r})
 # Pixel measurement check is deliberately isolated from neighbor/class effects.
 images={}
 for info in json.loads((I/'inputs.json').read_text()):
  p=R/info['path'];assert sha(p)==info['sha256'];images[int(p.stem[1:])]=Image.open(p).convert('L')
 pixel=[]
 for delta in [4,8]:
  measured=[]
  for r in records:
   crop=np.array(images[r['page']].crop((r['x'],r['y'],r['right'],r['bottom'])));xx=np.where(crop<128)[1];p0=Image.new('L',(crop.shape[1]+40,crop.shape[0]+10),255);p0.paste(Image.fromarray(crop),(10+delta,5));new=np.where(np.array(p0)<128)[1];measured.append(int(new.min()-xx.min()-10))
  assert all(v==delta for v in measured);pixel.append({'displacement':delta,'measured':measured})
 classbits=np.array([r['shape_class']%2 for r in records]);correlated=fit(x+8*classbits,True,True);correlated['held_bit_accuracy']=float(max(np.mean(np.array(correlated['bits'])[held]==classbits[held]),np.mean(np.array(correlated['bits'])[held]!=classbits[held])))
 real=fit(x,True,True);baseline=fit(x,False,True);null=[]
 for b in range(199):
  if b%25==0:check()
  xx=np.rint(np.array(real['prediction'])+rng.uniform(-.5,.5,n));r=fit(xx);null.append({'positions':xx.tolist(),'result':r})
 p=(1+sum(v['result']['improvement']>=real['improvement'] for v in null))/200;real['null_upper_tail']=p;real['candidate']=bool(real['geometric_gate'] and p<=.01)
 def small(d):return {k:v for k,v in d.items() if k not in ['prediction','residual','bits','font_corrections','row_parameters']}
 summary={'real':small(real),'baseline':small(baseline),'controls':[{'displacement':c['displacement'],'replicate':c['replicate'],**small(c['result'])} for c in controls],'class_correlated_control':small(correlated),'counts':{'glyphs':n,'rows':len(rows),'training_glyphs':len(train),'held_prefix_glyphs':len(prefix),'held_suffix_glyphs':len(held),'classes':K,'nulls':199,'control_fixtures':20},'inputs':{'coordinates_sha256':sha(I/'coordinates.json'),'route_mapping_sha256':sha(I/'route-mapping.json'),'width_arrays_sha256':sha(I/'width-arrays.npz'),'images':json.loads((I/'inputs.json').read_text())}}
 save('repaired-evidence.json.gz',{'seed':33011501,'records':records,'classes':classes,'train':train.tolist(),'held_prefix':prefix.tolist(),'held_suffix':held.tolist(),'class_median_width':med,'feature_matrix':X.tolist(),'row_design':Z.tolist(),'baseline_positions':base.tolist(),'real':real,'baseline':baseline,'controls':controls,'class_correlated':{'bits':classbits.tolist(),'positions':(x+8*classbits).tolist(),'result':correlated},'pixel_controls':pixel,'null':null,'summary':summary});(O/'repaired-summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary['real']),summary['counts'],flush=True)
if __name__=='__main__':main()
