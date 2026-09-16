import pathlib,json,numpy as np,ctypes,math,gzip,time,datetime,sys
R=pathlib.Path(__file__).parent;ROOT=R.parents[3];lib=ctypes.CDLL(str(R/'fit.dylib'));I=np.ctypeslib.ndpointer(np.int32,flags='C_CONTIGUOUS');F=np.ctypeslib.ndpointer(np.float64,flags='C_CONTIGUOUS');L=np.ctypeslib.ndpointer(np.int64,flags='C_CONTIGUOUS');lib.fit.argtypes=[I,ctypes.c_ulonglong,I,F,L]
def gate():
 assert not(R.parent.parent/'STOP').exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def dump(name,x):(R/(name+'.json')).write_text(json.dumps(x,indent=2))
def counts(vs):return np.array([np.bincount(np.array(v[:-1])*29+v[1:],minlength=841).reshape(29,29) for v in vs])
def baseline(vs):
 tr=counts(vs)[::2].sum(0);hist=np.bincount(np.concatenate([np.array(v) for v in vs[::2]]),minlength=29);w=(hist+.5)/(hist.sum()+14.5);r=(np.trace(tr)+.5)/(tr.sum()+1);P=np.empty((29,29))
 for x in range(29):P[x]=w/(1-w[x])*(1-r);P[x,x]=r
 assert np.allclose(P.sum(1),1);return P,w,float(r)
def predictor(c,g):
 tab=np.zeros((17,17),dtype=int)
 for x in range(29):
  for y in range(29):tab[g[x],g[y]]+=c[x,y]
 T=(tab+1)/(tab.sum(1)[:,None]+17);P=np.empty((29,29));em=0
 for x in range(29):
  for y in range(29):
   a,b=g[x],g[y];e=1 if b>=12 else(.5 if a!=b else(.085 if x==y else .915));P[x,y]=T[a,b]*e;em+=c[x,y]*math.log(e)
 assert np.allclose(P.sum(1),1,atol=1e-12);objective=em+sum(math.lgamma(17)-math.lgamma(sum(row)+17)+sum(math.lgamma(int(n)+1) for n in row) for row in tab)
 return P,T,tab,float(objective)
def fit(vs,name):
 path=R/'fits'/(name+'.json.gz')
 if path.exists():
  with gzip.open(path,'rt') as f:return json.load(f)
 gate();start=time.monotonic();ct=counts(vs);tr=ct[::2].sum(0).astype(np.int32);he=ct[1::2].sum(0);b,w,r=baseline(vs);maps=np.empty(116,dtype=np.int32);scores=np.empty(4,dtype=np.float64);counters=np.empty(8,dtype=np.int64);lib.fit(tr.ravel(),330829,maps,scores,counters);rows=[]
 for i,g in enumerate(maps.reshape(4,29)):
  assert sorted(np.bincount(g,minlength=17))==[1]*5+[2]*12;P,T,tab,obj=predictor(tr,g);assert abs(obj-scores[i])<1e-7;gain=np.log(P/b);per=(ct*gain).sum((1,2));rows.append(dict(mapping=g.tolist(),training_objective=obj,T=T.tolist(),symbol_probabilities=P.tolist(),train_counts=tab.tolist(),held_gain=float((he*gain).sum()/he.sum()),perpage_total_gain=per.tolist(),valid_proposals=int(counters[2*i]),accepted=int(counters[2*i+1])))
 choice=int(np.argmax(scores));out=dict(name=name,cipher=[list(map(int,v)) for v in vs],rows=rows,selected_start=choice,score=rows[choice]['held_gain'],baseline=b.tolist(),baseline_weights=w.tolist(),baseline_repeat=r,perpage_counts=ct.tolist(),seconds=time.monotonic()-start)
 with gzip.open(path,'wt') as f:json.dump(out,f)
 return out

def gen_m1(lengths,w,r,rng):
 vs=[]
 for n in lengths:
  v=[int(rng.choice(29,p=w))]
  for i in range(1,n):
   if rng.random()<r:v.append(v[-1])
   else:
    q=w.copy();q[v[-1]]=0;q/=q.sum();v.append(int(rng.choice(29,p=q)))
  vs.append(v)
 return vs

def control(lengths,target,ix):
 rng=np.random.default_rng(330829+ix);g=np.array([i//2 for i in range(24)]+list(range(12,17)));rng.shuffle(g);bins=[np.flatnonzero(g==i) for i in range(17)];alpha=.2 if ix<6 else 2;Q=np.zeros((17,17))
 for i in range(17):Q[i,np.arange(17)!=i]=rng.dirichlet(np.full(16,alpha))
 A=Q.T-np.eye(17);A[-1]=1;rhs=np.zeros(17);rhs[-1]=1;pi=np.linalg.solve(A,rhs);assert np.all(pi>0) and np.allclose(pi@Q,pi);er=np.array([.085]*12+[1.]*5);d=target/float(pi@er);assert 0<d<1;T=d*np.eye(17)+(1-d)*Q;assert np.allclose(pi@T,pi);assert abs(float(np.sum(pi*np.diag(T)*er))-target)<1e-12
 vs=[];classes=[];draws=[];rawchoices=[]
 for n in lengths:
  u=rng.random((n,3));latent=[];v=[];raw=[];z=int(np.searchsorted(np.cumsum(pi),u[0,0]))
  for i in range(n):
   if i:z=int(np.searchsorted(np.cumsum(T[z]),u[i,0]))
   b=bins[z];x=int(b[min(int(u[i,1]*len(b)),len(b)-1)]);raw.append(x)
   if v and x==v[-1] and len(b)>1 and u[i,2]<.83:x=int(b[0] if x==b[1] else b[1])
   v.append(x);latent.append(z)
  assert np.array_equal(g[v],latent);vs.append(v);classes.append(latent);draws.append(u);rawchoices.append(raw)
 meta=dict(mapping=g.tolist(),bins=[b.tolist() for b in bins],Q=Q.tolist(),T=T.tolist(),pi=pi.tolist(),diagonal=d,target_repeat=target,expected_repeat=float(pi@er*d),alpha=alpha,classes=classes,rawchoices=rawchoices)
 np.savez_compressed(R/'controls'/(str(ix)+'-draws.npz'),uniform=np.concatenate(draws),lengths=lengths);dump('controls/'+str(ix)+'-generator',meta);return vs,meta

def setup():
 for d in ['fits','controls']:(R/d).mkdir(exist_ok=True)
 p=ROOT/'exploration/persistent-01/worker-f/F06-maps.json';maps=json.load(open(p));assert len(maps)==45;vs=[m['indices'] for m in maps];tr=counts(vs)[::2].sum(0);target=float(np.trace(tr)/tr.sum());dump('input',dict(pages=[m['page'] for m in maps],maps=maps,train_pages=[m['page'] for m in maps[::2]],held_pages=[m['page'] for m in maps[1::2]],target_repeat=target,lengths=list(map(len,vs))));return vs,list(map(len,vs)),target

def pilot():
 vs,lengths,target=setup();c,meta=control(lengths,target,0);r=fit(c,'control-0');dump('pilot',dict(seconds=r['seconds'],projected440fit_seconds=440*r['seconds'],held_control_gain=r['score'],selected=r['selected_start'],model_pattern='12doubleton+5singleton'));print('PILOT',r['seconds'],r['score'],flush=True)

def run():
 vs,lengths,target=setup();rng=np.random.default_rng(330830);ctls=[]
 for ix in range(12):
  c,meta=control(lengths,target,ix);r=fit(c,'control-'+str(ix));w=np.array(r['baseline_weights']);repeat=r['baseline_repeat'];null=[]
  for j in range(19):
   a=fit(gen_m1(lengths,w,repeat,rng),'control-'+str(ix)+'-null'+str(j));null.append(dict(name=a['name'],score=a['score']))
  g=r['rows'][r['selected_start']]['mapping'];truth=meta['mapping'];pairs=sum(g[x]==g[y] and truth[x]==truth[y] for x in range(29) for y in range(x+1,29));cc=counts(c);oracleP,oracleT,oraclect,oracleobj=predictor(cc[::2].sum(0),truth);oracle_gain=float((cc[1::2].sum(0)*np.log(oracleP/np.array(r['baseline']))).sum()/cc[1::2].sum());row=dict(oracle_gain=oracle_gain,oracle_training_objective=oracleobj,selected_training_objective=r['rows'][r['selected_start']]['training_objective'],control=ix,score=r['score'],tail=(1+sum(x['score']>=r['score'] for x in null))/20,recovered_true_pairs=pairs,total_true_pairs=12,actual_repeat=sum(sum(a==b for a,b in zip(v,v[1:])) for v in c)/sum(len(v)-1 for v in c),expected_repeat=meta['expected_repeat'],null=null);ctls.append(row);dump('control-results',ctls);print('CONTROL',ix,pairs,r['score'],row['tail'],flush=True)
 real=fit(vs,'real');null=[]
 for j in range(199):
  a=fit(gen_m1(lengths,np.array(real['baseline_weights']),real['baseline_repeat'],rng),'real-null'+str(j));null.append(dict(name=a['name'],score=a['score']))
 dump('result',dict(real_score=real['score'],real_tail=(1+sum(x['score']>=real['score'] for x in null))/200,selected_start=real['selected_start'],control_detected=sum(x['tail']<=.05 and x['score']>0 for x in ctls),control_total=12,controls=ctls,null=null,fit_packets=440,nominal_proposals=440*4*1500,pattern='12doubleton+5singleton',rng_after=rng.bit_generator.state));print('REAL',real['score'],(1+sum(x['score']>=real['score'] for x in null))/200,flush=True)
if __name__=='__main__':pilot() if sys.argv[1]=='pilot' else run()
