"""Independent arithmetic review of persisted fitted models, no search execution."""
import pathlib,json,gzip,math,collections
import numpy as np
B=pathlib.Path(__file__).resolve().parents[1];D=B/'worker-m/M27';n=0;models=0;scores={};maxgap=0
for path in sorted((D/'fits').glob('*.json.gz')):
 with gzip.open(path,'rt') as f:p=json.load(f)
 c=np.zeros((29,29),dtype=int);h=c.copy();freq=np.zeros(29,dtype=int)
 for i,v in enumerate(p['cipher']):
  dest=c if i%2==0 else h
  for a,b in zip(v,v[1:]):dest[a,b]+=1
  if i%2==0:
   for a in v:freq[a]+=1
 w=(freq+.5)/(sum(freq)+14.5);repeat=(np.trace(c)+.5)/(c.sum()+1);base=np.zeros((29,29))
 for a in range(29):
  for b in range(29):base[a,b]=repeat if a==b else (1-repeat)*w[b]/(1-w[a])
 assert np.max(abs(base-np.array(p['baseline'])))<1e-14
 vals=[]
 for row in p['rows']:
  g=row['mapping'];bins=collections.Counter(g);assert sorted(bins.values())==[1]*5+[2]*12
  z=np.zeros((17,17),dtype=int);elog=0
  for a in range(29):
   for b in range(29):
    z[g[a],g[b]]+=c[a,b];sz=bins[g[b]];e=1/sz
    if g[a]==g[b] and sz==2:e=.085 if a==b else .915
    elog+=c[a,b]*math.log(e)
  obj=elog+sum(math.lgamma(17)-math.lgamma(int(sum(v))+17)+sum(math.lgamma(int(x)+1) for x in v) for v in z)
  gap=abs(obj-row['training_objective']);maxgap=max(maxgap,gap);assert gap<1e-7
  pred=np.zeros((29,29))
  for a in range(29):
   for b in range(29):
    sz=bins[g[b]];e=1/sz
    if g[a]==g[b] and sz==2:e=.085 if a==b else .915
    pred[a,b]=(z[g[a],g[b]]+1)/(sum(z[g[a]])+17)*e
  assert np.max(abs(pred-np.array(row['symbol_probabilities'])))<1e-14
  score=float((h*np.log(pred/base)).sum()/h.sum());assert abs(score-row['held_gain'])<1e-12
  vals.append(obj);models+=1
 assert max(vals)-vals[p['selected_start']]<1e-7
 assert p['score']==p['rows'][p['selected_start']]['held_gain'];scores[p['name']]=p['score'];n+=1
out=dict(packets=n,models=models,max_training_objective_difference=maxgap,scope='Every saved training objective, baseline, predicted row, held score and training-only selection independently reconstructed. Optimizer paths and generation not rerun; worker checks separately preserve generation replay.')
(B/'coordinator/M27-arithmetic-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
