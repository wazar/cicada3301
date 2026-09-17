"""One fixed reversible swap kernel and parallel conditional comparison."""
import pathlib,json,hashlib,random,itertools,sys
import numpy as np
O=pathlib.Path(__file__).resolve().parent;R=O.parents[3]
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def step(x,i,j,eq):
 x[i],x[j]=x[j],x[i]
 valid=all((x[e]==x[e+1])==eq[e] for e in {i-1,i,j-1,j} if 0<=e<len(x)-1)
 if not valid:x[i],x[j]=x[j],x[i]
 return valid
def walk(start,nsteps,seed):
 x=list(start);free=[i for i,a in enumerate(x) if a!=0];eq=[a==b for a,b in zip(x,x[1:])];rng=random.Random(seed)
 pairs=np.zeros((nsteps,2),dtype=np.uint16);ok=np.zeros(nsteps,dtype=np.bool_);changed=0
 assert len(x)<65536 and free
 for t in range(nsteps):
  i=free[rng.randrange(len(free))];j=free[rng.randrange(len(free))];pairs[t]=[i,j];diff=x[i]!=x[j];ok[t]=step(x,i,j,eq);changed+=int(ok[t] and diff)
 assert sorted(x)==sorted(start) and [a==0 for a in x]==[a==0 for a in start] and [a==b for a,b in zip(x,x[1:])]==eq
 return x,pairs,ok,dict(proposals=nsteps,accepted=int(ok.sum()),changed=changed,hamming_from_start=sum(a!=b for a,b in zip(start,x)))
def selftest():
 cases=[]
 for c in [(0,1,2,1,2,3),(1,1,0,2,3,2),(0,1,2,3)]:
  eq=tuple(a==b for a,b in zip(c,c[1:]));fm=tuple(a==0 for a in c)
  states=sorted({v for v in itertools.permutations(c) if tuple(a==0 for a in v)==fm and tuple(a==b for a,b in zip(v,v[1:]))==eq});ix={v:i for i,v in enumerate(states)};free=[i for i,x in enumerate(c) if x!=0];den=len(free)**2
  K=np.zeros((len(states),len(states)),dtype=np.int64)
  for s,v in enumerate(states):
   for i in free:
    for j in free:
     x=list(v);step(x,i,j,eq);K[s,ix[tuple(x)]]+=1
  assert np.all(K.sum(axis=1)==den) and np.array_equal(K,K.T)
  Q=K@K;tot=0;low=0;triples=0
  for a,b,d in itertools.product(range(len(states)),repeat=3):
   n=sum(int(Q[a,h])*int(Q[h,b])*int(Q[h,d]) for h in range(len(states)))
   assert n==sum(int(Q[b,h])*int(Q[h,a])*int(Q[h,d]) for h in range(len(states)))
   assert n==sum(int(Q[d,h])*int(Q[h,b])*int(Q[h,a]) for h in range(len(states)))
   tot+=n;low+=n*int(1+int(b>=a)+int(d>=a)<=1);triples+=1
  expected=len(states)*den**6;assert tot==expected and 3*low<=tot
  # Actual implementation trace replay, including its rejected stays.
  out,pairs,ok,diag=walk(c,100,98765);x=list(c)
  for (i,j),accepted in zip(pairs,ok):assert step(x,int(i),int(j),eq)==bool(accepted)
  assert x==out
  cases.append(dict(input=c,states=len(states),proposal_denominator=den,triples=triples,total_integer_mass=tot,rank_le_one_third_numerator=low,denominator=tot,trace=diag))
 (O/'selftest.json').write_text(json.dumps(dict(passed=True,cases=cases,code_sha256=H(pathlib.Path(__file__))),indent=2)+'\n');print(json.dumps(cases))
def prepare():
 src=R/'exploration/persistent-02/decoder/reset-feedback/inputs.json';d=json.loads(src.read_text());controls=[c for c in d['controls'] if c['k']==8 and c['source'] in ['guest','mill','shelley','blake']];assert len(controls)==4
 records=[dict(id='actual-body',kind='actual',cipher=d['actual']['panels'][0],ends=d['actual']['ends'],reset_before=d['actual']['reset_before'])]
 records += [dict(id=c['source']+'-k8',kind='control',cipher=c['cipher'],ends=c['ends'],reset_before=c['reset_before'],truth=c['truth'],seed=c['seed'],source_control_id=c['id']) for c in controls]
 assert all(len(c['cipher'])==716 for c in records);assert not (O/'panels.json').exists();cases=[];traces={}
 for ix,c in enumerate(records):
  original=c.pop('cipher');n=100*len(original);seed=2026092400+100*ix;hub,pa,ok,di=walk(original,n,seed);traces[f'case{ix}_hub_pairs']=pa;traces[f'case{ix}_hub_accepted']=ok;panels=[original];meta=[dict(role='hub',seed=seed,**di)]
  for j in range(1,20):
   out,pa,ok,di=walk(hub,n,seed+j);panels.append(out);traces[f'case{ix}_spoke{j:02}_pairs']=pa;traces[f'case{ix}_spoke{j:02}_accepted']=ok;meta.append(dict(role=f'spoke{j}',seed=seed+j,hamming_from_actual=sum(a!=b for a,b in zip(out,original)),**di))
  cases.append(dict(**c,panels=panels,hub=hub,prefix_length=249,traces=meta));print(c['id'],'frozen',flush=True)
 trace=O/'proposal-traces.npz';np.savez_compressed(trace,**traces)
 out=dict(source=str(src.relative_to(R)),source_sha256=H(src),sampler_sha256=H(pathlib.Path(__file__)),prereg_sha256=H(O/'PREREG.md'),trace_file=str(trace.relative_to(R)),trace_sha256=H(trace),models=d['models'],band=d['actual']['band'],cases=cases)
 (O/'panels.json').write_text(json.dumps(out,separators=(',',':'))+'\n');print('panels',H(O/'panels.json'))
if __name__=='__main__':
 if sys.argv[1]=='selftest':selftest()
 elif sys.argv[1]=='prepare':prepare()
