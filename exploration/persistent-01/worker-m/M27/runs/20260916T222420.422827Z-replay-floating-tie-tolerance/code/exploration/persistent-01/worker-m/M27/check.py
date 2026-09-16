import pathlib,json,gzip,numpy as np,hashlib
R=pathlib.Path(__file__).parent
inp=json.load(open(R/'input.json'));assert len(inp['pages'])==45 and not(set(inp['pages'])&{4,9,14,19,24,29,34,39,44,54})
files=sorted((R/'fits').glob('*.json.gz'));nrows=0;valid=0;accepted=0
for f in files:
 with gzip.open(f,'rt') as h:a=json.load(h)
 v=a['cipher'];C=np.zeros((45,29,29),dtype=int)
 for k,page in enumerate(v):
  assert len(page)==inp['lengths'][k]
  for x,y in zip(page,page[1:]):C[k,x,y]+=1
 assert np.array_equal(C,a['perpage_counts']);tr=C[::2].sum(0);he=C[1::2].sum(0)
 b=np.array(a['baseline']);assert np.allclose(b.sum(1),1)
 assert max(r['training_objective'] for r in a['rows'])-a['rows'][a['selected_start']]['training_objective']<1e-7
 for r in a['rows']:
  g=np.array(r['mapping']);T=np.array(r['T']);P=np.array(r['symbol_probabilities']);assert np.allclose(P.sum(1),1)
  tab=np.zeros((17,17),int)
  for x in range(29):
   for y in range(29):
    tab[g[x],g[y]]+=tr[x,y]
    emit=1/np.count_nonzero(g==g[y])
    if g[x]==g[y] and g[x]<12:emit=.5*(1-.83) if x==y else .5*(1+.83)
    assert abs(P[x,y]-T[g[x],g[y]]*emit)<1e-14
  assert np.allclose(T,(tab+1)/(tab.sum(1)[:,None]+17))
  for k in range(12):
   x,y=np.flatnonzero(g==k);outside=g!=k
   assert np.array_equal(P[x,outside],P[y,outside]);assert P[x,x]==P[y,y] and P[x,y]==P[y,x]
  assert abs(r['held_gain']-float((he*np.log(P/b)).sum()/he.sum()))<1e-12
  valid+=r['valid_proposals'];accepted+=r['accepted'];nrows+=1
for ix in range(12):
 meta=json.load(open(R/'controls'/f'{ix}-generator.json'));U=np.load(R/'controls'/f'{ix}-draws.npz')['uniform'];T=np.array(meta['T']);pi=np.array(meta['pi']);bins=meta['bins'];g=np.array(meta['mapping']);assert np.allclose(pi@T,pi)
 er=np.array([.085]*12+[1]*5);assert abs(float(pi@(np.diag(T)*er))-meta['target_repeat'])<1e-12
 with gzip.open(R/'fits'/f'control-{ix}.json.gz','rt') as h:actual=json.load(h)['cipher']
 start=0
 for page,(n,v) in enumerate(zip(inp['lengths'],actual)):
  u=U[start:start+n];start+=n;out=[];raw=[];cl=[];z=int(np.searchsorted(np.cumsum(pi),u[0,0]))
  for i in range(n):
   if i:z=int(np.searchsorted(np.cumsum(T[z]),u[i,0]))
   b=bins[z];x=b[int(u[i,1]*len(b))];raw.append(x);cl.append(z)
   if out and x==out[-1] and len(b)==2 and u[i,2]<.83:x=b[1-b.index(x)]
   out.append(x)
  assert out==v and raw==meta['rawchoices'][page] and cl==meta['classes'][page]
 assert start==len(U)
assert len(files)==440 and nrows==1760
manifest={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(R.rglob('*')) if p.is_file() and 'runs' not in p.parts and p.name not in ['manifest.json','checks.json']}
(R/'manifest.json').write_text(json.dumps(manifest,indent=2));out=dict(status='PASS',fit_packets=len(files),all_start_predictions=nrows,nominal_proposals=440*6000,actual_valid_proposals=valid,accepted=accepted,control_reencryptions=12*45,reserved_pages_read=0,all_rows_normalized=True,exact_row_sharing_diagonal_exception=True,training_only_selection=True)
(R/'checks.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
