import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import numpy as np,json,gzip,random
ROOT=Path(__file__).resolve().parents[3];B=ROOT/'exploration/persistent-01';P=B/'worker-p/P25-clean';Q=B/'coordinator/Q05-latin-clean'
assert not (B/'STOP').exists()
def read(f):
 with gzip.open(f,'rt') as z:return json.load(z)
keys=json.loads((P/'keys.json').read_text());base=json.loads((ROOT/'exploration/overnight-01/worker-a/r02/keys.json').read_text())['keys'][:16]
assert len(keys)==162
for k in keys:
 src=next(x for x in base if x['id']==k['key_id']);phase=k['phase'];assert k['key']==src['key'][phase:]+src['key'][:phase]
lookup={k['id']:k for k in keys};logp=np.load(Q/'model.npz')['logp'];controls=read(Q/'held-controls.json.gz');pages={p['page']:p for p in json.loads((B/'worker-f/F06-maps.json').read_text()) if p['page'] in [0,17,55]}
rows=[];alternatives=0;maxerr=0
for ix in range(7):
 packet=json.loads((P/f'packet-{ix}.json').read_text());c0=packet['cipher'];ends=packet['ends'];n=len(c0)
 if ix<4:
  assert packet['truth']==controls[ix]['indices'] and ends==controls[ix]['ends']
  key=lookup[packet['truth_id']];u=0;c=[]
  for i,v in enumerate(packet['truth']):
   if v==0 and i%3!=1:c.append(0)
   else:c.append((v-key['sign']*key['key'][u%len(key['key'])])%29);u+=1
  assert c==c0 and u==packet['truth_used']
 else:
  page=pages[[0,17,55][ix-4]];assert c0==page['indices'] and ends==[w['end']-1 for w in page['words']]
 packetresults=[]
 for ni in [-1]+list(range(19)):
  name=f'packet-{ix}-'+('main' if ni<0 else f'null-{ni:02}');r=read(P/(name+'.json.gz'));c=r['cipher']
  if ni<0:assert c==c0
  else:
   seed=525200+100*ix+ni;assert seed==r['null_seed'];rng=random.Random(seed);expected=[]
   for i,v in enumerate(c0):
    if v==0:expected.append(0)
    elif i and v==c0[i-1]:expected.append(expected[-1])
    else:
     opts=[j for j in range(1,29) if not i or j!=expected[-1]];expected.append(opts[rng.randrange(len(opts))])
   assert c==expected
  assert ends==r['ends'] and [x['id'] for x in r['cells']]==[k['id'] for k in keys]
  allalts=[];tokenpos=np.arange(n)+np.searchsorted(ends,np.arange(n),side='left')
  for cell in r['cells']:
   k=lookup[cell['id']];alts=cell['alternatives'];a=np.asarray([x['plain'] for x in alts],int);lit=np.zeros(a.shape,bool)
   for j,x in enumerate(alts):lit[j,x['literal_positions']]=True
   assert np.all(np.logical_or(~lit,np.asarray(c)[None,:]==0))
   consumed=np.cumsum(~lit,axis=1)-1
   keyarray=np.asarray(k['key']);expected=np.where(lit,0,(np.asarray(c)[None,:]+k['sign']*keyarray[np.maximum(consumed,0)%len(keyarray)])%29)
   assert np.array_equal(a,expected)
   assert [int(z) for z in (~lit).sum(1)]==[x['used'] for x in alts]
   tokens=np.full((len(alts),n+len(ends)),29,int);tokens[:,tokenpos]=a
   b=np.concatenate([np.full((len(alts),1),29),tokens[:,:-1]],axis=1);aa=np.concatenate([np.full((len(alts),2),29),tokens[:,:-2]],axis=1)
   scores=logp[aa,b,tokens].sum(1)/tokens.shape[1];err=float(np.max(abs(scores-np.asarray([x['score'] for x in alts]))));maxerr=max(maxerr,err);assert err<1e-12
   assert all(alts[i]['score']>=alts[i+1]['score'] for i in range(len(alts)-1)) and cell['top_score']==alts[0]['score']
   allalts.extend(dict(id=cell['id'],**x) for x in alts);alternatives+=len(alts)
  allalts.sort(key=lambda x:x['score'],reverse=True);chosen=[];groups={}
  for alt in allalts:
   path=(tuple(alt['plain']),tuple(alt['literal_positions']))
   if path not in groups and len(chosen)<16:groups[path]=dict(**alt,aliases=[]);chosen.append(groups[path])
   if path in groups:groups[path]['aliases'].append(alt['id'])
  assert chosen==r['global16'] and r['maximum']==allalts[0]['score']
  if ni<0 and ix<4:
   d=r['control'];truthcell=next(x for x in r['cells'] if x['id']==packet['truth_id'])
   assert d['truth_key_rank']==1+sum(x['top_score']>truthcell['top_score'] for x in r['cells'])
   assert d['selected_rune_errors']==sum(a!=b for a,b in zip(chosen[0]['plain'],packet['truth']))
  packetresults.append(r['maximum'])
 summary=json.loads((P/f'packet-{ix}-summary.json').read_text());tail=(1+sum(x>=packetresults[0] for x in packetresults[1:]))/20;assert tail==summary['tail']
 rows.append(dict(packet=ix,name=packet['name'],tail=tail,maximum=packetresults[0]))
 print('checked',ix,flush=True)
(P/'independent-check.json').write_text(json.dumps(dict(pass_all=True,panels=140,cells=22680,alternatives=alternatives,maximum_vector_score_error=maxerr,rows=rows),indent=2)+'\n')
print((P/'independent-check.json').read_text())
