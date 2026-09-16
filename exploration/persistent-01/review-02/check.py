import json,gzip,pathlib,datetime,numpy as np
R=pathlib.Path('exploration/persistent-01/review-02'); F=R.parent/'worker-f'
M=json.load(open(F/'F01-maps.json'));E=json.load(gzip.open(F/'F01-evidence.json.gz','rt'));E3=json.load(gzip.open(F/'F03-evidence.json.gz','rt'));J=json.load(open(F/'F03-result.json'))
assert not {4,9,14,19,24,29,34,39,44,54}&{m['page'] for m in M}
X=[np.asarray(m['indices']) for m in M];Y=[np.asarray(m['labels']) for m in M]
def guard():
 assert not (R.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def G(t):
 t=np.asarray(t,float);a=t.sum(0);b=t.sum(1);n=t.sum();ans=0.
 for row in range(len(b)):
  positive=t[row]>0;ans+=np.sum(t[row,positive]*np.log(t[row,positive]*n/(b[row]*a[positive])))
 return float(2*ans)
def f01(xs,ys,offs=None,trim=False):
 tabs=[np.zeros((2,n)) for n in [29,29,841,2]*2]
 for p,(x,y) in enumerate(zip(xs,ys)):
  if offs is not None:y=np.concatenate((y[:,-offs[p]:],y[:,:-offs[p]]),axis=1) if offs[p] else y.copy()
  if trim:x=x[1:-1];y=y[:,1:-1]
  for k in range(2):
   for edge in range(2):np.add.at(tabs[4*k+edge],(y[2*k+edge],x),1)
   pair=x[:-1]*29+x[1:];same=x[:-1]==x[1:];bound=y[2*k,1:]
   np.add.at(tabs[4*k+2],(bound[~same],pair[~same]),1)
   np.add.at(tabs[4*k+3],(bound,same.astype(int)),1)
 return np.array([G(t) for t in tabs])
maxerr=0.;counts=0
for name in ['real','trim']:
 d=E[name];assert np.allclose(f01(X,Y,trim=name=='trim'),d['real'],atol=1e-9)
 for offsets,saved in zip(d['offsets'],d['null']):
  calc=f01(X,Y,offsets,trim=name=='trim');maxerr=max(maxerr,float(np.max(np.abs(calc-saved))));counts+=1
 guard()
control_checks=[]
for d in E['controls']:
 xs=[np.asarray(x) for x in d['streams']];assert np.allclose(f01(xs,Y),d['real'],atol=1e-9)
 # All stored control null tails independently checked; full rotations checked on first and last.
 for i in [0,-1]:assert np.allclose(f01(xs,Y,d['offsets'][i]),d['null'][i],atol=1e-9)
 tails=(1+(np.asarray(d['null'])>=d['real']).sum(0))/200
 assert np.allclose(tails,d['tails']);control_checks.append({'type':d['type'],'reject':bool(min(tails)*8<=.05)})
fold=np.asarray([m['page']%3 for m in M]);labs=[y[2].copy() for y in Y]
for y in labs:y[0]=0
def table(i,z):
 t=np.zeros((2,29));np.add.at(t,(z[1:],X[i][1:]),1);return t
def scan(zs):
 tt=np.asarray([table(i,z) for i,z in enumerate(zs)]);total=tt.sum(0);parts=[]
 for f in range(3):
  fit=tt[fold!=f].sum(0)+1;test=tt[fold==f].sum(0);fit/=fit.sum(1)[:,None];parts.append(float(np.dot(test[1],np.log(fit[1]/fit[0]))))
 return np.asarray([G(total),sum(parts)]),parts,tt
real,parts,tt=scan(labs);assert np.allclose(real,J['real']);assert np.array_equal(tt.sum(0),J['counts_by_rune']);assert np.allclose(parts,J['fold_scores'])
max3=0.;null=[]
for j,(maps,saved) in enumerate(zip(E3['null_start_maps'],E3['null'])):
 zs=[]
 for p,starts in enumerate(maps):
  z=np.zeros(len(X[p]),int);z[starts]=1;assert z[0]==0
  for s in E3['strata'][p]:assert z[s].sum()==labs[p][s].sum()
  zs.append(z)
 calc=scan(zs)[0];null.append(calc);max3=max(max3,float(np.max(np.abs(calc-saved))))
 if j%100==0:guard()
# Semantics derived from source-line and coordinates without opening raw originals.
sem=[];strata=[]
for m,x,y in zip(M,X,labs):
 lines={};cover=[];ss={}
 for w in m['words']:
  lines.setdefault(w['source_line'],[]).append(w);cover.extend(range(w['start'],w['end']))
  for i in range(w['start'],w['end']):
   if i: ss.setdefault((min(i-w['start'],4),min(w['end']-w['start'],8),min(2,3*i//len(x))),[]).append(i)
 assert cover==list(range(len(x)))
 starts=[ws[0]['start'] for ws in lines.values()];ends=[ws[-1]['end']-1 for ws in lines.values()]
 assert starts==np.flatnonzero(m['labels'][2]).tolist();assert ends==np.flatnonzero(m['labels'][3]).tolist()
 assert all(m['labels'][0][s] for s in starts)
 assert all(a<b for a,b in zip(m['source_char_positions'],m['source_char_positions'][1:]))
 sem.append({'page':m['page'],'source_lines':len(lines),'runes':len(x)})
 strata.append([np.asarray(v) for v in ss.values()])
rng=np.random.default_rng(1609202602);new=[];mapsout=[]
for j in range(999):
 zs=[]
 for y,ss in zip(labs,strata):
  z=np.zeros_like(y)
  for s in ss:z[rng.choice(s,int(y[s].sum()),replace=False)]=1
  zs.append(z)
 new.append(scan(zs)[0][0]);mapsout.append([np.flatnonzero(z).tolist() for z in zs])
 if j%100==0:guard()
infl=sorted([(real[0]-G(tt.sum(0)-t),m['page'],i) for i,(m,t) in enumerate(zip(M,tt))],reverse=True);deleted=[i for _,_,i in infl[:3]]
out={'status':'checked_exploratory_association_not_cipher_finding','pages':len(M),'runes':sum(map(len,X)),'line_count':sum(s['source_lines'] for s in sem),'f01':{'full_saved_real_rotations_checked':counts,'max_abs_error':maxerr,'line_start_G':E['real']['real'][4],'tail':E['real']['tails'][4],'trim_G':E['trim']['real'][4],'trim_tail':E['trim']['tails'][4],'control_real_checked':32,'control_null_rotations_checked':64,'all_control_tails_checked':True,'control_detection':{typ:sum(c['reject'] for c in control_checks if c['type']==typ) for typ in ['baseline','alphabet','successor','repeat']}},'f03':{'real':real.tolist(),'fold_scores':parts,'max_abs_error':max3,'saved_draws_checked':len(null),'tail':((1+(np.asarray(null)>=real).sum(0))/2000).tolist(),'stratum_count_invariants_checked':True,'removed_top3_pages':[p for _,p,_ in infl[:3]],'G_without_top3':G(np.delete(tt,deleted,axis=0).sum(0))},'falsifier':{'seed':1609202602,'null_count':999,'null_max':max(new),'G':real[0],'tail':(1+sum(v>=real[0] for v in new))/1000,'movable_starts':sum(int(y[s].sum()) for y,ss in zip(labs,strata) for s in ss if 0<y[s].sum()<len(s))},'semantics':sem}
(R/'checked-findings.json').write_text(json.dumps(out,indent=2));
with gzip.open(R/'falsifier-evidence.json.gz','wt') as f:json.dump({'null':new,'maps':mapsout},f)
print(json.dumps(out,indent=2))
