"""Finite page/period composite screen using C04's seed-independent equality statistic."""
import extend as ex
from invariant import simple_baseline,collisions
import numpy as np,json,random,pathlib,hashlib,sys,time
O=ex.O/'C07';O.mkdir(exist_ok=True)
PAGES=[p for p in ex.PAGES if p['page'] not in ex.CONFIG['reserved_originals'] and p['page']!=50]
assert len(PAGES)==45 and sorted(p['page'] for p in PAGES)==sorted(ex.ELIGIBLE+[0,17,55])
def prepare():
 src=ex.R/'exploration/persistent-02/decoder/fresh-controls.json';d=json.loads(src.read_text());rng=random.Random(2026092200);cases=[]
 for author in ['guest','mill','shelley','blake']:
  full=next(c for c in d['cases'] if c['id']==f'fresh-{author}-2')['truth']
  for n in [66,121,249]:
   for k in sorted(set([2,n//20-1])):
    p=full[:n];seed=[rng.randrange(29) for _ in range(k)];cases.append(dict(id=f'{author}-n{n}-k{k}',kind='language',source_id=f'fresh-{author}-2',plain=p,k=k,seed=seed,cipher=ex.q.enc(p,seed)))
 for n in [66,121,249]:
  for k in sorted(set([2,n//20-1])):
   p=[rng.randrange(29) for _ in range(n)];seed=[rng.randrange(29) for _ in range(k)];cases.append(dict(id=f'uniform-n{n}-k{k}',kind='uniform',plain=p,k=k,seed=seed,cipher=ex.q.enc(p,seed)))
 path=O/'inputs.json';assert not path.exists();path.write_text(json.dumps(dict(rng_seed=2026092200,source=str(src.relative_to(ex.R)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),pages=[dict(page=p['page'],cipher=p['indices'],ks=list(range(2,len(p['indices'])//20))) for p in PAGES],controls=cases),separators=(',',':'))+'\n');print('frozen',len(cases),len(PAGES),hashlib.sha256(path.read_bytes()).hexdigest())
def matrix(c,seedbase):
 ks=list(range(2,len(c)//20));assert ks;num=np.zeros((200,len(ks)),dtype=np.int64);den=np.zeros(len(ks),dtype=np.int64)
 for panel in range(200):
  cc=c if panel==0 else ex.q.null(c,seedbase+panel-1)
  for j,k in enumerate(ks):num[panel,j],den[j],_=collisions(simple_baseline(cc,k),k+1)
 frac=num/den[None,:];sd=frac.std(axis=0);assert np.all(sd>0);z=(frac-frac.mean(axis=0))/sd
 return ks,num,den,z
def summarize(label,features,nums,dens,zs,extras):
 num=np.concatenate(nums,axis=1);den=np.concatenate(dens);z=np.concatenate(zs,axis=1);mx=z.max(axis=1);winner=int(np.argmax(z[0]));rank=(1+int(np.sum(mx[1:]>=mx[0])))/200
 out=dict(label=label,rank=rank,maximum=float(mx[0]),selected=features[winner],features=features,**extras)
 np.savez_compressed(O/(label+'.npz'),numerators=num,denominators=den,z=z,family_maximum=mx);(O/(label+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(label,rank,features[winner],flush=True);return out
def control(ix):
 ex.guard();d=json.loads((O/'inputs.json').read_text());plant=d['controls'][ix];base=2026300000+1000*ix
 if not (O/f'control{ix:02}-local.json').exists():
  ks,num,den,z=matrix(plant['cipher'],base);j=ks.index(plant['k']);a,b,_=collisions(plant['plain'],plant['k']+1);assert num[0,j]==a and den[j]==b
  summarize(f'control{ix:02}-local',[dict(k=k) for k in ks],[num],[den],[z],dict(index=ix,id=plant['id'],seedbase=base,planted_k=plant['k'],scope='single-unit periodfamily'))
 if (O/f'control{ix:02}-book.json').exists():return
 features=[];nums=[];dens=[];zs=[];sources=[];start=time.monotonic()
 for p in d['pages']:
  ex.guard();page=p['page'];seedbase=2026600000+100000*ix+1000*page;c=plant['cipher'] if page==49 else ex.q.null(p['cipher'],seedbase+900);ks,num,den,z=matrix(c,seedbase);features.extend(dict(page_slot=page,k=k) for k in ks);nums.append(num);dens.append(den);zs.append(z);sources.append(dict(page_slot=page,kind='plant' if page==49 else 'uniform-mask-background',seedbase=seedbase,baseline_seed=None if page==49 else seedbase+900,cipher=c))
 summarize(f'control{ix:02}-book',features,nums,dens,zs,dict(index=ix,id=plant['id'],sources=sources,planted_k=plant['k'],seconds=time.monotonic()-start,scope='45-unit synthetic composite, original49slot replaced by control length'))
def actual():
 ex.guard();d=json.loads((O/'inputs.json').read_text());features=[];nums=[];dens=[];zs=[];locals=[];start=time.monotonic()
 for p in d['pages']:
  page=p['page'];base=2026400000+1000*page;ex.guard();ks,num,den,z=matrix(p['cipher'],base);features.extend(dict(page=page,k=k) for k in ks);nums.append(num);dens.append(den);zs.append(z);mx=z.max(axis=1);locals.append(dict(page=page,length=len(p['cipher']),ks=ks,seedbase=base,rank=(1+int(np.sum(mx[1:]>=mx[0])))/200,k_selected=ks[int(np.argmax(z[0]))],maximum=float(mx[0])))
  print('actual page',page,'complete',flush=True)
 summarize('actual',features,nums,dens,zs,dict(pages=locals,seconds=time.monotonic()-start,input_sha256=hashlib.sha256((O/'inputs.json').read_bytes()).hexdigest(),scope='45eligible pages, independent effective initial conditions, all sample-size-bounded periods; no seed fitting or imposed physical reset'))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='actual':actual()
 elif sys.argv[1]=='controls':
  for ix in map(int,sys.argv[2:]):control(ix)
