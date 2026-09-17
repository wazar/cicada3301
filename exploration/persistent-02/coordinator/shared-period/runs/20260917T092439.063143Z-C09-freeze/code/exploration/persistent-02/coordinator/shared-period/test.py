"""Reuse C07collision features to test a distributed common period, no seed sweep."""
import pathlib,sys,json,hashlib,random,time
import numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3]
sys.path.insert(0,str(R/'exploration/persistent-02/feedback'))
import page_invariant as P
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def aggregate(features,z):
 ks=sorted({f['k'] for f in features if sum(g['k']==f['k'] for g in features)>=2})
 cols=[np.array([i for i,f in enumerate(features) if f['k']==k]) for k in ks]
 t=np.column_stack([z[:,ix].sum(axis=1)/np.sqrt(len(ix)) for ix in cols]);sd=t.std(axis=0)
 s=np.divide(t-t.mean(axis=0),sd,out=np.zeros_like(t),where=sd>0);mx=s.max(axis=1)
 return dict(ks=ks,counts=[len(i) for i in cols],raw=t,standardized=s,maximum=mx,rank=(1+int(np.sum(mx[1:]>=mx[0])))/len(mx),winner=ks[int(np.argmax(s[0]))])
def prepare():
 src=R/'exploration/persistent-02/decoder/fresh-controls.json';fresh=json.loads(src.read_text())
 inv=R/'exploration/persistent-02/feedback/C07/inputs.json';pages=json.loads(inv.read_text())['pages']
 rng=random.Random(2026092300);cases=[]
 for author in ['guest','mill','shelley','blake','uniform']:
  for k in [2,5,8]:
   ix=len(cases);units=[]
   for p in pages:
    pid=p['page'];n=len(p['cipher']);base=2026700000+100000*ix+1000*pid
    u=dict(page=pid,seedbase=base,ks=p['ks'],kind='background')
    if k in p['ks']:
     if author=='uniform':plain=[rng.randrange(29) for _ in range(n)];start=None
     else:
      full=next(x['truth'] for x in fresh['cases'] if x['id']==f'fresh-{author}-2');assert len(full)>=n
      start=rng.randrange(len(full)-n+1);plain=full[start:start+n]
     seed=[rng.randrange(29) for _ in range(k)]
     u.update(kind='plant',plain=plain,source_start=start,seed=seed,cipher=P.ex.q.enc(plain,seed))
    else:u.update(cipher=P.ex.q.null(p['cipher'],base+900),background_seed=base+900)
    units.append(u)
   cases.append(dict(id=f'{author}-k{k}',author=author,k=k,units=units))
 out=O/'inputs.json';assert not out.exists();out.write_text(json.dumps(dict(source=str(src.relative_to(R)),source_sha256=H(src),inventory=str(inv.relative_to(R)),inventory_sha256=H(inv),rng_seed=2026092300,cases=cases),separators=(',',':'))+'\n');print('frozen',len(cases),H(out))
def save(label,features,num,den,z,extras):
 d=aggregate(features,z)
 np.savez_compressed(O/(label+'.npz'),numerators=num,denominators=den,feature_z=z,aggregate_raw=d['raw'],aggregate_z=d['standardized'],maximum=d['maximum'])
 out={k:d[k] for k in ['ks','counts','rank','winner']};out.update(label=label,features=features,actual_maximum=float(d['maximum'][0]),**extras)
 (O/(label+'.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k] for k in ['label','rank','winner','actual_maximum']}),flush=True)
def control(ix):
 P.ex.guard();d=json.loads((O/'inputs.json').read_text());case=d['cases'][ix];assert not (O/f'control{ix:02}.json').exists()
 fs=[];ns=[];ds=[];zs=[];t=time.monotonic()
 for u in case['units']:
  P.ex.guard();ks,num,den,z=P.matrix(u['cipher'],u['seedbase']);assert ks==u['ks'];fs += [dict(page=u['page'],k=k) for k in ks];ns.append(num);ds.append(den);zs.append(z)
  if u['kind']=='plant':
   j=ks.index(case['k']);a,b,_=P.collisions(u['plain'],case['k']+1);assert num[0,j]==a and den[j]==b
 save(f'control{ix:02}',fs,np.concatenate(ns,axis=1),np.concatenate(ds),np.concatenate(zs,axis=1),dict(input_sha256=H(O/'inputs.json'),control_id=case['id'],planted_k=case['k'],seconds=time.monotonic()-t))
def selftest():
 rng=np.random.default_rng(2026092301);fs=[dict(page=i,k=k) for i in range(5) for k in range(2,5)]
 z=rng.normal(size=(200,len(fs)));d=aggregate(fs,z)
 raw=np.array([[sum(float(z[r,i]) for i,f in enumerate(fs) if f['k']==k)/np.sqrt(5) for k in [2,3,4]] for r in range(200)])
 sc=(raw-raw.mean(axis=0))/raw.std(axis=0);assert np.allclose(sc,d['standardized'],atol=1e-14)
 for ix in [1,8,37,199]:
  perm=np.arange(200);perm[0],perm[ix]=perm[ix],perm[0];a=aggregate(fs,z[perm]);assert np.allclose(a['maximum'],d['maximum'][perm]);assert a['rank']==sum(d['maximum']>=d['maximum'][ix])/200
 ties=aggregate(fs,np.ones((200,len(fs))));assert ties['rank']==1 and np.all(ties['maximum']==0)
 (O/'selftest.json').write_text(json.dumps({'passed':True,'scalar_cells':600,'relabelings':4,'constant_ties':'rank1','code_sha256':H(pathlib.Path(__file__))},indent=2)+'\n');print('selftest PASS')
def actual():
 P.ex.guard();assert (O/'REVIEW-CLEARED').exists();assert not (O/'actual.json').exists()
 base=R/'exploration/persistent-02/feedback/C07';meta=json.loads((base/'actual.json').read_text());a=np.load(base/'actual.npz')
 save('actual',meta['features'],a['numerators'],a['denominators'],a['z'],dict(source_json_sha256=H(base/'actual.json'),source_arrays_sha256=H(base/'actual.npz'),new_seed_coverage=0,scope='same C07features; shared-period aggregate'))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='selftest':selftest()
 elif sys.argv[1]=='control':
  for ix in map(int,sys.argv[2:]):control(ix)
 elif sys.argv[1]=='actual':actual()
