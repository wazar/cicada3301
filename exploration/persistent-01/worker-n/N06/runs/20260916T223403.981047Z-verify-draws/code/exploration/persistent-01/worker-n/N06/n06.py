from pathlib import Path
from collections import Counter
import json,gzip,math,random,hashlib,statistics,datetime,shutil
O=Path('exploration/persistent-01/worker-n/N06');D=Path('exploration/persistent-01/worker-p/P05')
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime.fromisoformat('2026-09-17T03:30:37+00:00')
assert not Path('exploration/persistent-01/STOP').exists()
(O/'snapshots').mkdir(exist_ok=True)
inputs=[]
def load(path):
 data=path.read_bytes();inputs.append(dict(path=str(path),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
 (O/'snapshots'/path.name).write_bytes(data)
 return json.load(gzip.open(path,'rt') if path.suffix=='.gz' else open(path))
M=load(D/'model.json');un=[math.exp(v) for v in M['u']];tr=[math.exp(v) for v in M['tri']]
def cumulative(probs):
 out=[];s=0.
 for v in probs:s+=v;out.append(s)
 assert abs(s-1)<1e-12
 return out
uc=cumulative(un);tc=[cumulative(tr[i:i+17]) for i in range(0,len(tr),17)]
def pick(cdf,u):
 for i,v in enumerate(cdf):
  if u<v:return i
 raise AssertionError((cdf,u))
def generate(mapping,n,seed):
 source_rng=random.Random(seed);emission_rng=random.Random(seed+1)
 plain=[];sd=[];cipher=[];ed=[];bins=[[r for r,v in enumerate(mapping) if v==a] for a in range(17)]
 for i in range(n):
  v=source_rng.random();sd.append(v);a=pick(uc if i<2 else tc[plain[-2]*17+plain[-1]],v);plain.append(a)
  group=bins[a];initial=emission_rng.random();r=group[int(initial*len(group))];coin=redraw=None
  if cipher and r==cipher[-1] and len(group)>1:
   coin=emission_rng.random()
   if coin<.83:
    rest=[x for x in group if x!=r];redraw=emission_rng.random();r=rest[int(redraw*len(rest))]
  cipher.append(r);ed.append([initial,coin,redraw])
 assert [mapping[r] for r in cipher]==plain
 return plain,cipher,sd,ed
def terms(mapping,cipher):
 p=[mapping[r] for r in cipher];cnt=Counter(mapping);lm=[];em=[]
 for i,(r,a) in enumerate(zip(cipher,p)):
  lm.append(M['u'][a] if i<2 else M['tri'][(p[i-2]*17+p[i-1])*17+a])
  k=cnt[a]
  if k==1 or i==0 or p[i-1]!=a:prob=1/k
  elif r==cipher[i-1]:prob=.17/k
  else:prob=1/k+.83/(k*(k-1))
  em.append(math.log(prob))
 return lm,em
def ranking(vals):
 return dict(rank=1+sum(v>vals[0]+1e-9 for v in vals[1:]),ties=[i for i in range(1,9) if abs(vals[i]-vals[0])<=1e-9],margin=vals[0]-max(vals[1:]),selected=max(range(9),key=vals.__getitem__))
records=[];books=[]
for group in range(4):
 for control_rep in range(4):
  idx=4*group+control_rep;r=load(D/f'control-{group}-{control_rep}.json.gz');maps=[r['control']['truth']]+[a['map'] for a in r['alternatives']]
  n=len(r['cipher']);cut=r['cut'];books.append(dict(index=idx,group=group,control_rep=control_rep,n=n,cut=cut,source=M['sources'][5+group]['name'],maps=maps,identical_truth_maps=[i for i in range(1,9) if maps[i]==maps[0]],unique_map_count=len({tuple(m) for m in maps})))
  for rep in range(100):
   seed=1706000+1000*idx+2*rep;plain,cipher,sd,ed=generate(maps[0],n,seed);scores=[]
   for mapping in maps:
    lm,em=terms(mapping,cipher)
    scores.append(dict(prefix_lm=sum(lm[:cut]),prefix_emission=sum(em[:cut]),suffix_lm=sum(lm[cut:]),suffix_emission=sum(em[cut:])))
   for a in scores:
    a['prefix']=a['prefix_lm']+a['prefix_emission'];a['suffix']=a['suffix_lm']+a['suffix_emission'];a['full']=a['prefix']+a['suffix']
   ranks={part:ranking([s[part] for s in scores]) for part in ['prefix','suffix','full']}
   chosen=ranks['prefix']['selected'];observed={part:sorted(set(cipher[sl])) for part,sl in [('prefix',slice(0,cut)),('suffix',slice(cut,None))]}
   equivalence={part:[i for i in range(1,9) if all(maps[i][v]==maps[0][v] for v in ids)] for part,ids in observed.items()}
   # Equal labels on observed runes need not give equal likelihood: bin sizes matter.
   records.append(dict(codebook=idx,group=group,rep=rep,n=n,cut=cut,source_seed=seed,emission_seed=seed+1,source_uniforms=sd,emission_uniforms=ed,plain=plain,cipher=cipher,scores=scores,ranks=ranks,observed_label_equivalence=equivalence,prefix_selected_suffix_margin=scores[chosen]['suffix']-scores[0]['suffix'],prefix_selected_suffix_accuracy=sum(maps[chosen][cipher[i]]==plain[i] for i in range(cut,n))/(n-cut)))
  print(json.dumps(dict(codebook=idx,n=n,done=100)),flush=True)
def summarize(rr):
 out=dict(samples=len(rr))
 for part in ['prefix','suffix','full']:
  ranks=[r['ranks'][part] for r in rr];margins=[x['margin'] for x in ranks]
  out[part]=dict(truth_top=sum(x['rank']==1 for x in ranks),truth_strict_top=sum(x['margin']>1e-9 for x in ranks),truth_tied_top=sum(bool(x['rank']==1 and x['ties']) for x in ranks),truth_numeric_ties=sum(bool(x['ties']) for x in ranks),rank_hist=dict(Counter(x['rank'] for x in ranks)),mean_margin=statistics.mean(margins),median_margin=statistics.median(margins),min_margin=min(margins),max_margin=max(margins),pairwise_truth_advantage_means=[statistics.mean(r['scores'][0][part]-r['scores'][i][part] for r in rr) for i in range(1,9)])
 out['prefix_selected_suffix_accuracy_mean']=statistics.mean(r['prefix_selected_suffix_accuracy'] for r in rr)
 out['prefix_selected_suffix_margin_mean']=statistics.mean(r['prefix_selected_suffix_margin'] for r in rr)
 out['prefix_selected_alternative_count']=sum(r['ranks']['prefix']['selected']!=0 for r in rr)
 out['observed_label_equivalence_count']={part:sum(bool(r['observed_label_equivalence'][part]) for r in rr) for part in ['prefix','suffix']}
 return out
summary=dict(all=summarize(records),by_group=[dict(group=g,source=books[g*4]['source'],n=books[g*4]['n'],results=summarize([r for r in records if r['group']==g])) for g in range(4)],by_codebook=[dict(codebook=i,results=summarize([r for r in records if r['codebook']==i])) for i in range(16)],codebooks=books)
with gzip.open(O/'records.json.gz','wt') as f:json.dump(records,f)
(O/'results.json').write_text(json.dumps(summary,indent=2));(O/'inputs.json').write_text(json.dumps(inputs,indent=2));print(json.dumps(summary['all'],indent=2))
