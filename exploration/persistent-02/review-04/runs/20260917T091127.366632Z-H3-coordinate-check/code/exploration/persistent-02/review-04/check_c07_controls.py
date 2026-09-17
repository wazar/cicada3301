"""Targeted two synthetic-book composite checks, not repeated actual negatives."""
from check_c07 import O,R,F,independent_matrix,null,dump
import json,hashlib,math,numpy as np
def main():
 d=json.loads((F/'C07/inputs.json').read_text());rows=[]
 for ix in [0,1]:
  plant=d['controls'][ix];name=f'control{ix:02}';meta=json.loads((F/'C07'/(name+'-book.json')).read_text())
  with np.load(F/'C07'/(name+'-book.npz')) as raw:a={k:raw[k] for k in raw.files}
  expected=[];offsets={};offset=0
  for page,source in zip(d['pages'],meta['sources']):
   p=page['page'];base=2026600000+100000*ix+1000*p;c=plant['cipher'] if p==49 else null(page['cipher'],base+900);assert source['cipher']==c and source['page_slot']==p and source['seedbase']==base;assert source['baseline_seed']==(None if p==49 else base+900)
   ks=list(range(2,len(c)//20));expected.extend(dict(page_slot=p,k=k) for k in ks);offsets[p]=(offset,len(ks),c,base);offset+=len(ks)
  assert len(meta['sources'])==45 and meta['features']==expected and a['z'].shape==(200,len(expected))
  z=np.empty_like(a['z']);fraction=a['numerators']/a['denominators']
  for col in range(len(expected)):
   v=fraction[:,col].tolist();mu=math.fsum(v)/200;sd=math.sqrt(math.fsum((x-mu)**2 for x in v)/200);z[:,col]=[(x-mu)/sd for x in v]
  mx=z.max(axis=1);rank=(1+sum(x>=mx[0] for x in mx[1:]))/200;assert np.max(np.abs(z-a['z']))<1e-12 and np.max(np.abs(mx-a['family_maximum']))<1e-12;assert rank==meta['rank'] and expected[int(z[0].argmax())]==meta['selected']
  for p in [0,49]:
   start,count,c,seed=offsets[p];ks,num,den,zz=independent_matrix(c,seed);assert np.array_equal(num,a['numerators'][:,start:start+count]);assert np.array_equal(den,a['denominators'][start:start+count]);assert np.max(np.abs(zz-a['z'][:,start:start+count]))<1e-12
  local=json.loads((F/'C07'/(name+'-local.json')).read_text());ks,num,den,zz=independent_matrix(plant['cipher'],2026300000+1000*ix)
  with np.load(F/'C07'/(name+'-local.npz')) as q:assert np.array_equal(num,q['numerators']) and np.array_equal(den,q['denominators']) and np.max(np.abs(zz-q['z']))<1e-12
  mm=zz.max(axis=1);lr=(1+sum(x>=mm[0] for x in mm[1:]))/200;assert lr==local['rank']
  rows.append(dict(index=ix,id=plant['id'],features=len(expected),book_rank=rank,local_rank=lr,selected=meta['selected'],all45backgrounds_reconstructed=True,recomputed_period_matrices_for_slots=[0,49],book_metadata_sha256=hashlib.sha256((F/'C07'/(name+'-book.json')).read_bytes()).hexdigest()))
  print('C07 controlbook',ix,len(expected),rank,lr,flush=True)
 dump('c07-control-checks.json',dict(passed=True,rows=rows,scope='Allbookfeaturesaggregated independently;two200-panelunits perbook pluslocalpanel fullyrebuilt. Shortcontrolpower mustbe reported, nottransferred from716runes. NoactualC07scoring.'))
if __name__=='__main__':main()
