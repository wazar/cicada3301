import pathlib,json,numpy as np,hashlib,gzip,datetime
R=pathlib.Path(__file__).parent;M=json.load(open(R.parent/'worker-f/F06-maps.json'));C=[np.array(m['indices'],dtype=int) for m in M];rng=np.random.default_rng(2026091737);roots=[g for g in range(1,29) if len({pow(g,k,29) for k in range(28)})==28];assert len(roots)==12
powers=np.array([[pow(g,k,29) for k in range(29)] for g in roots])
def gate():
 assert not(R.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def encode(p,g):
 out=[];prev=0
 for v in p:c=int(v)*pow(g,-prev,29)%29;out.append(c);prev=c
 return np.array(out)
def decode(c,gi):return c*powers[gi,np.r_[0,c[:-1]]]%29
for g in roots:
 for prev in range(29):
  for p in range(29):assert ((p*pow(g,-prev,29)%29)*pow(g,prev,29))%29==p
def search(vs,retain=False):
 scores=[];outs=[];hist=[]
 for gi,g in enumerate(roots):
  ps=[decode(v,gi) for v in vs];train=np.concatenate([p[1:len(p)//2] for p in ps]);test=np.concatenate([p[len(p)//2:] for p in ps]);h=np.bincount(train,minlength=29)+1;q=h/h.sum();score=float(np.mean(np.log(29*q[test])));scores.append(score);hist.append(q.tolist())
  if retain:outs.append([p.tolist() for p in ps])
 return max(scores),scores,hist,outs
def params(vs):
 pre=[v[:len(v)//2] for v in vs];a=np.concatenate(pre);w=np.bincount(a,minlength=29)+1;w=w/w.sum();pairs=sum(len(v)-1 for v in pre);repeats=sum(int(np.sum(v[:-1]==v[1:])) for v in pre);repeat=repeats/pairs;matrix=np.empty((29,29))
 for last in range(29):
  row=w.copy();row[last]=0;row=row/row.sum()*(1-repeat);row[last]=repeat;matrix[last]=np.cumsum(row)
 return w,repeat,matrix
sample_count=0
def simulate(lengths,par):
 global sample_count
 w,repeat,cdf=par;out=[]
 for n in lengths:
  us=rng.random(n);v=np.empty(n,dtype=int);v[0]=np.searchsorted(np.cumsum(w),us[0])
  for i in range(1,n):v[i]=np.searchsorted(cdf[v[i-1]],us[i])
  out.append(v)
 sample_count+=1;return out
A='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';sources=[]
for f in pathlib.Path('audit/parallel-01/reference/sources').glob('solved_*.txt'):
 b=f.read_bytes();p=np.array([A.index(c) for c in b.decode() if c in A]);sources.append((len(p),str(f),p,hashlib.sha256(b).hexdigest()))
sources=sorted(sources,key=lambda r:(-r[0],r[1]))[:4];controls=[]
for gi,(n,path,p,sha) in enumerate(sources):
 gate();g=roots[gi];c=encode(p,g);assert np.array_equal(decode(c,gi),p);best,scores,hist,out=search([c],True);par=params([c]);null=[]
 for rep in range(99):null.append(search(simulate([len(c)],par))[0])
 controls.append(dict(source=path,sha256=sha,g=g,rune_count=len(p),source=p.tolist(),cipher=c.tolist(),exact_recovery=True,best_score=best,scores=scores,truth_rank=1+sum(s>scores[gi]+1e-12 for s in scores),tail=(1+sum(v>=best for v in null))/100,null=null,null_repeat_probability=par[1]))
assert any(c['tail']<=.05 and c['truth_rank']==1 for c in controls)
gate();best,scores,hist,outs=search(C,True);par=params(C);null=[];nullscores=[];repeatcounts=[]
for rep in range(199):
 if rep%20==0:gate()
 vs=simulate(list(map(len,C)),par);b,s,_,_=search(vs);null.append(b);nullscores.append(s);repeatcounts.append(sum(int(np.sum(v[1:]==v[:-1])) for v in vs))
r=dict(roots=roots,best_root=roots[int(np.argmax(scores))],best_score=best,scores=scores,tail=(1+sum(v>=best for v in null))/200,null=null,nullscores=nullscores,null_repeatcounts=repeatcounts,null_repeat_probability=par[1],null_symbol_weights=par[0].tolist(),controls=[{k:v for k,v in c.items() if k not in ['source','cipher','null']} for c in controls],real_candidates=12,real_null_searches=199,control_null_searches=396,total_simulations=sample_count,exhaustive_inverse_checks=12*29*29,seed=2026091737)
with gzip.open(R/'H17-evidence.json.gz','wt') as f:json.dump(dict(outputs=outs,prefix_probabilities=hist,controls=controls,real_cipher=[c.tolist() for c in C]),f)
(R/'H17-result.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k not in ['null','nullscores','null_repeatcounts','null_symbol_weights']},indent=2))
