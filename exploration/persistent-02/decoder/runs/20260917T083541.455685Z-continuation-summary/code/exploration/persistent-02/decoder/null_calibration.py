"""Fixed F-site and adjacent equality-mask null, full two-heading-policy grid."""
import random,json,gzip,time,hashlib
from compare import ROOT,O,LM,section,beam
from complementary import LM as OtherLM
from exact import decode
rng=random.Random(260917205);cells=section();whole=next(c['cipher'] for c in cells if c['policy']=='whole');packets=[]
for j in range(19):
 p=[]
 for i,v in enumerate(whole):
  if v==0:x=0
  elif i and v==whole[i-1]:x=p[-1]
  else:x=rng.choice([r for r in range(1,29) if not i or r!=p[-1]])
  p.append(x)
 assert [x==0 for x in p]==[x==0 for x in whole]
 assert [a==b for a,b in zip(p,p[1:])]==[a==b for a,b in zip(whole,whole[1:])]
 packets.append(p)
prereg=dict(seed=260917205,replicates=19,null='Uniform nonzero choices except previous value when observed adjacent unequal; exact ciphertext-F sites and adjacent-equality mask retained, original rune inventory not retained.',statistic='Maximum exact P03/complementary score over same84cells, reported separately for body/whole and total grid; exploratory conditional rank, not global puzzle significance.',packets=packets)
(O/'null-calibration-inputs.json').write_text(json.dumps(prereg,indent=2)+'\n');out=O/'null-calibration';out.mkdir(exist_ok=True)
for modelname,lm in [('p03',LM()),('complementary',OtherLM())]:
 for j,full in enumerate(packets):
  results=[];t=time.monotonic()
  for cell in cells:
   c=full[13:] if cell['policy']=='body' else full;ends=set(cell['ends']);key=cell['key'];sign=cell['sign'];a,d=decode(c,key,lm.extend,sign=sign,ends=ends,retain=1);b,bd=beam(c,ends,key,sign,lm,64);results.append(dict(id=cell['id'],policy=cell['policy'],exact=a[0],beam_best=b[0],gap=a[0]['score']-b[0]['score']))
  obj=dict(model=modelname,replicate=j,cipher=full,rows=results,seconds=time.monotonic()-t)
  (out/f'{modelname}-{j:02d}.json.gz').write_bytes(gzip.compress(json.dumps(obj).encode(),mtime=0));print(json.dumps(dict(model=modelname,replicate=j,maximum=max(x['exact']['score'] for x in results),seconds=obj['seconds'])),flush=True)
