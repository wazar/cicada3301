import os
for x in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[x]='1'
from pathlib import Path
import numpy as np,json,gzip,random,hashlib
R=Path(__file__).parent;B=R.parent
read=lambda p:json.load(gzip.open(p,'rt'))
P=B/'worker-p/P25';N=B/'worker-p/P25-clean';keys=json.loads((P/'keys.json').read_text());assert len(keys)==162
base=json.loads(Path('exploration/overnight-01/worker-a/r02/keys.json').read_text())['keys'][:16]
expected=[(x['id'],p,s,x['key'][p:]+x['key'][:p]) for x in base for p in range(len(x['key'])) for s in [-1,1]]
assert [(k['key_id'],k['phase'],k['sign'],k['key']) for k in keys]==expected
LM=[np.load(B/f'coordinator/{name}/model.npz')['logp'] for name in ['Q05-latin','Q05-latin-clean']]
pages={p['page']:p for p in json.loads((B/'worker-f/F06-maps.json').read_text())};held=read(B/'coordinator/Q05-latin/held-controls.json.gz');hashes={};stats=[];changedcells=changedsets=changedwinners=changedbestpaths=alternatives=0;maxerr=0.;leaders=[]
def track(p):
 data=p.read_bytes();hashes[str(p)]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
for ix in range(7):
 packet=json.loads((P/f'packet-{ix}.json').read_text());assert packet==json.loads((N/f'packet-{ix}.json').read_text());c0=packet['cipher'];ends=packet['ends']
 if ix>=4:
  p=pages[[0,17,55][ix-4]];assert c0==p['indices'] and ends==[w['end']-1 for w in p['words']]
 else:
  assert packet['truth']==held[ix]['indices'] and ends==held[ix]['ends'];k=next(k for k in keys if k['id']==packet['truth_id']);lit=[i for i,x in enumerate(packet['truth']) if x==0 and i%3!=1];assert lit==packet['truth_literal'];u=0
  for i,x in enumerate(packet['truth']):
   if i in lit:assert c0[i]==0
   else:assert c0[i]==(x-k['sign']*k['key'][u%len(k['key'])])%29;u+=1
  assert u==packet['truth_used']
 maxima=[[],[]]
 for ni in range(-1,19):
  name=f'packet-{ix}-'+('main' if ni<0 else f'null-{ni:02}')+'.json.gz';rs=[read(d/name) for d in [P,N]]
  for d in [P,N]:track(d/name)
  assert rs[0]['cipher']==rs[1]['cipher'] and rs[0]['ends']==rs[1]['ends']==ends and rs[0]['null_seed']==rs[1]['null_seed']
  c=rs[0]['cipher']
  if ni<0:assert c==c0
  else:
   seed=525200+100*ix+ni;assert seed==rs[0]['null_seed'];rng=random.Random(seed);out=[]
   for i,v in enumerate(c0):
    if v==0:y=0
    elif i and v==c0[i-1]:y=out[-1]
    else:
     opts=list(range(1,29))
     if i and out[-1] in opts:opts.remove(out[-1])
     y=opts[rng.randrange(len(opts))]
    out.append(y)
   assert c==out
  assert [x==0 for x in c]==[x==0 for x in c0] and [a==b for a,b in zip(c,c[1:])]==[a==b for a,b in zip(c0,c0[1:])]
  for mi,r in enumerate(rs):
   assert [x['id'] for x in r['cells']]==[k['id'] for k in keys];allpaths=[]
   for k,cell in zip(keys,r['cells']):
    alts=cell['alternatives'];aa=np.array([z['plain'] for z in alts]);mask=np.zeros_like(aa,bool)
    for row,z in enumerate(alts):
     assert z['literal_positions']==sorted(set(z['literal_positions']));mask[row,z['literal_positions']]=True
    assert np.all(np.where(mask,(aa==0)&(np.array(c)==0),True));used=(~mask).sum(1);assert used.tolist()==[z['used'] for z in alts]
    draw=np.cumsum(~mask,axis=1)-1;kk=np.array(k['key']);rec=np.where(mask,0,(aa-k['sign']*kk[draw%len(kk)])%29);assert np.all(rec==c)
    chunks=[];start=0
    for stop in ends:chunks.extend([aa[:,start:stop+1],np.full((len(aa),1),29)]);start=stop+1
    if start<len(c):chunks.append(aa[:,start:])
    tokens=np.concatenate(chunks,axis=1);padded=np.pad(tokens,((0,0),(2,0)),constant_values=29);sc=LM[mi][padded[:,:-2],padded[:,1:-1],padded[:,2:]].sum(1)/tokens.shape[1];err=float(abs(sc-np.array([z['score'] for z in alts])).max());maxerr=max(maxerr,err);assert err<1e-12
    assert cell['top_score']==max(z['score'] for z in alts) and all(alts[j]['score']>=alts[j+1]['score'] for j in range(len(alts)-1));alternatives+=len(alts);allpaths.extend(dict(id=k['id'],**z) for z in alts)
   ranked=sorted(allpaths,key=lambda z:-z['score']);unique={};top=[]
   for z in ranked:
    ident=(tuple(z['plain']),tuple(z['literal_positions']))
    if ident not in unique and len(top)<16:unique[ident]=dict(**z,aliases=[]);top.append(unique[ident])
    if ident in unique:unique[ident]['aliases'].append(z['id'])
   assert top==r['global16'] and ranked[0]['score']==r['maximum'];maxima[mi].append(r['maximum'])
   if ni<0 and ix<4:assert top[0]['plain']==packet['truth'] and top[0]['literal_positions']==packet['truth_literal'] and r['control']['truth_key_rank']==1
   if ni<0 and ix>=4:leaders.append({'packet':ix,'model':mi,'id':top[0]['id'],'plain':top[0]['plain'],'literal':top[0]['literal_positions']})
  changedcells+=sum(a['top_score']!=b['top_score'] for a,b in zip(rs[0]['cells'],rs[1]['cells']))
  ident=lambda a:[(x['plain'],x['literal_positions']) for x in a['alternatives']]
  changedsets+=sum(ident(a)!=ident(b) for a,b in zip(rs[0]['cells'],rs[1]['cells']))
  a,b=[r['global16'][0] for r in rs];changedwinners+=a['id']!=b['id'];changedbestpaths+=(a['plain'],a['literal_positions'])!=(b['plain'],b['literal_positions'])
 for mi,d in enumerate([P,N]):
  tail=(1+sum(x>=maxima[mi][0] for x in maxima[mi][1:]))/20;s=json.loads((d/f'packet-{ix}-summary.json').read_text());assert tail==s['tail'];stats.append({'packet':ix,'model':mi,'maximum':maxima[mi][0],'tail':tail})
 print('checked packet',ix,flush=True)
(R/'inputs.json').write_text(json.dumps(hashes,indent=2));(R/'leaders.json').write_text(json.dumps(leaders,indent=2));result=dict(status='PASS',panels=280,cells=45360,alternatives=alternatives,max_score_error=maxerr,changed_cells=changedcells,changed_pathsets=changedsets,changed_winners=changedwinners,changed_bestpaths=changedbestpaths,rows=stats,coverage='Saved beam-retained paths and selections; no claim of exact arbitrary-length path optimality');(R/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
