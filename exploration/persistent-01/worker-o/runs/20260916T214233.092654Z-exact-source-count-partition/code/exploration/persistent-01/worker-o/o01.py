import datetime,gzip,hashlib,json,pathlib
import numpy as np
R=pathlib.Path(__file__).resolve().parent
def guard():
 assert not (R.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
guard();seed=2026091731;rng=np.random.default_rng(seed)
path=R.parent/'worker-f/F06-maps.json';maps=json.loads(path.read_text())
reserved={4,9,14,19,24,29,34,39,44,54}
assert not reserved.intersection(m['page'] for m in maps)
rows=[]
for m in maps:
 heads=[];lengths=[];units=[]
 for i,w in enumerate(m['words']):
  u=m['indices'][w['start']:w['end']];assert len(u)>0
  heads.append(u[0]);lengths.append(min(8,len(u))-1)
  units.append({'unit_index':i,'runes':u,'span':[w['start'],w['end']],'source_char_positions':w['source_char_positions'],'length':len(u)})
 rows.append({'page':m['page'],'heads':heads,'length_bins':lengths,'units':units,'train_n':len(heads)*2//3})
ls=[np.array(r['length_bins'],dtype=int) for r in rows];heads=[np.array(r['heads'],dtype=int) for r in rows];cuts=[r['train_n'] for r in rows]
def fit_score(hs,details=False):
 joint=np.ones((29,8));prior=np.ones(8)
 for h,l,c in zip(hs,ls,cuts):
  np.add.at(joint,(h[:c],l[:c]),1);prior+=np.bincount(l[:c],minlength=8)
 # Likelihood P(head|length), with a separately learned local P(length).
 likelihood=joint/joint.sum(axis=0,keepdims=True)
 allg=[];pages=[]
 for r,h,l,c in zip(rows,hs,ls,cuts):
  baseline=np.bincount(l[:c],minlength=8)+1.;baseline/=baseline.sum()
  pr=likelihood[h[c:]]*baseline;pr/=pr.sum(axis=1,keepdims=True)
  gains=np.log(pr[np.arange(len(l)-c),l[c:]])-np.log(baseline[l[c:]])
  allg.extend(gains.tolist())
  if details:pages.append({'page':r['page'],'train_n':c,'test_n':len(l)-c,'gain':float(gains.mean()),'baseline':baseline.tolist(),'predictions':pr.tolist(),'truth':l[c:].tolist(),'test_heads':h[c:].tolist(),'per_unit_gain':gains.tolist()})
 out={'gain':float(np.mean(allg)),'n_test':len(allg)}
 if details:out.update(pages=pages,train_joint_counts=joint.tolist(),opcode_likelihood=likelihood.tolist())
 return out
def trial(hs,count):
 real=fit_score(hs,True);null=[];shifts=[]
 for i in range(count):
  if i%50==0:guard()
  off=[int(rng.integers(len(h))) for h in hs];shifts.append(off)
  null.append(fit_score([np.roll(h,o) for h,o in zip(hs,off)])['gain'])
 real.update(null=null,shifts=shifts,tail=(1+sum(v>=real['gain'] for v in null))/(count+1))
 return real
controls=[]
for k in range(4):
 perm=rng.permutation(29);groups=[a.tolist() for a in np.array_split(perm,8)]
 hh=[np.array([rng.choice(groups[int(v)]) for v in l]) for l in ls]
 t=trial(hh,99);t.update(groups=groups,heads=[h.tolist() for h in hh]);controls.append(t)
assert all(t['gain']>0 and t['tail']<=.05 for t in controls),'control gate failed'
real=trial(heads,999)
baseline=trial([rng.integers(0,29,len(l)) for l in ls],99)
# Reconstruct every original page stream to verify no symbol was dropped by mapping.
for r,m in zip(rows,maps):assert sum([u['runes'] for u in r['units']],[])==m['indices']
evidence={'rows':rows,'real':real,'controls':controls,'random_head_fixture':baseline,'seed':seed,'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
with gzip.open(R/'O01-evidence.json.gz','wt') as f:json.dump(evidence,f)
summary={'real':{k:real[k] for k in ['gain','n_test','tail']},'controls':[{k:t[k] for k in ['gain','n_test','tail']} for t in controls],'random_head_fixture':{k:baseline[k] for k in ['gain','n_test','tail']},'pages':len(rows),'units':sum(len(l) for l in ls),'fit_count':5+396+1+999+99,'input_sha256':evidence['input_sha256'],'seed':seed}
(R/'O01-result.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
