from pathlib import Path
import json,math,itertools,sys,time,hashlib
import numpy as np
O=Path('exploration/persistent-01/coordinator/Q04-prefix'); F=Path('exploration/persistent-01/worker-f/F06-maps.json')
P=json.loads(F.read_text()); sizes=[len(p['indices']) for p in P]; cuts=np.cumsum([0]+sizes); masks=[np.array(p['indices'][1:])==np.array(p['indices'][:-1]) for p in P]
shapes=[(2,3),(4,1)]
def stats(stream,parity):
 emit=np.zeros(29,dtype=int);prev=emit.copy();first=emit.copy()
 for j in range(parity,len(P),2):
  x=stream[cuts[j]:cuts[j+1]];first[x[0]]+=1
  z=x[1:]!=x[:-1];emit+=np.bincount(x[1:][z],minlength=29);prev+=np.bincount(x[:-1][z],minlength=29)
 return emit,prev,first

def ll(st,m,high):
 e,p,f=st;h=np.array(high,dtype=int)
 return float((e[h].sum()+f[h].sum())*math.log(m)-f.sum()*math.log(32)-p.sum()*math.log(31)-p[h].sum()*math.log((32-m)/31))
def base(st):
 e,p,f=st;return -float(f.sum()*math.log(29)+e.sum()*math.log(28))
def fit(stream):
 train=stats(stream,0);held=stats(stream,1);rows=[]
 for m,k in shapes:
  e,p,f=train;value=(e+f)*math.log(m)-p*math.log((32-m)/31)
  high=sorted(sorted(range(29),key=lambda i:(-value[i],i))[:k]);rows.append(dict(multiplier=m,high=high,train_ll=ll(train,m,high),held_gain=(ll(held,m,high)-base(held))/int(sum(held[0])+sum(held[2]))))
 best=max(rows,key=lambda r:r['train_ll']);return dict(best=best,profiles=rows)
def generate(seed,m,high):
 rng=np.random.default_rng(seed);w=np.ones(29);w[high]=m; W=w.sum(); cumulative=np.cumsum(w);out=np.zeros(sum(sizes),dtype=np.uint8)
 for j,n in enumerate(sizes):
  u=rng.random(n);x=out[cuts[j]:cuts[j+1]];x[0]=np.searchsorted(cumulative,u[0]*W,side='right')
  for t in range(1,n):
   if masks[j][t-1]:x[t]=x[t-1];continue
   previous=int(x[t-1]);v=u[t]*(W-w[previous]);lo=cumulative[previous]-w[previous]
   if v>=lo:v+=w[previous]
   x[t]=np.searchsorted(cumulative,v,side='right')
 return out

def panel(seed,m,high,count,nullseed,name):
 actual=generate(seed,m,high) if seed is not None else np.concatenate([p['indices'] for p in P]).astype(np.uint8)
 f=fit(actual); chosen=f['best'];nulls=[];outputs=[]
 for i in range(count):
  x=generate(nullseed+i,chosen['multiplier'],chosen['high']);outputs.append(x);nulls.append(fit(x))
 score=chosen['held_gain']; tail=(1+sum(r['best']['held_gain']<=score for r in nulls))/(1+count)
 record=dict(name=name,seed=seed,source_multiplier=m,source_high=high,fit=f,lower_tail=tail,null_seed_start=nullseed,nulls=nulls,actual_emissions=int(sum(stats(actual,1)[0])+sum(stats(actual,1)[2])))
 (O/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n');np.savez_compressed(O/(name+'.npz'),actual=actual,nulls=np.array(outputs,dtype=np.uint8));print(name,score,tail,flush=True);return record

def check():
 # A complete binary tree with29leaves and depth<=5 has these only integer depth counts.
 profiles=[]
 for c1 in range(3):
  for c2 in range(5):
   for c3 in range(9):
    for c4 in range(17):
     c5=29-c1-c2-c3-c4
     if c5>=0 and 16*c1+8*c2+4*c3+2*c4+c5==32:profiles.append([c1,c2,c3,c4,c5])
 assert profiles==[[0,0,0,3,26],[0,0,1,0,28]],profiles
 checks=[]
 for j,(m,h) in enumerate([(2,[0,7,19]),(4,[13]),(1,[])]):
  x=generate(609000+j,m,h);st=stats(x,0);f=fit(x)
  for row,(_,k) in zip(f['profiles'],shapes):
   best=max(ll(st,row['multiplier'],z) for z in itertools.combinations(range(29),k));assert abs(best-row['train_ll'])<1e-8
  for q in range(len(P)):assert np.array_equal(x[cuts[q]+1:cuts[q+1]]==x[cuts[q]:cuts[q+1]-1],masks[q])
  checks.append(f)
 # Independently sum per-symbol log probabilities and compare sufficient statistics.
 for parity in [0,1]:
  for m,h in [(2,[0,7,19]),(4,[13])]:
   total=0.;w=[m if a in h else 1 for a in range(29)]
   for j in range(parity,len(P),2):
    v=x[cuts[j]:cuts[j+1]];total+=math.log(w[v[0]]/32)
    for a,b in zip(v[:-1],v[1:]):
     if a!=b:total+=math.log(w[b]/(32-w[a]))
   assert abs(total-ll(stats(x,parity),m,h))<1e-7
 (O/'checks.json').write_text(json.dumps(dict(profiles=profiles,optimizer_checks=checks,input_sha256=hashlib.sha256(F.read_bytes()).hexdigest()),indent=2)+'\n')
 print('profiles, exhaustive optimizer, scalar likelihood and all masks PASS',flush=True)
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='check':check()
 elif mode=='pilot':panel(610000,2,[0,7,19],9,619000,'pilot')
 elif mode=='controls':
  specs=[(2,[0,7,19]),(2,[3,14,28]),(4,[13]),(4,[27])]+[(1,[])]*4
  results=[panel(610000+j,m,h,99,620000+j*1000,'control-'+str(j)) for j,(m,h) in enumerate(specs)]
  for r,(m,h) in zip(results[:4],specs[:4]):assert r['fit']['best']['multiplier']==m and r['fit']['best']['high']==h and r['fit']['best']['held_gain']>0
  print('positive gates PASS; ordinary adequacy ranks',[x['lower_tail'] for x in results[4:]])
 elif mode=='actual':panel(None,None,None,499,630000,'actual')
