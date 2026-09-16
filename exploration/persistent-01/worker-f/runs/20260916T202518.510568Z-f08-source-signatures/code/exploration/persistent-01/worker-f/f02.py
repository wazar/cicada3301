import pathlib,json,numpy as np,gzip,datetime
R=pathlib.Path(__file__).parent;rng=np.random.default_rng(2026091712);M=json.load(open(R/'F01-maps.json'));pages=[m['page'] for m in M];edges=[(i,j) for i,p in enumerate(pages) for j,q in enumerate(pages) if q==p+1];counts=[len(m['words']) for m in M]
def guard():
 assert not (R.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def tables(maps):
 out=[]
 for m in maps:
  a=np.zeros((8,29))
  for w in m['words']:a[min(7,w['end']-w['start']-1),m['indices'][w['end']-1]]+=1
  out.append(a)
 return np.array(out)
def distances(t):
 feats=[t.sum(2),t.reshape(len(t),-1)];out=[]
 for f in feats:
  f=np.sqrt(f/f.sum(1)[:,None]);out.append(((f[:,None,:]-f[None,:,:])**2).sum(2)/2)
 return np.array(out)
def trial(t,n):
 ds=distances(t);a=np.array([e[0] for e in edges]);b=np.array([e[1] for e in edges]);real=-ds[:,a,b].mean(1);perms=np.array([rng.permutation(len(t)) for _ in range(n)]);null=np.array([-ds[:,p[a],p[b]].mean(1) for p in perms]);tails=(1+(null>=real).sum(0))/(n+1)
 return {'tables':t.tolist(),'real':real.tolist(),'null':null.tolist(),'permutations':perms.tolist(),'tails':tails.tolist(),'bonferroni2':np.minimum(1,2*tails).tolist()}
real=trial(tables(M),1999);controls=[]
for typ in ['baseline','length','terminal','both']:
 for rep in range(8):
  guard();tab=[]
  for p,n in zip(pages,counts):
   state=int(p>=28);pl=np.full(8,.1);pr=np.full(29,.1)
   if typ in ['length','both']:pl[:3 if state==0 else 0]=3 if state==0 else .1;pl[5:]=3 if state else .1
   if typ in ['terminal','both']:pr[:7]=3 if state==0 else .1;pr[22:]=3 if state else .1
   a=rng.choice(8,n,p=pl/pl.sum());b=rng.choice(29,n,p=pr/pr.sum());tab.append(np.bincount(a*29+b,minlength=232).reshape(8,29))
  t=trial(np.array(tab),499);t.update(type=typ,rep=rep);controls.append(t)
summary={'pages':pages,'edges':[[pages[i],pages[j]] for i,j in edges],'statistics':['negative_mean_adjacent_length_hellinger','negative_mean_adjacent_length_terminal_hellinger'],'real':{k:v for k,v in real.items() if k in ['real','tails','bonferroni2']},'controls':[{k:v for k,v in t.items() if k in ['type','rep','real','tails','bonferroni2']} for t in controls],'detections':{typ:sum(min(t['bonferroni2'])<=.05 for t in controls if t['type']==typ) for typ in ['baseline','length','terminal','both']},'counts':{'real':1,'real_null':1999,'controls':32,'control_null':15968},'seed':2026091712}
with gzip.open(R/'F02-evidence.json.gz','wt') as f:json.dump({'real':real,'controls':controls},f)
(R/'F02-result.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
