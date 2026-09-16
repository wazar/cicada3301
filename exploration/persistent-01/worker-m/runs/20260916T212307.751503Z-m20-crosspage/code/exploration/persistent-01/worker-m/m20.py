import pathlib,json,numpy as np,hashlib,gzip,datetime,time,zlib,itertools
R=pathlib.Path(__file__).parent
D=np.array([[1,a,b] for a in range(29) for b in range(29)]+[[0,1,b] for b in range(29)]+[[0,0,1]],dtype=np.int64)
DI={tuple(v):i for i,v in enumerate(D.tolist())};rng=np.random.default_rng(2026091751)
def gate():
 assert not (R.parent/'STOP').exists()
 assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,9,17,3,30,37,tzinfo=datetime.timezone.utc)
def inv(m):
 a=np.c_[m.copy()%29,np.eye(3,dtype=int)]
 for i in range(3):
  j=next(j for j in range(i,3) if a[j,i]);a[[i,j]]=a[[j,i]];a[i]=a[i]*pow(int(a[i,i]),-1,29)%29
  for k in range(3):
   if k!=i:a[k]=(a[k]-a[k,i]*a[i])%29
 return a[:,3:]
def det(m):return int(np.dot(m[0],np.cross(m[1],m[2])))%29
def norm(v):return tuple((v*pow(int(next(x for x in v if x)),-1,29)%29).tolist())
def blocks(v,p):
 n=(len(v)-p)//3;ix=np.arange(p,p+3*n).reshape(-1,3);return v[ix],ix

def search(vs,detail=False):
 cached=[]
 for v in vs[:2]:
  cp=[]
  for p in range(3):
   b,ix=blocks(v,p);y=b@D.T%29;t=2*len(b)//3;cp.append((b,ix,y,t))
  cached.append(cp)
 options=[]
 for phases in itertools.product(range(3),repeat=2):
  parts=[cached[j][p] for j,p in enumerate(phases)];fit=np.concatenate([x[2][:x[3]] for x in parts]);val=np.concatenate([x[2][x[3]:] for x in parts]);y=np.concatenate([x[2] for x in parts]);cnt=np.bincount((fit+29*np.arange(871)).ravel(),minlength=871*29).reshape(871,29)+1;q=cnt/cnt.sum(1)[:,None]
  gains=np.log(29*q[np.arange(871)[:,None],val.T]).mean(1);selected=[]
  for idx in np.argsort(-gains,kind='stable'):
   if len(selected)<2 or det(D[selected+[int(idx)]]):selected.append(int(idx))
   if len(selected)==3:break
  z=y[:,selected];cnt2=np.array([np.bincount(z[:,j],minlength=29)+1 for j in range(3)]);q2=cnt2/cnt2.sum(1)[:,None]
  o=dict(phases=list(phases),selection_gain=float(gains[selected].sum()),selected=selected,q=q2.tolist(),train_blocks=[len(x[0]) for x in parts],fit_blocks=[x[3] for x in parts])
  if detail:o.update(all_validation_gains=gains.tolist(),train_outputs=z.tolist(),train_indices=[x[1].tolist() for x in parts])
  options.append(o)
 oi=max(range(9),key=lambda i:options[i]['selection_gain']);best=options[oi];matrix=D[best['selected']];inverse=inv(matrix);q=np.array(best['q']);test=[];cut=len(vs[2])//2
 for p in range(3):
  b,ix=blocks(vs[2],p);z=b@matrix.T%29;assert np.array_equal(z@inverse.T%29,b);pre=ix[:,-1]<cut;suf=ix[:,0]>=cut;ll=np.log(29*q[np.arange(3)[:,None],z.T]).mean(0)
  o=dict(phase=p,prefix_gain=float(ll[pre].mean()),suffix_gain=float(ll[suf].mean()),prefix_blocks=int(pre.sum()),suffix_blocks=int(suf.sum()))
  if detail:o.update(indices=ix.tolist(),outputs=z.tolist(),prefix_mask=pre.tolist(),suffix_mask=suf.tolist(),discarded_runes=sorted(set(range(len(vs[2])))-set(ix[pre|suf].ravel().tolist())))
  test.append(o)
 ti=max(range(3),key=lambda i:test[i]['prefix_gain']);out=dict(score=test[ti]['suffix_gain'],train_option=oi,train_phases=best['phases'],selected=best['selected'],test_phase=ti,train_options=options,test_options=test,matrix=matrix.tolist(),inverse=inverse.tolist())
 if detail:
  out['stats']={}
  for i,t in enumerate(test):
   z=np.array(t['outputs'])[t['suffix_mask']].ravel();counts=np.bincount(z,minlength=29);out['stats'][str(i)]=dict(ioc_times_n=float((counts*(counts-1)).sum()/max(1,len(z)-1)),min32distinct=min(len(set(z[j:j+32])) for j in range(max(1,len(z)-31))),zlib_bytes=len(zlib.compress(bytes(z.tolist()))),runes=len(z),non_english_lm='N/A: no language model')
 return out

def params(vs):
 out=[]
 for v in vs:
  pre=v[:len(v)//2];w=np.bincount(pre,minlength=29)+1;w=w/w.sum();rep=float(np.mean(pre[1:]==pre[:-1]));rows=[]
  for i in range(29):
   row=w.copy();row[i]=0;row=row/row.sum()*(1-rep);row[i]=rep;rows.append(np.cumsum(row))
  out.append((w,rep,np.array(rows)))
 return out

def simulate(vs,pars):
 out=[]
 for vv,(w,rep,mat) in zip(vs,pars):
  us=rng.random(len(vv));v=np.empty(len(vv),dtype=int);v[0]=np.searchsorted(np.cumsum(w),us[0])
  for i in range(1,len(v)):v[i]=np.searchsorted(mat[v[i-1]],us[i])
  out.append(v)
 return out

def save(name,data):
 with gzip.open(R/(name+'.json.gz'),'wt') as f:json.dump(data,f)
def evaluate(name,vs,n):
 gate();state=rng.bit_generator.state;real=search(vs,True);par=params(vs);null=[];start=time.monotonic()
 for i in range(n):
  if i%20==0:gate()
  null.append(search(simulate(vs,par)))
 out=dict(name=name,cipher=[v.tolist() for v in vs],result=real,null=null,null_count=n,tail=(1+sum(x['score']>=real['score'] for x in null))/(n+1),rng_before=state,rng_after=rng.bit_generator.state,null_parameters=[dict(weights=w.tolist(),repeat=r,cumulative_matrix=m.tolist()) for w,r,m in par],seconds=time.monotonic()-start)
 save(name,out);print(name,real['score'],out['tail'],out['seconds'],flush=True);return out

def main():
 gate();maps=[m for m in json.load(open(R.parent/'worker-f/F06-maps.json')) if m['page'] in [0,1,2]];assert [m['page'] for m in maps]==[0,1,2];vs=[np.array(m['indices']) for m in maps];lengths=list(map(len,vs));save('M20-maps',maps)
 A='ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ';sources=[]
 for f in pathlib.Path('audit/parallel-01/reference/sources').glob('solved_*.txt'):
  b=f.read_bytes();p=np.array([A.index(c) for c in b.decode() if c in A]);sources.append(dict(path=str(f),sha256=hashlib.sha256(b).hexdigest(),plain=p))
 sources.sort(key=lambda s:(-len(s['plain']),s['path']));controls=[];base=np.array([[1,1,1],[1,2,3],[1,4,9]])
 # Each control training pages use disjoint spans of one source; held page comes from a different source. Reverse and rotate registers across controls.
 for k in range(6):
  tr=sources[k%2];te=sources[2 if k>=4 else 1-k%2];offset=15*(k//2);tp=7*(k//2);ph=[k%3,(k+1)%3,(k+2)%3];K=(np.diag([1+k,3+k,9+k])@base)%29;KI=inv(K);shift=np.array([k,2*k+1,5*k+2])%29;assert np.array_equal(K@KI%29,np.eye(3,dtype=int));cursor=offset;cv=[];spans=[];truthplain=[]
  for j,(n,p) in enumerate(zip(lengths,ph)):
   nb=(n-p)//3;s=tr if j<2 else te;start=cursor if j<2 else tp;plain=s['plain'][start:start+nb*3];assert len(plain)==nb*3
   if j<2:cursor+=nb*3
   cipher=(plain.reshape(-1,3)@K.T+shift)%29;assert np.array_equal((cipher-shift)@KI.T%29,plain.reshape(-1,3));v=rng.integers(0,29,size=n);v[p:p+nb*3]=cipher.ravel();cv.append(v);truthplain.append(plain.tolist());spans.append(dict(source=s['path'],sha256=s['sha256'],start=start,end=start+len(plain),phase=p,leading=list(range(p)),trailing=list(range(p+nb*3,n))))
  r=evaluate('M20-control-'+str(k),cv,199);trueids={DI[norm(x)] for x in KI};c=dict(control=k,tail=r['tail'],score=r['result']['score'],direction_recovery=len(trueids&set(r['result']['selected'])),true_directions=sorted(trueids),phase_recovered=r['result']['train_phases']+[r['result']['test_phase']]==ph,true_phases=ph,selected_phases=r['result']['train_phases']+[r['result']['test_phase']],source_spans=spans,K=K.tolist(),inverse=KI.tolist(),affine_shift=shift.tolist(),plain=truthplain,exact_reencryption=True);controls.append(c);(R/'M20-controls.json').write_text(json.dumps(controls,indent=2))
 power=dict(controls=6,detected_at_01=sum(c['tail']<=.01 for c in controls),detected_at_05=sum(c['tail']<=.05 for c in controls),full_direction_recovery=sum(c['direction_recovery']==3 for c in controls),full_phase_recovery=sum(c['phase_recovered'] for c in controls));print('CONTROL_POWER',power,flush=True)
 real=evaluate('M20-real',vs,999);summary=dict(power=power,real_tail=real['tail'],real_score=real['result']['score'],real_train_phases=real['result']['train_phases'],real_test_phase=real['result']['test_phase'],matrix=real['result']['matrix'],inverse=real['result']['inverse'],controls=[{k:v for k,v in c.items() if k not in ['plain']} for c in controls],null_count=999,control_null_count=1194,total_search_calls=2200,seed=2026091751,input_lengths=lengths,reserved_pages_read=[],status='PREDICTIVE_CANDIDATE' if real['tail']<=.01 else ('MISS_WITH_MEASURED_POWER' if power['detected_at_01'] else 'UNDERPOWERED_REAL_DESCRIPTIVE'))
 (R/'M20-result.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
